from fastapi import FastAPI
from app.api.routes import activity, building, organization
from app.core.config import settings

app = FastAPI()

app.include_router(organization.router, prefix=settings.API_V1_STR)
app.include_router(building.router, prefix=settings.API_V1_STR)
