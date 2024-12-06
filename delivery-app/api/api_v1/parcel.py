from fastapi import Depends, APIRouter, Request, Response, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Annotated, List, Optional
from uuid import uuid4, UUID
from redis.asyncio import Redis

from models.parcel import ParcelType
from schemas.parcel import (
    ParcelCreate,
    ParcelTypeResponse,
    PaginatedParcelsResponse,
    ParcelResponse,
)
from core.db_helper import db_helper
from core.redis_helper import RedisHelper
from models import Parcel

router = APIRouter()
redis_helper = RedisHelper()
redis_client: Redis = redis_helper.redis


@router.post("/parcels/", response_model=UUID)
async def create_parcel(
    parcel_data: ParcelCreate,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    request: Request,
):
    redis_client = request.app.state.redis_client
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="Session not found")

    type_exists = await session.execute(
        select(ParcelType).filter(ParcelType.id == parcel_data.type_id)
    )
    if not type_exists.scalar():
        raise HTTPException(status_code=400, detail="Invalid parcel type")

    parcel_id = str(uuid4())
    new_parcel = Parcel(
        id=parcel_id,
        title=parcel_data.title,
        weight=parcel_data.weight,
        content_value=parcel_data.content_value,
        type_id=parcel_data.type_id,
        session_id=session_id,
    )
    session.add(new_parcel)
    await session.commit()

    return parcel_id


@router.get("/parcel-types/", response_model=List[ParcelTypeResponse])
async def get_parcel_types(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)]
):
    result = await session.execute(select(ParcelType))
    return result.scalars().all()


@router.get("/parcels/", response_model=PaginatedParcelsResponse)
async def get_parcels(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    request: Request,
    type_id: Optional[int] = None,
    has_delivery_cost: Optional[bool] = None,
    page: int = 1,
    page_size: int = 10,
):
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="Session not found")

    query = (
        select(Parcel, ParcelType)
        .join(ParcelType)
        .filter(Parcel.session_id == session_id)
    )
    if type_id:
        query = query.filter(Parcel.type_id == type_id)
    if has_delivery_cost is not None:
        if has_delivery_cost:
            query = query.filter(Parcel.delivery_cost.isnot(None))
        else:
            query = query.filter(Parcel.delivery_cost.is_(None))

    count_query = select(func.count()).select_from(query.subquery())
    total = (await session.execute(count_query)).scalar()

    result = await session.execute(
        query.offset((page - 1) * page_size).limit(page_size)
    )

    items = []
    for row in result.fetchall():
        parcel, parcel_type = row
        items.append(
            ParcelResponse(
                id=parcel.id,
                title=parcel.title,
                weight=parcel.weight,
                content_value=parcel.content_value,
                delivery_cost=parcel.delivery_cost,
                type_name=parcel_type.name,
            )
        )

    return PaginatedParcelsResponse(items=items, total=total)


@router.get("/parcels/{parcel_id}/", response_model=ParcelResponse)
async def get_parcel(
    parcel_id: UUID,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    request: Request,
):
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="Session not found")

    query = (
        select(Parcel, ParcelType)
        .join(ParcelType)
        .filter(Parcel.id == parcel_id, Parcel.session_id == session_id)
    )

    result = await session.execute(query)

    row = result.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Parcel not found")

    parcel, parcel_type = row

    return ParcelResponse(
        id=parcel.id,
        title=parcel.title,
        weight=parcel.weight,
        content_value=parcel.content_value,
        delivery_cost=parcel.delivery_cost,
        type_name=parcel_type.name,
    )
