import pandas as pd

from sqlalchemy import text
from app.model import model
def semantic_search(
    query,
    conn
):
    query_embedding = model.encode(
        query
    ).tolist()

    sql = text("""
        SELECT
            name,
            price,
            1 - (
                embedding <=> CAST(:embedding AS vector)
            ) AS similarity
        FROM games
        ORDER BY embedding <=> CAST(:embedding AS vector)
        LIMIT 50
    """)

    result = pd.read_sql(
        sql,
        conn,
        params={
            "embedding": str(query_embedding)
        }
    )

    return result