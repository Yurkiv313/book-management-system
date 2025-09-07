from pydantic import BaseModel, Field, validator
from typing import Optional
from enum import Enum
from datetime import datetime


class GenreEnum(str, Enum):
    fiction = "Fiction"
    non_fiction = "Non-Fiction"
    science = "Science"
    history = "History"


class BookBase(BaseModel):
    title: str = Field(..., min_length=1)
    genre: GenreEnum
    published_year: int

    @validator("published_year")
    def validate_year(cls, v):
        current_year = datetime.now().year
        if v < 1800 or v > current_year:
            raise ValueError(f"published_year must be between 1800 and {current_year}")
        return v


class BookCreate(BookBase):
    author_id: int


class BookUpdate(BaseModel):
    title: Optional[str]
    genre: GenreEnum
    published_year: Optional[int]
    author_id: Optional[int]

    @validator("published_year")
    def validate_year(cls, v):
        current_year = datetime.now().year
        if v < 1800 or v > current_year:
            raise ValueError(f"published_year must be between 1800 and {current_year}")
        return v


class BookOut(BookBase):
    id: int
    author_id: int

    class Config:
        from_attributes = True
