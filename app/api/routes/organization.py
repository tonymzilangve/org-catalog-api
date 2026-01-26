from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import joinedload, Session
from typing import List, Optional

from app.api.handlers.organisation import OrganizationHandler
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
def list_organizations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    organizations = db.query(Organization).options(
        joinedload(Organization.building),
        joinedload(Organization.activities)
    ).offset(skip).limit(limit).all()
    return organizations


@router.get("/{org_id}", response_model=OrganizationSchema)
def get_organization(org_id: int, db: Session = Depends(get_db)):

    db_org = db.query(Organization).options(
        joinedload(Organization.building),
        joinedload(Organization.activities)
    ).filter(Organization.id == org_id).first()

    if db_org is None:
        raise HTTPException(status_code=404, detail="Organization not found")

    return db_org


@router.get("/search/name", response_model=List[OrganizationSchema])
def search_organizations_by_name(
    name: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):
    organizations = db.query(Organization).options(
        joinedload(Organization.building),
        joinedload(Organization.activities)
    ).filter(Organization.name.ilike(f"%{name}%")).all()

    return organizations


@router.post("/", response_model=OrganizationSchema, status_code=status.HTTP_201_CREATED)
def create_organization(
    organization: OrganizationCreate,
    db: Session = Depends(get_db)
):
    try:
        building = db.query(Building).filter(Building.id == organization.building_id).first()
        if not building:
            raise ValueError("Building not found")
        
        activities = db.query(Activity).filter(
            Activity.id.in_(organization.activity_ids)
        ).all()
        
        if len(activities) != len(organization.activity_ids):
            raise ValueError("One or more activities not found")
        
        db_organization = Organization(
            name=organization.name,
            phone_numbers=organization.phone_numbers,
            building_id=organization.building_id
        )
        
        db.add(db_organization)
        db.commit()
        db.refresh(db_organization)

        db_organization.activities = activities
        db.commit()
        db.refresh(db_organization)
        
        return db_organization

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/building/{building_id}", response_model=List[OrganizationSchema])
def get_organizations_by_building(building_id: int, db: Session = Depends(get_db)):
    organizations = db.query(Organization).options(
        joinedload(Organization.building),
        joinedload(Organization.activities)
    ).filter(Organization.building_id == building_id).all()

    return organizations


def get_descendant_ids(db: Session, activity_id: int) -> List[int]:
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        return []
    
    ids = [activity_id]
    
    def get_child_ids(parent_id):
        children = db.query(Activity).filter(Activity.parent_id == parent_id).all()
        for child in children:
            ids.append(child.id)
            get_child_ids(child.id)
    
    get_child_ids(activity_id)
    return ids


@router.get("/activity/{activity_id}", response_model=List[OrganizationSchema])
def get_organizations_by_activity(activity_id: int, db: Session = Depends(get_db)):
    
    descendant_ids = get_descendant_ids(db, activity_id)
    
    organizations = db.query(Organization).options(
        joinedload(Organization.building),
        joinedload(Organization.activities)
    ).join(Organization.activities).filter(Activity.id.in_(descendant_ids)).all()
    
    return organizations


@router.post("/search/geo", response_model=List[OrganizationSchema])
def search_organizations_by_geo(
    geo_search: GeoSearch,
    db: Session = Depends(get_db)
):
    organizations = OrganizationHandler.search_organizations_by_geo(db, geo_search=geo_search)
    return organizations
