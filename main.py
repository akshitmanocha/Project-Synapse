"""
CLI entry point to run the Synapse agent.

<<<<<<< Updated upstream
Usage:
  python main.py --problem "A driver is en route to Restaurant XYZ, but there's a report of a major accident on the main highway."

If --problem is omitted, a default example will be used.
=======
Examples:
  python main.py --problem "Driver stuck in traffic en route to Merchant ABC; check alternatives and notify customer." --verbose
>>>>>>> Stashed changes
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from dotenv import load_dotenv
<<<<<<< Updated upstream
from src.agent import run_agent


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Run the Synapse agent on a problem statement.")
	parser.add_argument("--problem", type=str, default=None, help="Problem statement for the agent to solve.")
	parser.add_argument("--verbose", action="store_true", help="Print the full final state JSON.")
	return parser.parse_args()
=======


def parse_args() -> argparse.Namespace:
	p = argparse.ArgumentParser(description="Run the Synapse agent on a problem statement.")
	p.add_argument("--problem", type=str, default=None, help="Problem statement for the agent to solve.")
	p.add_argument("--verbose", action="store_true", help="Print the full final state JSON.")
	return p.parse_args()
>>>>>>> Stashed changes


def main() -> int:
	args = parse_args()
<<<<<<< Updated upstream
=======
	# Load .env upfront so the agent sees GROQ_API_KEY if present
	load_dotenv(override=False)

>>>>>>> Stashed changes
	problem = args.problem or (
		"A driver is en route to Restaurant XYZ, but there's a report of a major accident on the main highway."
	)

<<<<<<< Updated upstream
	# Load .env first to avoid false negative note
	load_dotenv(override=False)
	if not os.getenv("GROQ_API_KEY"):
		print("[note] GROQ_API_KEY not found; reasoning may fail fast. Set it in a .env file to enable the LLM.", file=sys.stderr)
=======
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
>>>>>>> Stashed changes

	final_state = run_agent(problem)
	if args.verbose:
		print(json.dumps(final_state, indent=2, ensure_ascii=False))
	else:
<<<<<<< Updated upstream
		# Compact summary
		plan = final_state.get("plan")
		done = final_state.get("done")
		step_count = len(final_state.get("steps", []))
		print(json.dumps({"done": done, "steps": step_count, "plan": plan}, indent=2, ensure_ascii=False))
=======
		print(json.dumps({
			"done": final_state.get("done"),
			"steps": len(final_state.get("steps", [])),
			"plan": final_state.get("plan"),
		}, indent=2, ensure_ascii=False))
>>>>>>> Stashed changes
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
