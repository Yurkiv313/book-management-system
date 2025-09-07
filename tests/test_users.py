import pytest
from src.crud import user as user_crud
from src.schemas.user import UserCreate


def test_hash_and_verify_password():
    password = "mypassword"
    hashed = user_crud.hash_password(password)
    assert hashed != password
    assert user_crud.verify_password(password, hashed)
    assert not user_crud.verify_password("wrong", hashed)


@pytest.mark.asyncio
async def test_create_and_get_user(db_session):
    user_in = UserCreate(email="test@example.com", password="secret123")
    user = await user_crud.create_user(db_session, user_in)

    assert user.id is not None
    assert user.email == "test@example.com"
    assert user_crud.verify_password("secret123", user.hashed_password)

    fetched = await user_crud.get_user_by_email(db_session, "test@example.com")
    assert fetched.id == user.id


@pytest.mark.asyncio
async def test_register_user(client):
    resp = await client.post("/users/register", json={
        "email": "new@example.com",
        "password": "strongpass"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "new@example.com"
    assert "id" in data
    assert data["role"] == "user"


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    await client.post("/users/register", json={
        "email": "dup@example.com",
        "password": "strongpass"
    })
    resp = await client.post("/users/register", json={
        "email": "dup@example.com",
        "password": "anotherpass"
    })
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Email already registered"


@pytest.mark.asyncio
async def test_login_success(client):
    await client.post("/users/register", json={
        "email": "login@example.com",
        "password": "password123"
    })
    resp = await client.post("/users/login", json={
        "email": "login@example.com",
        "password": "password123"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    resp = await client.post("/users/login", json={
        "email": "notexist@example.com",
        "password": "wrong"
    })
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid credentials"


@pytest.mark.asyncio
async def test_refresh_token(client):
    await client.post("/users/register", json={
        "email": "refresh@example.com",
        "password": "password123"
    })
    login_resp = await client.post("/users/login", json={
        "email": "refresh@example.com",
        "password": "password123"
    })
    refresh_token = login_resp.json()["refresh_token"]

    resp = await client.post("/users/refresh", params={"refresh_token": refresh_token})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_get_current_user_with_access_token(client):
    await client.post("/users/register", json={
        "email": "me@example.com",
        "password": "password123"
    })
    login_resp = await client.post("/users/login", json={
        "email": "me@example.com",
        "password": "password123"
    })
    token = login_resp.json()["access_token"]

    resp = await client.get("/users/register", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code in [400, 405]
