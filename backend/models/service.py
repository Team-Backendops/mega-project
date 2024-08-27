from pydantic import BaseModel, EmailStr
from typing import List, Optional

class ServiceProvider(BaseModel):
    name: str
    service_offered: str
    description: str
    location: dict
    contact_info: dict
    operating_hours: Optional[str] = None
    website: Optional[str] = None
    ratings: Optional[float] = None
    profile_image_id: Optional[str] = None
    adhaar_card_image_id: Optional[str] = None
    pan_card_image_id: Optional[str] = None
    office_images_ids: Optional[List[str]] = None

class Location(BaseModel):
    address: str
    city: str
    state: str
    zip_code: str

class ContactInfo(BaseModel):
    phone_number: str
    email: EmailStr
