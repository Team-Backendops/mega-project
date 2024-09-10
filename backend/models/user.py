from pydantic import BaseModel, validator
import re

class UserModel(BaseModel):
    username: str
    password: str

class RegisterModel(BaseModel):
    username: str
    password: str
    confirm_password: str

    @validator('password')
    def validate_password(cls, value):
        if not re.match(r'^(?=.*[A-Z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$', value):
            raise ValueError("Password must be at least 8 characters long, include an uppercase letter and a number.")
        return value

class TokenModel(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str
