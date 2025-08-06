from datetime import datetime
from typing import Optional
from database import get_db_connection
from models import Package, CallLog


def get_package_by_tracking_and_postal(tracking_number: str, postal_code: str) -> Optional[Package]:
    """Get package by tracking number and postal code"""
    conn = get_db_connection()
    try:
        cursor = conn.execute("""
            SELECT id, tracking_number, customer_name, phone, email, postal_code, 
                   street, street_number, status, scheduled_at
            FROM packages 
            WHERE tracking_number = ? AND postal_code = ?
        """, (tracking_number, postal_code))
        
        row = cursor.fetchone()
        if row:
            return Package(
                id=row['id'],
                tracking_number=row['tracking_number'],
                customer_name=row['customer_name'],
                phone=row['phone'],
                email=row['email'],
                postal_code=row['postal_code'],
                street=row['street'],
                street_number=row['street_number'],
                status=row['status'],
                scheduled_at=datetime.fromisoformat(row['scheduled_at'])
            )
        return None
    finally:
        conn.close()


def update_package_schedule(tracking_number: str, new_time: datetime) -> bool:
    """Update package scheduled_at time"""
    conn = get_db_connection()
    try:
        cursor = conn.execute("""
            UPDATE packages 
            SET scheduled_at = ?
            WHERE tracking_number = ?
        """, (new_time.isoformat(), tracking_number))
        
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()



def create_call_log(tracking_number: Optional[str] = None) -> int:
    """Create new call log entry, return ID"""
    conn = get_db_connection()
    try:
        cursor = conn.execute("""
            INSERT INTO call_logs (tracking_number, created_at)
            VALUES (?, ?)
        """, (tracking_number, datetime.now().isoformat()))
        
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def update_call_log_completed(log_id: int, transcript: str) -> bool:
    """Update call log with transcript and completion time"""
    conn = get_db_connection()
    try:
        cursor = conn.execute("""
            UPDATE call_logs 
            SET transcript = ?, completed = ?
            WHERE id = ?
        """, (transcript, datetime.now().isoformat(), log_id))
        
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def update_call_log_escalated(log_id: int) -> bool:
    """Mark call log as escalated"""
    conn = get_db_connection()
    try:
        cursor = conn.execute("""
            UPDATE call_logs 
            SET escalated = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), log_id))
        
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()
