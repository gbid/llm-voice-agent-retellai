import json
import logging
import os
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from retell import Retell
from models import RetellWebhookPayload
from services.database import (
    create_call_log,
    update_call_log_completed_by_retell_call_id,
    get_escalation_info_by_retell_call_id,
    get_package_by_tracking_number,
)
from services.email import send_escalation_email
from models import EscalationReason

retell = Retell(api_key=os.environ["RETELL_API_KEY"])

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/events")
async def handle_retell_webhook(request: Request):
    """Handle RetellAI webhook events, see https://docs.retellai.com/features/secure-webhook"""
    try:
        post_data = await request.json()
        valid_signature = retell.verify(
            json.dumps(post_data, separators=(",", ":"), ensure_ascii=False),
            api_key=str(os.environ["RETELL_API_KEY"]),
            signature=str(request.headers.get("X-Retell-Signature")),
        )
        if not valid_signature:
            logger.warning(
                "Received unauthorized webhook: event=%s call_id=%s",
                post_data["event"],
                post_data.get("call", {}).get("call_id", "unknown"),
            )
            return JSONResponse(status_code=401, content={"message": "Unauthorized"})

        payload = RetellWebhookPayload(**post_data)

        logger.info("Received webhook event: %s", payload.event)

        match payload.event:
            case "call_started":
                logger.debug("call_started payload: %s", payload.call)
                if not payload.call.call_id:
                    logger.error("Missing call_id in call_started webhook")
                    return JSONResponse(
                        status_code=400, content={"message": "Missing call_id"}
                    )
                create_call_log(retell_call_id=payload.call.call_id)
                return Response(status_code=204)

            case "call_ended":
                logger.debug("call_ended payload: %s", payload.call)
                if not payload.call.call_id:
                    logger.error("Missing call_id in call_ended webhook")
                    return JSONResponse(
                        status_code=400, content={"message": "Missing call_id"}
                    )

                # TODO: does the RetellAI API guarantee the transcript is present here?
                transcript = payload.call.transcript or ""
                update_call_log_completed_by_retell_call_id(
                    payload.call.call_id, transcript
                )

                # Check if this call was escalated and send escalation email with full transcript
                escalation_info = get_escalation_info_by_retell_call_id(
                    payload.call.call_id
                )
                if escalation_info:
                    package = get_package_by_tracking_number(
                        escalation_info.tracking_number
                    )

                    escalation_reason: EscalationReason = "agent_escalation"

                    send_escalation_email(
                        tracking_number=escalation_info.tracking_number,
                        escalation_reason=escalation_reason,
                        transcript=transcript,
                        customer_email=package.email if package else None,
                        customer_name=package.customer_name if package else None,
                    )

                    logger.info(
                        "Escalation email sent for tracking %s",
                        escalation_info.tracking_number,
                    )

                return Response(status_code=204)

            case "call_analyzed":
                logger.debug("call_analyzed payload: %s", payload.call)
                return Response(status_code=204)

            case _:
                return JSONResponse(
                    status_code=400,
                    content={"message": f"Unknown event type: {payload.event}"},
                )

    except Exception as err:
        logger.error("Error in webhook: %s", err, exc_info=True)
        return JSONResponse(
            status_code=500, content={"message": "Internal Server Error"}
        )
