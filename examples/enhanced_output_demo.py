#!/usr/bin/env python3
"""
Demo script showing the enhanced output formatting for Synapse Agent CLI.
This demonstrates what the output looks like with actual reasoning steps.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import print_chain_of_thought, print_final_plan, print_banner


def demo_enhanced_formatting():
    """Demonstrate the enhanced formatting with sample data."""
    
    # Print banner
    print_banner()
    
    print("🎯 Problem: A driver is at the customer's location, but the recipient is not available to receive a valuable package.")
    print()
    print("🚀 Starting Synapse Agent...")
    print("⏰ Time: 2025-09-01 00:12:47")
    print()
    
    # Sample reasoning steps
    sample_steps = [
        {
            "thought": "I need to contact the recipient first to see if they can receive the package or arrange an alternative time.",
            "action": {
                "tool_name": "contact_recipient_via_chat",
                "parameters": {
                    "recipient_id": "cust_789",
                    "message": "Your delivery is here. Are you available to receive it?"
                }
            },
            "observation": {
                "contact_successful": False,
                "status": "No response after 5 minutes",
                "recipient_response": None
            }
        },
        {
            "thought": "Contact failed - the recipient is not responding. Since this is a valuable package, I need to find a secure alternative. Let me reflect on the best approach.",
            "action": {
                "tool_name": "reflect",
                "parameters": {
                    "reason": "Recipient contact failed - need secure alternative for valuable package delivery"
                }
            },
            "observation": {
                "status": "reflection",
                "suggested_alternative": "suggest_safe_drop_off"
            }
        },
        {
            "thought": "Since this is a valuable package and the recipient is unavailable, I should look for a secure drop-off location that ensures package safety.",
            "action": {
                "tool_name": "suggest_safe_drop_off",
                "parameters": {
                    "location_type": "secure",
                    "package_value": "high"
                }
            },
            "observation": {
                "safe_option_available": True,
                "location": "Building concierge desk",
                "security_level": "High",
                "contact_info": "Concierge: +1-555-0199"
            }
        },
        {
            "thought": "Great! I found a secure location. Now I need to notify the customer about this alternative arrangement.",
            "action": {
                "tool_name": "notify_customer",
                "parameters": {
                    "customer_id": "cust_789",
                    "notification_type": "safe_drop_off",
                    "details": {
                        "location": "Building concierge desk",
                        "contact": "+1-555-0199"
                    }
                }
            },
            "observation": {
                "delivered": True,
                "message_id": "msg_456",
                "status": "Customer notified successfully"
            }
        }
    ]
    
    # Sample result
    sample_result = {
        "steps": sample_steps,
        "plan": "Coordinate with building concierge for secure package storage. Driver will leave the valuable package with the building concierge who will hold it securely until the recipient can collect it. Customer has been notified with pickup details including concierge contact information (+1-555-0199). This ensures package security while providing convenient access for the recipient.",
        "done": True,
        "needs_adaptation": True,
        "reflection_reason": "Recipient contact failed - need secure alternative for valuable package delivery"
    }
    
    print("⏰ Execution completed in 3.24 seconds")
    
    # Display the enhanced chain of thought
    print_chain_of_thought(sample_steps)
    
    # Display the enhanced final plan
    print_final_plan(sample_result)
    
    print("\n✅ Agent successfully resolved the logistics problem!")
    
    print("\n" + "=" * 70)
    print("🎨 FORMATTING FEATURES DEMONSTRATED:")
    print("=" * 70)
    print("✅ Clear boxed sections for each reasoning step")
    print("✅ Distinct headings: THOUGHT, ACTION, OBSERVATION")
    print("✅ Visual separation with box borders")
    print("✅ Professional FINAL PLAN presentation")
    print("✅ Structured EXECUTION SUMMARY")
    print("✅ Action vs Reflection step differentiation")
    print("✅ Proper line wrapping for readability")
    print("✅ Color-coded success/failure indicators")


if __name__ == "__main__":
    demo_enhanced_formatting()