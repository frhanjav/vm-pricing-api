import math
from pydantic import BaseModel, field_serializer
from typing import Optional, List
from datetime import datetime

class VMInstance(BaseModel):
    instance_name: str
    provider: str
    region: str
    vcpus: int
    memory_gb: Optional[float] = None
    storage_gb: int
    storage_type: str
    hourly_cost: Optional[float] = None
    monthly_cost: Optional[float] = None
    spot_price: Optional[float] = None
    currency: str = "USD"
    instance_family: Optional[str] = None
    network_performance: Optional[str] = None
    last_updated: datetime

    @field_serializer('hourly_cost', 'monthly_cost', 'spot_price', 'memory_gb')
    def serialize_floats(self, value: Optional[float]):
        if value is None or math.isnan(value):
            return None
        return value

    model_config = {
        "from_attributes": True
    }

class InstancesResponse(BaseModel):
    total: int
    instances: List[VMInstance]
    
class FilterOptions(BaseModel):
    providers: List[str]
    regions: List[str]
    instance_families: List[str]
    storage_types: List[str]

class Metrics(BaseModel):
    total_records: int
    last_updated_times: dict[str, Optional[datetime]]