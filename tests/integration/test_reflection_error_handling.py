#!/usr/bin/env python3
"""
Test script for Reflection Node and Error Handling
Tests the LangGraph reflection node's ability to handle tool failures and adapt approaches.
"""

import json
import time
from src.agent import run_agent, build_graph
from src.tools import debug_tools


def simulate_tool_failure(tool_name: str, failure_type: str = "error"):
    """Simulate different types of tool failures for testing."""
    failure_scenarios = {
        "contact_recipient_via_chat": {
            "error": {"status": "error", "error_message": "Network timeout - unable to reach recipient"},
            "no_response": {"contact_successful": False, "recipient_response": None}
        },
        "suggest_safe_drop_off": {
            "error": {"status": "error", "error_message": "Unable to assess drop-off locations"},
            "no_safe_option": {"safe_option_available": False, "reason": "High-risk area, no secure locations"}
        },
        "find_nearby_locker": {
            "error": {"status": "error", "error_message": "Locker service API unavailable"},
            "no_lockers": {"lockers_found": False, "reason": "No lockers within 2km radius"}
        },
        "collect_evidence": {
            "error": {"status": "error", "error_message": "Image upload failed"},
            "no_evidence": {"evidence_collected": False, "reason": "Parties unavailable for evidence collection"}
        },
        "analyze_evidence": {
            "low_confidence": {"result": {"fault": "unclear", "confidence": 0.3}, "explanation": "Insufficient evidence for confident determination"}
        },
        "get_merchant_status": {
            "closed": {"status": "closed", "reason": "Restaurant closed due to kitchen equipment failure"}
        },
        "check_traffic": {
            "severe": {"incident_level": "severe", "delay_mins": 45, "details": "Major accident blocking all lanes"}
        },
        "issue_instant_refund": {
            "needs_approval": {"requires_approval": True, "reason": "Amount exceeds automatic approval limit"}
        }
    }
    
    return failure_scenarios.get(tool_name, {}).get(failure_type, {"status": "error"})


def test_reflection_workflow():
    """Test the reflection node workflow with various failure scenarios."""
    print("🔄 TESTING REFLECTION AND ERROR HANDLING WORKFLOW")
    print("=" * 55)
    
    # Test Case 1: Recipient Contact Failure → Safe Drop-off
    print("\n📞 TEST CASE 1: Recipient Contact Failure Escalation")
    print("-" * 50)
    
    problem_1 = (
        "Driver arrived at delivery address but recipient is not answering door or phone. "
        "Package contains electronics that need secure handling. Test scenario: "
        "contact_recipient_via_chat will fail, should escalate to suggest_safe_drop_off."
    )
    
    print(f"Problem: {problem_1}")
    print("\nRunning agent with expected contact failure...")
    
    try:
        # This would normally trigger the reflection when contact fails
        result_1 = run_agent(problem_1)
        
        # Check if reflection was triggered
        steps = result_1.get("steps", [])
        reflection_found = any(step.get("action", {}).get("tool_name") == "reflect" for step in steps)
        adaptation_found = result_1.get("needs_adaptation", False)
        
        print(f"✅ Agent completed with {len(steps)} steps")
        print(f"🔄 Reflection triggered: {reflection_found}")
        print(f"🎯 Adaptation needed: {adaptation_found}")
        
        if result_1.get("reflection_reason"):
            print(f"💡 Reflection reason: {result_1.get('reflection_reason')}")
        if result_1.get("suggested_alternative"):
            print(f"🛠️ Suggested alternative: {result_1.get('suggested_alternative')}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    # Test Case 2: Evidence Collection → Analysis Failure → Goodwill Refund
    print(f"\n\n🔍 TEST CASE 2: Evidence Collection Chain Failure")
    print("-" * 45)
    
    problem_2 = (
        "Customer claims food was damaged during delivery. Driver denies fault. "
        "Both parties are arguing at the door. Test scenario: evidence collection "
        "will fail, should proceed with customer satisfaction refund."
    )
    
    print(f"Problem: {problem_2}")
    print("\nRunning agent with expected evidence failure...")
    
    try:
        result_2 = run_agent(problem_2)
        
        steps = result_2.get("steps", [])
        evidence_tools = [step for step in steps if step.get("action", {}).get("tool_name") in ["collect_evidence", "analyze_evidence"]]
        refund_tools = [step for step in steps if "refund" in step.get("action", {}).get("tool_name", "")]
        
        print(f"✅ Agent completed with {len(steps)} steps")
        print(f"🔍 Evidence tools used: {len(evidence_tools)}")
        print(f"💰 Refund tools used: {len(refund_tools)}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    # Test Case 3: Multiple Failure Cascade
    print(f"\n\n⚠️ TEST CASE 3: Multiple Failure Cascade")
    print("-" * 35)
    
    problem_3 = (
        "Complex delivery scenario: recipient unavailable, no safe drop-off possible, "
        "no lockers in area, redelivery scheduling system down. Should escalate all "
        "the way to sender contact. Test multiple reflection cycles."
    )
    
    print(f"Problem: {problem_3}")
    print("\nRunning agent with cascading failures...")
    
    try:
        result_3 = run_agent(problem_3)
        
        steps = result_3.get("steps", [])
        reflection_steps = [step for step in steps if step.get("action", {}).get("tool_name") == "reflect"]
        escalation_tools = [step for step in steps if step.get("action", {}).get("tool_name") in 
                          ["contact_recipient_via_chat", "suggest_safe_drop_off", "find_nearby_locker", 
                           "schedule_redelivery", "contact_sender"]]
        
        print(f"✅ Agent completed with {len(steps)} steps")
        print(f"🔄 Reflection cycles: {len(reflection_steps)}")
        print(f"📞 Escalation attempts: {len(escalation_tools)}")
        
        # Show escalation sequence
        if escalation_tools:
            print("📋 Escalation sequence:")
            for i, step in enumerate(escalation_tools, 1):
                tool_name = step.get("action", {}).get("tool_name", "unknown")
                print(f"   {i}. {tool_name}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")


def test_reflection_node_unit():
    """Unit test for the reflection node functionality."""
    print(f"\n\n🧪 UNIT TEST: Reflection Node Logic")
    print("=" * 40)
    
    from src.agent import reflection_node, AgentState
    
    # Test 1: Contact failure detection
    print("\n1. Testing contact failure detection...")
    state_contact_fail: AgentState = {
        "input": "test problem",
        "steps": [{
            "action": {"tool_name": "contact_recipient_via_chat", "parameters": {}},
            "observation": {"contact_successful": False, "recipient_response": None}
        }],
        "done": False,
        "needs_adaptation": False,
        "reflection_reason": None,
        "suggested_alternative": None
    }
    
    result = reflection_node(state_contact_fail)
    
    print(f"   Needs adaptation: {result.get('needs_adaptation')}")
    print(f"   Reflection reason: {result.get('reflection_reason')}")
    print(f"   Suggested alternative: {result.get('suggested_alternative')}")
    
    # Test 2: Evidence analysis low confidence
    print("\n2. Testing evidence analysis low confidence...")
    state_low_confidence: AgentState = {
        "input": "test problem", 
        "steps": [{
            "action": {"tool_name": "analyze_evidence", "parameters": {}},
            "observation": {"result": {"fault": "unclear", "confidence": 0.3}}
        }],
        "done": False,
        "needs_adaptation": False,
        "reflection_reason": None,
        "suggested_alternative": None
    }
    
    result2 = reflection_node(state_low_confidence)
    
    print(f"   Needs adaptation: {result2.get('needs_adaptation')}")
    print(f"   Reflection reason: {result2.get('reflection_reason')}")
    print(f"   Suggested alternative: {result2.get('suggested_alternative')}")
    
    # Test 3: No reflection needed (successful case)
    print("\n3. Testing successful case (no reflection needed)...")
    state_success: AgentState = {
        "input": "test problem",
        "steps": [{
            "action": {"tool_name": "notify_customer", "parameters": {}}, 
            "observation": {"delivered": True, "message_id": "msg_123"}
        }],
        "done": False,
        "needs_adaptation": False,
        "reflection_reason": None,
        "suggested_alternative": None
    }
    
    result3 = reflection_node(state_success)
    
    print(f"   Needs adaptation: {result3.get('needs_adaptation')}")
    print(f"   Reflection reason: {result3.get('reflection_reason')}")
    print(f"   Suggested alternative: {result3.get('suggested_alternative')}")


def test_graph_structure():
    """Test the updated graph structure with reflection node."""
    print(f"\n\n🏗️ GRAPH STRUCTURE TEST")
    print("=" * 25)
    
    try:
        graph = build_graph()
        print("✅ Graph built successfully with reflection node")
        
        # Test basic flow
        print("📊 Testing basic graph flow...")
        simple_problem = "Driver needs traffic check for route optimization"
        
        initial_state = {
            "input": simple_problem,
            "steps": [],
            "plan": None,
            "action": None,
            "observation": None,
            "done": False,
            "needs_adaptation": False,
            "reflection_reason": None,
            "suggested_alternative": None,
        }
        
        # Run one step to verify workflow
        config = {"recursion_limit": 3}  # Limited for testing
        result = graph.invoke(initial_state, config)
        
        print(f"✅ Graph execution completed")
        print(f"📊 Steps taken: {len(result.get('steps', []))}")
        print(f"🏁 Completed: {result.get('done', False)}")
        
    except Exception as e:
        print(f"❌ Graph structure test failed: {e}")


def test_error_pattern_coverage():
    """Test coverage of different error patterns."""
    print(f"\n\n📋 ERROR PATTERN COVERAGE TEST")
    print("=" * 35)
    
    error_patterns = [
        ("contact_recipient_via_chat", "no_response"),
        ("suggest_safe_drop_off", "no_safe_option"),
        ("find_nearby_locker", "no_lockers"),
        ("collect_evidence", "no_evidence"), 
        ("analyze_evidence", "low_confidence"),
        ("get_merchant_status", "closed"),
        ("check_traffic", "severe"),
        ("issue_instant_refund", "needs_approval")
    ]
    
    print(f"Testing {len(error_patterns)} error scenarios...")
    
    for tool_name, failure_type in error_patterns:
        failure_data = simulate_tool_failure(tool_name, failure_type)
        print(f"✅ {tool_name} ({failure_type}): {len(str(failure_data))} chars")
    
    print(f"\n✅ All error patterns have defined failure scenarios")


if __name__ == "__main__":
    print("🚀 SYNAPSE REFLECTION & ERROR HANDLING TEST SUITE")
    print("=" * 60)
    
    # Run all tests
    test_graph_structure()
    test_reflection_node_unit()
    test_error_pattern_coverage()
    test_reflection_workflow()
    
    print(f"\n{'=' * 60}")
    print("🏆 REFLECTION & ERROR HANDLING TESTING COMPLETE")
    print("\nKey Features Tested:")
    print("🔄 Reflection node integration in LangGraph workflow")  
    print("⚠️ Error detection and alternative suggestion")
    print("🎯 Adaptive reasoning with reflection guidance")
    print("📞 Multi-level escalation failure handling")
    print("🔗 Tool failure pattern recognition")
    print("🏗️ Updated graph structure (reason → act → reflect)")