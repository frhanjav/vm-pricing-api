from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "Cloud Pricing API"
    LOG_LEVEL: str = "INFO"

    DATABASE_URL: str

    CORS_ORIGINS: List[str] = ["http://localhost:5173"]

    SUPPORTED_PROVIDERS: List[str] = ["AWS", "GCP", "Azure", "DigitalOcean", "Linode", "Vultr", "PhoenixNAP", "Equinix Metal", "Hetzner Cloud", "Hetzner Bare Metal", "OVHcloud", "Scaleway"]
    DATA_FILE_PATH: str = "data/vm_pricing.csv"
    
    REFRESH_INTERVAL_AWS: int = 12
    REFRESH_INTERVAL_GCP: int = 12
    REFRESH_INTERVAL_HETZNER_CLOUD: int = 12
    REFRESH_INTERVAL_HETZNER_BARE_METAL: int = 24

    HETZNER_CLOUD_API_TOKEN: str = ""
    HETZNER_ROBOT_USERNAME: str = ""
    HETZNER_ROBOT_PASSWORD: str = ""
    HETZNER_INCLUDE_SERVER_MARKET: bool = True

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()