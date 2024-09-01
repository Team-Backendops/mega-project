from pydantic import BaseModel, EmailStr
from typing import List, Optional


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
