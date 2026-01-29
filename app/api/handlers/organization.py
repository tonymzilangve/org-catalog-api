from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.api.schemas import GeoSearch, OrganizationCreate, SearchType
from app.db.models import Activity, Building, Organization

from .building import BuildingHandler


class OrganizationHandler:

    @staticmethod
    async def create_organization(
        db: AsyncSession,
        organization: OrganizationCreate,
    ):
        try:
            building_result = await db.execute(
                select(Building).filter(Building.id == organization.building_id)
            )
            building = building_result.scalar_one_or_none()
            
            if not building:
                raise ValueError("Building not found")

            activities_result = await db.execute(
                select(Activity).filter(Activity.id.in_(organization.activity_ids))
            )
            activities = activities_result.scalars().all()
            
            if len(activities) != len(organization.activity_ids):
                raise ValueError("One or more activities not found")

            db_organization = Organization(
                name=organization.name,
                phone_numbers=organization.phone_numbers,
                building_id=organization.building_id,
                activities=activities
            )
            
            db.add(db_organization)
            await db.commit()
            await db.refresh(db_organization)
            
            return db_organization

        except ValueError as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    async def search_organizations_by_geo(db: AsyncSession, geo_search: GeoSearch):
        if geo_search.search_type == SearchType.radius:
            buildings = await BuildingHandler.search_buildings_in_radius(
                db, geo_search.latitude, geo_search.longitude, geo_search.radius_km
            )
        else:
            buildings = await BuildingHandler.search_buildings_in_rectangle(
                db, geo_search.north, geo_search.south, geo_search.east, geo_search.west
            )
        
        building_ids = [b.id for b in buildings]
        
        if not building_ids:
            return []

        stmt = select(Organization).options(
            joinedload(Organization.building),
            joinedload(Organization.activities)
        ).filter(Organization.building_id.in_(building_ids))
        
        result = await db.execute(stmt)
        return result.unique().scalars().all()
