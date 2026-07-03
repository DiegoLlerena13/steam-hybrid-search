import pandas as pd

from sqlalchemy import text
from app.model import model


def semantic_search(query, conn, limit=10):
    """
    Ejecuta la búsqueda vectorial pura.

    Este método funciona como baseline experimental frente al sistema híbrido.
    No aplica filtros SQL de precio, fecha, reseñas ni rating. Solo ordena los
    videojuegos por cercanía semántica entre el embedding de la consulta y el
    embedding almacenado en PostgreSQL mediante pgvector.

    Se devuelve appid porque la evaluación corregida calcula Recall@10 usando
    identificadores únicos de Steam, evitando errores por diferencias en nombres,
    símbolos, subtítulos o ediciones.
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
            1 - (
                embedding <=> CAST(:embedding AS vector)
            ) AS similarity
        FROM games
        ORDER BY embedding <=> CAST(:embedding AS vector)
        LIMIT :limit
    """)

    result = pd.read_sql(
        sql,
        conn,
        params={
            "embedding": str(query_embedding),
            "limit": limit
        }
    )

    return result