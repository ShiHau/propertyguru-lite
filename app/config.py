from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Literal


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env")

    # Database
    database_url: str = "sqlite:///./propertyguru.db"

    # App
    app_name: str = "PropertyGuru Lite"
    app_environment: Literal["development", "production"] = "development"

    # Assignment
    assignment_strategy: str = "round_robin_load_aware"


settings = Settings()
