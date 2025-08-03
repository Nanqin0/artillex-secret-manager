from pydantic import BaseModel, Field
from uuid import UUID

class CreateSecretReq(BaseModel):
    secret: str = Field(..., description="Base64 plaintext")

class CreateSecretResp(BaseModel):
    secret_id: UUID

class FetchSecretReq(BaseModel):
    secret_id: UUID

class FetchSecretResp(BaseModel):
    secret: str