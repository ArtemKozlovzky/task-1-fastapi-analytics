from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi_pagination import add_pagination

from app.routes import offers, metadata_endpoints
from app.cars_hub import cars_hub_endpoints, api_integration
from app.cars_hub.api_integration import scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    print("Scheduler started")
    yield
    scheduler.shutdown()
    print("Scheduler stopped")


app = FastAPI(lifespan=lifespan)

add_pagination(app)

app.include_router(offers.router)
app.include_router(metadata_endpoints.router)
app.include_router(cars_hub_endpoints.router)
app.include_router(api_integration.router)
