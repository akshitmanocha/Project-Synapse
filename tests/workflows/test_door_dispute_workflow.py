#!/usr/bin/env python3
"""
Quick test script for Scenario 2.3: At-Door Dispute Over Damaged Item
Tests the immediate dispute resolution workflow with real-time evidence collection.
"""

import json
from src.tools import collect_evidence, analyze_evidence, issue_instant_refund, exonerate_driver, log_merchant_packaging_feedback, notify_customer


def test_door_dispute_workflow():
    """Test the complete at-door dispute resolution workflow."""
    print("🚪 TESTING AT-DOOR DISPUTE WORKFLOW")
    print("=" * 40)
    
    # Test Case 1: Merchant Fault - Packaging Issue
    print("\n📦 TEST CASE 1: Merchant Fault - Poor Packaging")
    print("-" * 45)
    
    order_id = "ORDER_BELLA_001"
    driver_id = "DRIVER_789"
    customer_id = "CUST_456"
    merchant_id = "bellas_bistro"
    
    # Step 1: Immediate evidence collection (urgent!)
    print("1. 🚨 URGENT: Collecting evidence while parties present at door...")
    evidence_result = collect_evidence(order_id, requester="agent", ask_photos=True, seed=25)
    evidence_id = evidence_result.get('evidence_id')
    print(f"   Evidence collected: {evidence_id}")
    print(f"   Requests sent to customer & driver: {evidence_result.get('requests_sent')}")
    
    # Step 2: Rapid analysis (while parties wait)
    print("\n2. ⚡ RAPID: Analyzing evidence immediately...")
    analysis_result = analyze_evidence(evidence_id, seed=25)
    fault = analysis_result.get('result', {}).get('fault', 'unknown')
    confidence = analysis_result.get('result', {}).get('confidence', 0)
    explanation = analysis_result.get('explanation', '')
    
    print(f"   Analysis result: fault={fault}, confidence={confidence:.2f}")
    print(f"   Explanation: {explanation}")
    
    # Step 3: On-spot resolution based on analysis
    print(f"\n3. 💡 ON-SPOT RESOLUTION:")
    if fault == 'merchant' and confidence > 0.6:
        print("   → Merchant fault confirmed with high confidence")
        print("   → Processing immediate customer refund...")
        
        refund_result = issue_instant_refund(
            order_id, 
            28.50, 
            reason="Container leaked due to poor merchant packaging"
        )
        print(f"   Refund processed: ${refund_result.get('amount')} (ID: {refund_result.get('refund_id')})")
        
        print("   → Exonerating driver from fault...")
        exonerate_result = exonerate_driver(
            driver_id, 
            order_id, 
            reason="Evidence shows merchant packaging failure, not driver mishandling"
        )
        print(f"   Driver exonerated: {exonerate_result.get('exonerated')}")
        
        print("   → Maintaining professional relations with customer...")
        customer_msg = "We sincerely apologize for this packaging issue. A full refund has been processed immediately. This was due to restaurant packaging, not our driver's handling."
        notify_result = notify_customer(customer_id, customer_msg)
        print(f"   Customer notified professionally: {notify_result.get('delivered')}")
        
    elif fault == 'driver' and confidence > 0.6:
        print("   → Driver fault confirmed")
        print("   → Processing customer refund (driver accountability)")
        refund_result = issue_instant_refund(order_id, 28.50, reason="Driver mishandling confirmed")
        print(f"   Refund: ${refund_result.get('amount')}")
        print("   → Driver NOT exonerated (fault confirmed)")
        
    else:
        print("   → Fault unclear or low confidence")
        print("   → Processing goodwill refund for customer satisfaction")
        refund_result = issue_instant_refund(order_id, 14.25, reason="Goodwill refund for delivery issue")
        print(f"   Partial refund: ${refund_result.get('amount')}")
    
    # Step 4: Preventive feedback to merchant (after resolution)
    print(f"\n4. 🔄 PREVENTIVE: Logging merchant feedback...")
    feedback = {
        "issue_type": "packaging_failure",
        "details": "Pasta container leaked during delivery",
        "recommendation": "Use better sealing containers for liquid-containing items",
        "incident_id": evidence_id,
        "severity": "high"
    }
    
    feedback_result = log_merchant_packaging_feedback(merchant_id, feedback)
    print(f"   Merchant feedback logged: {feedback_result.get('logged')}")
    print(f"   Feedback ID: {feedback_result.get('feedback_id')}")
    
    # Test Case 2: Driver Fault Scenario
    print(f"\n\n🚗 TEST CASE 2: Driver Fault - Mishandling")
    print("-" * 40)
    
    order_id_2 = "ORDER_BELLA_002"
    evidence_2 = collect_evidence(order_id_2, seed=75)  # Different seed for driver fault
    analysis_2 = analyze_evidence(evidence_2.get('evidence_id'), seed=75)
    
    fault_2 = analysis_2.get('result', {}).get('fault', 'unknown')
    confidence_2 = analysis_2.get('result', {}).get('confidence', 0)
    
    print(f"   Analysis: fault={fault_2}, confidence={confidence_2:.2f}")
    
    if fault_2 == 'driver' and confidence_2 > 0.6:
        print("   ✅ Driver fault scenario - refund issued, no exoneration")
        refund_2 = issue_instant_refund(order_id_2, 28.50, reason="Driver mishandling confirmed")
        print(f"   Customer compensated: ${refund_2.get('amount')}")
        print("   Driver held accountable (no exoneration)")
        
        # Still log merchant feedback for improvement
        feedback_2 = {
            "issue_type": "general_feedback",
            "details": "Customer reported damage, consider reinforced packaging",
            "recommendation": "Double-bag items prone to damage",
            "severity": "medium"
        }
        log_merchant_packaging_feedback(merchant_id, feedback_2)
        print("   Merchant feedback still logged for continuous improvement")
    
    print(f"\n{'=' * 40}")
    print("✅ AT-DOOR DISPUTE WORKFLOW COMPLETE")
    print("\nKey Success Factors:")
    print("🚨 URGENCY: Evidence collected immediately while parties present")
    print("⚡ SPEED: Rapid analysis and on-spot resolution")
    print("🤝 PROFESSIONALISM: Maintained relationships with all parties")
    print("🔄 PREVENTION: Merchant feedback prevents future issues")
    print("⚖️ FAIRNESS: Evidence-based decisions protect innocent parties")


def test_tool_integration():
    """Test that all at-door dispute tools are properly integrated."""
    print("\n🔧 TESTING AT-DOOR DISPUTE TOOL INTEGRATION")
    print("=" * 45)
    
    try:
        from src.agent import _tool_registry
        registry = _tool_registry()
        
        required_tools = [
            'collect_evidence', 
            'analyze_evidence', 
            'issue_instant_refund', 
            'exonerate_driver',
            'log_merchant_packaging_feedback',
            'notify_customer'
        ]
        
        missing_tools = [tool for tool in required_tools if tool not in registry]
        
        if missing_tools:
            print(f"❌ Missing tools: {missing_tools}")
            return False
        else:
            print(f"✅ All at-door dispute tools integrated: {len(required_tools)}/6")
            
        # Test each tool adapter
        for tool_name in required_tools:
            try:
                tool_func = registry[tool_name]
                print(f"✅ {tool_name} adapter: OK")
            except Exception as e:
                print(f"❌ {tool_name} adapter: {e}")
                return False
                
        return True
        
    except Exception as e:
        print(f"❌ Tool integration test failed: {e}")
        return False


def test_urgency_simulation():
    """Simulate the urgency aspect of at-door disputes."""
    print("\n⏱️ URGENCY SIMULATION: At-Door Dispute Timeline")
    print("=" * 50)
    
    import time
    
    print("🚪 Parties present at door - dispute active")
    print("⏰ T+0s: Customer opens bag, discovers damage")
    print("😠 T+10s: Customer upset, blames driver")
    print("🛡️ T+15s: Driver denies fault, tension rising")
    
    start_time = time.time()
    
    print("🚨 T+20s: AGENT ACTIVATED - Evidence collection initiated")
    evidence = collect_evidence("URGENT_ORDER", seed=42)
    evidence_time = time.time() - start_time
    
    print("⚡ T+25s: Evidence analysis in progress...")
    analysis = analyze_evidence(evidence.get('evidence_id'), seed=42)
    analysis_time = time.time() - start_time
    
    print("💡 T+30s: Resolution determined, processing refund...")
    refund = issue_instant_refund("URGENT_ORDER", 25.99, reason="Immediate dispute resolution")
    resolution_time = time.time() - start_time
    
    print("🤝 T+35s: All parties informed, situation de-escalated")
    total_time = time.time() - start_time
    
    print(f"\n📊 PERFORMANCE METRICS:")
    print(f"   Evidence collection: {evidence_time:.2f}s")
    print(f"   Analysis completion: {analysis_time:.2f}s") 
    print(f"   Resolution delivery: {resolution_time:.2f}s")
    print(f"   Total dispute time: {total_time:.2f}s")
    
    if total_time < 2.0:  # Under 2 seconds is excellent
        print("🏆 EXCELLENT: Sub-2-second dispute resolution!")
    elif total_time < 5.0:
        print("✅ GOOD: Fast dispute resolution")
    else:
        print("⚠️ SLOW: May cause tension escalation")


if __name__ == "__main__":
    integration_ok = test_tool_integration()
    if integration_ok:
        test_door_dispute_workflow()
        test_urgency_simulation()
    else:
        print("❌ Tool integration failed - fix before testing workflow")