from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "Cloud Pricing API"
    LOG_LEVEL: str = "INFO"

    DATABASE_URL: str

    CORS_ORIGINS: List[str] = ["http://localhost:5173"]

    SUPPORTED_PROVIDERS: List[str] = ["AWS", "GCP", "Azure", "DigitalOcean", "Linode", "Vultr", "PhoenixNAP", "Equinix Metal", "Hetzner Cloud", "OVHcloud", "Scaleway"]
    DATA_FILE_PATH: str = "data/vm_pricing.csv"
    
    REFRESH_INTERVAL_AWS: int = 12
    REFRESH_INTERVAL_GCP: int = 12

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()