from fastapi import HTTPException
from sqlalchemy.orm import joinedload, Session

from app.api.schemas import GeoSearch, OrganizationCreate, SearchType
from app.db.models import Activity, Building, Organization

from .building import BuildingHandler


class OrganizationHandler:

    @staticmethod
    def create_organization(
        db: Session,
        organization: OrganizationCreate,
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

    @staticmethod
    def search_organizations_by_geo(db: Session, geo_search: GeoSearch):
        # Get buildings in area
        if geo_search.search_type == SearchType.radius:
            buildings = BuildingHandler.search_buildings_in_radius(
                db, geo_search.latitude, geo_search.longitude, geo_search.radius_km
            )
        else:  # rectangle
            buildings = BuildingHandler.search_buildings_in_rectangle(
                db, geo_search.north, geo_search.south, geo_search.east, geo_search.west
            )
        
        building_ids = [b.id for b in buildings]
        
        # Get organizations in those buildings
        return db.query(Organization).options(
            joinedload(Organization.building),
            joinedload(Organization.activities)
        ).filter(Organization.building_id.in_(building_ids)).all()
