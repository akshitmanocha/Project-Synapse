"""
<<<<<<< Updated upstream
CLI entry point to run the Synapse agent.

<<<<<<< Updated upstream
<<<<<<< Updated upstream
Usage:
  python main.py --problem "A driver is en route to Restaurant XYZ, but there's a report of a major accident on the main highway."

If --problem is omitted, a default example will be used.
=======
Examples:
  python main.py --problem "Driver stuck in traffic en route to Merchant ABC; check alternatives and notify customer." --verbose
>>>>>>> Stashed changes
=======
Examples:
  python main.py --problem "Driver stuck in traffic en route to Merchant ABC; check alternatives and notify customer." --verbose
>>>>>>> Stashed changes
=======
Synapse Agent - Autonomous Logistics Coordination CLI
>>>>>>> Stashed changes
"""

from __future__ import annotations

import argparse
<<<<<<< Updated upstream
import json
import os
import sys

from dotenv import load_dotenv
<<<<<<< Updated upstream
<<<<<<< Updated upstream
from src.agent import run_agent


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Run the Synapse agent on a problem statement.")
	parser.add_argument("--problem", type=str, default=None, help="Problem statement for the agent to solve.")
	parser.add_argument("--verbose", action="store_true", help="Print the full final state JSON.")
	return parser.parse_args()
=======
=======
>>>>>>> Stashed changes


def parse_args() -> argparse.Namespace:
	p = argparse.ArgumentParser(description="Run the Synapse agent on a problem statement.")
	p.add_argument("--problem", type=str, default=None, help="Problem statement for the agent to solve.")
	p.add_argument("--verbose", action="store_true", help="Print the full final state JSON.")
	return p.parse_args()
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes


def main() -> int:
	args = parse_args()
<<<<<<< Updated upstream
<<<<<<< Updated upstream
=======
	# Load .env upfront so the agent sees GROQ_API_KEY if present
	load_dotenv(override=False)
=======
import sys
from datetime import datetime
from typing import Dict, Any, List

from synapse import run_agent


def print_chain_of_thought(steps: List[Dict[str, Any]], verbose: bool = False):
    """Display agent's reasoning chain."""
    if not steps:
        print("\n🧠 No reasoning steps recorded")
        return
    
    print("\n" + "=" * 70)
    print("🧠 CHAIN OF THOUGHT")
    print("=" * 70)
    
    for i, step in enumerate(steps, 1):
        is_reflection = step.get("action", {}).get("tool_name") == "reflect"
        icon = "🤔" if is_reflection else "🛠️"
        
        print(f"\n{icon} Step {i}:")
        
        if "thought" in step and step["thought"]:
            print(f"   Thought: {step['thought'][:100]}...")
        
        if "action" in step and step["action"]:
            action = step["action"]
            tool = action.get("tool_name", "unknown")
            if tool != "reflect":
                print(f"   Action: {tool}")
        
        if verbose and "observation" in step:
            obs = str(step["observation"])[:100]
            print(f"   Result: {obs}...")


def print_final_plan(result: Dict[str, Any]):
    """Display final resolution."""
    print("\n" + "=" * 70)
    print("🎯 FINAL RESOLUTION")
    print("=" * 70)
    
    if "plan" in result and result["plan"]:
        print(f"\n{result['plan']}")
    else:
        print("\n⚠️ No plan generated")
    
    status = "✅ Completed" if result.get("done") else "⚠️ Partial"
    print(f"\nStatus: {status}")
    print(f"Steps: {len(result.get('steps', []))}")
>>>>>>> Stashed changes

>>>>>>> Stashed changes
=======
	# Load .env upfront so the agent sees GROQ_API_KEY if present
	load_dotenv(override=False)

<<<<<<< Updated upstream
>>>>>>> Stashed changes
	problem = args.problem or (
		"A driver is en route to Restaurant XYZ, but there's a report of a major accident on the main highway."
	)
=======
def get_scenarios() -> Dict[str, str]:
    """Predefined test scenarios."""
    return {
        "1.0": "Restaurant overloaded, cannot fulfill order on time",
        "2.0": "Package damaged, customer disputes fault",
        "2.2": "Item out of stock, needs replacement",
        "2.3": "Driver at door, order dispute",
        "2.4": "Recipient unavailable for valuable package",
        "traffic": "Driver stuck in traffic, 45min delay",
        "merchant": "Kitchen equipment broken",
        "weather": "Severe weather preventing delivery"
    }
>>>>>>> Stashed changes

<<<<<<< Updated upstream
<<<<<<< Updated upstream
	# Load .env first to avoid false negative note
	load_dotenv(override=False)
	if not os.getenv("GROQ_API_KEY"):
		print("[note] GROQ_API_KEY not found; reasoning may fail fast. Set it in a .env file to enable the LLM.", file=sys.stderr)
=======
=======
>>>>>>> Stashed changes
	try:
		from src.agent import run_agent
	except Exception as e:
		msg = (
			"Failed to import agent: " + str(e) +
			"\nHint: Use the project virtualenv or install requirements:\n"
			"  source .venv/bin/activate\n  python -m pip install -r requirements.txt\n"
		)
		print(msg, file=sys.stderr)
		return 1
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes

<<<<<<< Updated upstream
	final_state = run_agent(problem)
	if args.verbose:
		print(json.dumps(final_state, indent=2, ensure_ascii=False))
	else:
<<<<<<< Updated upstream
<<<<<<< Updated upstream
		# Compact summary
		plan = final_state.get("plan")
		done = final_state.get("done")
		step_count = len(final_state.get("steps", []))
		print(json.dumps({"done": done, "steps": step_count, "plan": plan}, indent=2, ensure_ascii=False))
=======
=======
>>>>>>> Stashed changes
		print(json.dumps({
			"done": final_state.get("done"),
			"steps": len(final_state.get("steps", [])),
			"plan": final_state.get("plan"),
		}, indent=2, ensure_ascii=False))
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
=======
def main():
    """Main CLI."""
    parser = argparse.ArgumentParser(description="Synapse Agent")
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument("problem", nargs="?", help="Problem to solve")
    group.add_argument("-s", "--scenario", help="Use predefined scenario")
    group.add_argument("-l", "--list", action="store_true", help="List scenarios")
    
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-q", "--quiet", action="store_true", help="Minimal output")
    
    args = parser.parse_args()
    
    if args.list:
        print("📋 Scenarios:")
        for k, v in get_scenarios().items():
            print(f"  {k}: {v}")
        return
    
    if args.scenario:
        scenarios = get_scenarios()
        if args.scenario not in scenarios:
            print(f"❌ Unknown scenario: {args.scenario}")
            sys.exit(1)
        problem = scenarios[args.scenario]
    else:
        problem = args.problem
        if not problem:
            print("❌ Provide a problem or use --scenario")
            sys.exit(1)
    
    if not args.quiet:
        print(f"🚀 Solving: {problem}\n")
    
    try:
        start = datetime.now()
        result = run_agent(problem)
        duration = (datetime.now() - start).total_seconds()
        
        if not args.quiet:
            print(f"\n⏱️ Completed in {duration:.1f}s")
            print_chain_of_thought(result.get("steps", []), args.verbose)
        
        print_final_plan(result)
        
    except KeyboardInterrupt:
        print("\n⏸️ Interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
>>>>>>> Stashed changes
