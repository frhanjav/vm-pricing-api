import asyncio
import pandas as pd
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models import VMInstance
from app.database import Base
from app.core.config import settings
import numpy as np

engine = create_async_engine(settings.DATABASE_URL)

async def migrate():
    print("Reading data from data/vm_pricing.csv...")
    try:
        df = pd.read_csv("data/vm_pricing.csv")
        df = df.replace({np.nan: None})
    except FileNotFoundError:
        print("Error: data/vm_pricing.csv not found. Run a fetch script first.")
        return

    df = df.where(pd.notnull(df), None)

    async with engine.begin() as conn:
        print("Dropping existing vm_instances table (if it exists)...")
        await conn.run_sync(Base.metadata.drop_all, checkfirst=True)
        print("Creating new vm_instances table...")
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with AsyncSessionLocal() as session:
        print(f"Migrating {len(df)} rows to the database. This may take a moment...")
        
        for _, row in df.iterrows():
            vm_instance = VMInstance(
                instance_name=row.get('instance_name'),
                provider=row.get('provider'),
                region=row.get('region'),
                vcpus=row.get('vcpus'),
                memory_gb=row.get('memory_gb'),
                storage_gb=row.get('storage_gb'),
                storage_type=row.get('storage_type'),
                hourly_cost=row.get('hourly_cost'),
                monthly_cost=row.get('monthly_cost'),
                spot_price=row.get('spot_price'),
                currency=row.get('currency'),
                instance_family=row.get('instance_family'),
                network_performance=row.get('network_performance'),
                last_updated=pd.to_datetime(row.get('last_updated'))
            )
            session.add(vm_instance)
        
        await session.commit()
        print("Migration successful!")

if __name__ == "__main__":
    asyncio.run(migrate())