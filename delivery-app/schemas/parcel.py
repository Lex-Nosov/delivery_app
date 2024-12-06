from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID


class ParcelCreate(BaseModel):
    title: str
    weight: float
    content_value: float
    type_id: int


class ParcelResponse(BaseModel):
    id: UUID
    title: str
    weight: float
    content_value: float
    delivery_cost: Optional[float]
    type_name: str


class ParcelTypeResponse(BaseModel):
    id: int
    name: str


class PaginatedParcelsResponse(BaseModel):
    items: List[ParcelResponse]
    total: int
