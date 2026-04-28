from fastapi import FastAPI
from fastapi_pagination import add_pagination
from app.routes import offers, metadata_endpoints
from app.cars_hub import api_integration

app = FastAPI()
add_pagination(app)

app.include_router(offers.router)
app.include_router(metadata_endpoints.router)
app.include_router(api_integration.router)

