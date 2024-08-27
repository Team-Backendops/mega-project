from models.service import ServiceProvider
from core.database import service_collection, fs

async def save_image(file):
    """Generic function to save any image to GridFS and return its ID."""
    if file:
        grid_in = fs.open_upload_stream(file.filename, metadata={"contentType": file.content_type})
        await grid_in.write(file.file.read())
        await grid_in.close()
        return str(grid_in._id)
    return None

async def create_service_provider(service_provider: ServiceProvider):
    service_provider_data = service_provider.dict()
    existing_business = await service_collection.find_one({"contact_info": service_provider_data.contact_info})
    if existing_business == None:
        await service_collection.insert_one(service_provider_data)
    return service_provider_data