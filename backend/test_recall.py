import pandas as pd
import numpy as np

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# -------------------------
# cargar datos
# -------------------------

df = pd.read_csv("../dataset/games_processed.csv")
df = df.head(500)

embeddings = np.load("../dataset/embeddings.npy")

model = SentenceTransformer(
    "BAAI/bge-base-en-v1.5"
)

# -------------------------
# consulta
# -------------------------

query = "zombie survival multiplayer"

# juegos que consideramos relevantes
relevant_games = [
    "Project Zomboid",
    "Unturned",
    "DayZ",
    "7 Days to Die",
    "State of Decay 2: Juggernaut Edition"
]

# -------------------------
# embedding consulta
# -------------------------

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

top_k = 10

retrieved = results.head(top_k)

retrieved_names = retrieved["name"].tolist()

# -------------------------
# Recall@K
# -------------------------

hits = 0

for game in relevant_games:
    if game in retrieved_names:
        hits += 1

recall = hits / len(relevant_games)

print("\nConsulta:")
print(query)

print("\nTop 10 encontrados:")
for name in retrieved_names:
    print("-", name)

print("\nJuegos relevantes:")
for game in relevant_games:
    print("-", game)

print("\nHits:", hits)

print("Recall@10:", recall)