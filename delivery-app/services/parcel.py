from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from typing import Annotated

from core.db_helper import db_helper


async def get_parcels(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)]
):
    pass
