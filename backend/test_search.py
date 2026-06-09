import pandas as pd
import numpy as np

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

df = pd.read_csv("../dataset/games_processed.csv")

embeddings = np.load(
    "../dataset/embeddings.npy"
)

model = SentenceTransformer(
    "BAAI/bge-base-en-v1.5"
)

query = "pixel art revenge adventure"

query_embedding = model.encode(query)

scores = cosine_similarity(
    [query_embedding],
    embeddings
)[0]

df["score"] = scores

results = df.sort_values(
    "score",
    ascending=False
)

print(
    results[["name", "score"]].head(10)
)