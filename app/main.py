from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    response_body = {
        "status_code": 200,
        "detail": "ok",
        "result": "working"
    }
    return response_body
