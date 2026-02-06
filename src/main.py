from fastapi import FastAPI
from dotenv import load_dotenv
from src.routers import authentication, tasks
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    authentication.router,
    prefix="/api/v1/auth",
    tags=["Authentication"]
)


app.include_router(
    tasks.router,
    prefix="/api/v1/tasks",
    tags=["Tasks"]
)
