from math import asin, cos, radians, sin, sqrt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, select

from app.db.models import Building
from app.api.schemas import BuildingCreate


class BuildingHandler:
    
    @staticmethod
    async def create_building(
        db: AsyncSession,
        building: BuildingCreate
    ):
        db_building = Building(
            address=building.address,
            latitude=building.latitude,
            longitude=building.longitude
        )
        db.add(db_building)
        await db.commit()
        await db.refresh(db_building)

        return db_building

    @staticmethod
    async def search_buildings_in_radius(
        db: AsyncSession, 
        latitude: float, 
        longitude: float, 
        radius_km: float
    ):
        R = 6371  # Earth radius (km)

        result = await db.execute(select(Building))
        buildings = result.scalars().all()
        
        filtered_buildings = []
        
        for building in buildings:
            lat1, lon1 = radians(latitude), radians(longitude)
            lat2, lon2 = radians(building.latitude), radians(building.longitude)
            
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            distance = R * c
            
            if distance <= radius_km:
                filtered_buildings.append(building)
        
        return filtered_buildings
    
    @staticmethod
    async def search_buildings_in_rectangle(
        db: AsyncSession,
        north: float,
        south: float,
        east: float,
        west: float
    ):
        stmt = select(Building).where(
            and_(
                Building.latitude.between(south, north),
                Building.longitude.between(west, east)
            )
        )
        
        result = await db.execute(stmt)
        return result.scalars().all()
