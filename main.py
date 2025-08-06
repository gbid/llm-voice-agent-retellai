from fastapi import FastAPI
from dotenv import load_dotenv
from api import functions, webhooks, dashboard, health

# Load environment variables from .env
load_dotenv()

app = FastAPI(
    title="Delivery Rescheduling API",
    description="API for handling package rescheduling via RetellAI voice agents",
    version="1.0.0",
)

app.include_router(health.router, prefix="/api")
app.include_router(functions.router, prefix="/api/functions")
app.include_router(webhooks.router, prefix="/api/webhooks")
app.include_router(dashboard.router, prefix="/api")
