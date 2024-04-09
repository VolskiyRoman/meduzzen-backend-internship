from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
    expose_headers=["Content-Disposition"],
)

@app.get("/")
def read_root():
    response_body = {
        "status_code": 200,
        "detail": "ok",
        "result": "working"
    }
    return response_body
