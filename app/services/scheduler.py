from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.providers.aws_provider import AWSProvider
# from app.providers.gcp_provider import GCPProvider # Import other providers
from app.data.data_manager import data_manager
from app.core.config import settings
import logging

# Configure logging
logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.INFO)

scheduler = AsyncIOScheduler()

async def refresh_provider_data(provider_instance):
    """Generic job to refresh data for a given provider."""
    provider_name = provider_instance.get_name()
    print(f"Starting data refresh for {provider_name}...")
    try:
        data = await provider_instance.fetch_data()
        await data_manager.update_provider_data(provider_name, data)
        print(f"Successfully refreshed data for {provider_name}. Found {len(data)} instances.")
    except Exception as e:
        print(f"Error refreshing data for {provider_name}: {e}")

def start_scheduler():
    """
    Adds jobs to the scheduler and starts it.
    """
    # Add a job for each provider based on config
    aws_provider = AWSProvider()
    scheduler.add_job(
        refresh_provider_data,
        'interval',
        hours=settings.REFRESH_INTERVAL_AWS,
        args=[aws_provider],
        id='aws_refresh_job'
    )
    
    # Example for another provider
    # gcp_provider = GCPProvider()
    # scheduler.add_job(refresh_provider_data, 'interval', hours=settings.REFRESH_INTERVAL_GCP, args=[gcp_provider])

    if not scheduler.running:
        scheduler.start()
    print("Scheduler started.")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
    print("Scheduler stopped.")