import io
import json
import pytest
from httpx import AsyncClient
from src.db.models import Author
from src.schemas.author import AuthorBase, AuthorCreate, AuthorOut
from src.crud import authors as crud


def test_author_schemas():
    base = AuthorBase(name="Test")
    assert base.name == "Test"

    create = AuthorCreate(name="Author X")
    assert isinstance(create, AuthorBase)
    assert create.name == "Author X"

    out = AuthorOut(id=1, name="Author Y")
    assert out.id == 1
    assert out.name == "Author Y"


@pytest.mark.asyncio
async def test_create_and_get_authors(db_session):
    author = AuthorCreate(name="Author CRUD")
    created = await crud.create_author(db_session, author)
    assert created.id is not None
    assert created.name == "Author CRUD"

    authors_list = await crud.get_authors(db_session)
    assert any(a.name == "Author CRUD" for a in authors_list)


@pytest.mark.asyncio
async def test_bulk_import_authors(db_session):
    authors_data = [AuthorCreate(name="Bulk One"), AuthorCreate(name="Bulk Two")]

    results = await crud.bulk_import_authors(db_session, authors_data)
    assert len(results) == 2
    assert {r["name"] for r in results} == {"Bulk One", "Bulk Two"}

    results2 = await crud.bulk_import_authors(db_session, authors_data)
    assert len(results2) == 2
    assert {r["name"] for r in results2} == {"Bulk One", "Bulk Two"}


@pytest.mark.asyncio
async def test_create_author_route(client: AsyncClient, db_session):
    payload = {"name": "Route Author"}
    r = await client.post("/authors/", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "Route Author"

    db_obj = await db_session.get(Author, data["id"])
    assert db_obj is not None


@pytest.mark.asyncio
async def test_read_authors_route(client: AsyncClient, db_session):
    db_session.add_all([Author(name="A1"), Author(name="A2")])
    await db_session.commit()

    r = await client.get("/authors/")
    assert r.status_code == 200
    data = r.json()
    names = [a["name"] for a in data]
    assert "A1" in names
    assert "A2" in names


@pytest.mark.asyncio
async def test_bulk_import_authors_route_success(client: AsyncClient, db_session):
    authors_data = [{"name": "Json One"}, {"name": "Json Two"}]
    file_content = json.dumps(authors_data).encode("utf-8")
    files = {"file": ("authors.json", io.BytesIO(file_content), "application/json")}

    r = await client.post("/authors/bulk", files=files)
    assert r.status_code == 200
    data = r.json()
    assert {a["name"] for a in data} == {"Json One", "Json Two"}


@pytest.mark.asyncio
async def test_bulk_import_authors_route_invalid_extension(client: AsyncClient):
    files = {"file": ("authors.txt", io.BytesIO(b"[]"), "text/plain")}
    r = await client.post("/authors/bulk", files=files)
    assert r.status_code == 400
    assert r.json()["detail"] == "Only JSON files are supported"


@pytest.mark.asyncio
async def test_bulk_import_authors_route_invalid_json(client: AsyncClient):
    files = {"file": ("authors.json", io.BytesIO(b"invalid json"), "application/json")}
    r = await client.post("/authors/bulk", files=files)
    assert r.status_code == 400
    assert r.json()["detail"] == "Invalid JSON file"
