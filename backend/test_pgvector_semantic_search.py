import psycopg2
import pandas as pd

from sentence_transformers import SentenceTransformer

# -------------------------
# Conexion
# -------------------------

conn = psycopg2.connect(
    host="localhost",
    port="5432",
    database="steam_search",
    user="postgres",
    password="1234"
)

cursor = conn.cursor()

# -------------------------
# Modelo
# -------------------------

model = SentenceTransformer(
    "BAAI/bge-base-en-v1.5"
)

# -------------------------
# Consulta
# -------------------------

query = "zombie survival multiplayer"

query_embedding = model.encode(query)

vector_str = "[" + ",".join(
    map(str, query_embedding)
) + "]"

# -------------------------
# SQL Vector Search
# -------------------------

sql = f"""
SELECT
    name,
    price,
    1 - (embedding <=> '{vector_str}'::vector) AS similarity
FROM games
ORDER BY embedding <=> '{vector_str}'::vector
LIMIT 10;
"""

df = pd.read_sql(sql, conn)

print(df)

conn.close()