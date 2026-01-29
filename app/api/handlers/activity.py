from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import Activity
from app.api.schemas import ActivityCreate


class ActivityHandler:
    
    @staticmethod
    async def create_activity(
        db: AsyncSession,
        activity: ActivityCreate
    ):
        try:
            level = 0
            if activity.parent_id:
                result = await db.execute(
                    select(Activity).filter(Activity.id == activity.parent_id)
                )
                parent = result.scalar_one_or_none()
                
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

            return db_activity

        except ValueError as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail=str(e))
