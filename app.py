from fastapi import FastAPI
from api.routes.auth import router as users_route
from api.routes.resume import router as resume_route
from contextlib import asynccontextmanager
from database.init_db import start_db



@asynccontextmanager
async def lifespan(app: FastAPI):
    start_db()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def read_root():
    return {"Hello": "World"}

app.include_router(users_route)
app.include_router(resume_route)


