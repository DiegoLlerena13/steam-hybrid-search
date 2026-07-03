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


def clean_description(text_value):
    if not text_value:
        return ""

    text_value = str(text_value)

    text_value = re.sub(r"<.*?>", " ", text_value)

    text_value = text_value.replace("&amp;", "&")
    text_value = text_value.replace("&quot;", '"')
    text_value = text_value.replace("&#39;", "'")

    text_value = re.sub(r"\s+", " ", text_value).strip()

    if len(text_value) > 500:
        return text_value[:500] + "..."

    return text_value


@router.get("/hybrid-search")
def hybrid_search(
    query: str,
    max_price: float = 999,
    min_date: str = "2000-01-01",
    max_date: str = "2100-01-01",
    min_reviews: int = 0,
    min_rating: float = 0,
    similarity_weight: float = 0.75,
    popularity_weight: float = 0.20,
    rating_weight: float = 0.05,
    title_query_compact: str = ""
):
    query_embedding = model.encode(query).tolist()

    sql = text("""
    SELECT
        appid,
        name,
        COALESCE(price, 0) AS price,
        release_date,
        genres,
        tags,
        COALESCE(pct_pos_total, 0) AS pct_pos_total,
        COALESCE(num_reviews_total, 0) AS num_reviews_total,
        about_the_game,
        detailed_description,

        1 - (
            embedding <=> CAST(:embedding AS vector)
        ) AS similarity,

        (
            (1 - (embedding <=> CAST(:embedding AS vector))) * :similarity_weight
            +
            (LEAST(COALESCE(num_reviews_total, 0), 100000) / 100000.0) * :popularity_weight
            +
            (COALESCE(pct_pos_total, 0) / 100.0) * :rating_weight
        ) AS final_score,

        CASE
            WHEN :title_query_compact <> ''
            AND regexp_replace(lower(name), '[^a-z0-9]+', '', 'g') = :title_query_compact
            THEN 2

            WHEN :title_query_compact <> ''
            AND regexp_replace(lower(name), '[^a-z0-9]+', '', 'g') LIKE '%' || :title_query_compact || '%'
            THEN 1

            ELSE 0
        END AS title_match_score

    FROM games

    WHERE COALESCE(price, 0) <= :max_price
    AND release_date >= CAST(:min_date AS date)
    AND release_date <= CAST(:max_date AS date)
    AND COALESCE(num_reviews_total, 0) >= :min_reviews
    AND COALESCE(pct_pos_total, 0) >= :min_rating

    ORDER BY title_match_score DESC, final_score DESC

    LIMIT 10
    """)

    with engine.connect() as conn:
        result = conn.execute(
            sql,
            {
                "embedding": str(query_embedding),
                "max_price": max_price,
                "min_date": min_date,
                "max_date": max_date,
                "min_reviews": min_reviews,
                "min_rating": min_rating,
                "similarity_weight": similarity_weight,
                "popularity_weight": popularity_weight,
                "rating_weight": rating_weight,
                "title_query_compact": title_query_compact
            }
        )

        rows = result.fetchall()

    return [
        {
            "appid": int(row.appid),
            "name": row.name,
            "price": float(row.price),
            "release_date": str(row.release_date),
            "genres": clean_genres(row.genres),
            "tags": clean_tags(row.tags),
            "description": clean_description(
                row.about_the_game
                if row.about_the_game
                else row.detailed_description
            ),
            "rating": float(row.pct_pos_total),
            "reviews": int(row.num_reviews_total),
            "similarity": float(row.similarity),
            "final_score": float(row.final_score),
            "title_match_score": int(row.title_match_score)
        }
        for row in rows
    ]