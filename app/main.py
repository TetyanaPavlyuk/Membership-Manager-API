import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv


load_dotenv()

app = FastAPI()

origins = [
    f"http://{os.getenv('FRONTEND_HOST')}:{os.getenv('FRONTEND_PORT')}"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
async def root():
    return {
        "status_code": 200,
        "detail": "ok",
        "result": "working"
    }
