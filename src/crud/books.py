from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from src.schemas.book import BookCreate, BookUpdate
from typing import List


async def create_book(db: AsyncSession, book: BookCreate):
    check_author = text("SELECT id FROM authors WHERE id = :id")
    result = await db.execute(check_author, {"id": book.author_id})
    author = result.mappings().first()

    if not author:
        raise HTTPException(status_code=400, detail=f"Author with id {book.author_id} does not exist")

    query = text("""
        INSERT INTO books (title, genre, published_year, author_id)
        VALUES (:title, :genre, :published_year, :author_id)
        RETURNING id, title, genre, published_year, author_id
    """)
    result = await db.execute(query, book.dict())
    row = result.mappings().first()
    await db.commit()
    return row


async def get_books(
        db: AsyncSession,
        title: str = None,
        genre: str = None,
        year_from: int = None,
        year_to: int = None,
        limit: int = 10,
        offset: int = 0,
        sort_by: str = "id",
        sort_order: str = "asc"
):
    query = "SELECT * FROM books WHERE 1=1"
    params = {}

    if title:
        query += " AND title ILIKE :title"
        params["title"] = f"%{title}%"

    if genre:
        query += " AND genre = :genre"
        params["genre"] = genre

    if year_from:
        query += " AND published_year >= :year_from"
        params["year_from"] = year_from

    if year_to:
        query += " AND published_year <= :year_to"
        params["year_to"] = year_to

    allowed_sort = {"id", "title", "published_year", "author_id"}
    if sort_by not in allowed_sort:
        sort_by = "id"

    order = "ASC" if sort_order.lower() == "asc" else "DESC"
    query += f" ORDER BY {sort_by} {order}"

    query += " LIMIT :limit OFFSET :offset"
    params["limit"] = limit
    params["offset"] = offset

    result = await db.execute(text(query), params)
    return result.mappings().all()


async def get_book(db: AsyncSession, book_id: int):
    query = text("SELECT * FROM books WHERE id = :id")
    result = await db.execute(query, {"id": book_id})
    return result.mappings().first()


async def update_book(db: AsyncSession, book_id: int, book_data: BookUpdate):
    fields = book_data.dict(exclude_unset=True)
    if not fields:
        return None

    set_clause = ", ".join([f"{k} = :{k}" for k in fields.keys()])
    fields["id"] = book_id

    query = text(f"""
        UPDATE books
        SET {set_clause}
        WHERE id = :id
        RETURNING id, title, genre, published_year, author_id
    """)
    result = await db.execute(query, fields)
    row = result.mappings().first()
    await db.commit()
    return row


async def delete_book(db: AsyncSession, book_id: int):
    query = text("""
        DELETE FROM books
        WHERE id = :id
        RETURNING id
    """)
    result = await db.execute(query, {"id": book_id})
    row = result.mappings().first()
    await db.commit()
    return row


async def bulk_import_books(db: AsyncSession, books: List[BookCreate]):
    results = []
    for book in books:
        # Перевірка чи автор існує
        check_author = text("SELECT id FROM authors WHERE id = :id")
        author = await db.execute(check_author, {"id": book.author_id})
        if not author.mappings().first():
            # Пропускаємо або кидаємо помилку — я пропоную помилку
            raise HTTPException(status_code=400, detail=f"Author with id {book.author_id} does not exist")

        # Перевірка чи книга існує
        check_query = text("""
            SELECT id, title, genre, published_year, author_id
            FROM books
            WHERE title = :title AND author_id = :author_id
        """)
        existing = await db.execute(check_query, {
            "title": book.title,
            "author_id": book.author_id
        })
        row = existing.mappings().first()

        if row:
            results.append(row)
        else:
            insert_query = text("""
                INSERT INTO books (title, genre, published_year, author_id)
                VALUES (:title, :genre, :published_year, :author_id)
                RETURNING id, title, genre, published_year, author_id
            """)
            result = await db.execute(insert_query, book.dict())
            row = result.mappings().first()
            results.append(row)

    await db.commit()
    return results

