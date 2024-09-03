from fastapi import APIRouter, HTTPException, File, UploadFile
from typing import List
from bson import ObjectId
from models.service import ServiceProvider
from crud.service import create_service_provider, save_image, add_images, get_service_provider, update_service_provider, delete_service_provider
from core.database import service_collection

router = APIRouter()

@router.post("/service-provider/")
async def add_service_provider(service: ServiceProvider):
    try:
        service_provider = {
            "name": service.name,
            "service_offered": service.service_offered,
            "description": service.description,
            "location": service.location.dict(),
            "contact_info": service.contact_info.dict(),
            "operating_hours": service.operating_hours,
            "website": service.website,
            "ratings": service.ratings,
        }
        
        existing_service_provider = await service_collection.find_one({"contact_info": service_provider["contact_info"]})
        if existing_service_provider == None:
            result = await create_service_provider(service_provider)
            return {"message": "Service provider created successfully", "service_id": str(result.inserted_id)}
        return {"message" : "service is already registered"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/service-providers/{service_id}")
async def get_service_provider_details(service_id: str):
    try:
        if not ObjectId.is_valid(service_id):
            raise HTTPException(status_code=400, detail="Invalid service provider ID")

        service_provider = await get_service_provider(service_id)
        if service_provider:
            return service_provider

        raise HTTPException(status_code=404, detail="Service provider not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/service-providers/")
async def get_all_service_providers():
    try:
        service_providers = []
        services = await service_collection.find({}).to_list(length=100)
        for service in services:
            service["_id"] = str(service["_id"])
            service_providers.append(service)
        return service_providers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/service-providers/{service_id}")
async def modify_service_provider(service_id: str, service: ServiceProvider):
    try:
        if not ObjectId.is_valid(service_id):
            raise HTTPException(status_code=400, detail="Invalid service provider ID")

        update_data = {
            "name": service.name,
            "service_offered": service.service_offered,
            "description": service.description,
            "location": service.location.dict(),
            "contact_info": service.contact_info.dict(),
            "operating_hours": service.operating_hours,
            "website": service.website,
            "ratings": service.ratings,
        }

        update_result = await update_service_provider(service_id, update_data)

        if update_result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Service provider not found")

        return {"message": "Service provider updated successfully", "service_id": service_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/service-providers/{service_id}")
async def remove_service_provider(service_id: str):
    try:
        if not ObjectId.is_valid(service_id):
            raise HTTPException(status_code=400, detail="Invalid service provider ID")

        delete_result = await delete_service_provider(service_id)

        if delete_result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Service provider not found")

        return {"message": "Service provider deleted successfully", "service_id": service_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#issues while uploading the image
@router.post("/service-providers/{service_id}/upload-images")
async def service_provider_images(
    service_id: str,
    profile_image: UploadFile = File(None),
    adhaar_card: UploadFile = File(None),
    pan_card: UploadFile = File(None),
    office_images: List[UploadFile] = File(None)
):
    try:
        profile_image_id = await save_image(profile_image) if profile_image else None
        adhaar_card_image_id = await save_image(adhaar_card) if adhaar_card else None
        pan_card_image_id = await save_image(pan_card) if pan_card else None
        office_images_ids = [await save_image(image) for image in office_images] if office_images else []
        
        images = {
                "service_id": service_id,
                "profile_image_id": profile_image_id,
                "adhaar_card_image_id": adhaar_card_image_id,
                "pan_card_image_id": pan_card_image_id,
                "office_images_ids": office_images_ids
            }

        result = await add_images(images)

        return {"message": "Images updated successfully", "service_id": service_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

