import psycopg2
import pandas as pd

conn = psycopg2.connect(
    host="localhost",
    port="5432",
    database="steam_search",
    user="postgres",
    password="1234"
)

query = """
SELECT
    id,
    name,
    price
FROM games
LIMIT 10
"""

df = pd.read_sql(query, conn)

print(df)

conn.close()