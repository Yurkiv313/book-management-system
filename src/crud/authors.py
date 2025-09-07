from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from src.db.models import Author
from src.schemas.author import AuthorCreate
from typing import List


async def create_author(db: AsyncSession, author: AuthorCreate) -> Author:
    new_author = Author(name=author.name)
    db.add(new_author)
    await db.commit()
    await db.refresh(new_author)
    return new_author


async def get_authors(db: AsyncSession):
    result = await db.execute(select(Author))
    return result.scalars().all()


async def bulk_import_authors(db: AsyncSession, authors: List[AuthorCreate]):
    results = []
    for author in authors:
        # Перевірка чи існує автор
        check_query = text("SELECT id, name FROM authors WHERE name = :name")
        existing = await db.execute(check_query, {"name": author.name})
        row = existing.mappings().first()

        if row:  # вже є → додаємо у results, але не вставляємо
            results.append(row)
        else:    # ще нема → вставляємо
            insert_query = text("""
                INSERT INTO authors (name)
                VALUES (:name)
                RETURNING id, name
            """)
            result = await db.execute(insert_query, {"name": author.name})
            row = result.mappings().first()
            results.append(row)

    await db.commit()
    return results