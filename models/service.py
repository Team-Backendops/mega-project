from pydantic import BaseModel

class ReviewModel(BaseModel):
    provider_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: str

class TokenModel(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None