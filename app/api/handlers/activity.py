from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.models import Activity
from app.api.schemas import ActivityCreate


class ActivityHandler:
    
    @staticmethod
    def create_activity(
        db: Session,
        activity: ActivityCreate
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
