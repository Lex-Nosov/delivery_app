from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4

from . import Base


class ParcelType(Base):
    __tablename__ = "parcel_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)


class Parcel(Base):
    __tablename__ = "parcels"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    title = Column(String, nullable=False)
    weight = Column(Float, nullable=False)
    content_value = Column(Float, nullable=False)
    delivery_cost = Column(Float, nullable=True)
    type_id = Column(Integer, ForeignKey("parcel_types.id"), nullable=False)
    session_id = Column(String, nullable=False)

    type = relationship("ParcelType")
