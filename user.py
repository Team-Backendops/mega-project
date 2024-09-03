from fastapi import APIRouter, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from core.config import settings
from models.user import UserModel, RegisterModel, TokenModel, TokenData
from core.database import MongoDBClient
import jwt
from datetime import datetime, timedelta

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
users_collection = MongoDBClient.get_db()['users']
SECRET_KEY = settings.SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

bearer_scheme = HTTPBearer(auto_error=True)

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
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except PyJWTError:
        raise credentials_exception

    user = await users_collection.find_one({"username": token_data.username})
    if user is None:
        raise credentials_exception
    return user

@router.post("/login")
async def post_login(user: UserModel, request: Request):
    try:
        user_in_db = await users_collection.find_one({"username": user.username})
        if not user_in_db:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")

        if not pwd_context.verify(user.password, user_in_db['hashed_password']):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid password")

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/logout")
async def logout(request: Request):
    try:
         # Add the token to the blacklist
        blacklist.add(token.credentials)
        return {"message": "You have been logged out."}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/register")
async def post_register(user: RegisterModel):
    try:
        if user.password != user.confirm_password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")

        user_in_db = await users_collection.find_one({"username": user.username})
        if user_in_db:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

        hashed_password = pwd_context.hash(user.password)
        await users_collection.insert_one({
            "username": user.username,
            "hashed_password": hashed_password
        }) 

        return {"message": "Registration successful. Please log in."}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))