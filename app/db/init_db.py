import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.api.handlers import ActivityHandler, BuildingHandler, OrganizationHandler
from app.api.schemas import ActivityCreate, BuildingCreate, OrganizationCreate
from app.db import async_session_maker, Base, engine


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as db:
        try:
            building1 = await BuildingHandler.create_building(db, BuildingCreate(
                address="г. Москва, ул. Ленина 1, офис 3",
                latitude=55.7558,
                longitude=37.6176
            ))
            
            building2 = await BuildingHandler.create_building(db, BuildingCreate(
                address="г. Москва, ул. Блюхера 32/1",
                latitude=55.7600,
                longitude=37.6200
            ))
            
            building3 = await BuildingHandler.create_building(db, BuildingCreate(
                address="г. Москва, ул. Тверская 10",
                latitude=55.7570,
                longitude=37.6150
            ))

            food = await ActivityHandler.create_activity(db, ActivityCreate(
                name="Еда",
                parent_id=None
            ))
            
            meat = await ActivityHandler.create_activity(db, ActivityCreate(
                name="Мясная продукция",
                parent_id=food.id
            ))
            
            dairy = await ActivityHandler.create_activity(db, ActivityCreate(
                name="Молочная продукция",
                parent_id=food.id
            ))
            
            cars = await ActivityHandler.create_activity(db, ActivityCreate(
                name="Автомобили",
                parent_id=None
            ))
            
            trucks = await ActivityHandler.create_activity(db, ActivityCreate(
                name="Грузовые",
                parent_id=cars.id
            ))
            
            passenger = await ActivityHandler.create_activity(db, ActivityCreate(
                name="Легковые",
                parent_id=cars.id
            ))
            
            jeep = await ActivityHandler.create_activity(db, ActivityCreate(
                name="Джипы",
                parent_id=cars.id
            ))
            
            parts = await ActivityHandler.create_activity(db, ActivityCreate(
                name="Запчасти",
                parent_id=cars.id
            ))
            
            accessories = await ActivityHandler.create_activity(db, ActivityCreate(
                name="Аксессуары",
                parent_id=cars.id
            ))

            org1 = await OrganizationHandler.create_organization(db, OrganizationCreate(
                name='ООО "Рога и Копыта"',
                phone_numbers=["2-222-222", "3-333-333", "8-923-666-13-13"],
                building_id=building1.id,
                activity_ids=[meat.id, dairy.id]
            ))
            
            org2 = await OrganizationHandler.create_organization(db, OrganizationCreate(
                name='ООО "АвтоМир"',
                phone_numbers=["4-444-444", "5-555-555"],
                building_id=building2.id,
                activity_ids=[trucks.id, jeep.id, passenger.id]
            ))
            
            org3 = await OrganizationHandler.create_organization(db, OrganizationCreate(
                name='ИП "Шумахер"',
                phone_numbers=["6-666-666"],
                building_id=building3.id,
                activity_ids=[jeep.id]
            ))
            
            org4 = await OrganizationHandler.create_organization(db, OrganizationCreate(
                name='ЗАО "Молоко"',
                phone_numbers=["7-777-777"],
                building_id=building1.id,
                activity_ids=[dairy.id]
            ))
            
            await db.commit()
            print("Test data created successfully!")
            
        except Exception as e:
            await db.rollback()
            print(f"Error creating test data: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(init_db())
