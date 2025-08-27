from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from app.database import Base
from datetime import datetime

class VMInstance(Base):
    __tablename__ = "vm_instances"

    id = Column(Integer, primary_key=True, index=True)
    instance_name = Column(String, index=True)
    provider = Column(String, index=True)
    region = Column(String, index=True)
    vcpus = Column(Integer)
    memory_gb = Column(Float)
    storage_gb = Column(Integer)
    storage_type = Column(String)
    hourly_cost = Column(Float, index=True)
    monthly_cost = Column(Float)
    spot_price = Column(Float, nullable=True)
    currency = Column(String, default="USD")
    instance_family = Column(String, index=True)
    network_performance = Column(String, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_provider_region_vcpus_memory', 'provider', 'region', 'vcpus', 'memory_gb'),
    )