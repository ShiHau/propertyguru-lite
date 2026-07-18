from pydantic_settings import BaseSettings
from pydantic import ConfigDict, Field
from typing import Literal


class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Database
    database_url: str = Field(..., validation_alias="DATABASE_URL")

    # Redis (Added these fields with fallback defaults)
    redis_host: str = Field("localhost", validation_alias="REDIS_HOST")
    redis_port: int = Field(6379, validation_alias="REDIS_PORT")
    redis_db: int = Field(0, validation_alias="REDIS_DB")

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
