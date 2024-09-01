from fastapi import APIRouter, HTTPException, status
from fastapi import BackgroundTasks
from fastapi.middleware.sessions import SessionMiddleware
from passlib.context import CryptContext
from core.config import settings
from models.user import UserModel, RegisterModel ,RatingModel 
from core.database import MongoDBClient  # Import MongoDBClient class

router = APIRouter()

# Initialize password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Access collections from MongoDBClient
users_collection = MongoDBClient.get_db()['users']
ratings_collection = MongoDBClient.get_db()['ratings']


SECRET_KEY = secrets.token_hex(16)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY, max_age=1800)  # 1800 seconds = 30 minutes

async def expire_sessions():
    # Expire sessions that have been inactive for more than 30 minutes
    await SessionMiddleware.expire_sessions()

background_tasks = BackgroundTasks()
background_tasks.add_task(expire_sessions, interval=600)

@router.post("/login")
async def post_login(user: UserModel, request: Request):
    try:
        user_in_db = await users_collection.find_one({"username": user.username})
        if not user_in_db:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")

        if not pwd_context.verify(user.password, user_in_db['hashed_password']):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid password")

        request.session["user_id"] = str(user_in_db["_id"])
        # If login is successful
        return {"message": "Login successful", "user_id": str(user_in_db["_id"])}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/logout")
async def logout(request: Request):
    try:
        request.session.clear() 
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
