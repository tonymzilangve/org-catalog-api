from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import joinedload, Session
from typing import List, Optional

from app.api.schemas import OrganizationSchema, OrganizationCreate
from app.core.dependencies import verify_api_key
from app.db import get_db

from app.db.models import Organization

router = APIRouter(
    prefix="/orgs",
    tags=["orgs"],
    dependencies=[Depends(verify_api_key)]
)


@router.get("/", response_model=List[OrganizationSchema])
def read_organizations(
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
def read_organization(org_id: int, db: Session = Depends(get_db)):

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
        # return crud.organization.create_organization(db=db, organization=organization)

        # Check if building exists
        building = db.query(models.Building).filter(models.Building.id == organization.building_id).first()
        if not building:
            raise ValueError("Building not found")
        
        # Check if activities exist
        activities = db.query(models.Activity).filter(
            models.Activity.id.in_(organization.activity_ids)
        ).all()
        
        if len(activities) != len(organization.activity_ids):
            raise ValueError("One or more activities not found")
        
        db_organization = models.Organization(
            name=organization.name,
            phone_numbers=organization.phone_numbers,
            building_id=organization.building_id
        )
        
        db.add(db_organization)
        db.commit()
        db.refresh(db_organization)
        
        # Add activities
        db_organization.activities = activities
        db.commit()
        db.refresh(db_organization)
        
        return db_organization


    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))



