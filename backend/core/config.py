from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongo_url: str = "mongodb://localhost:27017"
    database_name: str = "service_listing_db"

    class Config:
        env_file = ".env"

settings = Settings()