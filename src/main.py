from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from fastapi.responses import JSONResponse


from src.routes import user, authors, books
from src.core.limiter import limiter

app = FastAPI(title="Book Management System", version="1.0.0")


@app.get("/")
async def root():
    return JSONResponse(
        content={"message": "Book Management API is running 🚀"}
    )


app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(user.router)
app.include_router(authors.router)
app.include_router(books.router)
