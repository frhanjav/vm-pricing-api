from abc import ABC, abstractmethod
from typing import List
from app.api.schemas import VMInstance

class BaseProvider(ABC):
    def __init__(self, provider_name: str):
        self.provider_name = provider_name

    @abstractmethod
    async def fetch_data(self) -> List[VMInstance]:
        """
        Fetches pricing data from the cloud provider and transforms it
        into the common VMInstance schema.
        """
        pass

    def get_name(self) -> str:
        return self.provider_name