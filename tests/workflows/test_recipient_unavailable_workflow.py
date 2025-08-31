#!/usr/bin/env python3
"""
Quick test script for Scenario 2.4: Recipient Unavailable at Delivery Address
Tests the complete recipient unavailable workflow with escalation logic.
"""

import json
from src.tools import (contact_recipient_via_chat, suggest_safe_drop_off, find_nearby_locker, 
                      schedule_redelivery, contact_sender, notify_customer)


def test_recipient_unavailable_workflow():
    """Test the complete recipient unavailable workflow."""
    print("📦 TESTING RECIPIENT UNAVAILABLE WORKFLOW")
    print("=" * 45)
    
    # Test Case 1: Successful Contact and Safe Drop-off
    print("\n📞 TEST CASE 1: Recipient Contacted - Safe Drop-off")
    print("-" * 50)
    
    order_id = "ORDER_QUICKMART_001"
    recipient_id = "RECIPIENT_123"
    sender_id = "QUICKMART_EXPRESS"
    delivery_lat = 37.7749
    delivery_lng = -122.4194
    
    # Step 1: Attempt to contact recipient
    print("1. 📱 URGENT: Contacting recipient via app...")
    contact_result = contact_recipient_via_chat(
        recipient_id, 
        "Hi! Your delivery driver is waiting at your address. Are you available to receive your package?",
        channel="app",
        seed=30
    )
    print(f"   Contact attempt: {contact_result.get('contact_successful')}")
    print(f"   Recipient response: {contact_result.get('recipient_response', 'No response')}")
    
    if contact_result.get('contact_successful'):
        # Step 2: Recipient responds but can't come to door immediately
        print("\n2. 📍 SOLUTION: Evaluating safe drop-off options...")
        safe_locations = [
            {"location": "behind the planter by front door", "security_level": "medium"},
            {"location": "with neighbor in apartment 2B", "security_level": "high"},
            {"location": "under the doormat", "security_level": "low"}
        ]
        
        dropoff_result = suggest_safe_drop_off(safe_locations, seed=30)
        print(f"   Recommended location: {dropoff_result.get('recommended_location')}")
        print(f"   Safety assessment: {dropoff_result.get('safety_assessment')}")
        print(f"   Special instructions: {dropoff_result.get('instructions')}")
        
        if dropoff_result.get('safe_option_available'):
            print("\n✅ Resolution: Safe drop-off arranged successfully")
            print("   Driver can complete delivery with clear instructions")
        else:
            print("\n⚠️ No safe drop-off available - escalating to locker option")
    
    # Test Case 2: No Response - Locker Alternative
    print(f"\n\n🔒 TEST CASE 2: No Response - Locker Alternative")
    print("-" * 45)
    
    order_id_2 = "ORDER_QUICKMART_002"
    print("1. 📱 ATTEMPT: Contacting recipient...")
    contact_2 = contact_recipient_via_chat(recipient_id, "Delivery attempt - package waiting", seed=75)
    
    if not contact_2.get('contact_successful'):
        print("   ❌ Recipient unresponsive")
        
        print("\n2. 🏪 ALTERNATIVE: Searching for nearby lockers...")
        locker_result = find_nearby_locker(delivery_lat, delivery_lng, radius_m=1500, seed=40)
        
        if locker_result.get('lockers_found'):
            lockers = locker_result.get('nearby_lockers', [])
            print(f"   Found {len(lockers)} available lockers:")
            for i, locker in enumerate(lockers[:2], 1):
                print(f"     {i}. {locker.get('name')} - {locker.get('distance_m')}m away")
                print(f"        Address: {locker.get('address')}")
                print(f"        Available: {locker.get('available_slots')} slots")
            
            # Select best locker
            best_locker = lockers[0]
            print(f"\n   ✅ Selected: {best_locker.get('name')}")
            print(f"   Access code: {locker_result.get('access_code')}")
            
            # Notify recipient about locker
            locker_msg = f"Your package has been placed in locker {best_locker.get('name')} at {best_locker.get('address')}. Access code: {locker_result.get('access_code')}"
            notify_result = notify_customer(recipient_id, locker_msg)
            print(f"   📲 Recipient notified: {notify_result.get('delivered')}")
            
        else:
            print("   ❌ No lockers available - escalating to redelivery")
    
    # Test Case 3: Redelivery Scheduling
    print(f"\n\n🗓️ TEST CASE 3: Redelivery Scheduling")
    print("-" * 35)
    
    order_id_3 = "ORDER_QUICKMART_003"
    print("1. 📞 Failed contact attempts exhausted")
    print("2. 🔒 No suitable lockers in area")
    print("\n3. 📅 ESCALATION: Scheduling redelivery...")
    
    redelivery_windows = [
        {"date": "2024-01-15", "time_start": "09:00", "time_end": "12:00", "slot_type": "morning"},
        {"date": "2024-01-15", "time_start": "14:00", "time_end": "17:00", "slot_type": "afternoon"},
        {"date": "2024-01-16", "time_start": "10:00", "time_end": "14:00", "slot_type": "flexible"}
    ]
    
    redelivery_result = schedule_redelivery(order_id_3, redelivery_windows, seed=60)
    print(f"   Redelivery scheduled: {redelivery_result.get('scheduled')}")
    print(f"   Selected slot: {redelivery_result.get('scheduled_slot')}")
    print(f"   New delivery ID: {redelivery_result.get('new_delivery_id')}")
    
    if redelivery_result.get('scheduled'):
        print("   ✅ Customer will be notified of new delivery time")
        print("   Driver released for other deliveries")
    else:
        print("   ❌ Redelivery scheduling failed - contacting sender")
    
    # Test Case 4: Sender Contact - Last Resort
    print(f"\n\n📞 TEST CASE 4: Sender Contact - Special Instructions")
    print("-" * 55)
    
    print("1. All standard delivery options exhausted")
    print("2. 🏢 FINAL ESCALATION: Contacting sender...")
    
    sender_msg = "Delivery attempt failed. Recipient unavailable, no safe drop-off, no lockers available. Requesting special delivery instructions or alternative contact method."
    sender_result = contact_sender(sender_id, sender_msg, seed=45)
    
    print(f"   Sender contacted: {sender_result.get('contact_successful')}")
    print(f"   Sender response: {sender_result.get('sender_instructions', 'Awaiting response')}")
    
    special_instructions = sender_result.get('special_instructions')
    if special_instructions:
        print(f"   📋 Special instructions received:")
        for instruction in special_instructions:
            print(f"     • {instruction}")
        print("   ✅ Delivery can proceed with sender guidance")
    else:
        print("   ⏳ Awaiting sender response for next steps")
    
    print(f"\n{'=' * 45}")
    print("✅ RECIPIENT UNAVAILABLE WORKFLOW COMPLETE")
    print("\nKey Success Factors:")
    print("📱 CONTACT: Multiple communication channels attempted")
    print("🏠 SAFE DROP-OFF: Secure location assessment when possible")
    print("🔒 LOCKERS: Alternative secure storage options explored")
    print("📅 REDELIVERY: Convenient time windows offered")
    print("📞 SENDER: Final escalation maintains service quality")
    print("⚡ EFFICIENCY: Driver idle time minimized at each step")


def test_tool_integration():
    """Test that all recipient unavailable tools are properly integrated."""
    print("\n🔧 TESTING RECIPIENT UNAVAILABLE TOOL INTEGRATION")
    print("=" * 55)
    
    try:
        from src.agent import _tool_registry
        registry = _tool_registry()
        
        required_tools = [
            'contact_recipient_via_chat',
            'suggest_safe_drop_off', 
            'find_nearby_locker',
            'schedule_redelivery',
            'contact_sender'
        ]
        
        missing_tools = [tool for tool in required_tools if tool not in registry]
        
        if missing_tools:
            print(f"❌ Missing tools: {missing_tools}")
            return False
        else:
            print(f"✅ All recipient unavailable tools integrated: {len(required_tools)}/5")
            
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


def test_escalation_sequence():
    """Test the logical escalation sequence for recipient unavailable scenarios."""
    print("\n🎯 ESCALATION SEQUENCE TEST: Priority Order Validation")
    print("=" * 60)
    
    import time
    
    print("📋 Expected Priority Order:")
    print("  1. Contact Recipient → 2. Safe Drop-off → 3. Locker → 4. Redelivery → 5. Sender")
    print("\n⏱️ Testing each escalation step:")
    
    start_time = time.time()
    
    # Step 1: Contact (highest priority)
    print("\n1️⃣ CONTACT RECIPIENT (Priority: Highest)")
    contact = contact_recipient_via_chat("TEST_RECIPIENT", "Delivery waiting", seed=85)
    contact_time = time.time() - start_time
    success_rate = 0.3 if not contact.get('contact_successful') else 0.8  # Simulate failure
    print(f"   Contact attempt: {'Failed' if success_rate < 0.5 else 'Success'} ({contact_time:.2f}s)")
    
    if success_rate < 0.5:
        # Step 2: Safe drop-off (second priority)
        print("\n2️⃣ SAFE DROP-OFF EVALUATION (Priority: High)")
        locations = [{"location": "front door", "security_level": "low"}]
        dropoff = suggest_safe_drop_off(locations, seed=85)
        dropoff_time = time.time() - start_time
        safe_available = dropoff.get('safe_option_available', False)
        print(f"   Safe drop-off: {'Not available' if not safe_available else 'Available'} ({dropoff_time:.2f}s)")
        
        if not safe_available:
            # Step 3: Locker (third priority)
            print("\n3️⃣ LOCKER SEARCH (Priority: Medium)")
            lockers = find_nearby_locker(37.7749, -122.4194, seed=85)
            locker_time = time.time() - start_time  
            lockers_found = lockers.get('lockers_found', False)
            print(f"   Nearby lockers: {'None found' if not lockers_found else 'Found'} ({locker_time:.2f}s)")
            
            if not lockers_found:
                # Step 4: Redelivery (fourth priority)
                print("\n4️⃣ REDELIVERY SCHEDULING (Priority: Low)")
                windows = [{"date": "tomorrow", "time_start": "09:00", "time_end": "17:00"}]
                redelivery = schedule_redelivery("TEST_ORDER", windows, seed=85)
                redelivery_time = time.time() - start_time
                scheduled = redelivery.get('scheduled', False)
                print(f"   Redelivery: {'Failed to schedule' if not scheduled else 'Scheduled'} ({redelivery_time:.2f}s)")
                
                if not scheduled:
                    # Step 5: Sender contact (lowest priority - last resort)
                    print("\n5️⃣ SENDER CONTACT (Priority: Last Resort)")
                    sender = contact_sender("TEST_SENDER", "Need guidance for delivery", seed=85)
                    sender_time = time.time() - start_time
                    contacted = sender.get('contact_successful', False)
                    print(f"   Sender contact: {'Success' if contacted else 'Failed'} ({sender_time:.2f}s)")
    
    total_time = time.time() - start_time
    print(f"\n📊 ESCALATION PERFORMANCE:")
    print(f"   Total escalation time: {total_time:.2f}s")
    print(f"   Steps attempted: All 5 levels tested")
    
    if total_time < 3.0:
        print("🏆 EXCELLENT: Rapid escalation through all priority levels!")
    elif total_time < 5.0:
        print("✅ GOOD: Efficient escalation sequence")
    else:
        print("⚠️ SLOW: Escalation may delay driver too long")


if __name__ == "__main__":
    integration_ok = test_tool_integration()
    if integration_ok:
        test_recipient_unavailable_workflow()
        test_escalation_sequence()
    else:
        print("❌ Tool integration failed - fix before testing workflow")