Components:
    - FastAPI Webserver with SQLite database as backend
    - RetellAI.com for voice agents
    - Resend.com for sending emails

TODO:
    Rate limiting (calls expensive)
        Probably based on phone numbers since they are restricted heavily (at least with german origin)
        We might still need to limit the length and the frequency of calls from individual german / US numbers.
            I would decide this based on looking at actual usage data
    Partial failures, transactions, concurrency:
        Reschedule, email confirmation happen before final user confirmation in voice agent flow
            1. first look up available timeslots
            2. then confirm user choice in dialogue
            3. then reschedule and send email and fail upon race condition between initial lookup and final reschedule
        Reschedule and email confirmation does not happen atomically
            Track confirmation email sending status, retry with a cronjob for failed sends
        How to handle concurrent calls for the same package
            A robust solution would be to lock packages for rescheduling upon successfull call to verify_package
            For a more pragmatic approach (e.g. due to time / complexity reasons), last write wins could be sufficient
    Handle target times for reschedule properly (both in agent and backend)
        time intervals within timezones
        do not let LLM convert from "tomorrow morning" to timestamp, but do this symbolically in backend
        actual timing consideration for route planning
    Logging
    More states for delivery
    More robust authentication of calls based on phone number saved in package details
    Bonus exercise from problem statement (Post-Call QA with LLM and call log)
