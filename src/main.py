from fastapi import FastAPI
from dotenv import load_dotenv
import os
from src.routers import authentication, tasks
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()

app = FastAPI(title="Todo API")

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "resplendent-arithmetic-8c8312.netlify.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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


@app.get("/")
def root():
    return {"message": "Todo API is running"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
