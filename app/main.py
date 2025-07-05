from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.endpoints import router as api_router
from app.core.config import settings
from app.data.data_manager import data_manager
from app.services.scheduler import scheduler, start_scheduler, stop_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    await data_manager.load_data()
    start_scheduler()
    
    yield 
    
    print("Shutting down...")
    stop_scheduler()

app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

app.include_router(api_router, prefix="/api/v1")