from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_db
from src.crud import books
from src.schemas.book import BookCreate, BookOut, BookUpdate
from typing import List, Optional, Literal
import json
from src.auth.dependencies import get_current_user

router = APIRouter(prefix="/books", tags=["Books"])

GenreLiteral = Literal["Fiction", "Non-Fiction", "Science", "History"]


@router.post("/", response_model=BookOut)
async def create_book(
        book: BookCreate,
        db: AsyncSession = Depends(get_db),
        user=Depends(get_current_user)
):
    return await books.create_book(db, book)


@router.get("/", response_model=List[BookOut])
async def read_books(
        db: AsyncSession = Depends(get_db),
        title: Optional[str] = Query(None),
        genre: Optional[GenreLiteral] = Query(None),
        year_from: Optional[int] = Query(None),
        year_to: Optional[int] = Query(None),
        limit: int = Query(10, ge=1, le=100),
        offset: int = Query(0, ge=0),
        sort_by: str = Query("id", pattern="^(id|title|published_year|author_id)$"),
        sort_order: str = Query("asc", pattern="^(asc|desc)$")
):
    return await books.get_books(
        db, title, genre, year_from, year_to, limit, offset, sort_by, sort_order
    )


@router.get("/{book_id}", response_model=BookOut)
async def read_book(book_id: int, db: AsyncSession = Depends(get_db)):
    book = await books.get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.put("/{book_id}", response_model=BookOut)
async def update_book(book_id: int, book: BookUpdate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    updated_book = await books.update_book(db, book_id, book)
    if not updated_book:
        raise HTTPException(status_code=404, detail="Book not found")
    return updated_book


@router.delete("/{book_id}")
async def delete_book(book_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    deleted_book = await books.delete_book(db, book_id)
    if not deleted_book:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book deleted"}


@router.post("/bulk", response_model=List[BookOut])
async def bulk_import_books(
    db: AsyncSession = Depends(get_db),
    file: UploadFile = File(...)
):
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Only JSON files are supported")

    try:
        content = await file.read()
        data = json.loads(content.decode("utf-8"))
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")

    books_list = [BookCreate(**item) for item in data]
    return await books.bulk_import_books(db, books_list)
