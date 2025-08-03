from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from .schemas import *
from .crypto_utils import encrypt_b64, decrypt_to_b64
from .db import save_secret, get_secret, init_db
from .audit import init_audit, ensure_indexes, write_audit
import base64, binascii
from pymongo import MongoClient
from .config import MONGO_URI


@asynccontextmanager 
async def lifespan(app: FastAPI):
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    try:
        client.admin.command("ping")
    except Exception as e:
        raise RuntimeError(f"Failed to connect to MongoDB: {e}") from e
    
    db = client["vault"]
    init_db(db["secrets"])
    init_audit(db["audit_logs"])
    ensure_indexes()
    
    app.state.client = client
    try:
        yield
    finally:
        client.close()

app = FastAPI(title="Secret Manager", lifespan=lifespan)

def _validate_b64(s: str) -> None:
    try:
        base64.b64decode(s, validate=True)
    except binascii.Error as e:
        raise HTTPException(status_code=400, detail=f"invalid base64: {e}")
    

@app.post("/vault/secret/create/", response_model=CreateSecretResp)
def create_secret(req: CreateSecretReq, request: Request):
    try:
        _validate_b64(req.secret)
        cipher_b64 = encrypt_b64(req.secret)  # encrypt base64
        sid = save_secret(cipher_b64)  # save ciphertext_b64
        write_audit("create", "success", sid, request)
        return {"secret_id": sid}
    except HTTPException:
        write_audit("create", "bad_request", req=request, error='validation failed')
        raise 
    except Exception as e:
        write_audit("create", "error", req=request, error=str(e))
        raise HTTPException(status_code=500, detail='create failed')
    
    

@app.post("/vault/secret/fetch", response_model=FetchSecretResp)
def fetch_secret(req: FetchSecretReq, request: Request):
    cipher_b64 = get_secret(req.secret_id)
    if cipher_b64 is None:
        write_audit("fetch", "not_found", secret_id=str(req.secret_id), req=request)
        raise HTTPException(status_code=404, detail="Secret not found")
    try:
        plain_b64 = decrypt_to_b64(cipher_b64)
        write_audit("fetch", "success", secret_id=str(req.secret_id) , req=request)
        return {"secret": plain_b64}
    except Exception as e:
        write_audit("fetch", "error", error=str(e), req=request)
        raise HTTPException(status_code=500, detail=str(e))