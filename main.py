"""
CLI entry point to run the Synapse agent.

Usage:
  python main.py --problem "A driver is en route to Restaurant XYZ, but there's a report of a major accident on the main highway."

If --problem is omitted, a default example will be used.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from dotenv import load_dotenv
from src.agent import run_agent


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Run the Synapse agent on a problem statement.")
	parser.add_argument("--problem", type=str, default=None, help="Problem statement for the agent to solve.")
	parser.add_argument("--verbose", action="store_true", help="Print the full final state JSON.")
	return parser.parse_args()


def main() -> int:
	args = parse_args()
	problem = args.problem or (
		"A driver is en route to Restaurant XYZ, but there's a report of a major accident on the main highway."
	)

	# Load .env first to avoid false negative note
	load_dotenv(override=False)
	if not os.getenv("GROQ_API_KEY"):
		print("[note] GROQ_API_KEY not found; reasoning may fail fast. Set it in a .env file to enable the LLM.", file=sys.stderr)

	final_state = run_agent(problem)
	if args.verbose:
		print(json.dumps(final_state, indent=2, ensure_ascii=False))
	else:
		# Compact summary
		plan = final_state.get("plan")
		done = final_state.get("done")
		step_count = len(final_state.get("steps", []))
		print(json.dumps({"done": done, "steps": step_count, "plan": plan}, indent=2, ensure_ascii=False))
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
