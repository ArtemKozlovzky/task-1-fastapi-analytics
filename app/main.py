from fastapi import FastAPI
from fastapi_pagination import add_pagination
from app.routes import offers, metadata_endpoints, analytics_endpoints

app = FastAPI()
add_pagination(app)

app.include_router(offers.router)
app.include_router(metadata_endpoints.router)
app.include_router(analytics_endpoints.router)

