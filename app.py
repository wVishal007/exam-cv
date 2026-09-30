from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.staticfiles import StaticFiles
from api.routes.auth import router as users_route
from api.routes.resume import router as resume_route
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(lifespan=lifespan)
origins = [
    "http://localhost:8000",  
    "http://localhost:3000",  
    "http://127.0.0.1:3000",
    "http://localhost:5173",  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # Allows specific origins (or use ["*"] for all)
    allow_credentials=True,
    allow_methods=["*"],              # Allows all HTTP methods (GET, POST, PUT, etc.)
    allow_headers=["*"],              # Allows all headers
)

# @app.get("/")
# async def read_root():
#     return {"Hello": "World"}


app.include_router(users_route)
app.include_router(resume_route)

app.mount("/",StaticFiles(directory="frontend/dist",html=True),name="frontend")