"""
Synapse Logistics Tools - Comprehensive Simulated External API Layer

This module provides a complete ecosystem of 18+ specialized tools for last-mile logistics
coordination. Each tool simulates realistic interactions with external systems that would
exist in a production logistics platform, including traffic APIs, merchant systems,
customer communication channels, and payment processors.

Architecture Philosophy:
    The tools are designed as realistic simulators rather than simple mocks, providing:
    - Consistent, believable data that reflects real-world logistics scenarios
    - Appropriate failure modes and edge cases for robust agent training
    - Comprehensive coverage of logistics operations across all stakeholders
    - Rich, structured responses that enable sophisticated agent reasoning

Tool Categories:

🚗 Traffic & Routing Tools:
    - check_traffic: Real-time traffic condition analysis
    - re_route_driver: Dynamic route optimization and driver coordination

🏪 Merchant Operations Tools:
    - get_merchant_status: Restaurant/store operational status and capacity
    - contact_merchant: Direct communication channel with merchants
    - get_nearby_merchants: Alternative merchant discovery for substitutions
    - log_merchant_packaging_feedback: Quality feedback and improvement tracking

📱 Customer Communication Tools:
    - notify_customer: Multi-channel customer notification system
    - contact_recipient_via_chat: Direct recipient communication with fallback options

🚚 Driver Management Tools:
    - get_driver_status: Real-time driver location, status, and availability
    - exonerate_driver: Clearing drivers from false accusations with evidence

🕵️ Evidence & Dispute Resolution Tools:
    - collect_evidence: Comprehensive evidence gathering for dispute resolution
    - analyze_evidence: AI-powered fault analysis and confidence scoring

📦 Delivery Management Tools:
    - suggest_safe_drop_off: Secure package placement options
    - find_nearby_locker: Alternative secure storage location discovery
    - schedule_redelivery: Flexible redelivery scheduling and coordination
    - contact_sender: Sender communication for complex resolution scenarios

💰 Refund Processing Tools:
    - issue_instant_refund: Immediate customer compensation processing
    - issue_partial_refund: Nuanced refund handling for partial fault scenarios
    - propose_substitute: Alternative item recommendation and substitution

Design Principles:
    1. **Realistic Simulation**: Each tool behaves like a real external API with
       appropriate latency, failure modes, and data structures.
    
    2. **Rich Context**: Tools provide enough detail for sophisticated agent reasoning
       while maintaining clean, focused interfaces.
    
    3. **Failure Realism**: Tools include realistic failure modes that mirror
       real-world API limitations and external system constraints.
    
    4. **Extensibility**: New tools can be easily added following established patterns
       for parameter handling, response structure, and error modes.
    
    5. **Testing Support**: All tools provide deterministic modes for reliable testing
       while supporting randomization for realistic simulation.

Integration Notes:
    - All tools return structured dictionaries with consistent status indicators
    - Error conditions are handled gracefully with informative error messages  
    - Tools are designed to be easily replaced with real API integrations
    - Function signatures are stable to support seamless production transitions
    - Comprehensive logging supports debugging and performance analysis

Usage Example:
    # Traffic analysis
    traffic_result = check_traffic(route_id="I-280_SF_to_SJ") 
    
    # Customer communication  
    notify_result = notify_customer(
        customer_id="cust_123",
        message="Your delivery is running 15 minutes late due to traffic"
    )
    
    # Evidence collection for disputes
    evidence = collect_evidence(
        order_id="order_456", 
        requester="customer_service",
        ask_photos=True
    )

Authors: Project Synapse Team
License: MIT
Version: 1.0.0
"""
from __future__ import annotations 

import random
import time
from typing import Literal, Optional
from typing import Optional, Dict, Any, List
import random, datetime, uuid, json, os

# Import authorization system for approval-requiring actions
try:
    from synapse.core.authorization import auth_manager, APPROVAL_REQUIRED_ACTIONS
except ImportError:
    # Fallback for standalone testing
    auth_manager = None
    APPROVAL_REQUIRED_ACTIONS = {}

def _now_iso() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def _gen_id(prefix: str="id") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

# -----------------------------
# TOOL METADATA (for validation)
# -----------------------------
TOOL_METADATA = {
    "get_merchant_status": {"verticals":["GrabFood","GrabMart"], "params":["merchant_id"], "cost":"low"},
    "get_nearby_merchants": {"verticals":["GrabFood","GrabMart"], "params":["lat","lng"], "cost":"low"},
    "notify_customer": {"verticals":["All"], "params":["customer_id","message"], "cost":"low"},
    "issue_voucher": {"verticals":["GrabFood","GrabMart"], "params":["customer_id","amount"], "cost":"low", "approval_threshold":50.0},
    "collect_evidence": {"verticals":["GrabFood","GrabMart"], "params":["order_id"], "cost":"low"},
    "analyze_evidence": {"verticals":["GrabFood","GrabMart"], "params":["evidence_id"], "cost":"medium"},
    "issue_instant_refund": {"verticals":["GrabFood","GrabMart"], "params":["order_id","amount"], "cost":"medium", "approval_threshold":50.0},
    "exonerate_driver": {"verticals":["All"], "params":["driver_id"], "cost":"low"},
    "log_merchant_packaging_feedback": {"verticals":["GrabFood","GrabMart"], "params":["merchant_id","feedback"], "cost":"low"},
    "contact_merchant": {"verticals":["GrabFood","GrabMart"], "params":["merchant_id","message"], "cost":"low"},
    "propose_substitute": {"verticals":["GrabFood","GrabMart"], "params":["order_id","substitute_items"], "cost":"low"},
    "contact_recipient_via_chat": {"verticals":["GrabExpress"], "params":["recipient_id","message"], "cost":"low"},
    "suggest_safe_drop_off": {"verticals":["GrabExpress"], "params":["options"], "cost":"low"},
    "find_nearby_locker": {"verticals":["GrabExpress"], "params":["lat","lng"], "cost":"low"},
    "schedule_redelivery": {"verticals":["GrabExpress"], "params":["order_id","windows"], "cost":"low"},
    "verify_address_with_customer": {"verticals":["GrabExpress"], "params":["customer_id","provided_address"], "cost":"low"},
    "contact_sender": {"verticals":["GrabExpress"], "params":["sender_id","message"], "cost":"low"},
    "check_traffic": {"verticals":["GrabCar"], "params":["route_id"], "cost":"low"},
    "calculate_alternative_route": {"verticals":["GrabCar"], "params":["route_id"], "cost":"low"},
    "notify_passenger_and_driver": {"verticals":["GrabCar"], "params":["trip_id","message"], "cost":"low"},
    "check_flight_status": {"verticals":["GrabCar"], "params":["flight_number"], "cost":"low"},
    "reroute_driver_to_safe_location": {"verticals":["GrabCar"], "params":["driver_id","location"], "cost":"low"},
    "contact_support_live": {"verticals":["All"], "params":["issue","priority"], "cost":"high"},
    "locate_trip_path": {"verticals":["All"], "params":["trip_id"], "cost":"low"},
    "initiate_lost_and_found_flow": {"verticals":["All"], "params":["trip_id"], "cost":"low"},
    "get_driver_status": {"verticals":["All"], "params":["driver_id"], "cost":"low"},
    "hold_order_with_merchant": {"verticals":["GrabFood","GrabMart"], "params":["order_id","merchant_id"], "cost":"low"},
    "issue_partial_refund": {"verticals":["GrabFood","GrabMart"], "params":["order_id","amount"], "cost":"low"},
    "re_route_driver": {"verticals":["All"], "params":["driver_id","new_route"], "cost":"low"},
    "cancel_booking": {"verticals":["All"], "params":["booking_id","reason"], "cost":"low"},
    "find_replacement_driver": {"verticals":["All"], "params":["booking_id","location"], "cost":"medium"},
}

# -----------------------------
# Helper: error response builder
# -----------------------------
def _error(tool_name: str, code: str, message: str, details: Optional[Dict[str,Any]]=None) -> Dict[str,Any]:
    return {
        "tool_name": tool_name,
        "status": "error",
        "error_code": code,
        "message": message,
        "details": details or {},
        "timestamp": _now_iso()
    }



__all__ = [
    "get_merchant_status",
    "get_nearby_merchants",
    "notify_customer",
    "issue_voucher",
    "collect_evidence",
    "analyze_evidence",
    "issue_instant_refund",
    "exonerate_driver",
    "log_merchant_packaging_feedback",
    "contact_merchant",
    "propose_substitute",
    "contact_recipient_via_chat",
    "suggest_safe_drop_off",
    "find_nearby_locker",
    "schedule_redelivery",
    "verify_address_with_customer",
    "contact_sender",
    "check_traffic",
    "calculate_alternative_route",
    "notify_passenger_and_driver",
    "check_flight_status",
    "reroute_driver_to_safe_location",
    "contact_support_live",
    "locate_trip_path",
    "initiate_lost_and_found_flow",
    "get_driver_status",
    "hold_order_with_merchant",
    "issue_partial_refund",
    "re_route_driver",
    "cancel_booking",
    "find_replacement_driver",
    "TOOL_METADATA",
    "ScenarioRunner"
]



 #grab mart/grabfood tools 
def get_merchant_status(merchant_id: str, seed: Optional[int]=None) -> Dict[str,Any]:
    tool = "get_merchant_status"
    if not merchant_id:
        return _error(tool, "INVALID_PARAM", "merchant_id required")
    if seed is not None:
        random.seed(seed)
    prep_time = random.choice([15,20,25,30,40])
    stock = {"pizza": random.random() > 0.1, "burger": random.random() > 0.3, "soda": True}
    return {
        "tool_name": tool,
        "status": "ok",
        "merchant_id": merchant_id,
        "prep_time_mins": prep_time,
        "open": prep_time < 35,
        "estimated_ready_at": _now_iso(),
        "stock": stock,
        "timestamp": _now_iso()
    }

def get_nearby_merchants(lat: float, lng: float, radius_m: int=1000, cuisine: Optional[str]=None, seed: Optional[int]=None) -> Dict[str,Any]:
    tool = "get_nearby_merchants"
    try:
        lat_f = float(lat); lng_f = float(lng)
    except Exception as e:
        return _error(tool, "INVALID_PARAM", "lat and lng required and must be numeric", {"exception": str(e)})
    if seed is not None:
        random.seed(seed)
    sample = []
    base_names = ["Pizza Palace","Burger Bros","Noodle House","Coffee Corner","Sushi Spot"]
    for i in range(3):
        name = random.choice(base_names)
        sample.append({
            "id": _gen_id("M"),
            "name": name,
            "prep_time_mins": random.choice([10,15,20,25]),
            "rating": round(3.5 + random.random()*1.5,2),
            "distance_m": random.randint(50, radius_m)
        })
    return {
        "tool_name": tool,
        "status": "ok",
        "merchants": sample,
        "query": {"lat": lat_f, "lng": lng_f, "radius_m": radius_m, "cuisine": cuisine},
        "timestamp": _now_iso()
    }

def notify_customer(customer_id: str, message: str, channel: str="app", seed: Optional[int]=None) -> Dict[str,Any]:
    tool = "notify_customer"
    if not customer_id or not message:
        return _error(tool, "INVALID_PARAM", "customer_id and message required")
    
    # Simulate notification delivery time (0.1-0.3 seconds)
    import time
    time.sleep(random.uniform(0.1, 0.3))
    
    if seed is not None:
        random.seed(seed)
    delivered = random.random() > 0.05
    message_id = _gen_id("msg")
    return {
        "tool_name": tool,
        "status": "ok" if delivered else "error",
        "customer_id": customer_id,
        "channel": channel,
        "delivered": delivered,
        "message_id": message_id,
        "message": message,
        "timestamp": _now_iso()
    }

def issue_voucher(customer_id: str, amount: float, currency: str="USD", reason: Optional[str]=None, require_approval: bool=False, seed: Optional[int]=None) -> Dict[str,Any]:
    tool = "issue_voucher"
    if not customer_id or amount is None:
        return _error(tool, "INVALID_PARAM", "customer_id and amount required")
    if seed is not None:
        random.seed(seed)
    threshold = TOOL_METADATA.get(tool, {}).get("approval_threshold", 50.0)
    if require_approval or amount > threshold:
        return _error(tool, "APPROVAL_REQUIRED", f"Voucher amount {amount} exceeds threshold {threshold}")
    voucher_id = _gen_id("v")
    return {
        "tool_name": tool,
        "status": "ok",
        "voucher_id": voucher_id,
        "customer_id": customer_id,
        "amount": amount,
        "currency": currency,
        "issued": True,
        "reason": reason,
        "timestamp": _now_iso()
    }

def collect_evidence(order_id: str, requester: str="agent", ask_photos: bool=True, seed: Optional[int]=None) -> Dict[str,Any]:
    tool = "collect_evidence"
    if not order_id:
        return _error(tool, "INVALID_PARAM", "order_id required")
    evidence_id = _gen_id("e")
    return {
        "tool_name": tool,
        "status": "ok",
        "order_id": order_id,
        "requests_sent": {"customer": True, "driver": True} if ask_photos else {"customer": False, "driver": False},
        "evidence_id": evidence_id,
        "timestamp": _now_iso()
    }

def analyze_evidence(evidence_id: str, seed: Optional[int]=None) -> Dict[str,Any]:
    tool = "analyze_evidence"
    if not evidence_id:
        return _error(tool, "INVALID_PARAM", "evidence_id required")
    if seed is not None:
        random.seed(seed)
    r = random.random()
    if r < 0.60:
        fault = "merchant"; confidence = round(0.6 + random.random()*0.35, 2)
    elif r < 0.85:
        fault = "driver"; confidence = round(0.5 + random.random()*0.45, 2)
    else:
        fault = "unknown"; confidence = round(0.3 + random.random()*0.3, 2)
    explanation = "Simulated evidence analysis result based on image metadata and questionnaire."
    return {
        "tool_name": tool,
        "status": "ok",
        "evidence_id": evidence_id,
        "result": {"fault": fault, "confidence": confidence},
        "explanation": explanation,
        "timestamp": _now_iso()
    }

def issue_instant_refund(order_id: str, amount: float, currency: str="USD", reason: Optional[str]=None, require_approval: bool=False, seed: Optional[int]=None) -> Dict[str,Any]:
    tool = "issue_instant_refund"
    if not order_id or amount is None:
        return _error(tool, "INVALID_PARAM", "order_id and amount required")
    threshold = TOOL_METADATA.get(tool, {}).get("approval_threshold", 50.0)
    if require_approval or amount > threshold:
        return _error(tool, "APPROVAL_REQUIRED", f"Refund amount {amount} exceeds threshold {threshold}")
    refund_id = _gen_id("r")
    return {
        "tool_name": tool,
        "status": "ok",
        "order_id": order_id,
        "amount": amount,
        "currency": currency,
        "refund_id": refund_id,
        "issued": True,
        "reason": reason,
        "timestamp": _now_iso()
    }

def exonerate_driver(driver_id: str, order_id: Optional[str]=None, reason: Optional[str]=None, seed: Optional[int]=None) -> Dict[str,Any]:
    tool = "exonerate_driver"
    if not driver_id:
        return _error(tool, "INVALID_PARAM", "driver_id required")
    return {
        "tool_name": tool,
        "status": "ok",
        "driver_id": driver_id,
        "order_id": order_id,
        "exonerated": True,
        "note": reason or "Exonerated by agent decision",
        "timestamp": _now_iso()
    }

def log_merchant_packaging_feedback(merchant_id: str, feedback: Dict[str,Any], seed: Optional[int]=None) -> Dict[str,Any]:
    tool = "log_merchant_packaging_feedback"
    if not merchant_id or feedback is None:
        return _error(tool, "INVALID_PARAM", "merchant_id and feedback required")
    fb_ref = _gen_id("fb")
    return {
        "tool_name": tool,
        "status": "ok",
        "merchant_id": merchant_id,
        "logged": True,
        "feedback_ref": fb_ref,
        "timestamp": _now_iso()
    }

def contact_merchant(merchant_id: str, message: str, seed: Optional[int]=None) -> Dict[str,Any]:
    tool = "contact_merchant"
    if not merchant_id or not message:
        return _error(tool, "INVALID_PARAM", "merchant_id and message required")
    if seed is not None:
        random.seed(seed)
    acknowledged = random.random() > 0.1
    response = "Acknowledged" if acknowledged else "No response"
    status = "ok" if acknowledged else "error"
    return {
        "tool_name": tool,
        "status": status,
        "merchant_id": merchant_id,
        "acknowledged": acknowledged,
        "response": response,
        "timestamp": _now_iso()
    }

def propose_substitute(order_id: str, substitute_items: List[Dict[str,Any]], seed: Optional[int]=None) -> Dict[str,Any]:
    tool = "propose_substitute"
    if not order_id or substitute_items is None:
        return _error(tool, "INVALID_PARAM", "order_id and substitute_items required")
    return {
        "tool_name": tool,
        "status": "ok",
        "order_id": order_id,
        "substitutes": substitute_items,
        "requested_confirmation": True,
        "timestamp": _now_iso()
    }
#grabexpress tools
def contact_recipient_via_chat(recipient_id: str, message: str, channel: str="app", seed: Optional[int]=None) -> Dict[str,Any]:
    tool = "contact_recipient_via_chat"
    if not recipient_id or not message:
        return _error(tool, "INVALID_PARAM", "recipient_id and message required")
    if seed is not None:
        random.seed(seed)
    responded = random.random() > 0.25
    response = {"text": "Please leave at guard", "responded": True} if responded else {"text": None, "responded": False}
    status = "ok" if responded else "error"
    return {
        "tool_name": tool,
        "status": status,
        "recipient_id": recipient_id,
        "delivered": True,
        "response": response,
        "timestamp": _now_iso()
    }

def suggest_safe_drop_off(options: List[Dict[str,Any]], seed: Optional[int]=None) -> Dict[str,Any]:
    tool = "suggest_safe_drop_off"
    if options is None or len(options) == 0:
        return _error(tool, "INVALID_PARAM", "options list required")
    if seed is not None:
        random.seed(seed)
    selected = random.choice(options)
    return {
        "tool_name": tool,
        "status": "ok",
        "selected_option": selected,
        "all_options": options,
        "timestamp": _now_iso()
    }

def find_nearby_locker(lat: float, lng: float, radius_m: int=2000, seed: Optional[int]=None) -> Dict[str,Any]:
    tool = "find_nearby_locker"
    try:
        lat_f = float(lat); lng_f = float(lng)
    except Exception as e:
        return _error(tool, "INVALID_PARAM", "lat and lng required and numeric", {"exception": str(e)})
    if seed is not None:
        random.seed(seed)
    lockers = [
        {"id": _gen_id("L"), "location": "Mall Entrance", "available": random.random() > 0.2, "distance_m": random.randint(100, radius_m)},
        {"id": _gen_id("L"), "location": "Gas Station", "available": random.random() > 0.5, "distance_m": random.randint(100, radius_m)}
    ]
    return {
        "tool_name": tool,
        "status": "ok",
        "lockers": lockers,
        "selected": lockers[0] if lockers else None,
        "timestamp": _now_iso()
    }

def schedule_redelivery(order_id: str, windows: List[Dict[str,Any]], seed: Optional[int]=None) -> Dict[str,Any]:
    tool = "schedule_redelivery"
    if not order_id or not windows:
        return _error(tool, "INVALID_PARAM", "order_id and windows required")
    if seed is not None:
        random.seed(seed)
    chosen = random.choice(windows)
    return {
        "tool_name": tool,
        "status": "ok",
        "order_id": order_id,
        "scheduled": chosen,
        "timestamp": _now_iso()
    }

def verify_address_with_customer(customer_id: str, provided_address: Dict[str,Any], seed: Optional[int]=None) -> Dict[str,Any]:
    tool = "verify_address_with_customer"
    if not customer_id or provided_address is None:
        return _error(tool, "INVALID_PARAM", "customer_id and provided_address required")
    if seed is not None:
        random.seed(seed)
    verified = random.random() > 0.2
    corrected = None if verified else {**provided_address, "line1": provided_address.get("line1","")+" Apt 2"}
    return {
        "tool_name": tool,
        "status": "ok",
        "customer_id": customer_id,
        "provided_address": provided_address,
        "verified": verified,
        "corrected_address": corrected,
        "timestamp": _now_iso()
    }

def contact_sender(sender_id: str, message: str, seed: Optional[int]=None) -> Dict[str,Any]:
    tool = "contact_sender"
    if not sender_id or not message:
        return _error(tool, "INVALID_PARAM", "sender_id and message required")
    if seed is not None:
        random.seed(seed)
    ack = random.random() > 0.1
    return {
        "tool_name": tool,
        "status": "ok" if ack else "error",
        "sender_id": sender_id,
        "acknowledged": ack,
        "timestamp": _now_iso()
    }
#grabcar tools
def check_traffic(route_id: str, seed: Optional[int]=None) -> Dict[str,Any]:
    tool = "check_traffic"
    if not route_id:
        return _error(tool, "INVALID_PARAM", "route_id required")
    
    # Simulate realistic API response time (0.1-0.5 seconds)
    import time
    time.sleep(random.uniform(0.1, 0.5))
    
    if seed is not None:
        random.seed(seed)
    incident_level = random.choice(["minor","major","none"])
    blocked = incident_level == "major"
    delay_mins = 0 if incident_level == "none" else random.randint(5,45)
    details = {"location":"Junction X", "incident_type": "accident"} if blocked else {}
    return {
        "tool_name": tool,
        "status": "ok",
        "route_id": route_id,
        "incident_level": incident_level,
        "blocked": blocked,
        "delay_mins": delay_mins,
        "details": details,
        "timestamp": _now_iso()
    }

def calculate_alternative_route(route_id: str, constraints: Optional[Dict[str,Any]]=None, seed: Optional[int]=None) -> Dict[str,Any]:
    tool = "calculate_alternative_route"
    if not route_id:
        return _error(tool, "INVALID_PARAM", "route_id required")
    
    # Simulate route calculation time (0.2-0.8 seconds)
    import time
    time.sleep(random.uniform(0.2, 0.8))
    if seed is not None:
        random.seed(seed)
    alternatives = []
    for i in range(2):
        alternatives.append({
            "route_id": _gen_id("R"),
            "eta_delta_mins": random.choice([5,10,20]),
            "distance_m": random.choice([2000,5000,12000])
        })
    return {
        "tool_name": tool,
        "status": "ok",
        "alternatives": alternatives,
        "timestamp": _now_iso()
    }

def notify_passenger_and_driver(trip_id: str, message: str, seed: Optional[int]=None) -> Dict[str,Any]:
    tool = "notify_passenger_and_driver"
    if not trip_id or not message:
        return _error(tool, "INVALID_PARAM", "trip_id and message required")
    if seed is not None:
        random.seed(seed)
    pass_ack = random.random() > 0.1
    driver_ack = random.random() > 0.05
    status = "ok" if pass_ack and driver_ack else "error"
    return {
        "tool_name": tool,
        "status": status,
        "trip_id": trip_id,
        "passenger_ack": pass_ack,
        "driver_ack": driver_ack,
        "timestamp": _now_iso()
    }

def check_flight_status(flight_number: str, seed: Optional[int]=None) -> Dict[str,Any]:
    tool = "check_flight_status"
    if not flight_number:
        return _error(tool, "INVALID_PARAM", "flight_number required")
    if seed is not None:
        random.seed(seed)
    status = random.choice(["on-time","delayed","cancelled"])
    scheduled = _now_iso()
    return {
        "tool_name": tool,
        "status": "ok",
        "flight_number": flight_number,
        "scheduled_departure": scheduled,
        "status_text": status,
        "remarks": "",
        "timestamp": _now_iso()
    }

def reroute_driver_to_safe_location(driver_id: str, location: Dict[str,Any], seed: Optional[int]=None) -> Dict[str,Any]:
    tool = "reroute_driver_to_safe_location"
    if not driver_id or location is None:
        return _error(tool, "INVALID_PARAM", "driver_id and location required")
    return {
        "tool_name": tool,
        "status": "ok",
        "driver_id": driver_id,
        "new_location": location,
        "confirmed": True,
        "timestamp": _now_iso()
    }

def contact_support_live(issue: Dict[str,Any], priority: str="high", seed: Optional[int]=None) -> Dict[str,Any]:
    tool = "contact_support_live"
    if issue is None:
        return _error(tool, "INVALID_PARAM", "issue required")
    ticket = _gen_id("TKT")
    return {
        "tool_name": tool,
        "status": "ok",
        "ticket_id": ticket,
        "assigned_to": "support_agent_1",
        "escalated": True,
        "priority": priority,
        "timestamp": _now_iso()
    }

def locate_trip_path(trip_id: str, seed: Optional[int]=None) -> Dict[str,Any]:
    tool = "locate_trip_path"
    if not trip_id:
        return _error(tool, "INVALID_PARAM", "trip_id required")
    path = [{"lat": 1.23 + i*0.001, "lng": 103.8 + i*0.001, "ts": _now_iso()} for i in range(3)]
    return {
        "tool_name": tool,
        "status": "ok",
        "trip_id": trip_id,
        "path": path,
        "last_known": path[-1],
        "timestamp": _now_iso()
    }

def initiate_lost_and_found_flow(trip_id: str, details: Dict[str,Any], seed: Optional[int]=None) -> Dict[str,Any]:
    tool = "initiate_lost_and_found_flow"
    if not trip_id or details is None:
        return _error(tool, "INVALID_PARAM", "trip_id and details required")
    case = _gen_id("LF")
    return {
        "tool_name": tool,
        "status": "ok",
        "trip_id": trip_id,
        "case_id": case,
        "next_steps": ["contact_driver","check_vehicle"],
        "timestamp": _now_iso()
    }
#common utility tools
def get_driver_status(driver_id: str, seed: Optional[int]=None) -> Dict[str,Any]:
    tool = "get_driver_status"
    if not driver_id:
        return _error(tool, "INVALID_PARAM", "driver_id required")
    if seed is not None:
        random.seed(seed)
    state = random.choice(["idle","on_trip","arrived"])
    location = {"lat": 1.35 + random.random()*0.01, "lng": 103.8 + random.random()*0.01}
    return {
        "tool_name": tool,
        "status": "ok",
        "driver_id": driver_id,
        "location": location,
        "state": state,
        "timestamp": _now_iso()
    }

def hold_order_with_merchant(order_id: str, merchant_id: str, hold_minutes: int=15, seed: Optional[int]=None) -> Dict[str,Any]:
    tool = "hold_order_with_merchant"
    if not order_id or not merchant_id:
        return _error(tool, "INVALID_PARAM", "order_id and merchant_id required")
    if seed is not None:
        random.seed(seed)
    accepted = random.random() > 0.1
    if not accepted:
        return _error(tool, "MERCHANT_REJECTED", "merchant refused to hold order")
    held_until = (datetime.datetime.utcnow() + datetime.timedelta(minutes=hold_minutes)).replace(microsecond=0).isoformat() + "Z"
    return {
        "tool_name": tool,
        "status": "ok",
        "order_id": order_id,
        "merchant_id": merchant_id,
        "held_until": held_until,
        "timestamp": _now_iso()
    }

def issue_partial_refund(order_id: str, amount: float, currency: str="USD", seed: Optional[int]=None) -> Dict[str,Any]:
    tool = "issue_partial_refund"
    if not order_id or amount is None:
        return _error(tool, "INVALID_PARAM", "order_id and amount required")
    refund_id = _gen_id("pr")
    return {
        "tool_name": tool,
        "status": "ok",
        "refund_id": refund_id,
        "order_id": order_id,
        "amount": amount,
        "currency": currency,
        "timestamp": _now_iso()
    }

def re_route_driver(driver_id: str, new_route: Dict[str,Any], seed: Optional[int]=None) -> Dict[str,Any]:
    tool = "re_route_driver"
    if not driver_id or new_route is None:
        return _error(tool, "INVALID_PARAM", "driver_id and new_route required")
    return {
        "tool_name": tool,
        "status": "ok",
        "driver_id": driver_id,
        "new_route": new_route,
        "status_text": "rerouted",
        "timestamp": _now_iso()
    }

def cancel_booking(booking_id: str, reason: str, seed: Optional[int]=None) -> Dict[str,Any]:
    tool = "cancel_booking"
    if not booking_id or not reason:
        return _error(tool, "INVALID_PARAM", "booking_id and reason required")
    if seed is not None:
        random.seed(seed)
    # Simulate potential cancellation issues
    cancellation_successful = random.random() > 0.05  # 95% success rate
    cancellation_id = _gen_id("cancel")
    return {
        "tool_name": tool,
        "status": "ok" if cancellation_successful else "error",
        "booking_id": booking_id,
        "cancellation_id": cancellation_id if cancellation_successful else None,
        "cancelled": cancellation_successful,
        "reason": reason,
        "refund_processed": cancellation_successful,
        "error_message": None if cancellation_successful else "Cancellation failed - booking may be too advanced",
        "timestamp": _now_iso()
    }

def find_replacement_driver(booking_id: str, location: Dict[str,Any], seed: Optional[int]=None) -> Dict[str,Any]:
    tool = "find_replacement_driver"
    if not booking_id or location is None:
        return _error(tool, "INVALID_PARAM", "booking_id and location required")
    if seed is not None:
        random.seed(seed)
    # Simulate driver availability
    drivers_available = random.random() > 0.3  # 70% chance of finding replacement
    if drivers_available:
        replacement_driver_id = _gen_id("driver")
        eta_mins = random.choice([5, 10, 15, 20])
        return {
            "tool_name": tool,
            "status": "ok",
            "booking_id": booking_id,
            "replacement_driver_id": replacement_driver_id,
            "driver_found": True,
            "eta_minutes": eta_mins,
            "driver_location": {"lat": location.get("lat", 1.35) + random.random()*0.01, 
                              "lng": location.get("lng", 103.8) + random.random()*0.01},
            "timestamp": _now_iso()
        }
    else:
        return {
            "tool_name": tool,
            "status": "error",
            "booking_id": booking_id,
            "driver_found": False,
            "error_message": "No available drivers in the area",
            "suggested_wait_time": random.choice([15, 20, 30]),
            "timestamp": _now_iso()
        }

# -----------------------------
# ScenarioRunner (lightweight)
# -----------------------------
import csv, os, typing
class ScenarioRunner:
    """
    Lightweight runner that loads scenario CSV and validates tool calls against allowed_tools.
    The CSV is expected to have columns: id,vertical,title,description,initial_state,allowed_tools,success_criteria,escalation_threshold,seed
    """
    def __init__(self, scenario_csv: str):
        if not os.path.exists(scenario_csv):
            raise FileNotFoundError(scenario_csv)
        self.scenarios = {}
        with open(scenario_csv, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                row['allowed_tools'] = [t.strip() for t in row.get('allowed_tools','').split(',') if t.strip()]
                self.scenarios[row['id']] = row

    def get_scenario(self, scenario_id: str) -> Dict[str,Any]:
        return self.scenarios.get(scenario_id)

    def validate_tool(self, scenario_id: str, tool_name: str) -> bool:
        sc = self.get_scenario(scenario_id)
        if not sc: return False
        return tool_name in sc.get('allowed_tools', [])

    def run_tool(self, scenario_id: str, tool_func, params: Dict[str,Any]) -> Dict[str,Any]:
        tool_name = getattr(tool_func, "__name__", "unknown_tool")
        if not self.validate_tool(scenario_id, tool_name):
            return _error(tool_name, "TOOL_NOT_ALLOWED", f"Tool {tool_name} not allowed for scenario {scenario_id}")
        seed = None
        try:
            seed = int(self.scenarios[scenario_id].get('seed')) if self.scenarios[scenario_id].get('seed') else None
        except Exception:
            seed = None
        try:
            params_with_seed = {**params, "seed": seed}
            return tool_func(**params_with_seed)
        except TypeError:
            return tool_func(**params)



def _demo():
    import pprint
    pp = pprint.PrettyPrinter(indent=2)
    print("Running demo calls for simulated tools (seed=42)\n")
    seed = 42

    res = get_merchant_status("M42", seed=seed)
    print("get_merchant_status example:"); pp.pprint(res); print()

    res = get_nearby_merchants(1.3521, 103.8198, seed=seed)
    print("get_nearby_merchants example:"); pp.pprint(res); print()

    res = notify_customer("C123", "Your order is delayed 15 minutes.", seed=seed)
    print("notify_customer example:"); pp.pprint(res); print()

    res = collect_evidence("O123", seed=seed)
    print("collect_evidence example:"); pp.pprint(res); print()

    evidence_id = res.get("evidence_id")
    res = analyze_evidence(evidence_id, seed=seed)
    print("analyze_evidence example:"); pp.pprint(res); print()

    res = issue_instant_refund("O123", 8.5, seed=seed)
    print("issue_instant_refund example:"); pp.pprint(res); print()

    res = check_traffic("R1", seed=seed)
    print("check_traffic example:"); pp.pprint(res); print()

    res = calculate_alternative_route("R1", seed=seed)
    print("calculate_alternative_route example:"); pp.pprint(res); print()

    res = find_nearby_locker(1.3521, 103.8198, seed=seed)
    print("find_nearby_locker example:"); pp.pprint(res); print()

    print("Demo complete.")


def debug_tools(verbose: bool = False) -> bool:
    """Debug tools module functionality. Returns True if all tests pass."""
    print("=== Tools Module Debug ===")
    
    try:
        # Test core tools with deterministic seed
        seed = 42
        tests_passed = 0
        total_tests = 0
        
        # Test check_traffic
        total_tests += 1
        result = check_traffic("debug_route", seed=seed)
        if result.get('status') == 'ok' and result.get('tool_name') == 'check_traffic':
            print("✓ check_traffic working")
            tests_passed += 1
            if verbose:
                print(f"  Result: {result}")
        else:
            print(f"✗ check_traffic failed: {result}")
        
        # Test get_merchant_status
        total_tests += 1
        result = get_merchant_status("debug_merchant", seed=seed)
        if result.get('status') == 'ok' and result.get('tool_name') == 'get_merchant_status':
            print("✓ get_merchant_status working")
            tests_passed += 1
            if verbose:
                print(f"  Result: prep_time={result.get('prep_time_mins')}min")
        else:
            print(f"✗ get_merchant_status failed: {result}")
        
        # Test notify_customer
        total_tests += 1
        result = notify_customer("debug_customer", "Test message", seed=seed)
        if result.get('status') == 'ok' and result.get('tool_name') == 'notify_customer':
            print("✓ notify_customer working")
            tests_passed += 1
            if verbose:
                print(f"  Delivered: {result.get('delivered')}")
        else:
            print(f"✗ notify_customer failed: {result}")
        
        # Test get_nearby_merchants
        total_tests += 1
        result = get_nearby_merchants(1.3521, 103.8198, seed=seed)
        if result.get('status') == 'ok' and result.get('tool_name') == 'get_nearby_merchants':
            print("✓ get_nearby_merchants working")
            tests_passed += 1
            if verbose:
                merchants = result.get('merchants', [])
                print(f"  Found {len(merchants)} merchants")
        else:
            print(f"✗ get_nearby_merchants failed: {result}")
        
        # Test re_route_driver
        total_tests += 1
        result = re_route_driver("debug_driver", {"description": "test route"}, seed=seed)
        if result.get('status') == 'ok' and result.get('tool_name') == 're_route_driver':
            print("✓ re_route_driver working")
            tests_passed += 1
            if verbose:
                print(f"  Status: {result.get('status_text')}")
        else:
            print(f"✗ re_route_driver failed: {result}")
        
        # Test error handling
        total_tests += 1
        result = check_traffic("", seed=seed)  # Empty route should cause error
        if result.get('status') == 'error':
            print("✓ Error handling working")
            tests_passed += 1
            if verbose:
                print(f"  Error: {result.get('error_message')}")
        else:
            print(f"✗ Error handling failed: {result}")
        
        print(f"Tools module: {tests_passed}/{total_tests} tests passed")
        return tests_passed == total_tests
        
    except Exception as e:
        print(f"✗ Tools debug failed: {e}")
        return False


def debug_tool_metadata() -> bool:
    """Debug tool metadata structure."""
    print("=== Tool Metadata Debug ===")
    
    try:
        print(f"✓ TOOL_METADATA loaded with {len(TOOL_METADATA)} tools")
        
        # Check some key tools exist
        required_tools = ['check_traffic', 'get_merchant_status', 'notify_customer']
        missing = [tool for tool in required_tools if tool not in TOOL_METADATA]
        
        if missing:
            print(f"✗ Missing metadata for tools: {missing}")
            return False
        else:
            print("✓ Core tool metadata present")
            return True
            
    except Exception as e:
        print(f"✗ Metadata debug failed: {e}")
        return False


# =============================================================================
# APPROVAL-REQUIRING TOOLS - Financial and High-Impact Actions
# =============================================================================

def _request_approval(action_type: str, amount: float, description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Helper function to request approval for monetary/high-impact actions."""
    if not auth_manager:
        # Fallback when authorization system not available
        return {
            "approval_required": True,
            "approval_status": "simulated_approved",
            "approved_amount": amount,
            "conditions": ["Approval system not available - action simulated"],
            "approval_id": f"SIM_{int(time.time())}"
        }
    
    # Request approval through authorization system
    request = auth_manager.request_approval(
        action=action_type,
        description=description,
        monetary_value=amount,
        context=context or {},
        urgency="medium"
    )
    
    # Simulate approval decision for demo purposes
    if request.status.value == "pending":
        request = auth_manager.simulate_approval_decision(request)
    
    return {
        "approval_required": True,
        "approval_status": request.status.value,
        "approved_amount": amount if request.status.value in ["approved", "emergency_override"] else 0.0,
        "rejection_reason": request.rejection_reason,
        "conditions": request.conditions,
        "approval_id": request.request_id,
        "approver": request.approver,
        "authorization_level": request.authorization_level.value
    }


def issue_monetary_voucher(customer_id: str, amount: float, reason: str, seed: Optional[int] = None) -> Dict[str, Any]:
    """
    Issue a monetary voucher to customer - requires approval for amounts > $10.
    """
    tool = "issue_monetary_voucher"
    if not customer_id or not reason:
        return _error(tool, "INVALID_PARAM", "customer_id and reason required")
    
    if amount <= 0:
        return _error(tool, "INVALID_AMOUNT", "Amount must be positive")
    
    if amount > 1000:
        return _error(tool, "AMOUNT_TOO_HIGH", "Maximum voucher amount is $1000")
    
    # Request approval for monetary voucher
    approval_result = _request_approval(
        action_type="issue_monetary_voucher",
        amount=amount,
        description=f"Issue ${amount:.2f} voucher to customer {customer_id} - {reason}",
        context={
            "customer_id": customer_id,
            "reason": reason,
            "voucher_type": "monetary"
        }
    )
    
    voucher_id = _gen_id("voucher")
    
    if approval_result["approval_status"] in ["approved", "emergency_override"]:
        return {
            "tool_name": tool,
            "status": "ok",
            "customer_id": customer_id,
            "voucher_id": voucher_id,
            "amount": approval_result["approved_amount"],
            "reason": reason,
            "voucher_issued": True,
            "expiry_date": (datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%Y-%m-%d"),
            **approval_result,
            "timestamp": _now_iso()
        }
    else:
        return {
            "tool_name": tool,
            "status": "approval_denied",
            "customer_id": customer_id,
            "voucher_issued": False,
            "requested_amount": amount,
            **approval_result,
            "timestamp": _now_iso()
        }


def escalate_to_management(issue_type: str, description: str, urgency: str = "medium", 
                          estimated_cost: float = 0.0, seed: Optional[int] = None) -> Dict[str, Any]:
    """
    Escalate complex issues to management - requires approval based on estimated cost and urgency.
    """
    tool = "escalate_to_management"
    if not issue_type or not description:
        return _error(tool, "INVALID_PARAM", "issue_type and description required")
    
    valid_urgency = ["low", "medium", "high", "critical"]
    if urgency not in valid_urgency:
        urgency = "medium"
    
    approval_result = _request_approval(
        action_type="escalate_to_management",
        amount=estimated_cost,
        description=f"Management escalation: {issue_type} - {description}",
        context={
            "issue_type": issue_type,
            "description": description,
            "urgency": urgency,
            "estimated_cost": estimated_cost
        }
    )
    
    escalation_id = _gen_id("escalation")
    
    if approval_result["approval_status"] in ["approved", "emergency_override"]:
        assigned_manager = f"manager_{random.choice(['ops', 'customer', 'logistics'])}"
        return {
            "tool_name": tool,
            "status": "ok",
            "escalation_id": escalation_id,
            "issue_type": issue_type,
            "description": description,
            "urgency": urgency,
            "escalated": True,
            "assigned_to": assigned_manager,
            "estimated_resolution_time": f"{random.choice([2, 4, 8, 24])} hours",
            **approval_result,
            "timestamp": _now_iso()
        }
    else:
        return {
            "tool_name": tool,
            "status": "approval_denied",
            "escalated": False,
            "issue_type": issue_type,
            **approval_result,
            "timestamp": _now_iso()
        }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--debug":
            verbose = "--verbose" in sys.argv or "-v" in sys.argv
            print("Tools Module Debug")
            print("=" * 30)
            
            success = debug_tools(verbose) and debug_tool_metadata()
            
            if success:
                print("\n✓ All tools tests passed!")
            else:
                print("\n✗ Some tools tests failed!")
            
        elif sys.argv[1] == "--help":
            print("Usage:")
            print("  python -m src.tools           # Run demo")
            print("  python -m src.tools --debug   # Run debug tests")
            print("  python -m src.tools --debug --verbose  # Verbose debug")
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Use --help for available options")
    else:
        _demo()
