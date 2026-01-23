from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import joinedload, Session
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
def list_activities(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    activities = db.query(Activity).filter(
        Activity.parent_id.is_(None)
    ).offset(skip).limit(limit).all()

    return activities


@router.get("/{activity_id}", response_model=ActivitySchema)
def get_activity(activity_id: int, db: Session = Depends(get_db)):
    db_activity = db.query(Activity).options(
        joinedload(Activity.children)
    ).filter(Activity.id == activity_id).first()

    if db_activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")

    return db_activity


@router.post("/", response_model=ActivitySchema, status_code=status.HTTP_201_CREATED)
def create_activity(
    activity: ActivityCreate,
    db: Session = Depends(get_db)
):
    try:
        level = 0
        if activity.parent_id:
            parent = db.query(Activity).filter(Activity.id == activity.parent_id).first()
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
        db.commit()
        db.refresh(db_activity)

        return db_activity

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
