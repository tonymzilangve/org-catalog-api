from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import activity, building, organization
from app.core.config import settings

app = FastAPI(   
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="REST API для справочника Организаций, Зданий, Деятельности",
    docs_url="/docs"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(activity.router, prefix=settings.API_V1_STR)
app.include_router(building.router, prefix=settings.API_V1_STR)
app.include_router(organization.router, prefix=settings.API_V1_STR)
