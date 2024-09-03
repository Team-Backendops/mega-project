from pydantic import BaseModel, Field

class ReviewModel(BaseModel):
    provider_id: str
    rating: float = Field(..., ge=1, le=5)
    comment: str