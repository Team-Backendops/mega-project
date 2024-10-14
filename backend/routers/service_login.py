from fastapi import APIRouter, HTTPException, status, Depends, Request, File, UploadFile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from core.config import settings
from models.user import TokenModel, TokenData
from core.database import service_collection
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from datetime import datetime, timedelta
from typing import List, Set
from models.service import ServiceProviderRegister
from crud.service import get_service_provider_latlng, save_image, create_service_provider, add_images


router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = settings.SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

bearer_scheme = HTTPBearer(auto_error=True)
blacklist: Set[str] = set()

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt

async def get_current_user(token: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # Check if the token is in the blacklist
    if token.credentials in blacklist:
        raise credentials_exception

    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=["HS256"])
        name: str = payload.get("sub")
        if name is None:
            raise credentials_exception
        token_data = TokenData(name=name)

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except InvalidTokenError:
        raise credentials_exception

    user = await service_collection.find_one({"name": token_data.name})
    if user is None:
        raise credentials_exception
    return user

@router.post("/service-provider/login")
async def post_login(service: ServiceProviderRegister, request: Request):
    try:
        service_in_db = await service_collection.find_one({"name": service.name})
        if not service_in_db:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="service does not exist")

        if not pwd_context.verify(service.password, service_in_db['hashed_password']):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid password")

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": service.name},
            expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/service-provider/logout")
async def logout(token: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    try:
        blacklist.add(token.credentials)
        return {"message": "You have been logged out."}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/service-provider/register")
async def add_service_provider_with_images(
    service: ServiceProviderRegister,
    profile_image: UploadFile = File(None),
    adhar_card: UploadFile = File(None),
    office_images: List[UploadFile] = File(None)
):
    try:
        service_provider = service.dict(exclude_unset=False)

        # Check for existing service provider
        existing_service_provider = await service_collection.find_one({"phone_number": service_provider["phone_number"]})
        if existing_service_provider is not None:
            return {"message": "Service provider is already registered"}

        if service.password != service.confirm_password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")

        hashed_password = pwd_context.hash(service.password)
        service_provider["password"] = hashed_password

        # Create new service provider
        result = await create_service_provider(service_provider)
        service_id = str(result.inserted_id)

        # Update location with latitude and longitude
        latitude, longitude = get_service_provider_latlng(service_id)
        await service_collection.update_one(
            {"_id": ObjectId(service_id)},
            {"$set": {
                "latitude": latitude,
                "longitude": longitude
            }}
        )

        # Handle image uploads
        profile_image_id = await save_image(profile_image) if profile_image else None
        adhar_card_image_id = await save_image(adhar_card) if adhar_card else None
        office_images_ids = [await save_image(image) for image in office_images] if office_images else []

        # Prepare the images dictionary
        images = {
            "profile_image_id": profile_image_id,
            "adhar_card_image_id": adhar_card_image_id,
            "office_images_ids": office_images_ids
        }

        # Update service provider with image IDs
        updated_result = await add_images(service_id, images)
        if updated_result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Service provider not found")

        return {"message": "Service provider registration successful", "service_id": service_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))