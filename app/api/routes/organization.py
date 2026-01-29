from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from typing import List, Optional

from app.api.handlers.organization import OrganizationHandler
from app.api.schemas import GeoSearch, OrganizationSchema, OrganizationCreate
from app.core.dependencies import verify_api_key
from app.db import get_db

from app.db.models import Activity, Building, Organization

router = APIRouter(
    prefix="/orgs",
    tags=["orgs"],
    dependencies=[Depends(verify_api_key)]
)


@router.get("/", response_model=List[OrganizationSchema])
async def list_organizations(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Organization).options(
        joinedload(Organization.building),
        joinedload(Organization.activities)
    ).offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    organizations = result.unique().scalars().all()
    return organizations


@router.get("/{org_id}", response_model=OrganizationSchema)
async def get_organization(org_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Organization).options(
        joinedload(Organization.building),
        joinedload(Organization.activities)
    ).filter(Organization.id == org_id)
    
    result = await db.execute(stmt)
    db_org = result.unique().scalar_one_or_none()

    if db_org is None:
        raise HTTPException(status_code=404, detail="Organization not found")

    return db_org


@router.get("/search/name", response_model=List[OrganizationSchema])
async def search_organizations_by_name(
    name: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Organization).options(
        joinedload(Organization.building),
        joinedload(Organization.activities)
    ).filter(Organization.name.ilike(f"%{name}%"))
    
    result = await db.execute(stmt)
    organizations = result.unique().scalars().all()
    return organizations


@router.post("/", response_model=OrganizationSchema, status_code=status.HTTP_201_CREATED)
async def create_organization(
    organization: OrganizationCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        building_stmt = select(Building).filter(Building.id == organization.building_id)
        building_result = await db.execute(building_stmt)
        building = building_result.scalar_one_or_none()
        
        if not building:
            raise ValueError("Building not found")
        
        activities_stmt = select(Activity).filter(Activity.id.in_(organization.activity_ids))
        activities_result = await db.execute(activities_stmt)
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
        await db.refresh(db_organization, attribute_names=["activities", "building"])
        
        return db_organization

    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/building/{building_id}", response_model=List[OrganizationSchema])
async def get_organizations_by_building(building_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Organization).options(
        joinedload(Organization.building),
        joinedload(Organization.activities)
    ).filter(Organization.building_id == building_id)
    
    result = await db.execute(stmt)
    organizations = result.unique().scalars().all()
    return organizations


async def get_descendant_ids(db: AsyncSession, activity_id: int) -> List[int]:
    activity_stmt = select(Activity).filter(Activity.id == activity_id)
    activity_result = await db.execute(activity_stmt)
    activity = activity_result.scalar_one_or_none()
    
    if not activity:
        return []
    
    ids = [activity_id]
    
    async def get_child_ids(parent_id: int):
        children_stmt = select(Activity).filter(Activity.parent_id == parent_id)
        children_result = await db.execute(children_stmt)
        children = children_result.scalars().all()
        
        for child in children:
            ids.append(child.id)
            await get_child_ids(child.id)
    
    await get_child_ids(activity_id)
    return ids


@router.get("/activity/{activity_id}", response_model=List[OrganizationSchema])
async def get_organizations_by_activity(activity_id: int, db: AsyncSession = Depends(get_db)):
    descendant_ids = await get_descendant_ids(db, activity_id)
    
    if not descendant_ids:
        return []
    
    stmt = select(Organization).options(
        joinedload(Organization.building),
        joinedload(Organization.activities)
    ).join(Organization.activities).filter(Activity.id.in_(descendant_ids))
    
    result = await db.execute(stmt)
    organizations = result.unique().scalars().all()
    return organizations


@router.post("/search/geo", response_model=List[OrganizationSchema])
async def search_organizations_by_geo(
    geo_search: GeoSearch,
    db: AsyncSession = Depends(get_db)
):
    organizations = await OrganizationHandler.search_organizations_by_geo(db, geo_search=geo_search)
    return organizations
