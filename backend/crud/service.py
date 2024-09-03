from bson import ObjectId
from models.service import ServiceProvider
from core.database import service_collection, fs, images_collection
from fastapi import UploadFile, HTTPException, File
import logging

# issues while uploading the image
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

# testing is pending
# async def get_image(file_id: str):
#     try:
#         grid_out = fs.open_download_stream(ObjectId(file_id))
#         file_data = await grid_out.read()
#         content_type = grid_out.metadata.get("contentType", "application/octet-stream")

#         return file_data, content_type
#     except Exception as e:
#         print(f"Error retrieving image: {e}")
#         return None, None

# async def update_service_provider_images(service_id: str, update_data: dict):
#     try:
#         return await service_collection.update_one({"service_id": service_id}, {"$set": update_data})
#     except Exception as e:
#         print(f"Error updating images: {e}")
#         return None

# async def delete_images_by_service_id(service_id: str, image_fields: List[str] = None):
#     try:
#         if image_fields:
#             update_data = {field: None for field in image_fields}
#             return await service_collection.update_one({"service_id": service_id}, {"$unset": update_data})
#         else:
#             return await service_collection.delete_one({"service_id": service_id})
#     except Exception as e:
#         print(f"Error deleting images: {e}")
#         return None

