from pydantic_settings import BaseSettings
from pydantic import ConfigDict, Field, computed_field
from typing import Literal


class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Individual Database Variables
    postgres_user: str = Field("app_user", validation_alias="POSTGRES_USER")
    postgres_password: str = Field(
        "secure_local_password", validation_alias="POSTGRES_PASSWORD"
    )
    postgres_db: str = Field("app_db", validation_alias="POSTGRES_DB")
    postgres_host: str = Field("localhost", validation_alias="POSTGRES_HOST")
    postgres_port: int = Field(5432, validation_alias="POSTGRES_PORT")

    # This dynamically builds the URL string based on the active host variable
    @computed_field
    def database_url(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    # Redis Configuration
    redis_host: str = Field("localhost", validation_alias="REDIS_HOST")
    redis_port: int = Field(6379, validation_alias="REDIS_PORT")
    redis_db: int = Field(0, validation_alias="REDIS_DB")

    # App Settings
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
