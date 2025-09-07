from fastapi import FastAPI
from src.routes import user, authors, books

app = FastAPI(title="Book Management System")


app.include_router(user.router)
app.include_router(authors.router)
app.include_router(books.router)
