from pydantic import BaseModel, EmailStr
from typing import List, Optional
from abc import ABC, abstractmethod

class Location(BaseModel):
    address: str
    city: str
    state: str
    zip_code: str

class ContactInfo(BaseModel):
    phone_number: str
    email: EmailStr

class ServiceProvider(BaseModel):
    name: str
    service_offered: str
    description: str
    location: Location
    contact_info: ContactInfo
    operating_hours: Optional[str] = None
    website: Optional[str] = None
    ratings: Optional[float] = None
    profile_image_id: Optional[str] = None
    adhar_card_image_id: Optional[str] = None
    pan_card_image_id: Optional[str] = None
    office_images_ids: List[str] = None
