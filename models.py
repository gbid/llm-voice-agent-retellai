from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Literal


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