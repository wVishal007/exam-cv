from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes.auth import router as users_route
from api.routes.resume import router as resume_route
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)

origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def read_root():
    return {"message": "Resume Analyzer API is running"}


app.include_router(users_route)
app.include_router(resume_route)