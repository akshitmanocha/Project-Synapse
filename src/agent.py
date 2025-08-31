"""
AGENT MODULE SPEC (LangGraph skeleton)

Purpose:
- Provide a minimal, testable framework for a LangGraph-based agent that
	iteratively reasons, selects a tool to act, observes the outcome, and repeats
	until the problem is solved (Reason-Act-Observe loop).

This implementation wires up a minimal, runnable loop using:
- langgraph StateGraph for control flow
- langchain_groq ChatGroq (model: "openai/gpt-oss-120b") for the reasoning step
- src.tools for simulated tool calls

Core components in this file:
- AgentState (TypedDict): The shared state passed between nodes.
	keys:
		- input: str — the user problem description.
		- steps: list — intermediate actions/observations (append-only log).
		- plan: str | None — final structured plan once the agent decides to finish.
		- action: dict | None — the next action chosen by the Reasoning node
			(e.g., {"tool_name": "check_traffic", "parameters": {"route": "..."}}).
		- observation: any — the last tool result.
		- done: bool — set True to stop the loop.

- Nodes:
	1) reasoning_node(state: AgentState) -> AgentState
		 - Chooses next action or sets done and plan.
	2) tool_exec_node(state: AgentState) -> AgentState
		 - Executes the chosen tool and records observation.

- Graph wiring:
	- The graph alternates between reasoning_node and tool_exec_node
		until state['done'] is True.

Note:
- Keep prompts and tool IO simple and deterministic; expand in later milestones.
"""

from __future__ import annotations
import threading

from typing import Any, Dict, List, Optional, TypedDict, Callable, Tuple
import os
import json
import re

from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
import concurrent.futures

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from . import tools as sim_tools


class AgentState(TypedDict, total=False):
		"""Shared agent state across graph nodes.

		Fields:
				input: Problem description provided by the user.
				steps: Append-only list of intermediate steps (actions/observations).
				plan: Final plan text when the agent decides to finish.
				action: The next action dict chosen by the reasoning node.
				observation: The last tool result or observation.
				done: Whether the agent has reached a terminal state.
		"""

		input: str
		steps: List[Dict[str, Any]]
		plan: Optional[str]
		action: Optional[Dict[str, Any]]
		observation: Optional[Any]
		done: bool


def _load_system_prompt() -> str:
	"""Load the system prompt from prompts/system_prompt.txt (if available)."""
	# Resolve to project root relative to this file
	here = os.path.dirname(os.path.dirname(__file__))
	prompt_path = os.path.join(here, "prompts", "system_prompt.txt")
	try:
		with open(prompt_path, "r", encoding="utf-8") as f:
			return f.read()
	except Exception:
		# Minimal fallback
		return (
			"You are Synapse. Produce a Thought then an Action JSON with keys "
			"tool_name and parameters. Use finish when done."
		)


def _get_llm() -> ChatGoogleGenerativeAI:
	"""Return a configured Google Gemini chat model. Relies on GEMINI_API_KEY in env."""
	# Best-effort .env loading
	load_dotenv(override=False)
	# Ensure key exists to avoid opaque hangs
	if not os.getenv("GEMINI_API_KEY"):
		raise RuntimeError("GEMINI_API_KEY not set in environment.")
	# Instantiate LLM lazily - using Gemini model
	return ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=os.getenv("GEMINI_API_KEY"))


def _format_history(steps: List[Dict[str, Any]]) -> str:
	"""Render previous steps succinctly for the model context."""
	if not steps:
		return "(no prior steps)"
	lines = []
	for i, s in enumerate(steps, 1):
		act = s.get("action") or {}
		obs = s.get("observation")
		thought = s.get("thought")
		lines.append(
			f"Step {i}:\n- Thought: {thought}\n- Action: {json.dumps(act, ensure_ascii=False)}\n- Observation: {json.dumps(obs, ensure_ascii=False)}"
		)
	return "\n\n".join(lines)


def _parse_action(text: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
	"""Extract the action JSON and optional preceding Thought from the model output.

	Returns (action_dict, thought_text). If parsing fails, action_dict is None.
	"""
	# Capture Thought: ... up to Action:
	thought_match = re.search(r"Thought\s*:\s*(.*?)\s*Action\s*:\s*", text, re.DOTALL | re.IGNORECASE)
	thought = thought_match.group(1).strip() if thought_match else None

	# Find the first JSON object after Action:
	after = text[thought_match.end():] if thought_match else text
	# Heuristic: find the first {...} block
	brace_stack = []
	start = None
	for idx, ch in enumerate(after):
		if ch == '{':
			brace_stack.append('{')
			if start is None:
				start = idx
		elif ch == '}':
			if brace_stack:
				brace_stack.pop()
				if not brace_stack and start is not None:
					block = after[start:idx+1]
					try:
						data = json.loads(block)
						return data, thought
					except Exception:
						break
	# Fallback: try to parse any JSON object in text
	try:
		m = re.search(r"\{.*\}", text, re.DOTALL)
		if m:
			data = json.loads(m.group(0))
			return data, thought
	except Exception:
		pass
	return None, thought


def _tool_registry() -> Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]]:
	"""Return a registry of tool_name -> callable(params) mapping with adapters.

	Each callable accepts a parameters dict and returns an observation dict.
	"""
	def adapt_check_traffic(p: Dict[str, Any]) -> Dict[str, Any]:
		# Accept either 'route' or 'route_id'
		v = p.get("route") or p.get("route_id")
		return sim_tools.check_traffic(route_id=str(v) if v is not None else "")

	def adapt_get_merchant_status(p: Dict[str, Any]) -> Dict[str, Any]:
		return sim_tools.get_merchant_status(merchant_id=str(p.get("merchant_id", "")))

	def adapt_notify_customer(p: Dict[str, Any]) -> Dict[str, Any]:
		return sim_tools.notify_customer(
			customer_id=str(p.get("customer_id", "")),
			message=str(p.get("message", "")),
		)

	def adapt_re_route_driver(p: Dict[str, Any]) -> Dict[str, Any]:
		# Our tools expect new_route as a dict; accept a string description too.
		new_task_desc = p.get("new_task_description") or p.get("description")
		new_route = p.get("new_route") or ({"description": new_task_desc} if new_task_desc else None)
		return sim_tools.re_route_driver(
			driver_id=str(p.get("driver_id", "")),
			new_route=new_route or {},
		)

	def adapt_get_nearby_merchants(p: Dict[str, Any]) -> Dict[str, Any]:
		# Best effort: support location as "lat,lon" string, or keys lat/lng
		lat = p.get("lat")
		lng = p.get("lng") or p.get("lon")
		location = p.get("location")
		if (lat is None or lng is None) and isinstance(location, str) and "," in location:
			try:
				parts = [s.strip() for s in location.split(",", 1)]
				lat = float(parts[0]); lng = float(parts[1])
			except Exception:
				pass
		try:
			return sim_tools.get_nearby_merchants(float(lat), float(lng))
		except Exception:
			return {"tool_name": "get_nearby_merchants", "status": "error", "error_message": "invalid or missing lat/lng"}

	return {
		"check_traffic": adapt_check_traffic,
		"get_merchant_status": adapt_get_merchant_status,
		"notify_customer": adapt_notify_customer,
		"re_route_driver": adapt_re_route_driver,
		"get_nearby_merchants": adapt_get_nearby_merchants,
		# Special pseudo-tool handled in tool_exec_node: "finish"
	}


def reasoning_node(state: AgentState) -> AgentState:
	"""Reasoning node: decide next action or finish via LLM.

	Expects the LLM to produce:
	Thought: ...
	Action:
	{"tool_name": "...", "parameters": { ... }}
	"""
	# Initialize LLM; handle missing/invalid credentials gracefully
	try:
		llm = _get_llm()
	except Exception as e:
		state["done"] = True
		state["plan"] = f"LLM init error: {e}"
		state["action"] = None
		return state
	sys_prompt = _load_system_prompt()

	history = _format_history(state.get("steps", []))
	user_problem = state.get("input", "")

	messages = [
		SystemMessage(content=sys_prompt),
		HumanMessage(content=(
			"Problem: " + user_problem + "\n\n" +
			"Context (previous steps):\n" + history + "\n\n" +
			"Decide the next best single tool call."
		)),
	]

	# Run the LLM call with a protective timeout
	def _call():
		return llm.invoke(messages)

	try:
		with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
			fut = ex.submit(_call)
			resp = fut.result(timeout=30)
			text = getattr(resp, "content", str(resp))
	except concurrent.futures.TimeoutError:
		state["done"] = True
		state["plan"] = "LLM call timed out. Please check network or GROQ availability."
		state["action"] = None
		return state
	except Exception as e:
		# If LLM fails, attempt to finish gracefully
		state["done"] = True
		state["plan"] = f"LLM error: {e}"
		state["action"] = None
		return state

	action, thought = _parse_action(text or "")

	# If model decides to finish via explicit tool
	if action and action.get("tool_name") == "finish":
		final_plan = action.get("parameters", {}).get("final_plan")
		state["done"] = True
		state["plan"] = str(final_plan) if final_plan is not None else ""
		state["action"] = None
		# Log the final thought
		steps = state.setdefault("steps", [])
		steps.append({"thought": thought, "action": {"tool_name": "finish", "parameters": {"final_plan": state["plan"]}}, "observation": None})
		return state

	# Otherwise, ensure we have a valid action
	if not action or "tool_name" not in action or "parameters" not in action:
		# Fallback: ask the model to try again once by nudging format
		nudge_messages = messages + [
			HumanMessage(content="Your previous response did not contain a valid Action JSON. Respond ONLY with Action JSON next."),
		]
		try:
			resp2 = llm.invoke(nudge_messages)
			text2 = getattr(resp2, "content", str(resp2))
			action2, thought2 = _parse_action(text2 or "")
			action = action2 or action
			thought = thought2 or thought
		except Exception:
			pass

	# If still invalid, terminate gracefully
	if not action or "tool_name" not in action:
		state["done"] = True
		state["plan"] = (state.get("plan") or "Terminating due to invalid action from model.")
		state["action"] = None
		steps = state.setdefault("steps", [])
		steps.append({"thought": thought, "action": None, "observation": {"status": "error", "message": "invalid action"}})
		return state

	# Record chosen action and let the tool node execute it
	state["action"] = action
	# Keep for traceability in steps; the observation will be filled by the tool node
	steps = state.setdefault("steps", [])
	steps.append({"thought": thought, "action": action, "observation": None})
	state["done"] = False
	return state


def tool_exec_node(state: AgentState) -> AgentState:
	"""Tool execution node: run the selected tool and capture observation."""
	action = state.get("action") or {}
	tool_name = action.get("tool_name")
	params = action.get("parameters") or {}

	# Handle finish pseudo-tool (already finalized plan in reasoning node)
	if tool_name == "finish":
		state["observation"] = None
		state["action"] = None
		return state

	registry = _tool_registry()
	obs: Any
	if tool_name in registry:
		try:
			obs = registry[tool_name](params)
		except Exception as e:
			obs = {"tool_name": tool_name, "status": "error", "error_message": str(e)}
	else:
		obs = {"tool_name": tool_name, "status": "error", "error_message": f"unknown tool: {tool_name}"}

	state["observation"] = obs
	# Update last step's observation (append-only steps list)
	steps = state.get("steps", [])
	if steps and steps[-1].get("observation") is None:
		steps[-1]["observation"] = obs
	else:
		steps.append({"thought": None, "action": action, "observation": obs})
	# Clear action to allow next reasoning
	state["action"] = None
	return state


def build_graph():  # -> Compiled graph app
	"""Build and return the LangGraph workflow: reason <-> act until done."""
	graph = StateGraph(AgentState)
	graph.add_node("reason", reasoning_node)
	graph.add_node("act", tool_exec_node)

	def _route_after_reason(state: AgentState) -> str:
		return "end" if state.get("done") else "act"

	graph.set_entry_point("reason")
	graph.add_conditional_edges("reason", _route_after_reason, {"end": END, "act": "act"})
	graph.add_edge("act", "reason")
	return graph.compile()


def run_agent(input_text: str) -> AgentState:
	"""Convenience runner for the agent graph.

	Args:
		input_text: The user problem statement.

	Returns:
		Final AgentState after the graph finishes.
	"""
	app = build_graph()
	initial: AgentState = {
		"input": input_text,
		"steps": [],
		"plan": None,
		"action": None,
		"observation": None,
		"done": False,
	}
	# Invoke compiled graph; it will iterate until END
	final_state: AgentState = app.invoke(initial)
	return final_state


def debug_components(verbose: bool = False) -> bool:
	"""Debug individual agent components. Returns True if all tests pass."""
	print("=== Agent Component Debug ===")
	
	try:
		# Test system prompt
		prompt = _load_system_prompt()
		if len(prompt) > 50:
			print("✓ System prompt loaded")
		else:
			print("✗ System prompt too short or missing")
			return False
		
		# Test action parsing
		test_text = '''
		Thought: I need to check traffic.
		Action: {"tool_name": "check_traffic", "parameters": {"route": "test"}}
		'''
		action, thought = _parse_action(test_text)
		if action and action.get('tool_name') == 'check_traffic':
			print("✓ Action parsing working")
			if verbose:
				print(f"  Parsed action: {action}")
				print(f"  Parsed thought: {thought}")
		else:
			print(f"✗ Action parsing failed: {action}")
			return False
		
		# Test tool registry
		registry = _tool_registry()
		if len(registry) >= 5:
			print(f"✓ Tool registry loaded ({len(registry)} tools)")
			if verbose:
				print(f"  Available tools: {list(registry.keys())}")
		else:
			print("✗ Tool registry incomplete")
			return False
		
		# Test graph building
		graph = build_graph()
		if graph:
			print("✓ LangGraph built successfully")
		else:
			print("✗ Graph building failed")
			return False
		
		# Test LLM initialization
		try:
			llm = _get_llm()
			print("✓ LLM initialized")
			if verbose:
				print(f"  Model: {getattr(llm, 'model_name', 'unknown')}")
		except Exception as e:
			print(f"✗ LLM initialization failed: {e}")
			if 'GEMINI_API_KEY' in str(e):
				print("  Check your .env file has GEMINI_API_KEY set")
			return False
		
		return True
		
	except Exception as e:
		print(f"✗ Component debug failed: {e}")
		return False


def debug_llm_connection(verbose: bool = False) -> bool:
	"""Test LLM connection with a simple call. Returns True if successful."""
	print("=== LLM Connection Debug ===")
	
	try:
		from langchain_core.messages import HumanMessage
		
		llm = _get_llm()
		messages = [HumanMessage(content='Respond with exactly: {"status": "ok"}')]
		response = llm.invoke(messages)
		
		if verbose:
			print(f"Response: {response.content}")
		
		if '"status"' in response.content and '"ok"' in response.content:
			print("✓ LLM responding correctly")
			return True
		else:
			print(f"✗ LLM response unexpected: {response.content}")
			return False
			
	except Exception as e:
		print(f"✗ LLM test failed: {e}")
		if 'rate_limit' in str(e).lower() or '429' in str(e):
			print("  Rate limit error - wait a few minutes or use different model")
		elif 'GEMINI_API_KEY' in str(e):
			print("  Check your GEMINI_API_KEY in .env file")
		return False


def debug_simple_run(verbose: bool = False) -> bool:
	"""Test agent with a simple problem. Returns True if successful."""
	print("=== Simple Agent Run Debug ===")
	
	try:
		simple_problem = "Check traffic on route DEBUG."
		result = run_agent(simple_problem)
		
		if result.get('done'):
			print("✓ Agent completed successfully")
			print(f"  Final plan: {result.get('plan', 'None')[:100]}...")
			print(f"  Steps taken: {len(result.get('steps', []))}")
			
			if verbose:
				print("  Full result:")
				print(json.dumps(result, indent=2, ensure_ascii=False))
			
			return True
		else:
			print("✗ Agent did not complete")
			if verbose:
				print(f"  Current state: {result}")
			return False
			
	except Exception as e:
		print(f"✗ Agent test failed: {e}")
		if 'rate_limit' in str(e).lower() or '429' in str(e):
			print("  Rate limit hit - wait or use different model")
		return False


def debug_all(verbose: bool = False) -> bool:
	"""Run all debug tests. Returns True if all pass."""
	print("Synapse Agent Debug")
	print("=" * 40)
	
	# Environment check
	load_dotenv(override=False)
	gemini_key = os.getenv("GEMINI_API_KEY")
	groq_key = os.getenv("GROQ_API_KEY")
	print(f"GEMINI_API_KEY loaded: {bool(gemini_key)}")
	print(f"GROQ_API_KEY loaded: {bool(groq_key)}")
	if gemini_key and verbose:
		print(f"Gemini key starts with: {gemini_key[:10]}...")
	print()
	
	tests = [
		("Components", lambda: debug_components(verbose)),
		("LLM Connection", lambda: debug_llm_connection(verbose)),
		("Simple Run", lambda: debug_simple_run(verbose))
	]
	
	passed = 0
	for test_name, test_func in tests:
		print(f"Running {test_name} test...")
		if test_func():
			passed += 1
		print()
	
	print("=" * 40)
	print(f"Results: {passed}/{len(tests)} tests passed")
	
	if passed == len(tests):
		print("✓ All tests passed! Agent is working correctly.")
	else:
		print("✗ Some tests failed. Check errors above.")
	
	return passed == len(tests)


if __name__ == "__main__":
	import sys
	
	if len(sys.argv) > 1:
		if sys.argv[1] == "--debug":
			verbose = "--verbose" in sys.argv or "-v" in sys.argv
			debug_all(verbose)
		elif sys.argv[1] == "--debug-components":
			debug_components(True)
		elif sys.argv[1] == "--debug-llm":
			debug_llm_connection(True)
		elif sys.argv[1] == "--debug-simple":
			debug_simple_run(True)
		elif sys.argv[1] == "--help":
			print("Usage:")
			print("  python -m src.agent                    # Run default scenario")
			print("  python -m src.agent --debug            # Run all debug tests")
			print("  python -m src.agent --debug --verbose  # Verbose debug output")
			print("  python -m src.agent --debug-components # Test components only")
			print("  python -m src.agent --debug-llm        # Test LLM only")
			print("  python -m src.agent --debug-simple     # Test simple agent run")
		else:
			print(f"Unknown option: {sys.argv[1]}")
			print("Use --help for available options")
	else:
		# Default behavior - run the main scenario
		problem = "A driver is en route to Restaurant XYZ, but there's a report of a major accident on the main highway."
		try:
			result = run_agent(problem)
			print(json.dumps(result, indent=2, ensure_ascii=False))
		except Exception as e:
			print(f"Agent run failed: {e}")
			print("\nTry running with --debug to diagnose issues:")
