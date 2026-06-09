import pandas as pd
import numpy as np

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# cargar dataset

df = pd.read_csv("../dataset/games_processed.csv")
# cargar embeddings

embeddings = np.load("../dataset/embeddings.npy")

# modelo

model = SentenceTransformer(
    "BAAI/bge-base-en-v1.5"
)

# ------------------------
# consulta
# ------------------------

query = "zombie survival multiplayer"

# ------------------------
# filtros SQL simulados
# ------------------------

filtered = df[
    (df["price"] < 50)
]

# embeddings del subconjunto

filtered_embeddings = embeddings[
    filtered.index
]

# embedding consulta

query_embedding = model.encode(query)

# similitud

scores = cosine_similarity(
    [query_embedding],
    filtered_embeddings
)[0]

filtered = filtered.copy()

filtered["score"] = scores

results = filtered.sort_values(
    "score",
    ascending=False
)

print(
    results[
        ["name","price","score"]
    ].head(10)
)