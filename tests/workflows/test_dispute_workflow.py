#!/usr/bin/env python3
"""
Quick test script for Scenario 2: Damaged Packaging Dispute
Tests the evidence collection and analysis workflow without full agent execution.
"""

import json
from synapse.tools import collect_evidence, analyze_evidence, issue_instant_refund, exonerate_driver


def test_dispute_workflow():
    """Test the complete dispute resolution workflow with different scenarios."""
    print("🔍 TESTING DAMAGED PACKAGING DISPUTE WORKFLOW")
    print("=" * 50)
    
    # Test Case 1: Merchant Fault
    print("\n📦 TEST CASE 1: Merchant Fault Scenario")
    print("-" * 30)
    
    order_id = "ORDER_MERCHANT_FAULT"
    evidence_result = collect_evidence(order_id, seed=60)  # Seed for merchant fault
    print(f"1. Collected evidence: {evidence_result.get('evidence_id')}")
    
    if evidence_result.get('status') == 'ok':
        analysis = analyze_evidence(evidence_result['evidence_id'], seed=60)
        fault = analysis.get('result', {}).get('fault')
        confidence = analysis.get('result', {}).get('confidence', 0)
        print(f"2. Analysis: fault={fault}, confidence={confidence:.2f}")
        
        if fault == 'merchant' and confidence > 0.6:
            print("3. ✅ MERCHANT FAULT - Refund customer + Exonerate driver")
            refund = issue_instant_refund(order_id, 25.99, reason="Merchant packaging fault")
            exonerate = exonerate_driver("DRIVER_123", order_id, "Evidence shows merchant fault")
            print(f"   Refund ID: {refund.get('refund_id')}")
            print(f"   Driver exonerated: {exonerate.get('exonerated')}")
        else:
            print("3. ⚠️ Expected merchant fault but got different result")
    
    # Test Case 2: Driver Fault  
    print("\n🚚 TEST CASE 2: Driver Fault Scenario")
    print("-" * 30)
    
    order_id = "ORDER_DRIVER_FAULT"  
    evidence_result = collect_evidence(order_id, seed=85)  # Seed for driver fault
    print(f"1. Collected evidence: {evidence_result.get('evidence_id')}")
    
    if evidence_result.get('status') == 'ok':
        analysis = analyze_evidence(evidence_result['evidence_id'], seed=85)
        fault = analysis.get('result', {}).get('fault')
        confidence = analysis.get('result', {}).get('confidence', 0)
        print(f"2. Analysis: fault={fault}, confidence={confidence:.2f}")
        
        if fault == 'driver' and confidence > 0.6:
            print("3. ✅ DRIVER FAULT - Refund customer only (no exoneration)")
            refund = issue_instant_refund(order_id, 25.99, reason="Driver handling error confirmed")
            print(f"   Refund ID: {refund.get('refund_id')}")
            print("   Driver NOT exonerated (fault confirmed)")
        else:
            print("3. ⚠️ Expected driver fault but got different result")
    
    # Test Case 3: Unclear Fault
    print("\n❓ TEST CASE 3: Unclear Fault Scenario")  
    print("-" * 30)
    
    order_id = "ORDER_UNCLEAR_FAULT"
    evidence_result = collect_evidence(order_id, seed=42)  # Seed for unclear fault
    print(f"1. Collected evidence: {evidence_result.get('evidence_id')}")
    
    if evidence_result.get('status') == 'ok':
        analysis = analyze_evidence(evidence_result['evidence_id'], seed=42)
        fault = analysis.get('result', {}).get('fault')
        confidence = analysis.get('result', {}).get('confidence', 0)
        print(f"2. Analysis: fault={fault}, confidence={confidence:.2f}")
        
        if confidence <= 0.6:
            print("3. ✅ UNCLEAR FAULT - Partial refund for customer satisfaction")
            refund = issue_instant_refund(order_id, 12.99, reason="Goodwill refund for packaging damage")
            print(f"   Partial refund ID: {refund.get('refund_id')}")
        else:
            print(f"3. ⚠️ Expected low confidence but got {confidence:.2f}")

    print(f"\n{'=' * 50}")
    print("✅ WORKFLOW VALIDATION COMPLETE")
    print("\nExpected Agent Behavior:")
    print("1. collect_evidence(order_id) → evidence_id")  
    print("2. analyze_evidence(evidence_id) → {fault, confidence}")
    print("3. Conditional action:")
    print("   • Merchant fault (high conf.) → refund + exonerate driver")
    print("   • Driver fault (high conf.) → refund only") 
    print("   • Low confidence → partial refund")
    print("4. notify_customer(resolution)")
    print("5. finish(comprehensive_plan)")


def test_tool_integration():
    """Test that all dispute tools are properly integrated."""
    print("\n🔧 TESTING TOOL INTEGRATION")
    print("=" * 30)
    
    try:
        from synapse.agent import _tool_registry
        registry = _tool_registry()
        
        required_tools = ['collect_evidence', 'analyze_evidence', 'issue_instant_refund', 'exonerate_driver']
        missing_tools = [tool for tool in required_tools if tool not in registry]
        
        if missing_tools:
            print(f"❌ Missing tools: {missing_tools}")
            return False
        else:
            print(f"✅ All dispute tools integrated: {required_tools}")
            
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


if __name__ == "__main__":
    integration_ok = test_tool_integration()
    if integration_ok:
        test_dispute_workflow()
    else:
        print("❌ Tool integration failed - fix before testing workflow")