from pydantic import BaseModel
class RatingModel(BaseModel):
    username: str
    rating: int
    comment: str