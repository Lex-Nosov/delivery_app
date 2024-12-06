import pytest
from httpx import AsyncClient
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker

from models.base import Base
from models.parcel import Parcel, ParcelType
from main import main_app
from core.config import settings


@pytest.fixture
async def client():
    async with AsyncClient(app=main_app, base_url="http://testserver") as ac:
        yield ac


@pytest.fixture
async def session():
    engine = create_async_engine(settings.db.url, echo=True)

    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_create_parcel(client, session: AsyncSession):
    parcel_type = ParcelType(id=1, name="Clothes")
    session.add(parcel_type)
    await session.commit()

    cookies = {"session_id": str(uuid4())}

    payload = {
        "title": "My Parcel",
        "weight": 2.5,
        "content_value": 100,
        "type_id": 1,
    }

    response = await client.post("/parcels/", json=payload, cookies=cookies)
    assert response.status_code == 200
    parcel_id = response.json()
    assert isinstance(parcel_id, str)

    result = await session.execute(select(Parcel).filter(Parcel.id == parcel_id))
    parcel = result.scalar_one()
    assert parcel.title == "My Parcel"
    assert parcel.weight == 2.5
    assert parcel.type_id == 1
    assert parcel.session_id == cookies["session_id"]


@pytest.mark.asyncio
async def test_get_parcel_types(client, session: AsyncSession):
    parcel_types = [
        ParcelType(id=1, name="Clothes"),
        ParcelType(id=2, name="Electronics"),
    ]
    session.add_all(parcel_types)
    await session.commit()

    response = await client.get("/parcel-types/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["id"] == 1
    assert data[0]["name"] == "Clothes"
    assert data[1]["id"] == 2
    assert data[1]["name"] == "Electronics"


@pytest.mark.asyncio
async def test_get_parcels(client, session: AsyncSession):
    session_id = str(uuid4())
    cookies = {"session_id": session_id}

    parcel_type = ParcelType(id=1, name="Clothes")
    session.add(parcel_type)
    parcel = Parcel(
        id=str(uuid4()),
        title="Parcel 1",
        weight=1.2,
        content_value=50,
        type_id=1,
        session_id=session_id,
    )
    session.add(parcel)
    await session.commit()

    response = await client.get("/parcels/", cookies=cookies)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "Parcel 1"


@pytest.mark.asyncio
async def test_get_parcel(client, session: AsyncSession):
    session_id = str(uuid4())
    cookies = {"session_id": session_id}

    parcel_type = ParcelType(id=1, name="Clothes")
    session.add(parcel_type)
    parcel = Parcel(
        id=str(uuid4()),
        title="Parcel 1",
        weight=1.2,
        content_value=50,
        type_id=1,
        session_id=session_id,
    )
    session.add(parcel)
    await session.commit()

    response = await client.get(f"/parcels/{parcel.id}/", cookies=cookies)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Parcel 1"
    assert data["weight"] == 1.2
    assert data["type_name"] == "Clothes"


@pytest.mark.asyncio
async def test_create_parcel_invalid_type(client, session: AsyncSession):
    cookies = {"session_id": str(uuid4())}

    payload = {
        "title": "My Parcel",
        "weight": 2.5,
        "content_value": 100,
        "type_id": 99,
    }

    response = await client.post("/parcels/", json=payload, cookies=cookies)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid parcel type"


@pytest.mark.asyncio
async def test_get_parcel_not_found(client, session: AsyncSession):
    cookies = {"session_id": str(uuid4())}

    response = await client.get(f"/parcels/{uuid4()}/", cookies=cookies)
    assert response.status_code == 404
    assert response.json()["detail"] == "Parcel not found"
