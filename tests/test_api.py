import os
import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app import models

client = TestClient(app)
API_KEY = os.getenv("API_KEY", "supersecretapikey")
HEADERS = {"x-api-key": API_KEY}


def test_create_and_get_org():
    # create an activity first
    r = client.post("/activities/", json={"name": "TestRoot"}, headers=HEADERS)
    assert r.status_code == 200
    root = r.json()
    root_id = root["id"]

    # create organization with building and phone and activity
    payload = {
        "name": "Test Org",
        "phones": [{"number": "123"}],
        "building": {"address": "Test St 1", "latitude": 55.0, "longitude": 37.0},
        "activities": [root_id],
    }
    r = client.post("/organizations/", json=payload, headers=HEADERS)
    assert r.status_code == 200
    org = r.json()
    oid = org["id"]

    # get by id
    r = client.get(f"/organizations/{oid}", headers=HEADERS)
    assert r.status_code == 200
    got = r.json()
    assert got["name"] == "Test Org"
    assert len(got["phones"]) == 1
    assert got["building"]["address"] == "Test St 1"

    # search by name
    r = client.get("/organizations/search_name/", params={"q": "Test"}, headers=HEADERS)
    assert r.status_code == 200
    arr = r.json()
    assert any(a["id"] == oid for a in arr)


def test_orgs_by_building_and_activity():
    # create activity and org
    r = client.post("/activities/", json={"name": "FoodRoot"}, headers=HEADERS)
    assert r.status_code == 200
    act = r.json()
    aid = act["id"]

    payload = {
        "name": "Food Org",
        "phones": [{"number": "9-9-9"}],
        "building": {"address": "Food St 1", "latitude": 55.01, "longitude": 37.01},
        "activities": [aid],
    }
    r = client.post("/organizations/", json=payload, headers=HEADERS)
    assert r.status_code == 200
    org = r.json()
    bid = org["building"]["id"]

    # by building
    r = client.get(f"/organizations/by-building/{bid}", headers=HEADERS)
    assert r.status_code == 200
    assert any(o["id"] == org["id"] for o in r.json())

    # by activity
    r = client.get(f"/organizations/by-activity/{aid}", headers=HEADERS)
    assert r.status_code == 200
    assert any(o["id"] == org["id"] for o in r.json())
