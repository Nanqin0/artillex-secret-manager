import uuid, datetime
from pymongo.collection import Collection
from uuid import UUID
from typing import Union, Optional

_col: Optional[Collection] = None

def init_db(col: Collection):
    global _col
    _col = col

def save_secret(ciphertext_b64: str) -> str:
    assert _col is not None, "Database not initialized"
    sid = str(uuid.uuid4())
    _col.insert_one({
        "_id": sid,
        "ciphertext": ciphertext_b64, 
        "created_at": datetime.datetime.now(datetime.UTC)})
    return sid

def get_secret(sid: Union[str, UUID]) -> Optional[str]:
    assert _col is not None, "Database not initialized"
    if isinstance(sid, UUID):
        sid = str(sid) 
    doc = _col.find_one({"_id": sid}, {"ciphertext": 1})
    return doc["ciphertext"] if doc else None