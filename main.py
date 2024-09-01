# from motor.motor_asyncio import AsyncIOMotorClient
# from pydantic import Field
# from typing import Optional
# from pymongo.errors import DuplicateKeyError, PyMongoError


# # Connect to MongoDB
# client = AsyncIOMotorClient('mongodb://localhost:27017')
# db = client['business_registrations']
# collection = db['business']


# # Define the Pydantic model
# class BusinessRegistration(BaseModel):
#     name: str
#     owner_name: str 
#     email: str
#     phone: str 
#     address: str 
#     category: str 
#     website: Optional[str]
#     description: Optional[str] 


# # Endpoint to serve the registration page
# @app.get("/register-business")
# async def get_register_business_page(request: Request):
#     try:
#         return templates.TemplateResponse("register.html", {"request": request})
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# # Define the API endpoint to save the data
# @app.post("/register-business")
# async def register_business(business: BusinessRegistration):
#     try:
#         # Check if a business with the given email already exists
#         existing_business = await collection.find_one({"email": business.email})
#         if existing_business:
#             raise HTTPException(status_code=400, detail="A business with this email already exists.")

#         # Insert the business data into the MongoDB collection
#         result = await collection.insert_one(business.dict())
        
#         # Return a success message with the ID of the inserted document
#         return {"message": "Business registered successfully", "business_id": str(result.inserted_id)}

#     except DuplicateKeyError:
#         # Handle the case where the email is already registered
#         raise HTTPException(status_code=400, detail="A business with this email already exists.")
    
#     except PyMongoError as e:
#         # Handle other potential MongoDB-related errors
#         raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
#     except Exception as e:
#         # Handle unexpected errors
#         raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

# Get service provider by ID

from pydantic import BaseModel, Field
from typing import List, Dict, Any
from models.service import ReviewModel,ServiceProvider

reviews_collection = MongoDBClient.get_db()['ratings']


# Get all service providers
@app.get("/service-providers/", response_model=List[ServiceProvider])
async def get_all_service_providers():
    providers = list(ServiceProvider.find())
    if not providers:
        raise HTTPException(status_code=404, detail="No service providers found")
    return providers

@app.get("/service-providers/{service_provider_id}", response_model=ServiceProvider)
async def get_service_provider(service_provider_id: str):
    provider = ServiceProvider.find_one({"_id": ObjectId(service_provider_id)})
    if not provider:
        raise HTTPException(status_code=404, detail="Service provider not found")
    return provider

# Delete service provider by ID
@app.delete("/service-providers/{service_provider_id}")
async def delete_service_provider(service_provider_id: str):
    result = ServiceProvider.delete_one({"_id": ObjectId(service_provider_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Service provider not found")
    return {"message": "Service provider deleted successfully"}

# Update service provider by ID
@app.put("/service-providers/{service_provider_id}", response_model=ServiceProvider)
async def update_service_provider(service_provider_id: str, updated_info: ServiceProvider):
    result = ServiceProvider.update_one(
        {"_id": ObjectId(service_provider_id)},
        {"$set": updated_info.dict()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Service provider not found")
    return ServiceProvider.find_one({"_id": ObjectId(service_provider_id)})

# Add a review for a service provider
@app.post("/service-providers/{provider_id}/reviews/")
async def add_review(provider_id: str, review: ReviewModel):
    review_data = review.dict()
    review_data["provider_id"] = provider_id
    result = reviews_collection.insert_one(review_data)
    if result.inserted_id:
        return {"message": "Review added successfully", "review_id": str(result.inserted_id)}
    else:
        raise HTTPException(status_code=500, detail="Failed to add review")

# Get reviews for a specific service provider
@app.get("/service-providers/{provider_id}/reviews/", response_model=List[ReviewModel])
async def get_reviews(provider_id: str):
    reviews = list(reviews_collection.find({"provider_id": provider_id}))
    if reviews:
        return reviews
    else:
        raise HTTPException(status_code=404, detail="No reviews found for this service provider")

# Route to get the average rating for a specific service provider
@app.get("/service-providers/{provider_id}/average-rating/")
async def get_average_rating(provider_id: str):
    pipeline = [
        {"$match": {"provider_id": provider_id}},
        {"$group": {"_id": "$provider_id", "average_rating": {"$avg": "$rating"}}}
    ]
    result = list(reviews_collection.aggregate(pipeline))
    if result:
        return {"provider_id": provider_id, "average_rating": round(result[0]["average_rating"], 2)}
    else:
        raise HTTPException(status_code=404, detail="No reviews found for this service provider")