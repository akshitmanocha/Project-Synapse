"""
Command-line interface for Synapse Agent.
"""

import sys
import os

# Import the main CLI function from the root main.py
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from main import run_cli


def main():
    """Entry point for the synapse-agent command."""
    run_cli()


if __name__ == "__main__":
    main()