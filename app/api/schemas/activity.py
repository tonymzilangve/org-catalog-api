from pydantic import BaseModel, Field
from typing import List, Optional


class ActivityBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    parent_id: int | None = None


class ActivitySimpleSchema(ActivityBase):
    id: int
    name: str
    
    class Config:
        from_attributes = True


class Activity(ActivitySimpleSchema):
    parent_id: Optional[int] = None
    level: int
    children: List['Activity'] = []


class ActivityCreate(ActivityBase):
    pass
