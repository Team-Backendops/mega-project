from pydantic import BaseModel

class UserModel(BaseModel):
    username: str
    password: str

class RegisterModel(BaseModel):
    username: str
    password: str
    confirm_password: str
