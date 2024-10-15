from bson import ObjectId
from models.service import ServiceProvider
from core.database import service_collection, fs
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

async def add_images(service_id: str, images: dict):
    result = await service_collection.update_one(
        {"_id": ObjectId(service_id)},
        {"$set": images}
        )
    return result

async def get_image_ids(service_id: str):
    try:
        document = await service_collection.find_one({"_id": ObjectId(service_id)})
        if not document:
            return None
        return {
            "profile_image_id": document.get("profile_image_id"),
            "adhaar_card_image_id": document.get("adhaar_card_image_id"),
            "office_images_ids": document.get("office_images_ids", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def get_service_provider_latlng(service_id: str):
    try:
        service_provider = await get_service_provider(service_id)
        if not service_provider:
            raise HTTPException(status_code=404, detail="Service provider not found")

        location = service_provider.get("location")
        if not location:
            raise HTTPException(status_code=400, detail="Location data is missing")

        # Google Maps API Key
        google_maps_api_key = settings.google_maps_api_key

        # Geocoding request to Google Maps API
        geocode_url = (
            f"https://maps.googleapis.com/maps/api/geocode/json"
            f"?address={location['address']}, {location['city']}, {location['state']} {location['zip_code']}"
            f"&key={google_maps_api_key}"
        )

        response = requests.get(geocode_url)
        geocode_data = response.json()

        # Debugging: Print geocode response
        logging.info(f"Geocode data: {geocode_data}")

        if not geocode_data['results']:
            raise HTTPException(status_code=404, detail="Unable to geocode address")

        # Extracting latitude and longitude from the geocode data
        location_data = geocode_data['results'][0]['geometry']['location']
        latitude = location_data['lat']
        longitude = location_data['lng']

        return latitude, longitude

    except Exception as e:
        logging.error(f"Error in get_service_provider_latlng: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
