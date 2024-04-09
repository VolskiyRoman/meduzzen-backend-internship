from fastapi import APIRouter

router = APIRouter()


@router.get("/healthcheck")
def healthcheck():
    response_body = {
        "status_code": 200,
        "detail": "ok",
        "result": "working"
    }
    return response_body
