"""
Supabase Client — Database connection and CRUD operations.
Manages PostgreSQL 15 via Supabase for all QuantumSight data storage.
Falls back to in-memory store when Supabase credentials are not configured.
"""
import os
import logging
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

_supabase_client = None
_USE_MEMORY_STORE = False
_INITIALIZED = False

# In-memory store for demo mode (no Supabase configured)
_memory_store: Dict[str, List[Dict]] = {
    "assets": [],
    "scan_results": [],
    "cbom_entries": [],
    "pqc_scores": [],
    "hndl_risk": [],
    "cyber_ratings": [],
    "migration_plans": [],
    "certificates": [],
    "audit_logs": [],
    "scan_sessions": [],
}


def get_client():
    """Get or initialize Supabase client. Only initializes once."""
    global _supabase_client, _USE_MEMORY_STORE, _INITIALIZED

    if _INITIALIZED:
        return _supabase_client

    _INITIALIZED = True
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_KEY", "")

    if not url or not key or url == "your_supabase_url":
        logger.info("Supabase not configured — running in demo/memory mode")
        _USE_MEMORY_STORE = True
        return None

    try:
        from supabase import create_client
        _supabase_client = create_client(url, key)
        logger.info("Supabase client initialized successfully")
        return _supabase_client
    except Exception as e:
        logger.error(f"Supabase initialization failed: {e} — falling back to memory store")
        _USE_MEMORY_STORE = True
        return None


def is_memory_mode() -> bool:
    get_client()
    return _USE_MEMORY_STORE


# ── Generic CRUD helpers ─────────────────────────────────────────────────────

def upsert_record(table: str, record: dict) -> Optional[dict]:
    """Insert or update a record in the given table."""
    if "id" not in record or not record["id"]:
        record["id"] = str(uuid.uuid4())

    client = get_client()

    if _USE_MEMORY_STORE or client is None:
        # Memory store upsert
        records = _memory_store.get(table, [])
        for i, r in enumerate(records):
            if r.get("id") == record.get("id"):
                records[i] = record
                return record
        records.append(record)
        _memory_store[table] = records
        return record

    try:
        result = client.table(table).upsert(record).execute()
        return result.data[0] if result.data else record
    except Exception as e:
        logger.error(f"DB upsert error ({table}): {e}")
        return record


def insert_record(table: str, record: dict) -> Optional[dict]:
    """Insert a new record."""
    if "id" not in record or not record["id"]:
        record["id"] = str(uuid.uuid4())

    client = get_client()

    if _USE_MEMORY_STORE or client is None:
        records = _memory_store.get(table, [])
        records.append(record)
        _memory_store[table] = records
        return record

    try:
        result = client.table(table).insert(record).execute()
        return result.data[0] if result.data else record
    except Exception as e:
        logger.error(f"DB insert error ({table}): {e}")
        return record


def get_records(table: str, filters: dict = None, limit: int = 500) -> List[dict]:
    """Retrieve records from a table with optional filters."""
    client = get_client()

    if _USE_MEMORY_STORE or client is None:
        records = _memory_store.get(table, [])
        if filters:
            for k, v in filters.items():
                records = [r for r in records if r.get(k) == v]
        return records[:limit]

    try:
        query = client.table(table).select("*")
        if filters:
            for k, v in filters.items():
                query = query.eq(k, v)
        result = query.limit(limit).execute()
        return result.data or []
    except Exception as e:
        logger.error(f"DB query error ({table}): {e}")
        return []


def get_record_by_id(table: str, record_id: str) -> Optional[dict]:
    """Retrieve a single record by ID."""
    client = get_client()

    if _USE_MEMORY_STORE or client is None:
        records = _memory_store.get(table, [])
        for r in records:
            if r.get("id") == record_id:
                return r
        return None

    try:
        result = client.table(table).select("*").eq("id", record_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"DB get_by_id error ({table}): {e}")
        return None


def log_audit_event(
    action: str,
    target: str = "",
    outcome: str = "success",
    user_id: str = "system",
    metadata: dict = None
) -> None:
    """Log an audit event to the audit_logs table."""
    record = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "action": action,
        "target_domain": target,
        "outcome": outcome,
        "metadata": metadata or {},
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    insert_record("audit_logs", record)


def get_memory_store() -> Dict[str, List]:
    """Return the full in-memory store (for debugging)."""
    return _memory_store


def clear_memory_store() -> None:
    """Clear all in-memory data (useful for testing)."""
    global _memory_store
    for key in _memory_store:
        _memory_store[key] = []
