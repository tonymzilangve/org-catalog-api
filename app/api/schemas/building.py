from pydantic import BaseModel, Field
from typing import List, Optional


class BuildingBase(BaseModel):
    address: str = Field(..., min_length=1, max_length=500)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class Building(BuildingBase):
    id: int
    
    class Config:
        from_attributes = True
