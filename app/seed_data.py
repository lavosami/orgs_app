from .database import SessionLocal, engine
from . import models
from . import crud, schemas
import uuid


def seed():
    db = SessionLocal()
    try:
        # clear (for idempotence)
        db.query(models.organization_activity).delete(synchronize_session=False)
        db.query(models.Phone).delete()
        db.query(models.Building).delete()
        db.query(models.Organization).delete()
        db.query(models.Activity).delete()
        db.commit()
    except Exception:
        db.rollback()

    # create activity tree:
    food = crud.create_activity(db, schemas.ActivityCreate(name="Еда"))
    meat = crud.create_activity(
        db, schemas.ActivityCreate(name="Мясо", parent_id=food.id)
    )
    dairy = crud.create_activity(
        db, schemas.ActivityCreate(name="Молоко", parent_id=food.id)
    )
    cars = crud.create_activity(db, schemas.ActivityCreate(name="Машины"))
    trucks = crud.create_activity(
        db, schemas.ActivityCreate(name="Грузовики", parent_id=cars.id)
    )
    parts = crud.create_activity(
        db, schemas.ActivityCreate(name="Детали грузовиков", parent_id=trucks.id)
    )

    o1 = crud.create_organization(
        db,
        schemas.OrganizationCreate(
            name="ООО Рога и Копыта",
            phones=[
                schemas.PhoneCreate(number="2-222-222"),
                schemas.PhoneCreate(number="3-333-333"),
            ],
            building=schemas.BuildingCreate(
                address="Блюхера, 32/1", latitude=55.80, longitude=37.5
            ),
            activities=[meat.id, dairy.id],
        ),
    )

    o2 = crud.create_organization(
        db,
        schemas.OrganizationCreate(
            name="ООО Тмыв",
            phones=[schemas.PhoneCreate(number="8-923-666-13-13")],
            building=schemas.BuildingCreate(
                address="г. Москва, ул. Ленина 1, офис 3",
                latitude=55.751244,
                longitude=37.618423,
            ),
            activities=[cars.id, trucks.id, dairy.id],
        ),
    )

    o3 = crud.create_organization(
        db,
        schemas.OrganizationCreate(
            name="ИП Пупкин",
            phones=[schemas.PhoneCreate(number="+7-900-000-00-01")],
            building=schemas.BuildingCreate(
                address="Тверская 10", latitude=55.764, longitude=37.602
            ),
            activities=[parts.id],
        ),
    )

    print("Seeded sample organizations:", o1.id, o2.id, o3.id)
    db.close()


if __name__ == "__main__":
    seed()
