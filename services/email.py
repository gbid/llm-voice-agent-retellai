import os
import resend
from datetime import datetime
from typing import Optional
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
    tracking_number: str,
    escalation_reason: EscalationReason,
    transcript: str = "",
    customer_email: Optional[str] = None,
    customer_name: Optional[str] = None,
) -> bool:
    """Send escalation notification to support team when issue needs human intervention"""

    if not resend.api_key:
        print("Warning: RESEND_API_KEY not configured")
        return False

    params: resend.Emails.SendParams = {
        "from": f"Delivery Service <{source_email}>",
        "to": [escalation_target_email],
        "subject": f"ESCALATION REQUIRED - Package {tracking_number}",
        "html": f"""
        <html>
        <body>
            <h2>Customer Support Escalation</h2>
            
            <h3>Details:</h3>
            <ul>
                <li><strong>Tracking Number:</strong> {tracking_number}</li>
                <li><strong>Escalated At:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}</li>
                {f"<li><strong>Customer Name:</strong> {customer_name}</li>" if customer_name else ""}
                {f"<li><strong>Customer Email:</strong> {customer_email}</li>" if customer_email else ""}
            </ul>
            
            <h3>Call Transcript:</h3>
            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; white-space: pre-wrap; font-family: monospace; margin: 10px 0;">{transcript if transcript else "No transcript available"}</div>
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
