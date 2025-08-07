from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Literal

# Type definitions
EscalationReason = Literal[
    "verification_failed", "reschedule_failed", "user_declined", "agent_escalation"
]


# Custom webhook models - RetellAI webhook docs promise "all fields from call object"
# but their SDK WebCallResponse/CallResponse types can't parse node_transition roles
# in transcript_with_tool_calls that their actual webhooks send
class RetellWebhookCall(BaseModel):
    call_id: str
    agent_id: str
    call_status: str
    transcript: Optional[str] = None
    # Skip transcript_with_tool_calls - RetellAI SDK can't parse their own webhook data


class RetellWebhookPayload(BaseModel):
    event: Literal["call_started", "call_ended", "call_analyzed"]
    call: RetellWebhookCall


class PackageCreate(BaseModel):
    tracking_number: str
    customer_name: str
    phone: str
    email: str
    postal_code: str
    street: str
    street_number: str
    status: Literal["scheduled", "out_for_delivery", "delivered"]
    scheduled_at: datetime


class Package(BaseModel):
    id: int
    tracking_number: str
    customer_name: str
    phone: str
    email: str
    postal_code: str
    street: str
    street_number: str
    status: Literal["scheduled", "out_for_delivery", "delivered"]
    scheduled_at: datetime


class CallLogCreate(BaseModel):
    retell_call_id: str
    tracking_number: Optional[str] = None
    transcript: Optional[str] = None
    completed: Optional[datetime] = None
    escalated: Optional[datetime] = None
    created_at: datetime


class CallLog(BaseModel):
    id: int
    retell_call_id: str
    tracking_number: Optional[str] = None
    transcript: Optional[str] = None
    completed: Optional[datetime] = None
    escalated: Optional[datetime] = None
    created_at: datetime


class EscalationInfo(BaseModel):
    tracking_number: str
    escalated: str  # ISO datetime string from database
