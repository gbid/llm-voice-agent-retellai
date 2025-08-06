from fastapi import APIRouter
from typing import List
from models import Package, CallLog
from services.database import get_all_packages, get_all_call_logs

router = APIRouter()


@router.get("/packages", response_model=List[Package])
async def get_packages():
    """Get all packages for dashboard"""
    return get_all_packages()


@router.get("/call_logs", response_model=List[CallLog])
async def get_call_logs():
    """Get all call logs for dashboard"""
    return get_all_call_logs()