from fastapi import APIRouter
from sqlalchemy import text
import ast
import re

from app.database import engine
from app.model import model

router = APIRouter()


def clean_tags(tags_text):
    """
    Limpia el campo de tags almacenado en PostgreSQL.

    En el dataset de Steam, los tags pueden venir como diccionario o lista
    serializada en texto. Esta función permite mostrar solo las etiquetas
    principales en la respuesta del sistema.
    """
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
    """
    Limpia el campo de géneros.

    Esto evita devolver texto crudo o estructuras serializadas en la interfaz.
    """
    try:
        genres_list = ast.literal_eval(genres_text)

        if isinstance(genres_list, list):
            return genres_list

    except Exception:
        return []

    return []


def clean_description(text_value):
    """
    Limpia la descripción del videojuego para mostrarla al usuario.

    Se eliminan etiquetas HTML simples, entidades comunes y espacios repetidos.
    También se recorta el texto para que la respuesta no sea demasiado extensa.
    """
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
    rating_weight: float = 0.05
):
    """
    Ejecuta la búsqueda híbrida del sistema.

    Esta función combina:
    1. Búsqueda semántica mediante embeddings y pgvector.
    2. Filtros relacionales SQL como precio, fecha, reseñas y rating.
    3. Ranking ponderado usando similitud, popularidad y valoración positiva.

    Se incluye appid en la respuesta porque la evaluación corregida debe comparar
    resultados usando el identificador único de Steam y no solo el nombre del juego.
    """

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
            (1 - (embedding <=> CAST(:embedding AS vector))) * :similarity_weight
            +
            (LEAST(num_reviews_total, 100000) / 100000.0) * :popularity_weight
            +
            (pct_pos_total / 100.0) * :rating_weight
        ) AS final_score

    FROM games

    WHERE price <= :max_price
    AND release_date >= :min_date
    AND release_date <= :max_date
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
            "max_date": max_date,
            "min_reviews": min_reviews,
            "min_rating": min_rating,
            "similarity_weight": similarity_weight,
            "popularity_weight": popularity_weight,
            "rating_weight": rating_weight
        }
    )

    rows = result.fetchall()

    return [
        {
            "appid": int(row.appid),
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