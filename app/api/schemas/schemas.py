from pydantic import BaseModel, Field
from typing import List, Optional


class ActivityBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    parent_id: int | None


class BuildingBase(BaseModel):
    address: str = Field(..., min_length=1, max_length=500)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class OrganizationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    phone_numbers: List[str]
    building_id: int
