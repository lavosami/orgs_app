from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table, Text
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# association table for many-to-many between Organization and Activity
org_activity = Table(
    "org_activity",
    Base.metadata,
    Column("organization_id", Integer, ForeignKey("organizations.id", ondelete="CASCADE"), primary_key=True),
    Column("activity_id", Integer, ForeignKey("activities.id", ondelete="CASCADE"), primary_key=True),
)

class Building(Base):
    __tablename__ = "buildings"
    id = Column(Integer, primary_key=True)
    address = Column(String(512), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    organizations = relationship("Organization", back_populates="building", cascade="all, delete")

class Activity(Base):
    __tablename__ = "activities"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=False)
    parent_id = Column(Integer, ForeignKey("activities.id", ondelete="SET NULL"), nullable=True)

    parent = relationship("Activity", remote_side=[id], backref="children")
    organizations = relationship("Organization", secondary=org_activity, back_populates="activities")

class Organization(Base):
    __tablename__ = "organizations"
    id = Column(Integer, primary_key=True)
    name = Column(String(300), nullable=False)
    phones = Column(Text, nullable=True)
    building_id = Column(Integer, ForeignKey("buildings.id", ondelete="CASCADE"), nullable=False)

    building = relationship("Building", back_populates="organizations")
    activities = relationship("Activity", secondary=org_activity, back_populates="organizations")