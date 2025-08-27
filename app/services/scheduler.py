from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.providers.aws_provider import AWSProvider
# from app.providers.gcp_provider import GCPProvider
from app.data.data_manager import update_provider_data
from app.database import SessionLocal
from app.core.config import settings
import logging

logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.INFO)

scheduler = AsyncIOScheduler()

async def refresh_provider_data(provider_instance):
    """Generic job to refresh data for a given provider."""
    provider_name = provider_instance.get_name()
    print(f"Starting data refresh for {provider_name}...")
    
    async with SessionLocal() as db_session:
        try:
            data = await provider_instance.fetch_data()
            if data:
                count = await update_provider_data(db_session, provider_name, data)
                print(f"Successfully refreshed and saved {count} instances for {provider_name}.")
            else:
                print(f"No data fetched for {provider_name}.")
        except Exception as e:
            print(f"Error refreshing data for {provider_name}: {e}")

def start_scheduler():
    """
    Adds jobs to the scheduler and starts it.
    """
    aws_provider = AWSProvider()
    scheduler.add_job(
        refresh_provider_data,
        'interval',
        hours=settings.REFRESH_INTERVAL_AWS,
        args=[aws_provider],
        id='aws_refresh_job'
    )
    
    # gcp_provider = GCPProvider()
    # scheduler.add_job(refresh_provider_data, 'interval', hours=settings.REFRESH_INTERVAL_GCP, args=[gcp_provider])

    if not scheduler.running:
        scheduler.start()
    print("Scheduler started.")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
    print("Scheduler stopped.")