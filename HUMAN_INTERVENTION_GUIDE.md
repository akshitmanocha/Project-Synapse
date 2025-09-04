# Human Intervention System - Complete Guide

## 🚨 Overview
The Synapse agent includes a comprehensive human intervention system designed to handle critical situations that require human oversight, legal review, safety protocols, or crisis management.

## 🔧 Human Intervention Tools

### 1. `contact_support_live`
**Purpose**: Create immediate support tickets for human agent intervention

**Parameters**:
- `issue`: Description object with incident details
- `priority`: "low", "medium", "high", "critical"

**Response**:
```json
{
  "tool_name": "contact_support_live",
  "status": "ok",
  "ticket_id": "TKT_xyz123",
  "assigned_to": "support_agent_1",
  "escalated": true,
  "priority": "high",
  "timestamp": "2025-09-04T09:57:40Z"
}
```

### 2. `escalate_to_management`
**Purpose**: Escalate complex issues requiring management approval and oversight

**Parameters**:
- `issue_type`: Category (safety, legal, financial, crisis, etc.)
- `description`: Detailed issue description
- `urgency`: "low", "medium", "high", "critical"  
- `estimated_cost`: Financial impact estimation

**Response**:
```json
{
  "tool_name": "escalate_to_management",
  "escalation_id": "escalation_abc789",
  "assigned_to": "manager_ops",
  "approval_status": "approved",
  "authorization_level": "emergency",
  "approved_amount": 500.0,
  "estimated_resolution_time": "2 hours"
}
```

### 3. `issue_voucher`
**Purpose**: Provide financial compensation with approval workflows

**Parameters**:
- `customer_id`: Recipient identifier
- `amount`: Compensation amount
- `reason`: Justification for voucher

## 🔄 Escalation Chains

The agent automatically triggers human intervention through escalation chains:

### Chain 1: Service Failure → Human Intervention
```
Service Tool Fails → Reflection System → contact_support_live
```

### Chain 2: Financial Issues → Management Approval  
```
High Cost Action → Authorization Check → escalate_to_management
```

### Chain 3: Safety Issues → Emergency Protocol
```
Safety Threat Detected → Immediate Escalation → Both Tools + Emergency Authorization
```

## 📋 Human Intervention Scenarios

### Scenario human.1: Driver Safety Threat
**Trigger**: Physical violence threats, safety concerns
**Workflow**:
1. `contact_support_live` - Immediate safety protocol activation
2. `escalate_to_management` - Emergency management notification 
3. Safety rerouting and driver support

### Scenario human.2: Fraud Investigation
**Trigger**: Theft allegations, disputed transactions
**Workflow**:
1. `collect_evidence` - Gather incident documentation
2. `analyze_evidence` - AI-powered fault assessment
3. `escalate_to_management` - Legal review initiation

### Scenario human.3: Insurance/Legal Issues
**Trigger**: Accidents, liability concerns, high damages
**Workflow**:
1. `escalate_to_management` - Legal department notification
2. `contact_support_live` - Multi-department coordination
3. Insurance claim processing

### Scenario human.4: Crisis Management
**Trigger**: Viral social media, PR crises, brand damage
**Workflow**:
1. `escalate_to_management` - Crisis management team activation
2. `contact_support_live` - Multi-channel response coordination  
3. Compensation and PR response authorization

### Scenario human.5: Regulatory Compliance
**Trigger**: Health violations, regulatory inspections
**Workflow**:
1. `escalate_to_management` - Compliance team notification
2. `contact_support_live` - Regulatory coordination
3. Corrective action planning

## 💰 Authorization System Integration

The system includes multi-level approval workflows:

| Cost Range | Authorization Level | Approver | Typical Resolution |
|------------|-------------------|-----------|-------------------|
| $0 - $50 | Automatic | System | Instant |
| $50 - $500 | Supervisor | Team Lead | 30 minutes |
| $500 - $2,500 | Manager | Department Manager | 2 hours |
| $2,500 - $10,000 | Director | VP/Director | 24 hours |
| $10,000+ | Regulatory | Legal/Compliance | 72 hours |

### Emergency Override
For critical safety situations, the system can bypass normal approval chains:
- **Emergency Authorization Level**: Immediate approval up to $10,000
- **Safety Protocols**: Instant activation for physical threats
- **Crisis Management**: Immediate budget allocation for brand protection

## 🔍 Real-World Example

Here's how the human intervention system handles a safety incident:

### Input Scenario
```
"Driver reports customer threatened physical violence over late delivery"
```

### Agent Response Chain
1. **Assessment**: Agent identifies safety threat
2. **Immediate Action**: `contact_support_live` creates ticket TKT_xyz123
3. **Management Escalation**: `escalate_to_management` with "safety_critical" type  
4. **Emergency Authorization**: $500 approved for driver support
5. **Follow-up**: Driver rerouting and customer notification

### Human Touchpoints
- **Support Agent**: Immediate safety protocol activation
- **Operations Manager**: Incident review and driver support
- **Emergency Authorization**: Bypass normal approval for safety
- **Complete Audit Trail**: Full documentation for legal/HR review

## 🛡️ Key Safety Features

### Immediate Response
- **Sub-minute escalation** for critical safety issues
- **24/7 support agent assignment** for emergency tickets
- **Emergency authorization bypass** for time-sensitive situations

### Comprehensive Coverage
- **Legal Protection**: Automatic legal team notification for liability issues
- **Financial Controls**: Multi-level approval prevents unauthorized spending
- **Crisis Management**: Coordinated response for brand protection
- **Regulatory Compliance**: Automatic compliance team engagement

### Audit & Transparency
- **Complete Paper Trail**: Every escalation fully documented
- **Approval Chains**: Clear authorization hierarchy
- **Performance Tracking**: Response time and resolution monitoring
- **Legal Documentation**: Court-ready incident reports

## 🚀 Integration with Agent Reflection System

The human intervention system integrates seamlessly with the agent's reflection system:

### Automatic Trigger Conditions
```python
# Example from agent.py reflection system
elif observation.get("cancelled") is False and tool_name == "cancel_booking":
    needs_reflection = True
    reflection_reason = "Booking cancellation failed - escalate to support"
    alternative_approach = "contact_support_live"
```

### Intelligent Escalation
- **Context-Aware**: Escalations include full problem context
- **Cost-Conscious**: Automatic cost estimation for approval workflows
- **Time-Sensitive**: Urgent issues get priority routing
- **Multi-Modal**: Can handle phone, chat, email, and in-person coordination

This system ensures that while the agent handles 90%+ of logistics issues autonomously, critical situations requiring human judgment, legal expertise, or safety protocols are immediately and appropriately escalated to qualified human personnel.