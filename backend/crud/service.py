from bson import ObjectId
from models.service import ServiceProvider
from core.database import service_collection, fs, images_collection
from fastapi import UploadFile, HTTPException, File
import logging

async def save_image(image: UploadFile):
    if image:
        try:
            grid_in = fs.open_upload_stream(
                image.filename,
                metadata={"contentType": image.content_type}
            )
            image_content = await image.read()
            await grid_in.write(image_content)
            await grid_in.close()

            return str(grid_in._id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save image to GridFS: {str(e)}")
    return None

async def create_service_provider(service_provider: ServiceProvider):
    result = await service_collection.insert_one(service_provider)
    return result

async def update_service_provider(service_id: str, update_data: dict):
    result = await service_collection.update_one(
        {"_id": ObjectId(service_id)},
        {"$set": update_data}
    )
    return result

async def get_service_provider(service_id: str):
    service_provider = await service_collection.find_one({"_id": ObjectId(service_id)})
    if service_provider:
        service_provider["_id"] = str(service_provider["_id"])
    return service_provider

async def delete_service_provider(service_id: str):
    result = await service_collection.delete_one({"_id": ObjectId(service_id)})
    return result

async def add_images(images: dict):
    result = await images_collection.insert_one(images)
    return result
