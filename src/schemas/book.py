from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from enum import Enum


class GenreEnum(str, Enum):
    fiction = "Fiction"
    non_fiction = "Non-Fiction"
    science = "Science"
    history = "History"


class BookBase(BaseModel):
    title: str = Field(..., min_length=1)
    genre: GenreEnum
    published_year: int

    @field_validator("published_year")
    @classmethod
    def validate_year(cls, v):
        if v < 0:
            raise ValueError("Year must be positive")
        return v


class BookCreate(BookBase):
    author_id: int


class BookUpdate(BaseModel):
    title: Optional[str] = None
    genre: Optional[GenreEnum] = None
    published_year: Optional[int] = None
    author_id: Optional[int] = None

    @field_validator("published_year")
    @classmethod
    def validate_year(cls, v):
        if v < 0:
            raise ValueError("Year must be positive")
        return v


class BookOut(BookBase):
    id: int
    author_id: int

    model_config = ConfigDict(from_attributes=True)
