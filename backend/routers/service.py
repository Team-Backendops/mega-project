from fastapi import APIRouter, HTTPException, File, UploadFile
from fastapi.responses import StreamingResponse
from typing import List
from bson import ObjectId
from gridfs import GridFSBucket
from core.database import fs
from io import BytesIO
from models.service import ServiceProvider
from models.user import UserModel
from crud.service import create_service_provider, save_image, add_images, get_service_provider, update_service_provider, delete_service_provider, get_image_ids
from core.database import service_collection

router = APIRouter()

@router.post("/service-provider/")
async def add_service_provider(service: ServiceProvider,current_user: UserModel = Depends(get_current_user)):
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
            "profile_image_id": service.profile_image_id,
            "adhar_card_image_id": service.adhar_card_image_id,
            "pan_card_image_id": service.pan_card_image_id,
            "office_images_ids": service.office_images_ids
        }
        
        existing_service_provider = await service_collection.find_one({"contact_info": service_provider["contact_info"]})
        if existing_service_provider == None:
            result = await create_service_provider(service_provider)
            return {"message": "Service provider created successfully", "service_id": str(result.inserted_id)}
        return {"message" : "service is already registered"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/service-providers/{service_id}")
async def get_service_provider_details(service_id: str,current_user: UserModel = Depends(get_current_user)):
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
async def get_all_service_providers(current_user: UserModel = Depends(get_current_user)):
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
async def modify_service_provider(service_id: str, service: ServiceProvider,current_user: UserModel = Depends(get_current_user)):
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
            "profile_image_id": service.profile_image_id,
            "adhar_card_image_id": service.adhar_card_image_id,
            "pan_card_image_id": service.pan_card_image_id,
            "office_images_ids": service.office_images_ids
        }

        update_result = await update_service_provider(service_id, update_data)

        if update_result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Service provider not found")

        return {"message": "Service provider updated successfully", "service_id": service_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/service-providers/{service_id}")
async def remove_service_provider(service_id: str,current_user: UserModel = Depends(get_current_user)):
    try:
        if not ObjectId.is_valid(service_id):
            raise HTTPException(status_code=400, detail="Invalid service provider ID")

        delete_result = await delete_service_provider(service_id)

        if delete_result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Service provider not found")

        return {"message": "Service provider deleted successfully", "service_id": service_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/service-providers/{service_id}/upload-images")
async def service_provider_images(
    service_id: str,
    profile_image: UploadFile = File(None),
    adhar_card: UploadFile = File(None),
    pan_card: UploadFile = File(None),
    office_images: List[UploadFile] = File(None),current_user: UserModel = Depends(get_current_user)
):
    try:
        profile_image_id = await save_image(profile_image) if profile_image else None
        adhar_card_image_id = await save_image(adhar_card) if adhar_card else None
        pan_card_image_id = await save_image(pan_card) if pan_card else None
        office_images_ids = [await save_image(image) for image in office_images] if office_images else []
        
        images = {
                "profile_image_id": profile_image_id,
                "adhar_card_image_id": adhar_card_image_id,
                "pan_card_image_id": pan_card_image_id,
                "office_images_ids": office_images_ids
            }

        updated_result = await add_images(service_id, images)
        if updated_result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Service provider not found")

        return {"message": "Images updated successfully", "service_id": service_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/service-providers/image/{image_id}")
async def get_image(image_id: str,current_user: UserModel = Depends(get_current_user)):
    try:
        grid_out = await fs.open_download_stream(ObjectId(image_id))
        if not grid_out:
            raise HTTPException(status_code=404, detail="Image not found")
        
        file_data = await grid_out.read()

        return StreamingResponse(BytesIO(file_data), media_type=grid_out.metadata["contentType"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        

@router.get("/service-providers/{service_id}/images/")
async def list_images(service_id: str,current_user: UserModel = Depends(get_current_user)):
    try:
        image_ids = await get_image_ids(service_id)
        if not image_ids:
            raise HTTPException(status_code=404, detail="Service provider not found or no images available")

        images = {}
        for key, image_id in image_ids.items():
            if image_id:
                images[key] = f"/service-providers/image/{image_id}"

        return images
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/service-providers/{service_id}/image/{image_key}")
async def delete_image(service_id: str, image_key: str,current_user: UserModel = Depends(get_current_user)):
    """
    Delete an image (profile_image, adhar_card, pan_card, or office_image) from a service provider's record
    and remove it from GridFS.
    
    :param image_key: The key indicating which image to delete (profile_image_id, adhar_card_image_id, etc.)
    """
    try:
        if not ObjectId.is_valid(service_id):
            raise HTTPException(status_code=400, detail="Invalid service provider ID")

        service_provider = await service_collection.find_one({"_id": ObjectId(service_id)})
        if not service_provider:
            raise HTTPException(status_code=404, detail="Service provider not found")

        image_id = service_provider.get(image_key)
        if not image_id:
            raise HTTPException(status_code=404, detail=f"No image found for the key: {image_key}")

        try:
            await fs.delete(ObjectId(image_id))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete image from GridFS: {str(e)}")

        update_data = {image_key: None}
        if image_key == "office_images_ids":
            update_data = {image_key: []} 

        update_result = await service_collection.update_one(
            {"_id": ObjectId(service_id)},
            {"$set": update_data}
        )

        if update_result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Service provider not found or image could not be updated")

        return {"message": "Image deleted successfully", "service_id": service_id, "image_key": image_key}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete image: {str(e)}")


@router.delete("/service-providers/{service_id}/office-image/{image_id}")
async def delete_office_image(service_id: str, image_id: str,current_user: UserModel = Depends(get_current_user)):
    try:
        if not ObjectId.is_valid(service_id) or not ObjectId.is_valid(image_id):
            raise HTTPException(status_code=400, detail="Invalid service or image ID")

        service_provider = await service_collection.find_one({"_id": ObjectId(service_id)})
        if not service_provider:
            raise HTTPException(status_code=404, detail="Service provider not found")

        office_images_ids = service_provider.get("office_images_ids", [])
        if image_id not in office_images_ids:
            raise HTTPException(status_code=404, detail="Image not found in office images")

        office_images_ids.remove(image_id)
        
        update_result = await service_collection.update_one(
            {"_id": ObjectId(service_id)},
            {"$set": {"office_images_ids": office_images_ids}}
        )
        
        await fs.delete(ObjectId(image_id))
        
        if update_result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Failed to update service provider")

        return {"message": "Office image deleted successfully", "image_id": image_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
