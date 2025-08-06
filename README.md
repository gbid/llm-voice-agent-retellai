Package rescheduling service.
Components:
    - FastAPI Webserver with SQLite database as backend
    - RetellAI.com for voice agents
    - Resend.com for sending emails

Backend:
    - FastAPI Webserver using uvicorn
    - .env for secrets
    - requirements.txt for dependencies
    - endpoints:
        /events (handles webhook calls from RetellAI)
            - event "call_started" => insert entry into call_logs
            - event "call_ended" with call_object => update call_logs entry with transcript, completed
                TODO: do we have to update "escalated" and "tracking_number" in the function calls?
        /functions
            These functions can be called by the RetellAI voice agent in the course of conversations with a user:
            /verify_package(tracking_number: str, postal_code: str) -> Option<Package>
                - tracking_number and postal_code are asked by the voice agent from the user
                - this needs to verify the corresponding package exists in the database and has status "scheduled" or "out_for_delivery"
            /reschedule(tracking_number: str, postal_code: str, target_time: timestamp)
                TODO: target in the user conversation is just "tomorrow AM, tomorrow PM, Saturday AM"
                    - how do we best handle this in target_time?
                    - convert this into timestamp in the retell agent already before the function call, or only in our backend?
            /escalate(tracking_number: str, postal_code: str)
                This escalates from the retellAI voice agent to a human via email in the following cases:
                    - verify_package failed
                    - delivery cannot be rescheduled
                        TODO: when is this the case, only upon server error on /reschedule endpoint?


SQLite:
    - table "packages":
        id: primary key
        tracking_number: str (unique constraint)
        customer_name: str
        phone: str
        address (TODO: should we split this into postal code, street, street_number?)
        status: scheduled | out_for_delivery | delivered
        scheduled_at: timestamp
    - table "call_logs":
        id: primary key
        tracking_number: optional str (unique constraint)
        transcript: optional str
        completed: optional timestamp
        escalated: optional timestamp
        created_at: timestamp

RetellAI:
    Conversation flow Agent has logic coded as graph.
    Nodes are conversation states.
    Edges define conditional transitions
    In control flow:
        tracking_number, postal_code = ask_from_user
        let verified = verify_package(tracking_number, postal_code)
        if not verified:
            escalate(tracking_number, postal_code)
            TODO: why do we even need to do this in the agent instead of the backend?
            return
        let target_time = ask_from_user
        let rescheduled = reschedule(tracking_number, postal_code, target_time)
        if not rescheduled:
            escalate(tracking_number, postal_code)
            TODO: why do we even need to do this in the agent instead of the backend?
            return
        let confirmed = ask_user
        if !confirmed:
            escalate(tracking_number, postal_code)
