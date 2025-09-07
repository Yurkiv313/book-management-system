import pytest
import io
import json
from httpx import AsyncClient
from src.db.models import Book, Author
from src.schemas.book import BookCreate, BookUpdate, BookOut, GenreEnum


def test_book_create_schema_valid():
    book = BookCreate(title="1984", genre=GenreEnum.fiction, published_year=1949, author_id=1)
    assert book.title == "1984"
    assert book.genre == GenreEnum.fiction
    assert book.published_year == 1949
    assert book.author_id == 1


def test_book_create_schema_invalid_year():
    with pytest.raises(ValueError):
        BookCreate(title="Bad", genre=GenreEnum.science, published_year=-100, author_id=1)


def test_book_update_schema_partial():
    update = BookUpdate(title="New Title", genre=GenreEnum.history, published_year=2020, author_id=2)
    assert update.title == "New Title"
    assert update.genre == GenreEnum.history
    assert update.published_year == 2020
    assert update.author_id == 2


def test_book_out_schema_from_model():
    data = {"id": 1, "title": "Book", "genre": "Science", "published_year": 2000, "author_id": 2}
    out = BookOut.model_validate(data)
    assert out.id == 1
    assert out.genre == GenreEnum.science
    assert out.published_year == 2000


@pytest.mark.asyncio
async def test_create_book_success(db_session, client: AsyncClient):
    author = Author(name="Book Author")
    db_session.add(author)
    await db_session.commit()
    await db_session.refresh(author)

    payload = {"title": "1984", "genre": "Fiction", "published_year": 1949, "author_id": author.id}
    r = await client.post("/books/", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "1984"
    assert data["author_id"] == author.id


@pytest.mark.asyncio
async def test_create_book_invalid_author(db_session, client: AsyncClient):
    payload = {"title": "Orphan Book", "genre": "Science", "published_year": 2021, "author_id": 9999}
    r = await client.post("/books/", json=payload)
    assert r.status_code == 400
    assert "does not exist" in r.json()["detail"]


@pytest.mark.asyncio
async def test_read_books_and_filters(db_session, client: AsyncClient):
    author = Author(name="Filter Author")
    db_session.add(author)
    await db_session.commit()
    await db_session.refresh(author)

    books = [
        Book(title="A book", genre="Fiction", published_year=2000, author_id=author.id),
        Book(title="B book", genre="Science", published_year=2021, author_id=author.id)
    ]
    db_session.add_all(books)
    await db_session.commit()

    r = await client.get("/books/?title=A")
    assert r.status_code == 200
    assert any("A book" in b["title"] for b in r.json())

    r2 = await client.get("/books/?genre=Science")
    assert r2.status_code == 200
    assert all(b["genre"] == "Science" for b in r2.json())


@pytest.mark.asyncio
async def test_read_book_found_and_not_found(db_session, client: AsyncClient):
    author = Author(name="Read Author")
    db_session.add(author)
    await db_session.commit()
    await db_session.refresh(author)

    book = Book(title="Read Me", genre="History", published_year=1990, author_id=author.id)
    db_session.add(book)
    await db_session.commit()
    await db_session.refresh(book)

    r = await client.get(f"/books/{book.id}")
    assert r.status_code == 200
    assert r.json()["title"] == "Read Me"

    r2 = await client.get("/books/99999")
    assert r2.status_code == 404
    assert r2.json()["detail"] == "Book not found"


@pytest.mark.asyncio
async def test_update_book_success_and_not_found(db_session, client: AsyncClient):
    author = Author(name="Upd Author")
    db_session.add(author)
    await db_session.commit()
    await db_session.refresh(author)

    book = Book(title="Old", genre="Fiction", published_year=2000, author_id=author.id)
    db_session.add(book)
    await db_session.commit()
    await db_session.refresh(book)

    payload = {"title": "Updated", "genre": "Non-Fiction"}
    r = await client.put(f"/books/{book.id}", json=payload)
    assert r.status_code == 200
    assert r.json()["title"] == "Updated"

    r2 = await client.put("/books/99999", json=payload)
    assert r2.status_code == 404
    assert r2.json()["detail"] == "Book not found"


@pytest.mark.asyncio
async def test_delete_book_success_and_not_found(db_session, client: AsyncClient):
    author = Author(name="Del Author")
    db_session.add(author)
    await db_session.commit()
    await db_session.refresh(author)

    book = Book(title="Delete Me", genre="Science", published_year=2010, author_id=author.id)
    db_session.add(book)
    await db_session.commit()
    await db_session.refresh(book)

    r = await client.delete(f"/books/{book.id}")
    assert r.status_code == 200
    assert r.json()["message"] == "Book deleted"

    r2 = await client.delete("/books/99999")
    assert r2.status_code == 404
    assert r2.json()["detail"] == "Book not found"


@pytest.mark.asyncio
async def test_bulk_import_books_success_and_errors(db_session, client: AsyncClient):
    author = Author(name="Bulk Author")
    db_session.add(author)
    await db_session.commit()
    await db_session.refresh(author)

    valid_data = [
        {"title": "Bulk1", "genre": "Fiction", "published_year": 2001, "author_id": author.id},
        {"title": "Bulk2", "genre": "Science", "published_year": 2002, "author_id": author.id}
    ]
    files = {"file": ("books.json", io.BytesIO(json.dumps(valid_data).encode()), "application/json")}
    r = await client.post("/books/bulk", files=files)
    assert r.status_code == 200
    assert len(r.json()) == 2

    files2 = {"file": ("books.txt", io.BytesIO(b"[]"), "text/plain")}
    r2 = await client.post("/books/bulk", files=files2)
    assert r2.status_code == 400
    assert r2.json()["detail"] == "Only JSON files are supported"

    files3 = {"file": ("books.json", io.BytesIO(b"invalid"), "application/json")}
    r3 = await client.post("/books/bulk", files=files3)
    assert r3.status_code == 400
    assert r3.json()["detail"] == "Invalid JSON file"

    invalid_data = [{"title": "Orphan Bulk", "genre": "Fiction", "published_year": 2020, "author_id": 999}]
    files4 = {"file": ("books.json", io.BytesIO(json.dumps(invalid_data).encode()), "application/json")}
    r4 = await client.post("/books/bulk", files=files4)
    assert r4.status_code == 400
    assert "does not exist" in r4.json()["detail"]
