from fastapi import HTTPException
from starlette import status


async def raise_not_enough_permissions():
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="You dont have permissions to perform this action",
    )
