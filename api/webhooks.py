import json
import os
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from retell import Retell
from models import RetellWebhookPayload
from services.database import create_call_log, update_call_log_completed

retell = Retell(api_key=os.environ["RETELL_API_KEY"])

router = APIRouter()


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
            print(
                "Received Unauthorized",
                post_data["event"],
                post_data.get("call", {}).get("call_id", "unknown"),
            )
            return JSONResponse(status_code=401, content={"message": "Unauthorized"})

        payload = RetellWebhookPayload(**post_data)

        print(f"Received webhook event: {payload.event}")

        match payload.event:
            case "call_started":
                # TODO: RetellAI does not have a specification for call_started data
                print(f"call_started payload: {payload.call}")
                return Response(status_code=204)

            case "call_ended":
                print(f"call_ended payload: {payload.call}")
                call_log_id = create_call_log(tracking_number=None)

                # TODO: does the RetellAI API guarantee the transcript is present here?
                transcript = payload.call.transcript or ""
                update_call_log_completed(call_log_id, transcript)

                return Response(status_code=204)

            case "call_analyzed":
                print(f"call_analyzed payload: {payload.call}")
                return Response(status_code=204)

            case _:
                return JSONResponse(
                    status_code=400,
                    content={"message": f"Unknown event type: {payload.event}"},
                )

    except Exception as err:
        print(f"Error in webhook: {err}")
        return JSONResponse(
            status_code=500, content={"message": "Internal Server Error"}
        )
