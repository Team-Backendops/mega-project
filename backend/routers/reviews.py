from fastapi import APIRouter, HTTPException
from bson import ObjectId
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from models.reviews import ReviewModel
from core.database import user_reviews

router = APIRouter()

@router.post("/service-providers/{provider_id}/reviews/")
async def add_review(provider_id: str, review: ReviewModel):
    try:
        review_data = review.dict()
        review_data["provider_id"] = provider_id
        result = await user_reviews.insert_one(review_data)
        if result.inserted_id:
            return {"message": "Review added successfully", "review_id": str(result.inserted_id)}
        else:
            raise HTTPException(status_code=500, detail=f"Failed to add review: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add review: {str(e)}")

@router.get("/service-providers/{provider_id}/reviews/", response_model=List[ReviewModel])
async def get_reviews(provider_id: str):
    try:
        reviews = await user_reviews.find({"provider_id": provider_id}).to_list(length=10)
        if reviews:
            return reviews
        else:
            raise HTTPException(status_code=404, detail="No reviews found for this service provider")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get_reviews: {str(e)}")

@router.get("/service-providers/{provider_id}/average-rating/")
async def get_average_rating(provider_id: str):
    pipeline = [
        {"$match": {"provider_id": provider_id}},
        {"$group": {"_id": "$provider_id", "average_rating": {"$avg": "$rating"}}}
    ]
    result = await user_reviews.aggregate(pipeline).to_list(length=10)
    if result:
        return {"provider_id": provider_id, "average_rating": round(result[0]["average_rating"], 2)}
    else:
        raise HTTPException(status_code=404, detail="No reviews found for this service provider")

@router.delete("/service-providers/{review_id}/reviews/")
async def add_review(review_id: str):
    try:
        if not ObjectId.is_valid(review_id):
            raise HTTPException(status_code=400, detail="Invalid review ID")

        result = await user_reviews.delete_one({"_id": ObjectId(review_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Failed to delete provider review")

        return {"message": "review deleted successfully", "review_id": review_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete review: {str(e)}")
