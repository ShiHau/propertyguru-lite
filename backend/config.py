from pydantic_settings import BaseSettings
from pydantic import ConfigDict, Field
from typing import Literal


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env")

    # Database
    database_url: str = Field(..., validation_alias="DATABASE_URL")

    # App
    app_name: str = Field(..., validation_alias="APP_NAME")
    app_environment: Literal["development", "production"] = Field(
        ..., validation_alias="APP_ENVIRONMENT"
    )

    # Assignment
    assignment_strategy: str = Field(..., validation_alias="ASSIGNMENT_STRATEGY")

    # Auth
    jwt_secret_key: str = Field(..., validation_alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(..., validation_alias="JWT_ALGORITHM")


settings = Settings()
