import os
import sqlite3
from typing import List

# Use the project's top-level DB file (same location used by SQLAlchemy URL)
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tender_system.db"))


def table_columns(table: str, db_path: str = None) -> List[str]:
    db_path = db_path or DB_PATH
    if not os.path.exists(db_path):
        return []
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute(f"PRAGMA table_info('{table}')")
        rows = cur.fetchall()
        return [r[1] for r in rows]
    finally:
        conn.close()


def ensure_column(table: str, column_def: str, db_path: str = None) -> bool:
    """Ensure `column_def` (e.g. 'submission_method TEXT') exists on `table`.
    Returns True if added, False if already present.
    """
    db_path = db_path or DB_PATH
    col_name = column_def.split()[0]
    cols = table_columns(table, db_path=db_path)
    if col_name in cols:
        return False
    if not os.path.exists(db_path):
        # Nothing to do if DB doesn't exist yet
        return False
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        # SQLite supports simple ADD COLUMN
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {column_def}")
        conn.commit()
        return True
    finally:
        conn.close()


def ensure_db_schema(db_path: str = None):
    """Inspect common migrations and add any missing columns we know about.

    This is intentionally small and safe (only ADD COLUMN). Use proper
    migrations for larger schema changes.
    """
    db_path = db_path or DB_PATH
    if not os.path.exists(db_path):
        # nothing to fix on a brand new DB; tables will be created by SQLAlchemy
        return

    added = []
    # columns we expect on tenders table
    if ensure_column("tenders", "submission_method TEXT", db_path=db_path):
        added.append("tenders.submission_method")
    
    # Milestone updates
    if ensure_column("milestones", "inspection_status TEXT DEFAULT 'Pending'", db_path=db_path):
        added.append("milestones.inspection_status")
    if ensure_column("milestones", "quality_remarks TEXT", db_path=db_path):
        added.append("milestones.quality_remarks")
    if ensure_column("milestones", "signed_challan_id TEXT", db_path=db_path):
        added.append("milestones.signed_challan_id")

    # Payment updates
    if ensure_column("payments", "commission_amount FLOAT DEFAULT 0", db_path=db_path):
        added.append("payments.commission_amount")

    # User updates
    if ensure_column("users", "profile_image TEXT", db_path=db_path):
        added.append("users.profile_image")
    
    # Tender updates
    if ensure_column("tenders", "image_url TEXT", db_path=db_path):
        added.append("tenders.image_url")
    if ensure_column("tenders", "budget FLOAT DEFAULT 0.0", db_path=db_path):
        added.append("tenders.budget")

    # future-proof: if you add other columns that cause OperationalError,
    # list them here in the same form: (table, "col_name TYPE")

    if added:
        print("Added missing columns:", ", ".join(added))


if __name__ == "__main__":
    ensure_db_schema()
