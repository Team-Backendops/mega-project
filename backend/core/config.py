from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongo_url: str = "mongodb://localhost:27017"
    database_name: str = "service_listing_db"
    SECRET_KEY: str= "my_secret_key_1234567890"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    map_token : str = "pk.eyJ1IjoicHJhdGhrdW1iaGFyIiwiYSI6ImNtMHpldDB1YzA0dHEyaXF0eXQwZWZlZ2gifQ.VczNUn3co1MuTQJAr9K0uw"
    class Config:
        env_file = ".env"

settings = Settings()
