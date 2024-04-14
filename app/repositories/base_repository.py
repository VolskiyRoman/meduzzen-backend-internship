from datetime import datetime
from typing import List

from fastapi import HTTPException, status
from sqlalchemy import update, delete
from sqlalchemy.future import select as async_select

from app.db.connection import get_async_session
from app.db.models import Base


class BaseRepository:
    def __init__(self, model: Base):
        self.model = model

    async def create_one(self, data: dict) -> Base:
        async with get_async_session() as session:
            row = self.model(**data, created_at=datetime.now())
            session.add(row)
            await session.commit()
            await session.refresh(row)
            return row

    async def create_many(self, data: List[dict]) -> List[Base]:
        async with get_async_session() as session:
            rows = [self.model(**row) for row in data]
            session.bulk_save_objects(rows)
            await session.commit()
            return rows

    async def get_one(self, **params) -> Base:
        async with get_async_session() as session:
            query = async_select(self.model).filter_by(**params)
            result = await session.execute(query)
            return await result.scalars().one_or_none()

    async def get_many(self, **params) -> List[Base]:
        async with get_async_session() as session:
            query = async_select(self.model).filter_by(**params)
            result = await session.execute(query)
            return await result.scalars().all()

    async def update_one(self, model_uuid: str, data: dict) -> Base:
        async with get_async_session() as session:
            query = (
                update(self.model)
                .where(self.model.uuid == model_uuid)
                .values(**data)
                .returning(self.model)
            )
            result = await session.execute(query)
            updated_row = await result.scalar_one()
            updated_row.updated_at = datetime.now()
            await session.commit()
            return updated_row

    async def delete_one(self, model_uuid: str) -> Base:
        async with get_async_session() as session:
            query = (
                delete(self.model)
                .where(self.model.uuid == model_uuid)
                .returning(self.model)
            )
            result = await session.execute(query)
            deleted_row = await result.scalar_one()
            await session.commit()
            return deleted_row

    async def get_one_by_params_or_404(self, **params) -> Base:
        db_row = await self.get_one(**params)
        if not db_row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Object not found",
            )
        return db_row
