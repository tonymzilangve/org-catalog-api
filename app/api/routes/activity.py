from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from typing import List

from app.api.schemas import ActivitySchema, ActivityCreate
from app.core.dependencies import verify_api_key
from app.db import get_db
from app.db.models import Activity

router = APIRouter(
    prefix="/activities",
    tags=["activities"],
    dependencies=[Depends(verify_api_key)]
)


@router.get("/", response_model=List[ActivitySchema])
async def list_activities(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
    ):
    stmt = select(Activity).options(
        joinedload(Activity.children).joinedload(
            Activity.children
        ).joinedload(Activity.children)
    ).filter(
        Activity.parent_id.is_(None)
    ).offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    activities = result.unique().scalars().all()
    
    return activities


@router.get("/{activity_id}", response_model=ActivitySchema)
async def get_activity(activity_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Activity).options(
        joinedload(Activity.children).joinedload(
            Activity.children
        ).joinedload(Activity.children)
    ).filter(Activity.id == activity_id)
    
    result = await db.execute(stmt)
    db_activity = result.unique().scalar_one_or_none()
    
    if db_activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")

    return db_activity


@router.post("/", response_model=ActivitySchema, status_code=status.HTTP_201_CREATED)
async def create_activity(
    activity: ActivityCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        level = 0
        if activity.parent_id:
            parent_stmt = select(Activity).filter(Activity.id == activity.parent_id)
            parent_result = await db.execute(parent_stmt)
            parent = parent_result.scalar_one_or_none()
            
            if parent:
                level = parent.level + 1
                if level >= 3:
                    raise ValueError("Maximum nesting level is 3")

        db_activity = Activity(
            name=activity.name,
            parent_id=activity.parent_id,
            level=level
        )
        db.add(db_activity)
        await db.commit()
        await db.refresh(db_activity)

        await db.refresh(db_activity, attribute_names=["children"])

        return db_activity

    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
