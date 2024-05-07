from fastapi import HTTPException
from starlette import status


class AlreadyInCompanyException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already in company"
        )


class NotOwnerException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the owner of this company"
        )