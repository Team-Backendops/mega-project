from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from typing import List

from models.service import ServiceProvider
from crud.service import create_service_provider, save_image

router = APIRouter()

async def upload_image(file: UploadFile):
    return await save_image(file)

@router.post("/service-providers/")
async def add_service_provider(
    name: str = Form(...),
    service_offered: str = Form(None),
    description: str = Form(...),
    location: str = Form(...),
    contact_info: str = Form(...),
    operating_hours: str = Form(None),
    website: str = Form(None),
    ratings: float = Form(None),
    profile_image: UploadFile = File(None),
    adhaar_card: UploadFile = File(None),
    pan_card: UploadFile = File(None),
    office_images: List[UploadFile] = File(None)
):
    try:
        profile_image_id = await upload_image(profile_image) if profile_image else None
        adhaar_card_image_id = await upload_image(adhaar_card) if adhaar_card else None
        pan_card_image_id = await upload_image(pan_card) if pan_card else None
        office_images_ids = await upload_images(office_images) if office_images else []

        service_provider = ServiceProvider(
            name=name,
            service_offered=service_offered,
            description=description,  
            location=eval(location),
            contact_info=eval(contact_info),
            operating_hours=operating_hours,
            website=website,
            ratings=ratings,
            profile_image_id=profile_image_id,
            adhaar_card_image_id=adhaar_card_image_id,
            pan_card_image_id=pan_card_image_id,
            office_images_ids=office_images_ids
        )

        result = await create_service_provider(service_provider)
        return {"message": "Service provider created successfully", "service_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
