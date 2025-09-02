"""
Authorization and Permission Management System for Synapse Agent

This module implements a comprehensive approval workflow system for actions that require
human oversight, monetary approvals, or regulatory compliance checks.
"""

import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta


class AuthorizationLevel(Enum):
    """Different levels of authorization required for various actions."""
    AUTOMATIC = "automatic"          # No approval needed
    SUPERVISOR = "supervisor"        # Team supervisor approval
    MANAGER = "manager"              # Department manager approval  
    DIRECTOR = "director"            # Director/VP approval
    EXECUTIVE = "executive"          # C-level approval
    REGULATORY = "regulatory"        # Legal/compliance approval
    EMERGENCY = "emergency"          # Emergency override available


class ApprovalStatus(Enum):
    """Status of approval requests."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"
    EXPIRED = "expired"
    EMERGENCY_OVERRIDE = "emergency_override"


@dataclass
class ApprovalRequest:
    """Represents a request for human approval."""
    request_id: str
    action_type: str
    description: str
    monetary_value: float
    authorization_level: AuthorizationLevel
    requester: str = "synapse_agent"
    timestamp: datetime = field(default_factory=datetime.now)
    expiry_time: Optional[datetime] = None
    context: Dict[str, Any] = field(default_factory=dict)
    stakeholders: List[str] = field(default_factory=list)
    attempted_resolutions: List[str] = field(default_factory=list)
    urgency: str = "medium"  # low, medium, high, critical
    
    # Approval tracking
    status: ApprovalStatus = ApprovalStatus.PENDING
    approver: Optional[str] = None
    approval_timestamp: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    conditions: List[str] = field(default_factory=list)


class AuthorizationManager:
    """
    Manages approval workflows and authorization levels for the Synapse agent.
    Determines when human intervention is required and routes requests appropriately.
    """
    
    def __init__(self):
        self.pending_requests: Dict[str, ApprovalRequest] = {}
        self.approval_history: List[ApprovalRequest] = []
        
        # Authorization thresholds (configurable per organization)
        self.monetary_thresholds = {
            AuthorizationLevel.AUTOMATIC: 0.0,      # Free actions
            AuthorizationLevel.SUPERVISOR: 25.0,     # Up to $25
            AuthorizationLevel.MANAGER: 100.0,       # Up to $100
            AuthorizationLevel.DIRECTOR: 500.0,      # Up to $500
            AuthorizationLevel.EXECUTIVE: 2000.0,    # Up to $2000
            AuthorizationLevel.REGULATORY: float('inf')  # Any amount if legal issue
        }
        
        # Auto-approval rules for common scenarios
        self.auto_approval_rules = {
            "standard_delivery_delay_notification": AuthorizationLevel.AUTOMATIC,
            "traffic_rerouting": AuthorizationLevel.AUTOMATIC,
            "merchant_status_check": AuthorizationLevel.AUTOMATIC,
            "customer_notification": AuthorizationLevel.AUTOMATIC,
        }
        
        # Emergency override capabilities
        self.emergency_override_enabled = True
        self.emergency_contact = "emergency@logistics.company.com"
    
    def check_authorization_required(self, action: str, monetary_value: float = 0.0, 
                                   context: Dict[str, Any] = None) -> Tuple[bool, AuthorizationLevel]:
        """
        Determine if action requires authorization and at what level.
        
        Returns:
            Tuple of (requires_authorization, authorization_level)
        """
        context = context or {}
        
        # Check for automatic approval scenarios
        if action in self.auto_approval_rules:
            level = self.auto_approval_rules[action]
            if level == AuthorizationLevel.AUTOMATIC:
                return False, level
        
        # Safety and emergency scenarios - immediate escalation
        safety_keywords = ["accident", "injury", "emergency", "threat", "danger", "assault"]
        if any(keyword in action.lower() or keyword in str(context).lower() 
               for keyword in safety_keywords):
            return True, AuthorizationLevel.EMERGENCY
        
        # Legal and regulatory scenarios
        legal_keywords = ["lawsuit", "legal", "court", "police", "fraud", "theft", "compliance"]
        if any(keyword in action.lower() or keyword in str(context).lower() 
               for keyword in legal_keywords):
            return True, AuthorizationLevel.REGULATORY
        
        # High-value delivery scenarios
        if context.get("delivery_value", 0) > 1000:
            return True, AuthorizationLevel.MANAGER
        
        # Monetary thresholds
        for level, threshold in sorted(self.monetary_thresholds.items(), 
                                     key=lambda x: x[1]):
            if monetary_value <= threshold:
                if level == AuthorizationLevel.AUTOMATIC:
                    return False, level
                else:
                    return True, level
        
        # Default to highest level for unknown scenarios
        return True, AuthorizationLevel.EXECUTIVE
    
    def request_approval(self, action: str, description: str, monetary_value: float = 0.0,
                        context: Dict[str, Any] = None, urgency: str = "medium") -> ApprovalRequest:
        """Create an approval request for human review."""
        requires_auth, auth_level = self.check_authorization_required(action, monetary_value, context)
        
        if not requires_auth:
            # Auto-approve
            request = ApprovalRequest(
                request_id=f"AUTO_{int(time.time() * 1000)}",
                action_type=action,
                description=description,
                monetary_value=monetary_value,
                authorization_level=auth_level,
                context=context or {},
                urgency=urgency,
                status=ApprovalStatus.APPROVED,
                approver="system_auto",
                approval_timestamp=datetime.now()
            )
            self.approval_history.append(request)
            return request
        
        # Create approval request
        request_id = f"REQ_{int(time.time() * 1000)}"
        request = ApprovalRequest(
            request_id=request_id,
            action_type=action,
            description=description,
            monetary_value=monetary_value,
            authorization_level=auth_level,
            context=context or {},
            urgency=urgency,
            expiry_time=self._calculate_expiry_time(urgency, auth_level)
        )
        
        self.pending_requests[request_id] = request
        return request
    
    def simulate_approval_decision(self, request: ApprovalRequest) -> ApprovalRequest:
        """
        Simulate human approval decision for demonstration purposes.
        In production, this would integrate with actual approval workflows.
        """
        # Simulate decision based on various factors
        approval_probability = self._calculate_approval_probability(request)
        
        import random
        decision = random.random()
        
        if decision < approval_probability:
            request.status = ApprovalStatus.APPROVED
            request.approver = f"{request.authorization_level.value}_approver"
            request.approval_timestamp = datetime.now()
            
            # Add conditions for certain approvals
            if request.monetary_value > 100:
                request.conditions.append("Requires receipt documentation")
            if "refund" in request.action_type.lower():
                request.conditions.append("Customer satisfaction survey required")
                
        else:
            request.status = ApprovalStatus.REJECTED
            request.approver = f"{request.authorization_level.value}_approver"
            request.approval_timestamp = datetime.now()
            request.rejection_reason = self._generate_rejection_reason(request)
        
        # Move from pending to history
        if request.request_id in self.pending_requests:
            del self.pending_requests[request.request_id]
        self.approval_history.append(request)
        
        return request
    
    def check_emergency_override_available(self, request: ApprovalRequest) -> bool:
        """Check if emergency override is available for urgent situations."""
        if not self.emergency_override_enabled:
            return False
        
        # Emergency override available for high urgency situations
        emergency_scenarios = [
            request.urgency == "critical",
            "emergency" in request.action_type.lower(),
            "safety" in request.description.lower(),
            request.authorization_level == AuthorizationLevel.EMERGENCY
        ]
        
        return any(emergency_scenarios)
    
    def apply_emergency_override(self, request: ApprovalRequest, override_reason: str) -> ApprovalRequest:
        """Apply emergency override to bypass approval workflow."""
        request.status = ApprovalStatus.EMERGENCY_OVERRIDE
        request.approver = "emergency_override_system"
        request.approval_timestamp = datetime.now()
        request.conditions.append(f"Emergency override: {override_reason}")
        request.conditions.append("Post-incident review required")
        
        # Log emergency override for audit
        self._log_emergency_override(request, override_reason)
        
        return request
    
    def get_approval_summary(self) -> Dict[str, Any]:
        """Get summary of approval requests and patterns."""
        total_requests = len(self.approval_history) + len(self.pending_requests)
        if total_requests == 0:
            return {"total_requests": 0}
        
        approved = len([r for r in self.approval_history if r.status == ApprovalStatus.APPROVED])
        rejected = len([r for r in self.approval_history if r.status == ApprovalStatus.REJECTED])
        pending = len(self.pending_requests)
        emergency_overrides = len([r for r in self.approval_history 
                                 if r.status == ApprovalStatus.EMERGENCY_OVERRIDE])
        
        total_monetary_value = sum(r.monetary_value for r in self.approval_history)
        
        return {
            "total_requests": total_requests,
            "approved": approved,
            "rejected": rejected,
            "pending": pending,
            "emergency_overrides": emergency_overrides,
            "approval_rate": (approved / len(self.approval_history) * 100) if self.approval_history else 0,
            "total_monetary_value": total_monetary_value,
            "avg_monetary_value": total_monetary_value / len(self.approval_history) if self.approval_history else 0
        }
    
    def _calculate_expiry_time(self, urgency: str, auth_level: AuthorizationLevel) -> datetime:
        """Calculate when approval request expires based on urgency and level."""
        base_hours = {
            "critical": 1,
            "high": 4, 
            "medium": 24,
            "low": 72
        }
        
        # Higher authorization levels get more time
        multiplier = {
            AuthorizationLevel.SUPERVISOR: 1.0,
            AuthorizationLevel.MANAGER: 1.5,
            AuthorizationLevel.DIRECTOR: 2.0,
            AuthorizationLevel.EXECUTIVE: 3.0,
            AuthorizationLevel.REGULATORY: 5.0,
            AuthorizationLevel.EMERGENCY: 0.5
        }
        
        hours = base_hours.get(urgency, 24) * multiplier.get(auth_level, 1.0)
        return datetime.now() + timedelta(hours=hours)
    
    def _calculate_approval_probability(self, request: ApprovalRequest) -> float:
        """Calculate probability of approval for simulation."""
        base_prob = 0.8  # 80% base approval rate
        
        # Adjust based on monetary value
        if request.monetary_value > 500:
            base_prob -= 0.2
        elif request.monetary_value > 100:
            base_prob -= 0.1
        
        # Adjust based on urgency
        if request.urgency == "critical":
            base_prob += 0.1
        elif request.urgency == "low":
            base_prob -= 0.1
        
        # Adjust based on authorization level
        if request.authorization_level in [AuthorizationLevel.EXECUTIVE, AuthorizationLevel.REGULATORY]:
            base_prob -= 0.2
        
        return max(0.1, min(0.95, base_prob))
    
    def _generate_rejection_reason(self, request: ApprovalRequest) -> str:
        """Generate realistic rejection reasons."""
        reasons = [
            "Insufficient justification provided",
            "Exceeds authorized spending limits", 
            "Alternative lower-cost solution available",
            "Requires additional documentation",
            "Policy violation detected",
            "Needs secondary approval",
            "Insufficient evidence of customer fault"
        ]
        
        if request.monetary_value > 100:
            reasons.extend([
                "Amount exceeds threshold for this scenario type",
                "Requires detailed cost-benefit analysis"
            ])
        
        import random
        return random.choice(reasons)
    
    def _log_emergency_override(self, request: ApprovalRequest, reason: str):
        """Log emergency override for audit trail."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "request_id": request.request_id,
            "action": request.action_type,
            "monetary_value": request.monetary_value,
            "override_reason": reason,
            "urgency": request.urgency
        }
        
        # In production, this would write to audit log
        print(f"🚨 EMERGENCY OVERRIDE LOGGED: {log_entry}")


# Actions requiring approval with their typical monetary values and contexts
APPROVAL_REQUIRED_ACTIONS = {
    # Monetary vouchers and refunds
    "issue_monetary_voucher": {
        "base_amount": 10.0,
        "description": "Issue monetary voucher to customer",
        "typical_context": ["order_delay", "quality_issue", "service_failure"]
    },
    
    "issue_full_refund": {
        "base_amount": 50.0,
        "description": "Process full order refund",
        "typical_context": ["order_cancelled", "delivery_failure", "customer_dissatisfaction"]
    },
    
    "issue_partial_refund": {
        "base_amount": 25.0,
        "description": "Process partial refund for order issues",
        "typical_context": ["partial_damage", "missing_items", "late_delivery"]
    },
    
    # Premium service offerings
    "upgrade_to_priority_delivery": {
        "base_amount": 15.0,
        "description": "Upgrade customer to priority delivery at no charge",
        "typical_context": ["service_recovery", "vip_customer", "severe_delay"]
    },
    
    "provide_free_redelivery": {
        "base_amount": 8.0,
        "description": "Arrange free redelivery attempt",
        "typical_context": ["delivery_failure", "address_issue", "customer_unavailable"]
    },
    
    # Driver compensation and support
    "authorize_driver_bonus": {
        "base_amount": 20.0,
        "description": "Authorize performance bonus for driver",
        "typical_context": ["exceptional_service", "difficult_conditions", "customer_complaint_resolution"]
    },
    
    "cover_driver_expenses": {
        "base_amount": 30.0,
        "description": "Reimburse driver for incident-related expenses",
        "typical_context": ["vehicle_damage", "parking_fees", "equipment_replacement"]
    },
    
    # Merchant relations
    "issue_merchant_credit": {
        "base_amount": 75.0,
        "description": "Issue credit to merchant for platform issues",
        "typical_context": ["system_downtime", "order_processing_error", "payment_delay"]
    },
    
    # High-value interventions
    "escalate_to_legal_team": {
        "base_amount": 200.0,
        "description": "Escalate matter to legal department",
        "typical_context": ["fraud_suspected", "liability_claim", "regulatory_violation"]
    },
    
    "arrange_premium_support": {
        "base_amount": 100.0,
        "description": "Provide premium customer support intervention",
        "typical_context": ["vip_customer", "viral_complaint", "media_attention"]
    }
}


# Global authorization manager instance
auth_manager = AuthorizationManager()