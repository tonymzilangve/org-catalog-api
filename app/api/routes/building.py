from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.api.schemas import BuildingSchema, BuildingCreate
from app.core.dependencies import verify_api_key
from app.db import get_db
from app.db.models import Building

router = APIRouter(
    prefix="/buildings",
    tags=["buildings"],
    dependencies=[Depends(verify_api_key)]
)


@router.get("/", response_model=List[BuildingSchema])
async def list_buildings(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Building).offset(skip).limit(limit)
    result = await db.execute(stmt)
    buildings = result.scalars().all()
    return buildings


@router.get("/{building_id}", response_model=BuildingSchema)
async def get_building(building_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Building).filter(Building.id == building_id)
    result = await db.execute(stmt)
    db_building = result.scalar_one_or_none()

    if db_building is None:
        raise HTTPException(status_code=404, detail="Building not found")

    return db_building


@router.post("/", response_model=BuildingSchema, status_code=status.HTTP_201_CREATED)
async def create_building(
    building: BuildingCreate,
    db: AsyncSession = Depends(get_db)
):
    db_building = Building(
        address=building.address,
        latitude=building.latitude,
        longitude=building.longitude
    )
    db.add(db_building)
    await db.commit()
    await db.refresh(db_building)

    return db_building
