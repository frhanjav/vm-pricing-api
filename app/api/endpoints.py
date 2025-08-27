from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, distinct, func
from typing import List, Optional

from app.data import data_manager
from app.database import get_db
from app.api import schemas
from app import models

router = APIRouter()

@router.get("/filters/options", response_model=schemas.FilterOptions)
async def get_filters(db: AsyncSession = Depends(get_db)):
    """Provides unique values for all filter dropdowns."""
    return await data_manager.get_filter_options(db)

@router.get("/instances", response_model=schemas.InstancesResponse)
async def read_instances(
    providers: Optional[List[str]] = Query(None),
    regions: Optional[List[str]] = Query(None),
    min_vcpus: Optional[int] = Query(None),
    min_memory: Optional[float] = Query(None),
    instance_families: Optional[List[str]] = Query(None),
    storage_types: Optional[List[str]] = Query(None),
    min_storage: Optional[int] = Query(None),
    instance_name: Optional[str] = Query(None),

    sort_by: str = Query("hourly_cost", enum=["hourly_cost", "vcpus", "memory_gb"]),
    sort_order: str = Query("asc", enum=["asc", "desc"]),
    offset: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Get instances from the database with powerful filtering, sorting, and pagination.
    """
    result = await data_manager.get_instances(
        db=db,
        providers=providers,
        regions=regions,
        instance_families=instance_families,
        storage_types=storage_types,
        min_vcpus=min_vcpus,
        min_memory=min_memory,
        min_storage=min_storage,
        instance_name=instance_name,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=offset,
        limit=limit
    )
    return result

@router.get("/providers", response_model=List[str])
async def get_providers(db: AsyncSession = Depends(get_db)):
    """Lists all supported providers that have data in the database."""
    query = select(distinct(models.VMInstance.provider)).order_by(models.VMInstance.provider)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/regions", response_model=List[str])
async def get_regions(provider: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    """Lists all available regions, optionally filtered by provider."""
    query = select(distinct(models.VMInstance.region))
    if provider:
        query = query.where(models.VMInstance.provider == provider)
    query = query.order_by(models.VMInstance.region)
    
    result = await db.execute(query)
    regions = result.scalars().all()
    if not regions and provider:
         raise HTTPException(status_code=404, detail=f"Provider '{provider}' not found or has no data.")
    return regions

@router.get("/metrics", response_model=schemas.Metrics)
async def get_metrics(db: AsyncSession = Depends(get_db)):
    """Returns basic metrics about the dataset from the database."""
    
    count_query = select(func.count()).select_from(models.VMInstance)
    total_records = await db.scalar(count_query)

    last_updated_query = (
        select(
            models.VMInstance.provider,
            func.max(models.VMInstance.last_updated).label("last_update")
        )
        .group_by(models.VMInstance.provider)
    )
    
    last_updated_results = await db.execute(last_updated_query)
    last_updated_times = {row.provider: row.last_update for row in last_updated_results}

    return {
        "total_records": total_records,
        "last_updated_times": last_updated_times
    }

@router.get("/health")
async def health_check():
    return {"status": "ok"}