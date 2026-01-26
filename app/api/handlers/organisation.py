from math import asin, cos, radians, sin, sqrt

from sqlalchemy.orm import joinedload, Session
from sqlalchemy import and_

from app.api.schemas import GeoSearch, SearchType
from app.db.models import Organization

from .building import BuildingHandler


class OrganizationHandler:

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
