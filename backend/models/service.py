from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional
from abc import ABC, abstractmethod
import re

# class Location(BaseModel):
#     address: str
#     city: str
#     state: str
#     zip_code: str
#     latitude: Optional[str] = None
#     longitude: Optional[str] = None

# class ContactInfo(BaseModel):
#     phone_number: str
#     email: EmailStr

class ServiceProviderRegister(BaseModel):
    name: str
    service_offered: str
    description: str
    address: str
    district: str
    state: str
    zip_code: str
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    phone_number: str
    email: EmailStr
    operating_hours: Optional[str] = None
    website: Optional[str] = None
    ratings: Optional[float] = None
    profile_image_id: Optional[str] = None
    adhar_card_image_id: Optional[str] = None
    office_images_ids: List[str] = None
    password: str
    confirm_password: str

    @validator('password')
    def validate_password(cls, value):
        if not re.match(r'^(?=.*[A-Z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$', value):
            raise ValueError("Password must be at least 8 characters long, include an uppercase letter and a number.")
        return value

class ServiceProvider(BaseModel):
    name: str
    service_offered: str
    description: str
    address: str
    district: str
    state: str
    zip_code: str
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    phone_number: str
    email: EmailStr
    operating_hours: Optional[str] = None
    website: Optional[str] = None
    ratings: Optional[float] = None
    profile_image_id: Optional[str] = None
    adhar_card_image_id: Optional[str] = None
    office_images_ids: List[str] = None

# {
#   "name": "string",
#   "service_offered": "string",
#   "description": "string",
#   "location": {
#     "address": "string",
#     "city": "string",
#     "state": "string",
#     "zip_code": "string",
#     "latitude": "string",
#     "longitude": "string"
#   },
#   "contact_info": {
#     "phone_number": "string",
#     "email": "user@example.com"
#   },
#   "operating_hours": "string",
#   "website": "string",
#   "ratings": 0,
#   "profile_image_id": "string",
#   "adhar_card_image_id": "string",
#   "pan_card_image_id": "string",
#   "office_images_ids": [
#     "string"
#   ],
# }
