from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
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
def list_buildings(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    buildings = db.query(Building).offset(skip).limit(limit).all()
    return buildings


@router.get("/{building_id}", response_model=BuildingSchema)
def get_building(building_id: int, db: Session = Depends(get_db)):
    db_building = db.query(Building).filter(Building.id == building_id).first()

    if db_building is None:
        raise HTTPException(status_code=404, detail="Building not found")

    return db_building


@router.post("/", response_model=BuildingSchema, status_code=status.HTTP_201_CREATED)
def create_building(
    building: BuildingCreate,
    db: Session = Depends(get_db)
):
    db_building = Building(
        address=building.address,
        latitude=building.latitude,
        longitude=building.longitude
    )
    db.add(db_building)
    db.commit()
    db.refresh(db_building)

    return db_building
