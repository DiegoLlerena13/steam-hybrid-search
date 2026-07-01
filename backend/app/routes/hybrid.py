from fastapi import APIRouter
from sqlalchemy import text
import ast
import re

from app.database import engine
from app.model import model

router = APIRouter()


def clean_tags(tags_text):
    try:
        tags_dict = ast.literal_eval(tags_text)

        if isinstance(tags_dict, dict):
            return list(tags_dict.keys())[:10]

        if isinstance(tags_dict, list):
            return tags_dict[:10]

    except Exception:
        return []

    return []


def clean_genres(genres_text):
    try:
        genres_list = ast.literal_eval(genres_text)

        if isinstance(genres_list, list):
            return genres_list

    except Exception:
        return []

    return []


def clean_description(text):
    if not text:
        return ""

    text = str(text)

    # Quitar etiquetas HTML simples
    text = re.sub(r"<.*?>", " ", text)

    # Quitar entidades comunes
    text = text.replace("&amp;", "&")
    text = text.replace("&quot;", '"')
    text = text.replace("&#39;", "'")

    # Limpiar espacios
    text = re.sub(r"\s+", " ", text).strip()

    if len(text) > 500:
        return text[:500] + "..."

    return text


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
        appid,
        name,
        price,
        release_date,
        genres,
        tags,
        pct_pos_total,
        num_reviews_total,
        about_the_game,
        detailed_description,

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
            "appid": row.appid,
            "name": row.name,
            "price": row.price,
            "release_date": str(row.release_date),
            "genres": clean_genres(row.genres),
            "tags": clean_tags(row.tags),
            "description": clean_description(
                row.about_the_game
                if row.about_the_game
                else row.detailed_description
            ),
            "rating": row.pct_pos_total,
            "reviews": row.num_reviews_total,
            "similarity": float(row.similarity),
            "final_score": float(row.final_score)
        }
        for row in rows
    ]