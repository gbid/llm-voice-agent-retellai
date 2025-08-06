import sqlite3
import os
from datetime import datetime, timedelta

DATABASE_PATH = "delivery_service.db"


def get_db_connection():
    """Get database connection with row factory for easier access"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize database with schema and seed data"""
    conn = get_db_connection()

    # Create tables
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS packages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tracking_number TEXT UNIQUE NOT NULL,
            customer_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            postal_code TEXT NOT NULL,
            street TEXT NOT NULL,
            street_number TEXT NOT NULL,
            status TEXT NOT NULL CHECK (status IN ('scheduled', 'out_for_delivery', 'delivered')),
            scheduled_at DATETIME NOT NULL
        );
        
        CREATE TABLE IF NOT EXISTS call_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tracking_number TEXT,
            transcript TEXT,
            completed DATETIME,
            escalated DATETIME,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_package_lookup ON packages (tracking_number, postal_code);
    """)

    # Add seed data
    tomorrow = datetime.now() + timedelta(days=1)
    seed_packages = [
        (
            "PKG001",
            "John Smith",
            "+1234567890",
            "john@example.com",
            "12345",
            "Main St",
            "123",
            "out_for_delivery",
            tomorrow,
        ),
        (
            "PKG002",
            "Jane Doe",
            "+1987654321",
            "jane@example.com",
            "67890",
            "Oak Ave",
            "456",
            "scheduled",
            tomorrow + timedelta(hours=2),
        ),
        (
            "PKG003",
            "Bob Wilson",
            "+1122334455",
            "bob@example.com",
            "54321",
            "Pine Rd",
            "789",
            "delivered",
            datetime.now(),
        ),
    ]

    conn.executemany(
        """
        INSERT OR IGNORE INTO packages 
        (tracking_number, customer_name, phone, email, postal_code, street, street_number, status, scheduled_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        seed_packages,
    )

    conn.commit()
    conn.close()
    print(f"Database initialized at {DATABASE_PATH}")


if __name__ == "__main__":
    init_database()
