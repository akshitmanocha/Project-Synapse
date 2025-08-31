"""
TOOLS MODULE SPEC (Simulated)

Purpose:
- Provide a thin, test-friendly layer of simulated external tools the agent can call.
- Each tool returns hardcoded or randomized stub data and prints side effects where relevant.

Contracts (inputs -> outputs / effects):
- check_traffic(route: str) -> Literal['heavy','moderate','light']
  Returns a random traffic level for the given route.

- get_merchant_status(merchant_id: str | int) -> dict
  Example: { 'status': 'open', 'prep_time_minutes': 40 }
  Returns a simulated status and prep time.

- notify_customer(customer_id: str | int, message: str) -> bool
  Prints a notification message to stdout and returns True.

- re_route_driver(driver_id: str | int, new_task_id: str | int) -> bool
  Prints a re-routing action to stdout and returns True.

- get_driver_location(driver_id: str | int) -> dict
  Example: { 'lat': 37.7749, 'lon': -122.4194, 'accuracy_m': 25 }
  Returns a simulated geo-position for a driver.

- estimate_eta(route: str, traffic_status: str | None = None) -> int
  Returns a simulated ETA in minutes based on traffic.

- get_order_status(order_id: str | int) -> dict
  Example: { 'status': 'preparing', 'ready_in_minutes': 15 }
  Returns a simulated order status snapshot.

- log_event(event: str, metadata: dict | None = None) -> None
  Prints a structured log line for observability during simulation.

Notes:
- Keep tools deterministic enough for tests when needed; allow seeding via random if desired.
- Replace implementations with real integrations later (APIs/DBs/SDKs). Keep function signatures stable.
"""
from typing import Optional, Dict, Any, List
import random, datetime, uuid, json, os

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

from __future__ import annotations

import random
import time
from typing import Literal, Optional

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

    print("Demo complete. File saved as simulated_tools_full.py")

if __name__ == "__main__":
    _demo()
