from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional

from .activity import ActivitySimpleSchema
from .building import Building


class OrganizationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    phone_numbers: List[str]
    building_id: int


class Organization(OrganizationBase):
    id: int
    activities: List[ActivitySimpleSchema] = []
    building: Building
    
    class Config:
        from_attributes = True


class OrganizationCreate(OrganizationBase):
    activity_ids: List[int]


class SearchType(str, Enum):
    radius = "radius"
    rectangle = "rectangle"


class GeoSearch(BaseModel):
    latitude: float
    longitude: float
    radius_km: Optional[float] = None 
    north: Optional[float] = None
    south: Optional[float] = None
    east: Optional[float] = None
    west: Optional[float] = None
    search_type: SearchType
