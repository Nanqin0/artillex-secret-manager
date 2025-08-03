import os
import datetime
from typing import Optional, Dict, Any
from pymongo.collection import Collection
from pymongo import ASCENDING
from fastapi import Request

AUDIT_ENABLED = os.getenv("AUDIT_ENABLED", "true").lower() == "true"
AUDIT_TTL_DAYS = int(os.getenv("AUDIT_TTL_DAYS", "0"))

_audit_col: Optional[Collection] = None

def init_audit(col: Collection):
    global _audit_col
    _audit_col = col

def ensure_indexes() -> None:
    assert _audit_col is not None, "Audit collection not initialized"
    _audit_col.create_index([("ts", ASCENDING)])
    if AUDIT_TTL_DAYS > 0:
        _audit_col.create_index("ts", expireAfterSeconds=AUDIT_TTL_DAYS * 24 * 3600)

def _client_ip(req: Optional[Request]) -> Optional[str]:
    if not req:
        return None
    xff = req.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    return req.headers.get("x-real-ip") or (req.client.host if req.client else None)

def write_audit(
    action: str,                      # "create" / "fetch"
    status: str,                      # "success" / "error" / "not_found" / "bad_request"
    secret_id: Optional[str] = None,
    req: Optional[Request] = None,
    error: Optional[str] = None,      
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    if not AUDIT_ENABLED:
        return
    assert _audit_col is not None, "Audit collection not initialized"
    doc = {
        "ts": datetime.datetime.utcnow(),
        "action": action,
        "status": status,
        "secret_id": secret_id,
        "ip": _client_ip(req),
        "ua": req.headers.get("user-agent") if req else None,
    }
    if error:
        doc["error"] = str(error)[:300]  
    if extra:
        doc["extra"] = extra
    _audit_col.insert_one(doc)
