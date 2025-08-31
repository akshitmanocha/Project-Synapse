#!/usr/bin/env python3
"""
Demo script showing verbose mode output formatting.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import print_chain_of_thought


def demo_verbose_formatting():
    """Demonstrate the verbose formatting with detailed observations."""
    
    print("🎯 VERBOSE MODE DEMONSTRATION")
    print("=" * 70)
    
    # Sample steps with detailed observations for verbose mode
    verbose_steps = [
        {
            "thought": "I need to analyze the evidence from the damaged package dispute to determine fault.",
            "action": {
                "tool_name": "analyze_evidence",
                "parameters": {
                    "evidence_id": "ev_123",
                    "dispute_type": "packaging_damage",
                    "analysis_depth": "detailed"
                }
            },
            "observation": {
                "result": {
                    "fault": "merchant_packaging",
                    "confidence": 0.85,
                    "evidence_items": [
                        "Insufficient bubble wrap",
                        "Box too large for item",
                        "No 'fragile' marking"
                    ],
                    "driver_actions": "Proper handling confirmed via GPS data",
                    "merchant_response": "Acknowledged packaging error"
                },
                "explanation": "Evidence strongly suggests merchant packaging error. Driver GPS data shows no rough handling or drops during delivery. Merchant acknowledged using inappropriate box size without adequate protection.",
                "recommendation": "Partial refund appropriate, merchant training recommended"
            }
        }
    ]
    
    print("\nNormal Mode:")
    print_chain_of_thought(verbose_steps, verbose=False)
    
    print("\n" + "=" * 70)
    print("Verbose Mode:")
    print_chain_of_thought(verbose_steps, verbose=True)


if __name__ == "__main__":
    demo_verbose_formatting()