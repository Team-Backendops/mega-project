from pydantic import BaseModel, Field
from typing import List, Dict, Any
from models.service import ReviewModel,ServiceProvider,TokenData

reviews_collection = MongoDBClient.get_db()['ratings']


# Get all service providers - requires authentication
@router.get("/service-providers/", response_model=List[ServiceProvider])
async def get_all_service_providers(current_user: dict = Depends(get_current_user)):
    providers = list(ServiceProvider.find())
    if not providers:
        raise HTTPException(status_code=404, detail="No service providers found")
    return providers

# Get service provider by ID - requires authentication
@router.get("/service-providers/{service_provider_id}", response_model=ServiceProvider)
async def get_service_provider(
    service_provider_id: str,
    current_user: dict = Depends(get_current_user)
):
    provider = service_providers_collection.find_one({"_id": ObjectId(service_provider_id)})
    if not provider:
        raise HTTPException(status_code=404, detail="Service provider not found")
    return provider

# Delete service provider by ID - requires authentication
@router.delete("/service-providers/{service_provider_id}")
async def delete_service_provider(
    service_provider_id: str,
    current_user: dict = Depends(get_current_user)
):
    result = service_providers_collection.delete_one({"_id": ObjectId(service_provider_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Service provider not found")
    return {"message": "Service provider deleted successfully"}

# Update service provider by ID - requires authentication
@router.put("/service-providers/{service_provider_id}", response_model=ServiceProvider)
async def update_service_provider(
    service_provider_id: str,
    updated_info: ServiceProvider,
    current_user: dict = Depends(get_current_user)
):
    result = service_providers_collection.update_one(
        {"_id": ObjectId(service_provider_id)},
        {"$set": updated_info.dict(exclude_unset=True)}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Service provider not found")
    
    updated_provider = service_providers_collection.find_one({"_id": ObjectId(service_provider_id)})
    return updated_provider

# Add a review for a service provider - requires authentication
@router.post("/service-providers/{provider_id}/reviews/")
async def add_review(provider_id: str, review: ReviewModel, current_user: dict = Depends(get_current_user)):
    review_data = review.dict()
    review_data["provider_id"] = provider_id
    review_data["user_id"] = current_user["_id"]  # Optionally track the user who submitted the review
    result = await reviews_collection.insert_one(review_data)
    if result.inserted_id:
        return {"message": "Review added successfully", "review_id": str(result.inserted_id)}
    else:
        raise HTTPException(status_code=500, detail="Failed to add review")

# Get reviews for a specific service provider - requires authentication
@router.get("/service-providers/{provider_id}/reviews/", response_model=List[ReviewModel])
async def get_reviews(provider_id: str, current_user: dict = Depends(get_current_user)):
    reviews = list(reviews_collection.find({"provider_id": provider_id}))
    if reviews:
        return reviews
    else:
        raise HTTPException(status_code=404, detail="No reviews found for this service provider")

# Get the average rating for a specific service provider - requires authentication
@router.get("/service-providers/{provider_id}/average-rating/")
async def get_average_rating(provider_id: str, current_user: dict = Depends(get_current_user)):
    pipeline = [
        {"$match": {"provider_id": provider_id}},
        {"$group": {"_id": "$provider_id", "average_rating": {"$avg": "$rating"}}}
    ]
    result = list(reviews_collection.aggregate(pipeline))
    if result:
        return {"provider_id": provider_id, "average_rating": round(result[0]["average_rating"], 2)}
    else:
        raise HTTPException(status_code=404, detail="No reviews found for this service provider")