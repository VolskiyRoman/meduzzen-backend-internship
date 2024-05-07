from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.connection import get_async_session
from app.models.user import User
from app.models.company_member import CompanyMember


async def first_task(session: AsyncSession = Depends(get_async_session)):
    query = (
        select(User)
        .filter(User.id == 1)
    )
    result = await session.execute(query)
    user = result.scalar()
    if user:
        my_user = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
        }
        print("JSIODFJISDIJOFJIOSDFJOISDFJOISJIDOFJIOSFD", my_user)
    else:
        return None
