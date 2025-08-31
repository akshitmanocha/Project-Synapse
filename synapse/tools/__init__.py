"""
Tools module for Synapse logistics coordination system.

This module contains 29 simulated logistics tools across categories:
- Traffic and routing
- Merchant operations
- Customer communication
- Evidence and dispute resolution
- Delivery management
- Refund processing
"""

from .tools import (
    # Debugging utilities
    debug_tools,
    debug_tool_metadata,
    
    # Traffic and routing
    check_traffic,
    
    # Merchant operations  
    get_merchant_status,
    get_nearby_merchants,
    contact_merchant,
    
    # Customer communication
    notify_customer,
    contact_recipient_via_chat,
    
    # Driver management
    get_driver_status,
    re_route_driver,
    exonerate_driver,
    
    # Evidence and disputes
    collect_evidence,
    analyze_evidence,
    log_merchant_packaging_feedback,
    
    # Delivery management
    suggest_safe_drop_off,
    find_nearby_locker,
    schedule_redelivery,
    contact_sender,
    
    # Stock and substitutions
    propose_substitute,
    
    # Refunds
    issue_instant_refund,
    issue_partial_refund,
)

__all__ = [
    # Debugging
    "debug_tools",
    "debug_tool_metadata",
    
    # All operational tools
    "check_traffic",
    "get_merchant_status",
    "get_nearby_merchants",
    "contact_merchant",
    "notify_customer",
    "contact_recipient_via_chat",
    "get_driver_status",
    "re_route_driver",
    "exonerate_driver",
    "collect_evidence",
    "analyze_evidence",
    "log_merchant_packaging_feedback",
    "suggest_safe_drop_off",
    "find_nearby_locker",
    "schedule_redelivery",
    "contact_sender",
    "propose_substitute",
    "issue_instant_refund",
    "issue_partial_refund",
]