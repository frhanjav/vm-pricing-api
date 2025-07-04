from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from app.api.schemas import VMInstance, Metrics
from app.data.data_manager import data_manager
from app.core.config import settings
import pandas as pd

router = APIRouter()

@router.get("/providers", response_model=List[str])
async def get_providers():
    """Lists all supported cloud providers."""
    return settings.SUPPORTED_PROVIDERS

@router.get("/regions", response_model=List[str])
async def get_regions(provider: Optional[str] = None):
    """Lists all available regions, optionally filtered by provider."""
    df = data_manager.get_all_instances()
    if provider:
        if provider not in df['provider'].unique():
            raise HTTPException(status_code=404, detail=f"Provider '{provider}' not found or has no data.")
        regions = df[df['provider'] == provider]['region'].unique().tolist()
    else:
        regions = df['region'].unique().tolist()
    return sorted(regions)

@router.get("/instances", response_model=List[VMInstance])
async def get_instances(
    provider: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    min_vcpus: Optional[int] = Query(None),
    max_vcpus: Optional[int] = Query(None),
    min_memory: Optional[float] = Query(None),
    max_memory: Optional[float] = Query(None),
    max_hourly_cost: Optional[float] = Query(None),
    sort_by: str = Query("hourly_cost", enum=["hourly_cost", "vcpus", "memory_gb"]),
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """Get all instances with powerful filtering and pagination."""
    df = data_manager.get_all_instances()
    
    # Filtering
    if provider:
        df = df[df['provider'] == provider]
    if region:
        df = df[df['region'] == region]
    if min_vcpus:
        df = df[df['vcpus'] >= min_vcpus]
    # ... other filters ...

    # Sorting
    df = df.sort_values(by=sort_by).reset_index(drop=True)

    # Pagination
    paginated_df = df.iloc[offset : offset + limit]

    return paginated_df.to_dict(orient="records")


@router.get("/metrics", response_model=Metrics)
async def get_metrics():
    """Returns basic metrics about the dataset."""
    return {
        "total_records": len(data_manager.get_all_instances()),
        "last_updated_times": data_manager.get_last_update_times()
    }

@router.get("/health")
async def health_check():
    return {"status": "ok"}