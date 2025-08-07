from fastapi import APIRouter, Request
from pydantic import BaseModel
from datetime import datetime
from typing import Literal, Union
from services.database import (
    get_package_by_tracking_and_postal,
    update_package_schedule,
)
from services.email import send_reschedule_confirmation_email, send_escalation_email
from models import EscalationReason

router = APIRouter()


class VerifyPackageArgs(BaseModel):
    tracking_number: str
    postal_code: str


class RetellVerifyPackageRequest(BaseModel):
    call: dict
    name: Literal["verify_package"]
    args: VerifyPackageArgs


class VerifyPackageResponse(BaseModel):
    tracking_number: str
    customer_name: str
    status: Literal["scheduled", "out_for_delivery", "delivered"]
    scheduled_at: datetime


class RescheduleArgs(BaseModel):
    tracking_number: str
    postal_code: str
    target_time: datetime


class RetellRescheduleRequest(BaseModel):
    call: dict
    name: Literal["reschedule"]
    args: RescheduleArgs


class RescheduleResponse(BaseModel):
    message: str
    tracking_number: str
    new_schedule: datetime


class EscalateArgs(BaseModel):
    tracking_number: str
    postal_code: str


class RetellEscalateRequest(BaseModel):
    call: dict
    name: Literal["escalate"]
    args: EscalateArgs


class EscalateResponse(BaseModel):
    message: str
    tracking_number: str


# Error types
class PackageNotFoundError(BaseModel):
    error_type: Literal["package_not_found"]
    message: str


class PackageAlreadyDeliveredError(BaseModel):
    error_type: Literal["package_already_delivered"]
    message: str
    current_status: str


class DatabaseError(BaseModel):
    error_type: Literal["database_error"]
    message: str


class EmailError(BaseModel):
    error_type: Literal["email_error"]
    message: str


@router.post("/verify_package")
async def verify_package(
    request: RetellVerifyPackageRequest,
) -> Union[VerifyPackageResponse, PackageNotFoundError, PackageAlreadyDeliveredError]:
    package = get_package_by_tracking_and_postal(
        request.args.tracking_number, request.args.postal_code
    )

    if not package:
        return PackageNotFoundError(
            error_type="package_not_found",
            message="Package not found with the provided tracking number and postal code",
        )

    # Business logic: only scheduled or out_for_delivery packages can be managed
    if package.status not in ["scheduled", "out_for_delivery"]:
        return PackageAlreadyDeliveredError(
            error_type="package_already_delivered",
            message="Package cannot be rescheduled because it has already been delivered",
            current_status=package.status,
        )

    return VerifyPackageResponse(
        tracking_number=package.tracking_number,
        customer_name=package.customer_name,
        status=package.status,
        scheduled_at=package.scheduled_at,
    )


@router.post("/reschedule")
async def reschedule_package(
    request: RetellRescheduleRequest,
) -> Union[
    RescheduleResponse,
    PackageNotFoundError,
    PackageAlreadyDeliveredError,
    DatabaseError,
    EmailError,
]:
    # TODO: Improve time handling for natural language inputs
    # Currently the LLM converts "tomorrow morning" -> "2025-08-10T09:00:00"
    # Issues: ambiguous times, no validation, timezone handling
    # Should add: predefined time slots, input validation, timezone awareness
    package = get_package_by_tracking_and_postal(
        request.args.tracking_number, request.args.postal_code
    )

    if not package:
        return PackageNotFoundError(
            error_type="package_not_found",
            message="Package not found with the provided tracking number and postal code",
        )

    if package.status not in ["scheduled", "out_for_delivery"]:
        return PackageAlreadyDeliveredError(
            error_type="package_already_delivered",
            message="Package cannot be rescheduled because it has already been delivered",
            current_status=package.status,
        )

    success = update_package_schedule(
        request.args.tracking_number, request.args.target_time
    )

    if not success:
        return DatabaseError(
            error_type="database_error",
            message="Failed to update package schedule in database",
        )

    email_success = send_reschedule_confirmation_email(
        customer_email=package.email,
        customer_name=package.customer_name,
        tracking_number=package.tracking_number,
        new_time=request.args.target_time,
    )
    if not email_success:
        return EmailError(
            error_type="email_error",
            message="Package was rescheduled but confirmation email failed to send",
        )

    return RescheduleResponse(
        message="Package rescheduled successfully",
        tracking_number=request.args.tracking_number,
        new_schedule=request.args.target_time,
    )


@router.post("/escalate")
async def escalate_package(
    request: RetellEscalateRequest,
) -> Union[EscalateResponse, PackageNotFoundError, EmailError]:
    package = get_package_by_tracking_and_postal(
        request.args.tracking_number, request.args.postal_code
    )

    if not package:
        return PackageNotFoundError(
            error_type="package_not_found",
            message="Package not found with the provided tracking number and postal code",
        )

    escalation_reason: EscalationReason = "agent_escalation"
    email_success = send_escalation_email(
        customer_email=package.email,
        customer_name=package.customer_name,
        tracking_number=package.tracking_number,
        escalation_reason=escalation_reason,
    )
    if not email_success:
        return EmailError(
            error_type="email_error", message="Failed to send escalation email"
        )

    # TODO: Update call log with escalation

    return EscalateResponse(
        message="Escalation email sent successfully",
        tracking_number=request.args.tracking_number,
    )
