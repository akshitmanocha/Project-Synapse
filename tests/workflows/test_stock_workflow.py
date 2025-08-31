#!/usr/bin/env python3
"""
Quick test script for Scenario 2.2: Item Out of Stock
Tests the stock management and substitute workflow without full agent execution.
"""

import json
from src.tools import get_merchant_status, contact_merchant, propose_substitute, issue_partial_refund, notify_customer


def test_stock_workflow():
    """Test the complete item out of stock resolution workflow."""
    print("📦 TESTING ITEM OUT OF STOCK WORKFLOW")
    print("=" * 45)
    
    # Test Case 1: Stock Issue with Successful Substitution
    print("\n🍕 TEST CASE 1: Stock Issue with Substitution")
    print("-" * 35)
    
    order_id = "ORDER_MARIO_001"
    merchant_id = "mario_pizzeria"
    
    # Step 1: Check merchant status (should show items out of stock)
    print("1. Checking merchant status...")
    merchant_status = get_merchant_status(merchant_id, seed=30)  # Seed for stock issues
    print(f"   Merchant: {merchant_status.get('merchant_id')}")
    print(f"   Open: {merchant_status.get('open')}")
    print(f"   Stock: {merchant_status.get('stock', {})}")
    
    # Check if there are stock issues
    stock = merchant_status.get('stock', {})
    out_of_stock_items = [item for item, available in stock.items() if not available]
    print(f"   Out of stock: {out_of_stock_items}")
    
    # Step 2: Contact merchant to confirm and get alternatives
    print("\n2. Contacting merchant for confirmation...")
    contact_result = contact_merchant(
        merchant_id, 
        f"Customer order {order_id} includes items that show as out of stock: {out_of_stock_items}. Can you confirm availability and suggest alternatives?",
        seed=30
    )
    print(f"   Merchant acknowledged: {contact_result.get('acknowledged')}")
    print(f"   Response: {contact_result.get('response')}")
    
    # Step 3: Propose substitutes (if merchant confirms stock issues)
    if contact_result.get('acknowledged') and out_of_stock_items:
        print("\n3. Proposing substitute items...")
        substitute_items = [
            {"original": "garlic_bread", "substitute": "cheesy_breadsticks", "price_difference": 0.50},
            {"original": "coke", "substitute": "pepsi", "price_difference": 0.0}
        ]
        
        substitute_result = propose_substitute(order_id, substitute_items, seed=30)
        print(f"   Substitutes proposed: {substitute_result.get('substitutes')}")
        print(f"   Customer confirmation requested: {substitute_result.get('requested_confirmation')}")
        
        # Step 4: Notify customer of substitutes
        print("\n4. Notifying customer of available substitutes...")
        customer_message = f"Your order from Mario's Pizzeria has some items unavailable. We've proposed alternatives: {substitute_items}. Please confirm if you'd like these substitutes or prefer a partial refund."
        
        notify_result = notify_customer("CUST_001", customer_message, seed=30)
        print(f"   Customer notified: {notify_result.get('delivered')}")
        print(f"   Message ID: {notify_result.get('message_id')}")
    
    # Test Case 2: No Suitable Substitutes - Partial Refund Path
    print(f"\n\n💸 TEST CASE 2: No Substitutes - Partial Refund")
    print("-" * 40)
    
    order_id_2 = "ORDER_MARIO_002"
    
    # Simulate customer declining substitutes or no suitable alternatives
    print("1. Customer declined substitutes or no alternatives available...")
    print("2. Processing partial refund...")
    
    # Calculate refund amount (for unavailable items)
    unavailable_items_value = 8.50  # garlic bread $4.00 + coke $4.50
    refund_result = issue_partial_refund(order_id_2, unavailable_items_value, seed=30)
    
    print(f"   Refund processed: {refund_result.get('issued')}")
    print(f"   Refund ID: {refund_result.get('refund_id')}")
    print(f"   Amount: ${refund_result.get('amount')}")
    
    # Step 3: Notify customer of refund
    print("\n3. Notifying customer of partial refund...")
    refund_message = f"We've processed a partial refund of ${refund_result.get('amount')} for the unavailable items. Your remaining order (Margherita pizza) is being prepared and will be delivered as scheduled."
    
    final_notify = notify_customer("CUST_002", refund_message, seed=30)
    print(f"   Final notification sent: {final_notify.get('delivered')}")

    print(f"\n{'=' * 45}")
    print("✅ STOCK WORKFLOW VALIDATION COMPLETE")
    print("\nExpected Agent Behavior:")
    print("1. get_merchant_status(merchant_id) → identify stock issues")
    print("2. contact_merchant(merchant_id, inquiry) → confirm availability")  
    print("3. propose_substitute(order_id, alternatives) → offer options")
    print("4. notify_customer(alternatives) → customer choice")
    print("5. IF accepted: update order")
    print("   IF declined: issue_partial_refund(unavailable_items)")
    print("6. notify_customer(final_resolution)")
    print("7. finish(comprehensive_plan)")


def test_tool_integration():
    """Test that all stock management tools are properly integrated."""
    print("\n🔧 TESTING STOCK TOOL INTEGRATION")
    print("=" * 35)
    
    try:
        from src.agent import _tool_registry
        registry = _tool_registry()
        
        required_tools = ['get_merchant_status', 'contact_merchant', 'propose_substitute', 'issue_partial_refund', 'notify_customer']
        missing_tools = [tool for tool in required_tools if tool not in registry]
        
        if missing_tools:
            print(f"❌ Missing tools: {missing_tools}")
            return False
        else:
            print(f"✅ All stock management tools integrated: {len(required_tools)}/5")
            
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
        test_stock_workflow()
    else:
        print("❌ Tool integration failed - fix before testing workflow")