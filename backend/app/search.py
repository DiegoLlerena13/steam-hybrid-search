import pandas as pd

from sqlalchemy import text
from app.model import model


def semantic_search(query, conn, limit=10):
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