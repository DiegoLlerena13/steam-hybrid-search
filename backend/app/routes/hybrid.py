from fastapi import APIRouter
from sqlalchemy import text

from app.database import engine
from app.model import model

router = APIRouter()

@router.get("/hybrid-search")
def hybrid_search(
    query: str,
    max_price: float = 999,
    min_date: str = "2000-01-01",
    min_reviews: int = 0,
    min_rating: float = 0
):

    query_embedding = model.encode(query).tolist()

    sql = text("""
    SELECT
        name,
        price,
        release_date,
        pct_pos_total,
        num_reviews_total,

        1 - (
            embedding <=> CAST(:embedding AS vector)
        ) AS similarity,

        (
            (1 - (embedding <=> CAST(:embedding AS vector))) * 0.75
            +
            (LEAST(num_reviews_total, 100000) / 100000.0) * 0.20
            +
            (pct_pos_total / 100.0) * 0.05
        ) AS final_score

    FROM games

    WHERE price <= :max_price
    AND release_date >= :min_date
    AND num_reviews_total >= :min_reviews
    AND pct_pos_total >= :min_rating

    ORDER BY final_score DESC

    LIMIT 10
    """)

    with engine.connect() as conn:
        result = conn.execute(
            sql,
            {
                "embedding": str(query_embedding),
                "max_price": max_price,
                "min_date": min_date,
                "min_reviews": min_reviews,
                "min_rating": min_rating
            }
        )

        rows = result.fetchall()

    return [
        {
            "name": row.name,
            "price": row.price,
            "release_date": str(row.release_date),
            "rating": row.pct_pos_total,
            "reviews": row.num_reviews_total,
            "similarity": float(row.similarity),
            "final_score": float(row.final_score)
        }
        for row in rows
    ]