from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    HTTPException,
    Request
)
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_db
from src.crud import authors
from src.schemas.author import AuthorCreate, AuthorOut
from typing import List
import json
from src.core.limiter import limiter


router = APIRouter(prefix="/authors", tags=["Authors"])


@router.post("/", response_model=AuthorOut)
async def create_author(
        author: AuthorCreate,
        db: AsyncSession = Depends(get_db)
):
    return await authors.create_author(db, author)


@router.get("/", response_model=List[AuthorOut])
@limiter.limit("10/minute")
async def read_authors(request: Request, db: AsyncSession = Depends(get_db)):
    return await authors.get_authors(db)


@router.post("/bulk", response_model=List[AuthorOut])
async def bulk_import_authors(
    db: AsyncSession = Depends(get_db), file: UploadFile = File(...)
):
    if not file.filename.endswith(".json"):
        raise HTTPException(
            status_code=400,
            detail="Only JSON files are supported"
        )

    try:
        content = await file.read()
        data = json.loads(content.decode("utf-8"))
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")

    authors_list = [AuthorCreate(**item) for item in data]
    return await authors.bulk_import_authors(db, authors_list)
