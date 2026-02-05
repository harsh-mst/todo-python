from fastapi import FastAPI
from dotenv import load_dotenv
from .routers import authentication, tasks


load_dotenv()

app = FastAPI()


app.include_router(authentication.router)
app.include_router(tasks.router)
