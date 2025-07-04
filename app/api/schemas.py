from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class VMInstance(BaseModel):
    instance_name: str
    provider: str
    region: str
    vcpus: int
    memory_gb: float
    storage_gb: int
    storage_type: str
    hourly_cost: Optional[float] = None
    monthly_cost: Optional[float] = None
    spot_price: Optional[float] = None
    currency: str = "USD"
    instance_family: Optional[str] = None
    network_performance: Optional[str] = None
    last_updated: datetime

class Metrics(BaseModel):
    total_records: int
    last_updated_times: dict[str, Optional[datetime]]