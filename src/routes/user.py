from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.user import UserLogin
from src.db.database import get_db
from src.crud import user as user_crud
from src.schemas.user import UserCreate, UserOut
from src.auth.jwt_handler import (
    create_access_token,
    create_refresh_token,
    decode_token
)

router = APIRouter(prefix="/users", tags=["Users"])


# 📌 Реєстрація нового користувача
@router.post("/register", response_model=UserOut)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await user_crud.get_user_by_email(db, user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await user_crud.create_user(db, user)


@router.post("/login")
async def login_user(user: UserLogin, db: AsyncSession = Depends(get_db)):
    db_user = await user_crud.get_user_by_email(db, user.email)
    if not db_user or not user_crud.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": db_user.email})
    refresh_token = create_refresh_token({"sub": db_user.email})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


# 📌 Оновлення access токена за refresh
@router.post("/refresh")
async def refresh_token(refresh_token: str):
    payload = decode_token(refresh_token, refresh=True)
    new_access = create_access_token({"sub": payload["sub"]})
    return {"access_token": new_access, "token_type": "bearer"}
