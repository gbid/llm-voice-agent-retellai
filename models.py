from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Literal
from retell.types import CallResponse

# Type definitions
EscalationReason = Literal[
    "verification_failed", "reschedule_failed", "user_declined", "agent_escalation"
]


# RetellAI Webhook Types
class RetellWebhookPayload(BaseModel):
    event: Literal["call_started", "call_ended", "call_analyzed"]
    call: CallResponse


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
    tracking_number: Optional[str] = None
    transcript: Optional[str] = None
    completed: Optional[datetime] = None
    escalated: Optional[datetime] = None
    created_at: datetime


class CallLog(BaseModel):
    id: int
    tracking_number: Optional[str] = None
    transcript: Optional[str] = None
    completed: Optional[datetime] = None
    escalated: Optional[datetime] = None
    created_at: datetime
