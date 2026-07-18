from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings


class FrontendSettings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")

    frontend_app_name: str = Field(
        "PropertyGuru Lite Frontend", validation_alias="FRONTEND_APP_NAME"
    )
    frontend_backend_base_url: str = Field(
        "http://127.0.0.1:8000",
        validation_alias="FRONTEND_BACKEND_BASE_URL",
    )


settings = FrontendSettings()
