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
# Cargar dataset
# -------------------------

df = pd.read_csv(
    "../dataset/games_processed.csv"
)

df = df.head(500)
# -------------------------
# Cargar embeddings
# -------------------------

embeddings = np.load(
    "../dataset/embeddings.npy"
)

print("Juegos:", len(df))
print("Embeddings:", len(embeddings))

# -------------------------
# Insertar registros
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
            semantic_text,
            embedding
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        """,
        (
            int(row["appid"]),
            row["name"],
            float(row["price"]),
            row["release_date"],
            row["semantic_text"],
            embedding
        )
    )

    if i % 100 == 0:
        print(f"Insertados {i}")

# -------------------------
# Guardar cambios
# -------------------------

conn.commit()

cursor.close()
conn.close()

print("Carga finalizada")