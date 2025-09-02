# 🔐 Authorization & Approval System

## Overview

The Synapse agent includes a comprehensive authorization system that determines when human approval is required for financial, high-impact, or sensitive actions. This makes the system more realistic for enterprise deployment and demonstrates sophisticated business logic.

## 🎯 Key Features

### Authorization Levels
- **AUTOMATIC**: No approval needed (free actions)
- **SUPERVISOR**: Team supervisor approval (up to $25)
- **MANAGER**: Department manager approval (up to $100) 
- **DIRECTOR**: Director/VP approval (up to $500)
- **EXECUTIVE**: C-level approval (up to $2000)
- **REGULATORY**: Legal/compliance approval (any amount)
- **EMERGENCY**: Emergency override available

### Approval Triggers
1. **Monetary Thresholds**: Actions above certain dollar amounts
2. **Safety Keywords**: "accident", "injury", "emergency", "threat"
3. **Legal Keywords**: "lawsuit", "fraud", "theft", "compliance"
4. **High-Value Deliveries**: Orders over $1000
5. **VIP Customers**: Special handling requirements

## 🛠️ New Approval-Requiring Tools

### Financial Actions
- **`issue_monetary_voucher`**: Issue compensation vouchers to customers
- **`authorize_driver_bonus`**: Award performance bonuses to drivers  
- **`issue_merchant_credit`**: Credit merchants for platform issues
- **`arrange_premium_redelivery`**: Premium service with waived fees

### Management Escalations
- **`escalate_to_management`**: Route complex issues to human managers
- **Emergency override capabilities** for critical situations

## 📊 Authorization Matrix

| Action Type | Amount | Authorization Level | Typical Scenario |
|-------------|--------|-------------------|------------------|
| Standard notification | $0 | AUTOMATIC | Traffic delays, status updates |
| Small voucher | $1-25 | SUPERVISOR | Minor service issues |
| Medium compensation | $26-100 | MANAGER | Significant delays, quality issues |
| Large refunds | $101-500 | DIRECTOR | Major service failures |
| High-value actions | $501-2000 | EXECUTIVE | VIP customers, major incidents |
| Legal/safety issues | Any | REGULATORY/EMERGENCY | Safety threats, fraud, compliance |

## 🎮 New Scenarios

### Approval Scenarios (`approval.1-5`)
Test monetary authorization workflows:
- **approval.1**: $50 voucher for cold food (Manager approval)
- **approval.2**: VIP $2000 jewelry escalation (Executive approval)
- **approval.3**: Driver expense reimbursement (Supervisor approval)
- **approval.4**: Merchant platform credit (Manager approval) 
- **approval.5**: Premium redelivery fees waived (Supervisor approval)

### Human Intervention Scenarios (`human.1-5`)
Critical situations requiring immediate human oversight:
- **human.1**: Safety threat escalation (Emergency level)
- **human.2**: Theft accusation (Regulatory/Legal)
- **human.3**: Vehicle accident liability (Executive/Legal)
- **human.4**: Viral social media crisis (Executive)
- **human.5**: Regulatory compliance issue (Regulatory)

## 💻 Usage Examples

### Test Approval Workflows
```bash
# Monetary voucher requiring approval
python main.py --scenario approval.1

# High-value VIP escalation  
python main.py --scenario approval.2 --executive

# Safety emergency requiring human intervention
python main.py --scenario human.1 --verbose
```

### Direct Tool Usage
```python
from synapse.tools.tools import issue_monetary_voucher

# This will trigger approval workflow
result = issue_monetary_voucher(
    customer_id="cust_123",
    amount=75.0,  # Requires manager approval
    reason="Delivery failure with food spoilage"
)

print(f"Voucher issued: {result['voucher_issued']}")
print(f"Approval status: {result['approval_status']}")
print(f"Authorization level: {result['authorization_level']}")
```

## 🔄 Approval Workflow

```
1. Agent detects need for financial/high-impact action
   ↓
2. Authorization system checks thresholds and keywords
   ↓
3. If approval required:
   - Create approval request
   - Route to appropriate authorization level
   - Simulate approval decision (demo mode)
   ↓
4. If approved: Execute action with conditions
   If denied: Return rejection reason
   If emergency: Override available for critical situations
```

## 📈 Benefits for Enterprise Use

### Risk Management
- **Financial Controls**: Prevents unauthorized spending
- **Compliance**: Ensures regulatory approval for sensitive actions
- **Audit Trail**: Complete record of all approval decisions
- **Emergency Procedures**: Override capabilities for critical situations

### Business Realism
- **Approval Hierarchies**: Mirrors real corporate structures
- **Cost Controls**: Demonstrates expense management
- **Legal Protection**: Shows awareness of liability issues
- **Operational Excellence**: Professional business processes

### Demonstration Value
- **Executive Presentations**: Shows sophisticated business logic
- **Stakeholder Confidence**: Demonstrates enterprise readiness
- **Risk Awareness**: Highlights thoughtful system design
- **Scalability**: Configurable for different organization sizes

## ⚙️ Configuration

Thresholds and rules are fully configurable:

```python
# Customize monetary thresholds
auth_manager.monetary_thresholds = {
    AuthorizationLevel.SUPERVISOR: 50.0,    # Raise supervisor limit
    AuthorizationLevel.MANAGER: 200.0,      # Raise manager limit
    # ... other levels
}

# Add custom auto-approval rules
auth_manager.auto_approval_rules.update({
    "customer_satisfaction_survey": AuthorizationLevel.AUTOMATIC,
    "driver_location_update": AuthorizationLevel.AUTOMATIC
})
```

## 🎯 Integration with Executive Mode

The authorization system fully integrates with executive mode to show:
- **Approval Requests**: Real-time approval workflows
- **Cost Tracking**: Actual vs. approved amounts
- **Authorization Metrics**: Approval rates by level
- **Risk Analysis**: High-risk action patterns

This creates a comprehensive view of both operational performance and financial controls, perfect for executive demonstrations and enterprise deployments.

---

The authorization system transforms the Synapse agent from a simple problem solver into a **business-aware, enterprise-ready platform** that respects organizational hierarchies, financial controls, and regulatory requirements.