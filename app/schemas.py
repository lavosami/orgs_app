import uuid
from typing import List, Optional
from pydantic import BaseModel, Field


# Phone
class PhoneBase(BaseModel):
    number: str


class PhoneCreate(PhoneBase):
    pass


class PhoneRead(PhoneBase):
    id: uuid.UUID
    organization_id: uuid.UUID

    class Config:
        orm_mode = True


# Building
class BuildingBase(BaseModel):
    address: str
    latitude: float
    longitude: float


class BuildingCreate(BuildingBase):
    pass


class BuildingRead(BuildingBase):
    id: uuid.UUID
    organization_id: uuid.UUID

    class Config:
        orm_mode = True


# Activity
class ActivityBase(BaseModel):
    name: str
    parent_id: Optional[uuid.UUID] = None


class ActivityCreate(ActivityBase):
    pass


class ActivityRead(ActivityBase):
    id: uuid.UUID
    children: List["ActivityRead"] = Field(default_factory=list)

    class Config:
        orm_mode = True


ActivityRead.update_forward_refs()


# Organization
class OrganizationBase(BaseModel):
    name: str


class OrganizationCreate(OrganizationBase):
    phones: Optional[List[PhoneCreate]] = Field(default_factory=list)
    building: Optional[BuildingCreate] = None
    activities: Optional[List[uuid.UUID]] = Field(default_factory=list)


class OrganizationRead(OrganizationBase):
    id: uuid.UUID
    phones: List[PhoneRead] = Field(default_factory=list)
    building: Optional[BuildingRead] = None
    activities: List[ActivityRead] = Field(default_factory=list)

    class Config:
        orm_mode = True
