from fastapi import FastAPI
from core.config import settings

app = FastAPI()


@app.get("/")
def read_root():
    response_body = {
        "status_code": 200,
        "detail": "ok",
        "result": "working"
    }
    return response_body


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
    )
