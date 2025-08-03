import base64, secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from .config import MASTER_KEY

# 32‑byte key：如果 MASTER_KEY 是 base64，则先解码
key_bytes = base64.b64decode(MASTER_KEY) if len(MASTER_KEY) > 32 else MASTER_KEY.encode()
if len(key_bytes) != 32:
    raise ValueError("MASTER_KEY must be 32 bytes (256‑bit)")

def encrypt_b64(plain_b64: str) -> str:
    nonce = secrets.token_bytes(12)                 # 96‑bit nonce
    aesgcm = AESGCM(key_bytes)
    cipher = aesgcm.encrypt(nonce, base64.b64decode(plain_b64), None)
    return base64.b64encode(nonce + cipher).decode()

def decrypt_to_b64(cipher_b64: str) -> str:
    data  = base64.b64decode(cipher_b64)
    nonce, ct = data[:12], data[12:]
    aesgcm = AESGCM(key_bytes)
    plain = aesgcm.decrypt(nonce, ct, None)
    return base64.b64encode(plain).decode()