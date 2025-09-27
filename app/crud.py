from sqlalchemy.orm import Session
from sqlalchemy import text
from . import models, schemas
import uuid
import math

MAX_ACTIVITY_DEPTH = 3


def create_activity(db: Session, data: schemas.ActivityCreate):
    # enforce depth <= MAX_ACTIVITY_DEPTH
    depth = 1
    pid = data.parent_id
    while pid:
        parent = db.query(models.Activity).filter(models.Activity.id == pid).first()
        if not parent:
            break
        depth += 1
        pid = parent.parent_id
        if depth > MAX_ACTIVITY_DEPTH:
            raise ValueError(f"Activity depth would exceed {MAX_ACTIVITY_DEPTH}")
    act = models.Activity(name=data.name, parent_id=data.parent_id)
    db.add(act)
    db.commit()
    db.refresh(act)
    return act


def create_organization(db: Session, data: schemas.OrganizationCreate):
    org = models.Organization(name=data.name)

    # building (one)
    if data.building:
        org.building = models.Building(
            address=data.building.address,
            latitude=data.building.latitude,
            longitude=data.building.longitude,
        )

    # phones
    for ph in data.phones or []:
        org.phones.append(models.Phone(number=ph.number))

    # attach activities
    if data.activities:
        acts = (
            db.query(models.Activity)
            .filter(models.Activity.id.in_(data.activities))
            .all()
        )
        org.activities.extend(acts)

    db.add(org)
    db.commit()
    db.refresh(org)
    return org


def get_organization(db: Session, org_id: uuid.UUID):
    return (
        db.query(models.Organization).filter(models.Organization.id == org_id).first()
    )


def list_organizations_by_building(db: Session, building_id: uuid.UUID):
    # find organization that has building with this id
    return (
        db.query(models.Organization)
        .join(models.Building)
        .filter(models.Building.id == building_id)
        .all()
    )


def list_organizations_by_activity(db: Session, activity_id: uuid.UUID):
    return (
        db.query(models.Organization)
        .join(models.organization_activity)
        .filter(models.organization_activity.c.activity_id == activity_id)
        .all()
    )


def search_organizations_by_name(db: Session, q: str):
    return (
        db.query(models.Organization)
        .filter(models.Organization.name.ilike(f"%{q}%"))
        .all()
    )


def list_buildings(db: Session):
    return db.query(models.Building).all()


def get_activity_subtree_ids(db: Session, activity_id: uuid.UUID):
    sql = text(
        """
        WITH RECURSIVE subtree(id, parent_id, depth) AS (
            SELECT id, parent_id, 1 FROM activities WHERE id = :start
            UNION ALL
            SELECT a.id, a.parent_id, subtree.depth + 1
            FROM activities a
            JOIN subtree ON a.parent_id = subtree.id
            WHERE subtree.depth < :maxdepth
        )
        SELECT id FROM subtree;
        """
    )
    rows = db.execute(
        sql, {"start": str(activity_id), "maxdepth": MAX_ACTIVITY_DEPTH}
    ).fetchall()
    return [row[0] for row in rows]


def list_organizations_by_activity_with_descendants(
    db: Session, activity_id: uuid.UUID
):
    ids = get_activity_subtree_ids(db, activity_id)
    if not ids:
        return []
    return (
        db.query(models.Organization)
        .join(models.organization_activity)
        .filter(models.organization_activity.c.activity_id.in_(ids))
        .distinct()
        .all()
    )


def organizations_in_bbox(
    db: Session, lat_min: float, lat_max: float, lon_min: float, lon_max: float
):
    return (
        db.query(models.Organization)
        .join(models.Building)
        .filter(models.Building.latitude.between(lat_min, lat_max))
        .filter(models.Building.longitude.between(lon_min, lon_max))
        .all()
    )


def organizations_within_radius(
    db: Session, center_lat: float, center_lon: float, radius_m: float
):
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371000  # Earth radius in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = (
            math.sin(dphi / 2) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))
        return R * c

    orgs = (
        db.query(models.Organization)
        .join(models.Building)
        .filter(models.Building.latitude.isnot(None))
        .filter(models.Building.longitude.isnot(None))
        .all()
    )
    result = []
    for org in orgs:
        b = org.building
        if b:
            dist = haversine(center_lat, center_lon, b.latitude, b.longitude)
            if dist <= radius_m:
                result.append(org)
    return result
