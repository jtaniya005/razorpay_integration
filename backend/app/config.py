import json
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env"),
        extra="ignore",
    )

    razorpay_key_id: str
    razorpay_key_secret: str
    razorpay_webhook_secret: str
    cors_origins: Union[List[str], str] = [
        "http://localhost:5173",
        "https://razorpay-integration-mauve.vercel.app",
    ]
    database_path: str = "orders.db"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            # Comma-separated string support
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v


settings = Settings()
