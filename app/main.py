import os
from fastapi import FastAPI, Depends, HTTPException, Header, Query
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import SessionLocal, engine
import uuid

# create tables
models.Base.metadata.create_all(bind=engine)

API_KEY = os.getenv("API_KEY", "supersecretapikey")
app = FastAPI(title="Organizations Directory API", version="1.0")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def require_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


# --- Activities ---
@app.post(
    "/activities/",
    response_model=schemas.ActivityRead,
    dependencies=[Depends(require_api_key)],
)
def create_activity(item: schemas.ActivityCreate, db: Session = Depends(get_db)):
    try:
        act = crud.create_activity(db, item)
        return act
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get(
    "/activities/",
    response_model=list[schemas.ActivityRead],
    dependencies=[Depends(require_api_key)],
)
def list_activities(db: Session = Depends(get_db)):
    roots = db.query(models.Activity).filter(models.Activity.parent_id == None).all()
    return roots


# --- Organizations ---
@app.post(
    "/organizations/",
    response_model=schemas.OrganizationRead,
    dependencies=[Depends(require_api_key)],
)
def create_org(item: schemas.OrganizationCreate, db: Session = Depends(get_db)):
    org = crud.create_organization(db, item)
    return org


@app.get(
    "/organizations/{org_id}",
    response_model=schemas.OrganizationRead,
    dependencies=[Depends(require_api_key)],
)
def get_org(org_id: uuid.UUID, db: Session = Depends(get_db)):
    org = crud.get_organization(db, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org


@app.get(
    "/organizations/by-building/{building_id}",
    response_model=list[schemas.OrganizationRead],
    dependencies=[Depends(require_api_key)],
)
def orgs_by_building(building_id: uuid.UUID, db: Session = Depends(get_db)):
    return crud.list_organizations_by_building(db, building_id)


@app.get(
    "/organizations/by-activity/{activity_id}",
    response_model=list[schemas.OrganizationRead],
    dependencies=[Depends(require_api_key)],
)
def orgs_by_activity(activity_id: uuid.UUID, db: Session = Depends(get_db)):
    return crud.list_organizations_by_activity(db, activity_id)


@app.get(
    "/organizations/by-activity-desc/{activity_id}",
    response_model=list[schemas.OrganizationRead],
    dependencies=[Depends(require_api_key)],
)
def orgs_by_activity_desc(activity_id: uuid.UUID, db: Session = Depends(get_db)):
    """Return organizations linked to activity and its descendants (max depth 3)."""
    return crud.list_organizations_by_activity_with_descendants(db, activity_id)


@app.get(
    "/organizations/search_name/",
    response_model=list[schemas.OrganizationRead],
    dependencies=[Depends(require_api_key)],
)
def search_orgs_by_name(
    q: str = Query(..., min_length=1), db: Session = Depends(get_db)
):
    return crud.search_organizations_by_name(db, q)


@app.get(
    "/buildings/",
    response_model=list[schemas.BuildingRead],
    dependencies=[Depends(require_api_key)],
)
def get_buildings(db: Session = Depends(get_db)):
    return crud.list_buildings(db)


@app.get(
    "/organizations/in_bbox",
    response_model=list[schemas.OrganizationRead],
    dependencies=[Depends(require_api_key)],
)
def orgs_in_bbox(
    lat_min: float = Query(...),
    lat_max: float = Query(...),
    lon_min: float = Query(...),
    lon_max: float = Query(...),
    db: Session = Depends(get_db),
):
    return crud.organizations_in_bbox(db, lat_min, lat_max, lon_min, lon_max)


@app.get(
    "/organizations/within_radius",
    response_model=list[schemas.OrganizationRead],
    dependencies=[Depends(require_api_key)],
)
def orgs_within_radius(
    center_lat: float = Query(...),
    center_lon: float = Query(...),
    radius_m: float = Query(1000.0),
    db: Session = Depends(get_db),
):
    return crud.organizations_within_radius(db, center_lat, center_lon, radius_m)
