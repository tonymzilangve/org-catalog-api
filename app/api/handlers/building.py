from math import asin, cos, radians, sin, sqrt

from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.db.models import Building


class BuildingHandler:
    @staticmethod
    def search_buildings_in_radius(
        db: Session, 
        latitude: float, 
        longitude: float, 
        radius_km: float
    ):
        # Haversine formula for distance calculation
        R = 6371  # Earth's radius in kilometers
        
        buildings = db.query(Building).all()
        result = []
        
        for building in buildings:
            lat1, lon1 = radians(latitude), radians(longitude)
            lat2, lon2 = radians(building.latitude), radians(building.longitude)
            
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            distance = R * c
            
            if distance <= radius_km:
                result.append(building)
        
        return result
    
    @staticmethod
    def search_buildings_in_rectangle(
        db: Session,
        north: float,
        south: float,
        east: float,
        west: float
    ):
        return db.query(Building).filter(
            and_(
                Building.latitude.between(south, north),
                Building.longitude.between(west, east)
            )
        ).all()
