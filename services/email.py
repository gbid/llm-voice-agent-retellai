import os
import resend
from datetime import datetime
from models import EscalationReason


resend.api_key = os.getenv("RESEND_API_KEY")
source_email = "onboarding@resend.dev"
escalation_target_email = "escalation@bidlingmaier.net"


def send_reschedule_confirmation_email(
    customer_email: str, customer_name: str, tracking_number: str, new_time: datetime
) -> bool:
    """Send confirmation email after successful package reschedule"""

    if not resend.api_key:
        print("Warning: RESEND_API_KEY not configured")
        return False

    formatted_time = new_time.strftime("%A, %B %d, %Y at %I:%M %p")

    params: resend.Emails.SendParams = {
        "from": f"Delivery Service <{source_email}>",
        "to": [customer_email],
        "subject": f"Delivery Rescheduled - Package {tracking_number}",
        "html": f"""
        <html>
        <body>
            <h2>Delivery Rescheduled Successfully</h2>
            <p>Hello {customer_name},</p>
            
            <p>Your package delivery has been successfully rescheduled:</p>
            
            <ul>
                <li><strong>Tracking Number:</strong> {tracking_number}</li>
                <li><strong>New Delivery Time:</strong> {formatted_time}</li>
            </ul>
            
            <p>You will receive an SMS notification when your package is out for delivery.</p>
            
            <p>Thank you for choosing our delivery service!</p>
            
            <p>Best regards,<br>
            Delivery Service Team</p>
        </body>
        </html>
        """,
    }

    try:
        email = resend.Emails.send(params)
        return email is not None
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False


def send_escalation_email(
    customer_email: str,
    customer_name: str,
    tracking_number: str,
    escalation_reason: EscalationReason,
) -> bool:
    """Send escalation notification to support team when issue needs human intervention"""

    if not resend.api_key:
        print("Warning: RESEND_API_KEY not configured")
        return False

    reason_messages = {
        "verification_failed": "Unable to verify package information",
        "reschedule_failed": "Issue encountered while rescheduling delivery",
        "user_declined": "Customer declined proposed rescheduling options",
        "agent_escalation": "Automated system needs additional assistance",
    }

    reason_message = reason_messages.get(
        escalation_reason, "Additional assistance needed"
    )
    support_email = escalation_target_email

    params: resend.Emails.SendParams = {
        "from": f"Delivery Service <{source_email}>",
        "to": [escalation_target_email],
        "subject": f"ESCALATION REQUIRED - Package {tracking_number}",
        "html": f"""
        <html>
        <body>
            <h2>Customer Support Escalation</h2>
            
            <p><strong>Escalation Reason:</strong> {reason_message}</p>
            
            <h3>Customer Information:</h3>
            <ul>
                <li><strong>Name:</strong> {customer_name}</li>
                <li><strong>Email:</strong> {customer_email}</li>
                <li><strong>Tracking Number:</strong> {tracking_number}</li>
                <li><strong>Escalation Type:</strong> {escalation_reason}</li>
                <li><strong>Reference ID:</strong> ESC-{tracking_number}-{datetime.now().strftime("%Y%m%d")}</li>
                <li><strong>Escalated At:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}</li>
            </ul>
        </body>
        </html>
        """,
    }

    try:
        email = resend.Emails.send(params)
        return email is not None
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False
