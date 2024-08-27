# from fastapi import FastAPI, Depends, HTTPException, Request, status
# from fastapi.responses import RedirectResponse
# from fastapi.templating import Jinja2Templates
# from pydantic import BaseModel
# from fastapi.staticfiles import StaticFiles
# from pymongo import MongoClient, errors as pymongo_errors
# from bson.objectid import ObjectId
# import bcrypt
# from starlette.middleware.sessions import SessionMiddleware
# import os
# from dotenv import load_dotenv

# load_dotenv()  # Load environment variables

# app = FastAPI()
# app.mount("/static", StaticFiles(directory="static"), name="static")
# app.add_middleware(SessionMiddleware, secret_key=os.getenv('SECRET_KEY', 'secretKey'), max_age=1800)  # 30 minutes

# templates = Jinja2Templates(directory="templates")
# client = MongoClient("mongodb://127.0.0.1:27017/")
# db = client["mydatabase"]
# users = db["users"]

# class UserModel(BaseModel):
#     username: str
#     password: str

# class RegisterModel(BaseModel):
#     username: str
#     password: str
#     confirm_password: str

# @app.get("/login")
# async def login(request: Request, message: str = None):
#     try:
#         message = request.query_params.get("message", "")
#         return templates.TemplateResponse("login.html", {"request": request, "message": message})
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# @app.post("/login")
# async def post_login(request: Request):
#     try:
#         form = await request.form()
#         username = form.get("username")
#         password = form.get("password")

#         # Fetch the user from the database
#         user = users.find_one({"username": username})
#         if not user:
#             return RedirectResponse(url="/login?message=User does not exist", status_code=status.HTTP_302_FOUND)

#         # Ensure the password from the database is in bytes before comparison
#         stored_hashed_password = user['password']
#         if isinstance(stored_hashed_password, str):
#             stored_hashed_password = stored_hashed_password.encode('utf-8')

#         if not bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password):
#             return RedirectResponse(url="/login?message=Invalid password", status_code=status.HTTP_302_FOUND)

#         # Login successful
#         request.session['user'] = username
#         return RedirectResponse(url="/protected?message=Login successful", status_code=status.HTTP_302_FOUND)
#     except pymongo_errors.PyMongoError as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error: " + str(e))
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# @app.get("/protected")
# async def protected(request: Request, message: str = None):
#     try:
#         if 'user' not in request.session:
#             message = request.query_params.get("message", "")
#             return RedirectResponse(url="/login?message=Session expired. Please log in again.", status_code=status.HTTP_302_FOUND)

#         return templates.TemplateResponse("protected.html", {"request": request, "user": request.session['user'], "message": message})
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# @app.get("/logout")
# async def logout(request: Request):
#     try:
#         request.session.clear()
#         return RedirectResponse(url="/login?message=You have been logged out.", status_code=status.HTTP_302_FOUND)
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# @app.get("/register")
# async def register(request: Request, message: str = None):
#     try:
#         message = request.query_params.get("message", "")
#         return templates.TemplateResponse("register.html", {"request": request, "message": message})
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# @app.post("/register")
# async def post_register(request: Request):
#     try:
#         form = await request.form()
#         username = form.get("username")
#         password = form.get("password")
#         confirm_password = form.get("confirm_password")

#         if password != confirm_password:
#             return RedirectResponse(url="/register?message=Passwords do not match", status_code=status.HTTP_302_FOUND)

#         if not username or not password or not confirm_password:
#             return RedirectResponse(url="/register?message=Please fill in all fields", status_code=status.HTTP_302_FOUND)

#         hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
#         users.insert_one({"username": username, "password": hashed_password})

#         return RedirectResponse(url="/login?message=Registration successful. Please log in.", status_code=status.HTTP_302_FOUND)
#     except pymongo_errors.PyMongoError as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error: " + str(e))
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8000)


from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import Field
from typing import Optional
from pymongo.errors import DuplicateKeyError, PyMongoError


# Connect to MongoDB
client = AsyncIOMotorClient('mongodb://localhost:27017')
db = client['business_registrations']
collection = db['business']


# Define the Pydantic model
class BusinessRegistration(BaseModel):
    name: str
    owner_name: str 
    email: str
    phone: str 
    address: str 
    category: str 
    website: Optional[str]
    description: Optional[str] 


# Endpoint to serve the registration page
@app.get("/register-business")
async def get_register_business_page(request: Request):
    try:
        return templates.TemplateResponse("register.html", {"request": request})
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# Define the API endpoint to save the data
@app.post("/register-business")
async def register_business(business: BusinessRegistration):
    try:
        # Check if a business with the given email already exists
        existing_business = await collection.find_one({"email": business.email})
        if existing_business:
            raise HTTPException(status_code=400, detail="A business with this email already exists.")

        # Insert the business data into the MongoDB collection
        result = await collection.insert_one(business.dict())
        
        # Return a success message with the ID of the inserted document
        return {"message": "Business registered successfully", "business_id": str(result.inserted_id)}

    except DuplicateKeyError:
        # Handle the case where the email is already registered
        raise HTTPException(status_code=400, detail="A business with this email already exists.")
    
    except PyMongoError as e:
        # Handle other potential MongoDB-related errors
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

