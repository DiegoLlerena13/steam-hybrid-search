import pandas as pd
import numpy as np
import psycopg2

# -------------------------
# Conexion PostgreSQL
# -------------------------

conn = psycopg2.connect(
    host="localhost",
    database="steam_search",
    user="postgres",
    password="1234"
)

cursor = conn.cursor()

# -------------------------
# Dataset
# -------------------------

df = pd.read_csv(
    "../dataset/games_processed.csv"
)

# -------------------------
# Embeddings
# -------------------------

embeddings = np.load(
    "../dataset/embeddings.npy"
)

print("Juegos:", len(df))
print("Embeddings:", len(embeddings))

# -------------------------
# Insertar
# -------------------------

for i, row in df.iterrows():

    embedding = embeddings[i].tolist()

    cursor.execute(
        """
        INSERT INTO games(
            appid,
            name,
            price,
            release_date,

            genres,
            tags,

            developers,
            publishers,

            positive,
            negative,

            pct_pos_total,
            num_reviews_total,

            average_playtime_forever,

            semantic_text,
            embedding
        )
        VALUES (
            %s,%s,%s,%s,
            %s,%s,
            %s,%s,
            %s,%s,
            %s,%s,
            %s,
            %s,%s
        )
        """,
        (
            int(row["appid"]),
            row["name"],
            float(row["price"]),
            row["release_date"],

            str(row["genres"]),
            str(row["tags"]),

            str(row["developers"]),
            str(row["publishers"]),

            int(row["positive"]) if pd.notna(row["positive"]) else 0,
            int(row["negative"]) if pd.notna(row["negative"]) else 0,

            float(row["pct_pos_total"]) if pd.notna(row["pct_pos_total"]) else 0,
            int(row["num_reviews_total"]) if pd.notna(row["num_reviews_total"]) else 0,

            float(row["average_playtime_forever"]) if pd.notna(row["average_playtime_forever"]) else 0,

            row["semantic_text"],
            embedding
        )
    )

    if i % 1000 == 0:
        print(f"Insertados {i}")

conn.commit()

cursor.close()
conn.close()

print("Carga finalizada")