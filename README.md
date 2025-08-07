# Delivery Rescheduling Voice AI

Voice AI agent for rescheduling package deliveries. Built with RetellAI.com, FastAPI, and SQLite.

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Add your API keys to .env
cp .env.example .env

# Initialize database with test data
python database.py

# Run server
uvicorn main:app --reload
```

## How it works

1. Customer calls the voice agent (RetellAI.com)
2. Agent asks for tracking number and postal code
3. Confirms details back to customer
4. Voice agent calls FastAPI backend via function calls to look up package in SQLite database
5. If found and eligible, offers 3 time slots
6. Voice agent calls backend to update schedule and send confirmation email via Resend.com
7. If anything fails, voice agent calls backend to escalate to human via email

## API Endpoints

The `/api/functions` endpoints are tool/function calls that the RetellAI voice agent can invoke during conversations:

- `/api/functions/verify_package` - Package lookup
- `/api/functions/reschedule` - Update delivery time
- `/api/functions/escalate` - Send to human support

Other endpoints:
- `/api/webhooks/events` - RetellAI webhook handler
- `/api/packages` - Dashboard: list all packages
- `/api/call_logs` - Dashboard: call history

## Testing

```bash
pytest test_functions.py
```

Tests cover the voice agent function calls (verify, reschedule, escalate) and RetellAI webhook handling with various success/failure scenarios.

Test data includes tracking numbers: 001, 002, 003 with postal codes 12345, 67890, 54321.

## TODO - What I'd do with more time

- **Rate limiting** (RetellAI calls are expensive)
  - Probably based on phone numbers since they are restricted heavily (at least german phone numbers)
  - We might still need to limit the length and the frequency of calls from individual german / US numbers.
  - I would decide this based on looking at actual usage data
- **Partial failures, transactions, concurrency:**
  - Reschedule, email confirmation happen before final user confirmation in voice agent flow
    1. first look up available timeslots
    2. then confirm user choice in dialogue
    3. then reschedule and send email and fail upon race condition between initial lookup and final reschedule
  - Reschedule and email confirmation does not happen atomically
    - Track confirmation email sending status, retry with a cronjob for failed sends
    - For something more critical than package delivery, if in doubt, I would rather rollback the changes if
      the confirmation could not be sent, i.e. implement this as a transaction.
  - How to handle concurrent calls for the same package
    - A robust solution would be to lock packages for rescheduling upon successfull call to verify_package until the end of the call.
    - For a more pragmatic approach (e.g. due to time / complexity reasons), last write wins could be sufficient.
- **Handle target times for reschedule properly** (both in agent and backend)
  - time intervals within timezones
  - do not let LLM convert from "tomorrow morning" to timestamp, but do this symbolically in backend
  - actual timing consideration for route planning
- **Logging and Monitoring**
  - log errors, escalations
  - monitor number of ongoing calls, number of escalations in last hour / day / week using Grafana or similar tools
- **More states for delivery**
- **More robust authentication of calls** based on phone number saved in package details
- **Bonus exercise from problem statement** (Post-Call QA with LLM and call log)
