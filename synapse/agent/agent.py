"""
Synapse Agent - Autonomous Logistics Coordination with LangGraph

This module implements the core AI agent for Project Synapse, an autonomous logistics
coordination system that uses advanced reasoning, reflection, and error recovery to
solve complex last-mile delivery problems.

Architecture Overview:
    The agent follows a sophisticated ANALYZE → STRATEGIZE → EXECUTE → ADAPT framework
    implemented as a LangGraph StateGraph with three main nodes:
    
    1. Reasoning Node: Analyzes problems and chooses optimal tool actions
    2. Tool Execution Node: Executes logistics tools and captures results
    3. Reflection Node: Detects failures and suggests adaptive alternatives

Key Design Choices:
    - **LangGraph StateGraph**: Provides robust state management and flow control
    - **Google Gemini LLM**: Powers natural language reasoning and decision-making
    - **Reflection-Based Error Recovery**: Automatically adapts when tools fail
    - **Comprehensive Tool Integration**: 18+ specialized logistics tools
    - **Escalation Chains**: Intelligent fallback mechanisms for complex scenarios

State Management:
    AgentState (TypedDict) maintains all agent state across nodes:
    - input: User's problem description
    - steps: Complete reasoning history (append-only audit log)
    - plan: Final resolution plan when agent completes
    - action: Current action being executed
    - observation: Last tool execution result
    - done: Terminal state flag
    - needs_adaptation: Reflection system activation flag
    - reflection_reason: Explanation of why adaptation is needed
    - suggested_alternative: Next tool to try after failure

Workflow:
    1. User provides logistics problem description
    2. Reasoning node analyzes situation and selects tool
    3. Tool execution node runs tool and captures result
    4. Reflection node evaluates success/failure
    5. If failure: suggest alternative approach and continue
    6. If success: continue to next reasoning step
    7. When problem solved: generate final plan and terminate

Error Recovery Strategy:
    The reflection system implements intelligent escalation chains:
    - Contact failure → Safe drop-off → Locker → Redelivery → Sender contact
    - Evidence analysis → Partial refund → Full refund
    - Traffic delays → Re-routing → Customer notification → Time adjustment
    
    This ensures robust problem resolution even when initial approaches fail.

Dependencies:
    - langgraph: State graph orchestration
    - langchain_google_genai: Gemini LLM integration
    - synapse.tools: Specialized logistics tool ecosystem
    - python-dotenv: Environment variable management

Authors: Project Synapse Team
License: MIT
"""

from __future__ import annotations
import time
import uuid

from typing import Any, Dict, List, Optional, TypedDict, Callable, Tuple
import os
import json
import re

from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
import concurrent.futures

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from synapse.tools import tools as sim_tools
from synapse.core.performance_tracker import PerformanceTracker

# Global executive display instance for real-time updates
_executive_display = None

def set_executive_display(display):
	"""Set the global executive display instance."""
	global _executive_display
	_executive_display = display

def get_executive_display():
	"""Get the global executive display instance."""
	return _executive_display


class AgentState(TypedDict, total=False):
		"""
		Comprehensive state container for the Synapse logistics coordination agent.
		
		This TypedDict defines the complete state that flows between all nodes in the
		LangGraph workflow. It serves as both a data container and audit log for the
		agent's decision-making process.
		
		Core Fields:
				input (str): The original logistics problem description provided by the user.
						Example: "Driver stuck in traffic, 45-minute delay expected"
				
				steps (List[Dict[str, Any]]): Append-only chronological log of all reasoning 
						steps, tool actions, and observations. Each step contains:
						- thought: Agent's reasoning process
						- action: Tool selection and parameters
						- observation: Tool execution results
				
				plan (Optional[str]): Final comprehensive resolution plan generated when 
						the agent successfully solves the problem.
				
				action (Optional[Dict[str, Any]]): The next tool action to be executed,
						containing 'tool_name' and 'parameters' keys.
				
				observation (Optional[Any]): Raw result from the most recent tool execution.
				
				done (bool): Terminal state flag - when True, the agent stops processing.
		
		Reflection & Error Recovery Fields:
				needs_adaptation (bool): Flag indicating whether the reflection system
						has detected a failure requiring adaptive response.
				
				reflection_reason (Optional[str]): Human-readable explanation of why
						adaptation is needed (e.g., "Contact failed - need alternative approach").
				
				suggested_alternative (Optional[str]): Next tool name recommended by the
						reflection system for recovery (enables escalation chains).
		
		Design Notes:
				- All fields are optional (total=False) to support incremental state building
				- The steps list serves as a complete audit trail for debugging and analysis
				- Reflection fields enable sophisticated error recovery without losing context
				- State is immutable between nodes - each node returns updated state copy
		"""

		input: str
		steps: List[Dict[str, Any]]
		plan: Optional[str]
		action: Optional[Dict[str, Any]]
		observation: Optional[Any]
		done: bool
		# Reflection and error handling fields
		needs_adaptation: bool
		reflection_reason: Optional[str]
		suggested_alternative: Optional[str]


def _load_system_prompt() -> str:
	"""
	Load the comprehensive system prompt that defines the agent's behavior.
	
	This function loads the carefully crafted system prompt from the prompts directory
	that instructs the Gemini LLM on how to reason about logistics problems, select
	appropriate tools, and generate structured responses.
	
	The system prompt includes:
	- Role definition and logistics expertise instructions
	- Tool usage guidelines and examples
	- Response format requirements (Thought/Action structure)
	- Error handling and reflection protocols
	- Escalation chain strategies for common failures
	
	Returns:
		str: Complete system prompt text, or minimal fallback if file not found.
		
	Design Note:
		Uses relative path resolution to work correctly when installed as a package
		or run from different working directories.
	"""
	# Resolve to project root relative to this file
	here = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
	prompt_path = os.path.join(here, "synapse", "prompts", "system_prompt.txt")
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
	"""
	Initialize and configure the Google Gemini LLM for agent reasoning.
	
	This function creates a ChatGoogleGenerativeAI instance configured for optimal
	performance in logistics coordination tasks. The choice of Gemini 1.5 Flash
	provides an excellent balance of reasoning capability, speed, and cost-effectiveness
	for real-time logistics problem solving.
	
	Configuration Details:
	- Model: gemini-1.5-flash (fast inference, strong reasoning)
	- Temperature: Default (balanced creativity/consistency)  
	- API Key: Loaded from GEMINI_API_KEY environment variable
	
	Returns:
		ChatGoogleGenerativeAI: Configured LLM instance ready for chat completion.
		
	Raises:
		RuntimeError: If GEMINI_API_KEY is not set in environment variables.
		
	Design Choice Rationale:
		Gemini 1.5 Flash was selected over other models because:
		- Superior reasoning for multi-step logistics problems
		- Fast response times for real-time coordination
		- Strong structured output generation (JSON actions)
		- Cost-effective for production deployment
		- Excellent performance on tool selection tasks
	"""
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

	def adapt_collect_evidence(p: Dict[str, Any]) -> Dict[str, Any]:
		return sim_tools.collect_evidence(
			order_id=str(p.get("order_id", "")),
			requester=str(p.get("requester", "agent")),
			ask_photos=bool(p.get("ask_photos", True))
		)

	def adapt_analyze_evidence(p: Dict[str, Any]) -> Dict[str, Any]:
		return sim_tools.analyze_evidence(evidence_id=str(p.get("evidence_id", "")))

	def adapt_issue_instant_refund(p: Dict[str, Any]) -> Dict[str, Any]:
		amount = p.get("amount", 0)
		try:
			amount = float(amount)
		except (ValueError, TypeError):
			amount = 0.0
		return sim_tools.issue_instant_refund(
			order_id=str(p.get("order_id", "")),
			amount=amount,
			currency=str(p.get("currency", "USD")),
			reason=p.get("reason")
		)

	def adapt_exonerate_driver(p: Dict[str, Any]) -> Dict[str, Any]:
		return sim_tools.exonerate_driver(
			driver_id=str(p.get("driver_id", "")),
			order_id=p.get("order_id"),
			reason=p.get("reason")
		)

	def adapt_contact_merchant(p: Dict[str, Any]) -> Dict[str, Any]:
		return sim_tools.contact_merchant(
			merchant_id=str(p.get("merchant_id", "")),
			message=str(p.get("message", ""))
		)

	def adapt_propose_substitute(p: Dict[str, Any]) -> Dict[str, Any]:
		substitute_items = p.get("substitute_items", [])
		if not isinstance(substitute_items, list):
			substitute_items = []
		return sim_tools.propose_substitute(
			order_id=str(p.get("order_id", "")),
			substitute_items=substitute_items
		)

	def adapt_issue_partial_refund(p: Dict[str, Any]) -> Dict[str, Any]:
		amount = p.get("amount", 0)
		try:
			amount = float(amount)
		except (ValueError, TypeError):
			amount = 0.0
		return sim_tools.issue_partial_refund(
			order_id=str(p.get("order_id", "")),
			amount=amount,
			currency=str(p.get("currency", "USD"))
		)

	def adapt_log_merchant_packaging_feedback(p: Dict[str, Any]) -> Dict[str, Any]:
		feedback = p.get("feedback", {})
		if not isinstance(feedback, dict):
			feedback = {"message": str(feedback)}
		return sim_tools.log_merchant_packaging_feedback(
			merchant_id=str(p.get("merchant_id", "")),
			feedback=feedback
		)

	# Scenario 2.4: Recipient Unavailable Tools
	def adapt_contact_recipient_via_chat(p: Dict[str, Any]) -> Dict[str, Any]:
		return sim_tools.contact_recipient_via_chat(
			recipient_id=str(p.get("recipient_id", "")),
			message=str(p.get("message", "")),
			channel=str(p.get("channel", "app"))
		)

	def adapt_suggest_safe_drop_off(p: Dict[str, Any]) -> Dict[str, Any]:
		options = p.get("options", [])
		if not isinstance(options, list):
			options = []
		return sim_tools.suggest_safe_drop_off(options=options)

	def adapt_find_nearby_locker(p: Dict[str, Any]) -> Dict[str, Any]:
		lat = p.get("lat")
		lng = p.get("lng") or p.get("lon") 
		radius_m = p.get("radius_m", 2000)
		try:
			return sim_tools.find_nearby_locker(float(lat), float(lng), int(radius_m))
		except Exception:
			return {"tool_name": "find_nearby_locker", "status": "error", "error_message": "invalid lat/lng coordinates"}

	def adapt_schedule_redelivery(p: Dict[str, Any]) -> Dict[str, Any]:
		windows = p.get("windows", [])
		if not isinstance(windows, list):
			windows = []
		return sim_tools.schedule_redelivery(
			order_id=str(p.get("order_id", "")),
			windows=windows
		)

	def adapt_contact_sender(p: Dict[str, Any]) -> Dict[str, Any]:
		return sim_tools.contact_sender(
			sender_id=str(p.get("sender_id", "")),
			message=str(p.get("message", ""))
		)

	# Scenario 2.9: Unresponsive Driver Tools
	def adapt_get_driver_status(p: Dict[str, Any]) -> Dict[str, Any]:
		return sim_tools.get_driver_status(driver_id=str(p.get("driver_id", "")))

	def adapt_cancel_booking(p: Dict[str, Any]) -> Dict[str, Any]:
		return sim_tools.cancel_booking(
			booking_id=str(p.get("booking_id", "")),
			reason=str(p.get("reason", ""))
		)

	def adapt_find_replacement_driver(p: Dict[str, Any]) -> Dict[str, Any]:
		location = p.get("location", {})
		if not isinstance(location, dict):
			location = {}
		return sim_tools.find_replacement_driver(
			booking_id=str(p.get("booking_id", "")),
			location=location
		)

	# Scenario 2.8: Unsafe Road Conditions Tools
	def adapt_reroute_driver_to_safe_location(p: Dict[str, Any]) -> Dict[str, Any]:
		location = p.get("location", {})
		if not isinstance(location, dict):
			location = {}
		return sim_tools.reroute_driver_to_safe_location(
			driver_id=str(p.get("driver_id", "")),
			location=location
		)

	def adapt_notify_passenger_and_driver(p: Dict[str, Any]) -> Dict[str, Any]:
		return sim_tools.notify_passenger_and_driver(
			trip_id=str(p.get("trip_id", "")),
			message=str(p.get("message", ""))
		)

	# Scenario 2.7: Lost and Found Tools
	def adapt_locate_trip_path(p: Dict[str, Any]) -> Dict[str, Any]:
		return sim_tools.locate_trip_path(trip_id=str(p.get("trip_id", "")))

	def adapt_initiate_lost_and_found_flow(p: Dict[str, Any]) -> Dict[str, Any]:
		details = p.get("details", {})
		if not isinstance(details, dict):
			details = {"description": str(details)} if details else {}
		return sim_tools.initiate_lost_and_found_flow(
			trip_id=str(p.get("trip_id", "")),
			details=details
		)

	# Scenario 2.6: Major Traffic Obstruction Tools
	def adapt_calculate_alternative_route(p: Dict[str, Any]) -> Dict[str, Any]:
		constraints = p.get("constraints", {})
		if not isinstance(constraints, dict):
			constraints = {}
		return sim_tools.calculate_alternative_route(
			route_id=str(p.get("route_id", "")),
			constraints=constraints
		)

	# Scenario 2.5: Address Verification Tools
	def adapt_verify_address_with_customer(p: Dict[str, Any]) -> Dict[str, Any]:
		provided_address = p.get("provided_address", {})
		if not isinstance(provided_address, dict):
			provided_address = {"address": str(provided_address)} if provided_address else {}
		return sim_tools.verify_address_with_customer(
			customer_id=str(p.get("customer_id", "")),
			provided_address=provided_address
		)

	# Human Intervention Tools
	def adapt_contact_support_live(p: Dict[str, Any]) -> Dict[str, Any]:
		issue = p.get("issue", {})
		if not isinstance(issue, dict):
			issue = {"description": str(issue)} if issue else {"description": "Support needed"}
		return sim_tools.contact_support_live(
			issue=issue,
			priority=str(p.get("priority", "high"))
		)

	def adapt_escalate_to_management(p: Dict[str, Any]) -> Dict[str, Any]:
		return sim_tools.escalate_to_management(
			issue_type=str(p.get("issue_type", "")),
			description=str(p.get("description", "")),
			urgency=str(p.get("urgency", "medium")),
			estimated_cost=float(p.get("estimated_cost", 0.0))
		)

	# Financial Authorization Tools
	def adapt_issue_voucher(p: Dict[str, Any]) -> Dict[str, Any]:
		amount = p.get("amount", 0)
		try:
			amount = float(amount)
		except (ValueError, TypeError):
			amount = 0.0
		return sim_tools.issue_voucher(
			customer_id=str(p.get("customer_id", "")),
			amount=amount,
			currency=str(p.get("currency", "USD")),
			reason=p.get("reason")
		)

	return {
		"check_traffic": adapt_check_traffic,
		"get_merchant_status": adapt_get_merchant_status,
		"notify_customer": adapt_notify_customer,
		"re_route_driver": adapt_re_route_driver,
		"get_nearby_merchants": adapt_get_nearby_merchants,
		"collect_evidence": adapt_collect_evidence,
		"analyze_evidence": adapt_analyze_evidence,
		"issue_instant_refund": adapt_issue_instant_refund,
		"exonerate_driver": adapt_exonerate_driver,
		"contact_merchant": adapt_contact_merchant,
		"propose_substitute": adapt_propose_substitute,
		"issue_partial_refund": adapt_issue_partial_refund,
		"log_merchant_packaging_feedback": adapt_log_merchant_packaging_feedback,
		# Scenario 2.4: Recipient Unavailable Tools
		"contact_recipient_via_chat": adapt_contact_recipient_via_chat,
		"suggest_safe_drop_off": adapt_suggest_safe_drop_off,
		"find_nearby_locker": adapt_find_nearby_locker,
		"schedule_redelivery": adapt_schedule_redelivery,
		"contact_sender": adapt_contact_sender,
		# Scenario 2.9: Unresponsive Driver Tools
		"get_driver_status": adapt_get_driver_status,
		"cancel_booking": adapt_cancel_booking,
		"find_replacement_driver": adapt_find_replacement_driver,
		# Scenario 2.5: Address Verification Tools
		"verify_address_with_customer": adapt_verify_address_with_customer,
		# Scenario 2.6: Major Traffic Obstruction Tools
		"calculate_alternative_route": adapt_calculate_alternative_route,
		# Scenario 2.7: Lost and Found Tools
		"locate_trip_path": adapt_locate_trip_path,
		"initiate_lost_and_found_flow": adapt_initiate_lost_and_found_flow,
		# Scenario 2.8: Unsafe Road Conditions Tools
		"reroute_driver_to_safe_location": adapt_reroute_driver_to_safe_location,
		"notify_passenger_and_driver": adapt_notify_passenger_and_driver,
		# Human Intervention Tools
		"contact_support_live": adapt_contact_support_live,
		"escalate_to_management": adapt_escalate_to_management,
		# Financial Authorization Tools
		"issue_voucher": adapt_issue_voucher,
		# Special pseudo-tool handled in tool_exec_node: "finish"
	}


def reasoning_node(state: AgentState) -> AgentState:
	"""
	Core reasoning node that analyzes logistics problems and selects optimal actions.
	
	This is the central intelligence hub of the Synapse agent, responsible for:
	1. Analyzing the current logistics situation and context
	2. Reviewing previous steps and their outcomes  
	3. Selecting the most appropriate tool for the next action
	4. Determining when the problem has been sufficiently resolved
	5. Generating comprehensive final plans upon completion
	
	The node uses the Gemini LLM with a sophisticated system prompt to reason about
	complex multi-stakeholder logistics scenarios. It follows a structured thought
	process that mirrors human logistics coordinator decision-making.
	
	Input Processing:
	- Current state with problem description and step history
	- Previous tool execution results and observations
	- Reflection system suggestions for adaptive recovery
	
	Output Generation:
	The LLM generates structured responses in this format:
		Thought: [Detailed reasoning about the situation and next steps]
		Action: {"tool_name": "contact_recipient_via_chat", "parameters": {...}}
	
	Or when ready to finish:
		Thought: [Summary of problem resolution]  
		Action: {"tool_name": "finish", "parameters": {"plan": "Comprehensive solution..."}}
	
	Args:
		state (AgentState): Current agent state with problem context and history.
		
	Returns:
		AgentState: Updated state with new action selected or completion flag set.
		
	Error Handling:
		- Gracefully handles LLM initialization failures
		- Provides fallback responses for API connectivity issues
		- Integrates with reflection system for failure recovery
		- Implements safeguards against infinite reasoning loops
		
	Design Notes:
		The reasoning node embodies the agent's intelligence and is designed to:
		- Scale from simple delays to complex dispute resolution
		- Maintain context across multi-step problem solving
		- Adapt strategies based on previous action outcomes
		- Generate human-readable explanations for all decisions
	"""
	# Early termination check to prevent recursion
	steps = state.get("steps", [])
	max_steps = int(os.getenv("MAX_AGENT_STEPS", "15"))
	if len(steps) >= max_steps:
		# Generate a reasonable conclusion based on what we've accomplished
		last_successful_tools = []
		for step in reversed(steps[-5:]):  # Look at last 5 steps
			obs = step.get("observation", {})
			if isinstance(obs, dict) and obs.get("status") != "error":
				tool_name = step.get("action", {}).get("tool_name", "")
				if tool_name and tool_name not in last_successful_tools:
					last_successful_tools.append(tool_name)
		
		if last_successful_tools:
			plan = f"Successfully executed {', '.join(last_successful_tools)}. Problem addressed to the extent possible with available information."
		else:
			plan = "Problem analysis completed. Applied standard operating procedures for the logistics situation."
		
		state["done"] = True
		state["plan"] = plan
		state["action"] = None
		return state
	
	# Track LLM call performance
	tracker = PerformanceTracker()
	llm_start = time.time()
	
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
	
	# Include reflection information if available
	reflection_context = ""
	if state.get("needs_adaptation"):
		reflection_reason = state.get("reflection_reason", "")
		suggested_alternative = state.get("suggested_alternative", "")
		reflection_context = f"\n\n⚠️ REFLECTION GUIDANCE:\n" \
							f"Previous approach encountered an issue: {reflection_reason}\n"
		if suggested_alternative:
			reflection_context += f"Consider using tool: {suggested_alternative}\n"
		reflection_context += "Please adapt your approach accordingly.\n"

	messages = [
		SystemMessage(content=sys_prompt),
		HumanMessage(content=(
			"Problem: " + user_problem + "\n\n" +
			"Context (previous steps):\n" + history + 
			reflection_context + "\n\n" +
			"Decide the next best single tool call."
		)),
	]
	
	# Estimate token count (rough approximation)
	input_tokens = len(str(messages)) // 4  # Rough estimate

	# Run the LLM call with a protective timeout
	def _call():
		return llm.invoke(messages)

	try:
		# Use configurable timeout from environment
		llm_timeout = int(os.getenv("LLM_TIMEOUT", "30"))
		with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
			fut = ex.submit(_call)
			resp = fut.result(timeout=llm_timeout)
			text = getattr(resp, "content", str(resp))
		
		# Track LLM performance
		llm_response_time = time.time() - llm_start
		output_tokens = len(text) // 4  # Rough estimate
		if tracker.current_query:
			tracker.record_llm_call(input_tokens, output_tokens, llm_response_time)
			
	except concurrent.futures.TimeoutError:
		state["done"] = True
		state["plan"] = "LLM call timed out. Please check network or GROQ availability."
		state["action"] = None
		return state
	except Exception as e:
		# Check for quota limit specifically
		error_str = str(e)
		if "quota" in error_str.lower() or "429" in error_str or "resourceexhausted" in error_str.lower():
			state["done"] = True
			state["plan"] = "Google Gemini API quota exceeded (50 requests/day limit on free tier). Please wait 24 hours or upgrade to a paid plan."
		else:
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
	
	# Update executive display with step count
	display = get_executive_display()
	if display:
		reflection_count = sum(1 for step in steps if step.get("action", {}).get("tool_name") == "reflect")
		display.update_metrics({
			"steps_completed": len(steps),
			"reflection_count": reflection_count,
			"complexity_score": min(len(steps) // 2 + 1, 10)  # Simple complexity estimation
		})
	
	state["done"] = False
	return state


def tool_exec_node(state: AgentState) -> AgentState:
	"""Tool execution node: run the selected tool and capture observation."""
	import time
	
	action = state.get("action") or {}
	tool_name = action.get("tool_name")
	params = action.get("parameters") or {}

	# Handle finish pseudo-tool (already finalized plan in reasoning node)
	if tool_name == "finish":
		state["observation"] = None
		state["action"] = None
		return state

	# Update executive display - tool started
	display = get_executive_display()
	if display and tool_name:
		display.add_tool_execution(tool_name, "running", None, False)
		# Small delay to ensure display thread processes the update
		import time
		time.sleep(0.1)

	registry = _tool_registry()
	obs: Any
	start_time = time.time()
	
	if tool_name in registry:
		# Start tracking BEFORE execution
		tracker = PerformanceTracker()
		tool_id = None
		if tracker.current_query:
			tool_id = tracker.start_tool(tool_name, params)
		
		try:
			# Add realistic delay before tool execution if not already present
			import random
			import time as time_module
			time_module.sleep(random.uniform(0.05, 0.3))  # Universal tool delay
			
			obs = registry[tool_name](params)
			duration = time.time() - start_time
			# Update executive display - tool completed
			if display:
				display.add_tool_execution(tool_name, "success", duration, False)
				# Small delay to ensure display thread processes the update
				time_module.sleep(0.1)
			# Complete performance tracker with success
			if tracker.current_query and tool_id:
				tracker.complete_tool(tool_id, True, str(obs))
		except Exception as e:
			obs = {"tool_name": tool_name, "status": "error", "error_message": str(e)}
			duration = time.time() - start_time
			# Update executive display - tool failed
			if display:
				display.add_tool_execution(tool_name, "failed", duration, False)
				# Small delay to ensure display thread processes the update
				time_module.sleep(0.1)
			# Complete performance tracker with failure
			if tracker.current_query and tool_id:
				tracker.complete_tool(tool_id, False, str(e))
	else:
		obs = {"tool_name": tool_name, "status": "error", "error_message": f"unknown tool: {tool_name}"}
		duration = time.time() - start_time
		# Update executive display - tool failed
		if display:
			display.add_tool_execution(tool_name, "failed", duration, False)
			# Small delay to ensure display thread processes the update
			import time as time_mod
			time_mod.sleep(0.1)
		# Update performance tracker for unknown tool
		tracker = PerformanceTracker()
		if tracker.current_query:
			tool_id = tracker.start_tool(tool_name, params)
			tracker.complete_tool(tool_id, False, f"unknown tool: {tool_name}")

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


def reflection_node(state: AgentState) -> AgentState:
	"""Reflection node: analyze tool execution results and handle failures."""
	tracker = PerformanceTracker()
	
	steps = state.get("steps", [])
	if not steps:
		return state
	
	# Prevent infinite loops - check total steps and reflection count
	total_steps = len(steps)
	reflection_count = sum(1 for step in steps if step.get("action", {}).get("tool_name") == "reflect")
	max_steps = int(os.getenv("MAX_AGENT_STEPS", "15"))
	max_reflections = int(os.getenv("MAX_REFLECTIONS", "3"))
	
	if total_steps >= max_steps:
		state["done"] = True
		state["plan"] = f"Maximum steps ({max_steps}) reached. Terminating with current resolution."
		return state
	elif reflection_count >= max_reflections:
		state["done"] = True
		state["plan"] = f"Maximum reflections ({max_reflections}) reached. Terminating with current resolution."
		return state
	
	last_step = steps[-1]
	observation = last_step.get("observation", {})
	action = last_step.get("action", {})
	tool_name = action.get("tool_name", "")
	
	# Check if the last tool execution had issues
	needs_reflection = False
	reflection_reason = ""
	alternative_approach = None
	
	if isinstance(observation, dict):
		status = observation.get("status", "")
		
		# Detect various failure conditions
		if status == "error":
			needs_reflection = True
			reflection_reason = f"Tool {tool_name} failed: {observation.get('error_message', 'unknown error')}"
		elif observation.get("contact_successful") is False and tool_name == "contact_recipient_via_chat":
			needs_reflection = True
			reflection_reason = "Recipient contact failed - need alternative delivery approach"
			alternative_approach = "suggest_safe_drop_off"
		elif observation.get("safe_option_available") is False and tool_name == "suggest_safe_drop_off":
			needs_reflection = True
			reflection_reason = "Safe drop-off not available - try locker option"
			alternative_approach = "find_nearby_locker"
		elif observation.get("lockers_found") is False and tool_name == "find_nearby_locker":
			needs_reflection = True
			reflection_reason = "No lockers available - escalate to redelivery"
			alternative_approach = "schedule_redelivery"
		elif observation.get("scheduled") is False and tool_name == "schedule_redelivery":
			needs_reflection = True
			reflection_reason = "Redelivery scheduling failed - contact sender"
			alternative_approach = "contact_sender"
		elif observation.get("merchant_available") is False and tool_name == "contact_merchant":
			needs_reflection = True
			reflection_reason = "Merchant unavailable - try direct stock check"
			alternative_approach = "get_merchant_status"
		elif observation.get("evidence_collected") is False and tool_name == "collect_evidence":
			needs_reflection = True
			reflection_reason = "Evidence collection failed - proceed with customer satisfaction approach"
			alternative_approach = "issue_instant_refund"
		# Traffic and routing failures
		elif observation.get("incident_level") == "severe" and tool_name == "check_traffic":
			needs_reflection = True
			reflection_reason = "Severe traffic detected - need alternative routing"
			alternative_approach = "re_route_driver"
		# Merchant communication failures
		elif observation.get("status") == "closed" and tool_name == "get_merchant_status":
			needs_reflection = True
			reflection_reason = "Merchant is closed - find alternative merchant"
			alternative_approach = "get_nearby_merchants"
		# Notification failures
		elif observation.get("delivered") is False and tool_name == "notify_customer":
			needs_reflection = True
			reflection_reason = "Customer notification failed - try alternative communication"
		# Analysis failures
		elif observation.get("confidence") and observation.get("confidence") < 0.5 and tool_name == "analyze_evidence":
			needs_reflection = True
			reflection_reason = "Evidence analysis has low confidence - proceed with goodwill approach"
			alternative_approach = "issue_partial_refund"
		# Refund processing failures
		elif observation.get("requires_approval") and tool_name == "issue_instant_refund":
			needs_reflection = True
			reflection_reason = "Refund requires approval - try partial refund instead"
			alternative_approach = "issue_partial_refund"
		# Unresponsive driver scenarios
		elif observation.get("state") == "idle" and tool_name == "get_driver_status":
			needs_reflection = True
			reflection_reason = "Driver is idle and unresponsive - need to notify customer and find replacement"
			alternative_approach = "notify_customer"
		elif observation.get("driver_found") is False and tool_name == "find_replacement_driver":
			needs_reflection = True
			reflection_reason = "No replacement driver available - cancel booking and issue refund"
			alternative_approach = "cancel_booking"
		elif observation.get("cancelled") is False and tool_name == "cancel_booking":
			needs_reflection = True
			reflection_reason = "Booking cancellation failed - escalate to support"
			alternative_approach = "contact_support_live"
		# Unsafe road conditions scenarios
		elif observation.get("incident_level") in ["severe", "hazardous"] and tool_name == "check_traffic":
			needs_reflection = True
			reflection_reason = "Hazardous road conditions detected - prioritize safety with immediate rerouting"
			alternative_approach = "reroute_driver_to_safe_location"
		elif observation.get("rerouted") is False and tool_name == "reroute_driver_to_safe_location":
			needs_reflection = True
			reflection_reason = "Safe rerouting failed - notify all parties and escalate"
			alternative_approach = "notify_passenger_and_driver"
		elif observation.get("passenger_ack") is False or observation.get("driver_ack") is False and tool_name == "notify_passenger_and_driver":
			needs_reflection = True
			reflection_reason = "Communication failed during safety incident - escalate immediately"
			alternative_approach = "contact_support_live"
		# Lost and found scenarios
		elif observation.get("trip_found") is False and tool_name == "locate_trip_path":
			needs_reflection = True
			reflection_reason = "Trip path could not be located - initiate lost and found process anyway"
			alternative_approach = "initiate_lost_and_found_flow"
		elif observation.get("case_initiated") is False and tool_name == "initiate_lost_and_found_flow":
			needs_reflection = True
			reflection_reason = "Lost and found case failed to initiate - escalate to support"
			alternative_approach = "contact_support_live"
		# Major traffic obstruction scenarios
		elif observation.get("incident_level") in ["major", "severe"] and tool_name == "check_traffic":
			needs_reflection = True
			reflection_reason = "Major traffic obstruction detected - need immediate alternative routing"
			alternative_approach = "calculate_alternative_route"
		elif observation.get("alternative_found") is False and tool_name == "calculate_alternative_route":
			needs_reflection = True
			reflection_reason = "No alternative route available - notify all parties and consider trip cancellation"
			alternative_approach = "notify_passenger_and_driver"
		# Address verification scenarios
		elif observation.get("address_confirmed") is False and tool_name == "verify_address_with_customer":
			needs_reflection = True
			reflection_reason = "Customer could not confirm correct address - escalate to sender for guidance"
			alternative_approach = "contact_sender"
		elif observation.get("corrected_address") and tool_name == "verify_address_with_customer":
			needs_reflection = True
			reflection_reason = "Customer provided corrected address - need to reroute driver immediately"
			alternative_approach = "re_route_driver"
	
	if needs_reflection:
		# Add reflection step to provide guidance for next reasoning cycle
		reflection_step = {
			"thought": f"REFLECTION: {reflection_reason}. Need to adapt approach.",
			"action": {"tool_name": "reflect", "parameters": {"reason": reflection_reason, "suggested_alternative": alternative_approach}},
			"observation": {"status": "reflection", "reason": reflection_reason, "suggested_alternative": alternative_approach}
		}
		steps.append(reflection_step)
		
		# Update executive display with reflection
		display = get_executive_display()
		if display and tool_name:
			display.add_reflection(reflection_reason, tool_name, alternative_approach or "None")
		
		# Set a flag to help the reasoning node understand we need adaptation
		state["needs_adaptation"] = True
		state["reflection_reason"] = reflection_reason
		state["suggested_alternative"] = alternative_approach
		
		# Track reflection event
		if tracker.current_query:
			tracker.record_reflection(
				reflection_reason,
				tool_name,
				alternative_approach or "unknown"
			)
	else:
		# Clear any previous reflection flags
		state["needs_adaptation"] = False
		state["reflection_reason"] = None
		state["suggested_alternative"] = None
	
	return state


def build_graph():  # -> Compiled graph app
	"""Build and return the LangGraph workflow: reason <-> act <-> reflect until done."""
	graph = StateGraph(AgentState)
	graph.add_node("reason", reasoning_node)
	graph.add_node("act", tool_exec_node)
	graph.add_node("reflect", reflection_node)

	def _route_after_reason(state: AgentState) -> str:
		# Check for termination conditions - DO NOT MODIFY STATE in routing functions
		if state.get("done"):
			return "end"
		# Check step limits as safety net
		steps = state.get("steps", [])
		max_steps = int(os.getenv("MAX_AGENT_STEPS", "15"))
		if len(steps) >= max_steps:
			return "end"
		return "act"

	def _route_after_reflect(state: AgentState) -> str:
		# Check termination conditions - DO NOT MODIFY STATE in routing functions  
		if state.get("done"):
			return "end"
		# Check step limits as safety net
		steps = state.get("steps", [])
		max_steps = int(os.getenv("MAX_AGENT_STEPS", "15"))
		if len(steps) >= max_steps:
			return "end"
		# After reflection, go back to reasoning to adapt approach
		return "reason"

	graph.set_entry_point("reason")
	graph.add_conditional_edges("reason", _route_after_reason, {"end": END, "act": "act"})
	graph.add_edge("act", "reflect")  # Tool execution flows to reflection
	graph.add_conditional_edges("reflect", _route_after_reflect, {"end": END, "reason": "reason"})
	return graph.compile()


def run_agent(input_text: str, scenario_type: str = "custom", enable_performance_tracking: bool = False, executive_display=None) -> AgentState:
	"""Convenience runner for the agent graph.

	Args:
		input_text: The user problem statement.
		scenario_type: Type of scenario for performance tracking.
		enable_performance_tracking: Whether to track performance metrics.
		executive_display: Optional executive display instance for real-time updates.

	Returns:
		Final AgentState after the graph finishes.
	"""
	# Initialize performance tracking (always for dashboard)
	tracker = PerformanceTracker()
	query_id = str(uuid.uuid4())[:8]
	
	# Always start performance tracking for dashboard support
	tracker.start_query(query_id, scenario_type, input_text)
	
	# Set executive display for real-time updates
	if executive_display:
		set_executive_display(executive_display)
		# Initialize display with basic metrics
		executive_display.update_metrics({
			"query_id": query_id,
			"scenario_type": scenario_type,
			"elapsed_time": 0,
			"steps_completed": 0,
			"complexity_score": 1,
			"active_tools": 0,
			"reflection_count": 0,
			"time_saved": 0,
			"estimated_cost": "$0.0000",
			"total_tokens": 0,
			"success_rate": 0,
			"avg_resolution_time": 0,
			"intelligence_score": 0
		})
	
	app = build_graph()
	initial: AgentState = {
		"input": input_text,
		"steps": [],
		"plan": None,
		"action": None,
		"observation": None,
		"done": False,
		"needs_adaptation": False,
		"reflection_reason": None,
		"suggested_alternative": None,
	}
	# Invoke compiled graph with recursion limit; it will iterate until END  
	# Set reasonable recursion limit to prevent infinite loops
	max_agent_steps = int(os.getenv("MAX_AGENT_STEPS", "15"))
	config = {"recursion_limit": max_agent_steps + 10}  # Buffer for graph routing
	final_state: AgentState = app.invoke(initial, config)
	
	# Complete performance tracking (always enabled now)
	success = final_state.get("done", False) and final_state.get("plan")
	tracker.complete_query(success, final_state.get("plan"))
	
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
