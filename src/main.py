from fastapi import FastAPI
from src.routes import user

app = FastAPI(title="Book Management System")


app.include_router(user.router)
