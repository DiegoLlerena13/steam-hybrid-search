import pandas as pd
import numpy as np

from sentence_transformers import SentenceTransformer

print("Cargando dataset...")

df = pd.read_csv("../dataset/games_processed.csv")

print("Cantidad de juegos:", len(df))

print("Cargando modelo...")

model = SentenceTransformer(
    "BAAI/bge-base-en-v1.5"
)

print("Generando embeddings...")

embeddings = model.encode(
    df["semantic_text"].tolist(),
    show_progress_bar=True
)

print("Shape:", embeddings.shape)

np.save(
    "../dataset/embeddings.npy",
    embeddings
)

print("Embeddings guardados correctamente")