from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from app.api.schemas import VMInstance as VMInstanceSchema
from sqlalchemy import select, func, distinct
from app import models
from typing import List, Optional

async def get_instances(
    db: AsyncSession,
    providers: Optional[List[str]] = None,
    regions: Optional[List[str]] = None,
    instance_families: Optional[List[str]] = None,
    storage_types: Optional[List[str]] = None,
    min_vcpus: Optional[int] = None,
    min_memory: Optional[float] = None,
    min_storage: Optional[int] = None,
    instance_name: Optional[str] = None,
    sort_by: str = "hourly_cost",
    sort_order: str = "asc",
    skip: int = 0,
    limit: int = 10
):
    base_query = select(models.VMInstance)

    if providers:
        base_query = base_query.where(models.VMInstance.provider.in_(providers))
    if regions:
        base_query = base_query.where(models.VMInstance.region.in_(regions))
    if instance_families:
        base_query = base_query.where(models.VMInstance.instance_family.in_(instance_families))
    if storage_types:
        base_query = base_query.where(models.VMInstance.storage_type.in_(storage_types))
    if min_vcpus:
        base_query = base_query.where(models.VMInstance.vcpus >= min_vcpus)
    if min_memory:
        base_query = base_query.where(models.VMInstance.memory_gb >= min_memory)
    if min_storage:
        base_query = base_query.where(models.VMInstance.storage_gb >= min_storage)
    if instance_name:
        base_query = base_query.where(models.VMInstance.instance_name.ilike(f'%{instance_name}%'))

    count_query = select(func.count()).select_from(base_query.subquery())
    total = await db.scalar(count_query)

    sort_column = getattr(models.VMInstance, sort_by, models.VMInstance.hourly_cost)
    if sort_order == "desc":
        paginated_query = base_query.order_by(sort_column.desc())
    else:
        paginated_query = base_query.order_by(sort_column.asc())
    
    paginated_query = paginated_query.offset(skip).limit(limit)
    
    result = await db.execute(paginated_query)
    instances = result.scalars().all()
    
    return {"total": total, "instances": instances}

async def get_filter_options(db: AsyncSession):
    """
    Gets unique values for filter dropdowns on the frontend.
    """

    providers_query = select(distinct(models.VMInstance.provider)).order_by(models.VMInstance.provider)
    providers_res = await db.execute(providers_query)
    providers = [p for p in providers_res.scalars().all() if p]

    regions_query = select(distinct(models.VMInstance.region)).order_by(models.VMInstance.region)
    regions_res = await db.execute(regions_query)
    regions = [r for r in regions_res.scalars().all() if r]

    families_query = select(distinct(models.VMInstance.instance_family)).order_by(models.VMInstance.instance_family)
    families_res = await db.execute(families_query)
    instance_families = [f for f in families_res.scalars().all() if f]

    storage_types_query = select(distinct(models.VMInstance.storage_type)).order_by(models.VMInstance.storage_type)
    storage_types_res = await db.execute(storage_types_query)
    storage_types = [s for s in storage_types_res.scalars().all() if s]

    return {
        "providers": providers,
        "regions": regions,
        "instance_families": instance_families,
        "storage_types": storage_types
    }

async def update_provider_data(db: AsyncSession, provider: str, instances_data: List[VMInstanceSchema]):
    """
    Updates the database with a fresh list of instances for a specific provider.
    This function performs an "upsert" (insert or update).
    """
    if not instances_data:
        return 0

    delete_statement = models.VMInstance.__table__.delete().where(
        models.VMInstance.provider == provider
    )
    await db.execute(delete_statement)

    new_instances = [
        instance.model_dump() for instance in instances_data
    ]
    
    insert_statement = insert(models.VMInstance).values(new_instances)
    
    result = await db.execute(insert_statement)
    await db.commit()
    
    return len(new_instances)