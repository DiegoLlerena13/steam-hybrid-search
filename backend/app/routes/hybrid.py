from fastapi import APIRouter
from sqlalchemy import text

from app.database import engine
from app.model import model

router = APIRouter()

@router.get("/hybrid-search")
def hybrid_search(
    query: str,
    max_price: float = 999,
    min_date: str = "2000-01-01"
):

    query_embedding = model.encode(
        query
    ).tolist()

    sql = text("""
    SELECT
        name,
        price,
        release_date,
        1 - (
            embedding <=> CAST(:embedding AS vector)
        ) AS similarity
    FROM games
    WHERE price <= :max_price
    AND release_date >= :min_date
    ORDER BY embedding <=> CAST(:embedding AS vector)
    LIMIT 10
    """)

    with engine.connect() as conn:

        result = conn.execute(
            sql,
            {
                "embedding": str(query_embedding),
                "max_price": max_price,
                "min_date": min_date
            }
        )

        rows = result.fetchall()

    return [
        {
            "name": row.name,
            "price": row.price,
            "release_date": str(row.release_date),
            "similarity": float(row.similarity)
        }
        for row in rows
    ]