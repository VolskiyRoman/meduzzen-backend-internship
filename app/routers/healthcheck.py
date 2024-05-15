from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def healthcheck():
    response_body = {
        "status_code": 200,
        "detail": "ok",
        "result": "working"
    }
    return response_body


@router.get("/run_task/{task_name}")
async def run_task(task_name: str):
    result = test_task.delay(task_name)
    return {"task_id": result.id}
