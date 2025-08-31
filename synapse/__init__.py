"""
Synapse: Autonomous Logistics Coordination Agent

A sophisticated multi-stakeholder coordination platform for last-mile logistics,
featuring advanced decision-making, error handling, and adaptive problem-solving.
"""

__version__ = "1.0.0"
__author__ = "Synapse Team"

from synapse.agent.agent import run_agent, build_graph, AgentState
from synapse.tools.tools import debug_tools

__all__ = [
    "run_agent",
    "build_graph", 
    "AgentState",
    "debug_tools",
]