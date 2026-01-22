from pydantic import BaseModel, Field
from typing import List, Optional


class ActivityBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    parent_id: int | None


class Activity(ActivityBase):
    id: int
    level: int
    children: List['Activity'] = []
    
    class Config:
        from_attributes = True
