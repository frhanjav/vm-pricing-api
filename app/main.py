from fastapi import FastAPI
from app.api.endpoints import router as api_router
from app.core.config import settings
from app.data.data_manager import data_manager
from app.services.scheduler import scheduler, start_scheduler, stop_scheduler

app = FastAPI(title=settings.APP_NAME)

@app.on_event("startup")
async def startup_event():
    """
    On startup, load initial data and start the background scheduler.
    """
    await data_manager.load_data()
    start_scheduler()

@app.on_event("shutdown")
def shutdown_event():
    stop_scheduler()

app.include_router(api_router, prefix="/api/v1")