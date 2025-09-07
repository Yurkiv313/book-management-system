from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from enum import Enum

Base = declarative_base()


class GenreEnum(str, Enum):
    fiction = "Fiction"
    non_fiction = "Non-Fiction"
    science = "Science"
    history = "History"


class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    books = relationship("Book", back_populates="author")


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    genre = Column(String, nullable=False)
    published_year = Column(Integer, nullable=False)

    author_id = Column(Integer, ForeignKey("authors.id"))
    author = relationship("Author", back_populates="books")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="user")
