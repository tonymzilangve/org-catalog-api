from pydantic import BaseModel, Field
from typing import List, Optional

from .activity import Activity
from .building import Building


class OrganizationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    phone_numbers: List[str]
    building_id: int


class Organization(OrganizationBase):
    id: int
    activities: List[Activity] = []
    building: Building
    
    class Config:
        from_attributes = True


class OrganizationCreate(OrganizationBase):
    activity_ids: List[int]
