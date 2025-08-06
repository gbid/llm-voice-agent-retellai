from fastapi import APIRouter, HTTPException
from models import RetellWebhookPayload
from services.database import create_call_log, update_call_log_completed

router = APIRouter()


@router.post("/events")
async def handle_retell_webhook(payload: RetellWebhookPayload):
    """Handle RetellAI webhook events"""

    match payload.event:
        case "call_started":
            # TODO: RetellAI does not have a specification for call_started data
            print(f"call_started payload: {payload.call}")
            return {"status": "success"}

        case "call_ended":
            call = payload.call
            call_log_id = create_call_log(tracking_number=None)

            # TODO: does the RetellAI API guarantee the transcript is present here?
            transcript = getattr(call, "transcript", "") or ""
            update_call_log_completed(call_log_id, transcript)

            return {"status": "success"}

        case "call_analyzed":
            return {"status": "success"}

        case _:
            raise HTTPException(
                status_code=400, detail=f"Unknown event type: {payload.event}"
            )
