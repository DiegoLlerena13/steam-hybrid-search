from fastapi import FastAPI

from app.database import engine
from app.search import semantic_search

app = FastAPI()

@app.get("/")
def home():
    return {
        "message": "Steam Hybrid Search API"
    }

@app.get("/search")
def search_games(
    query: str
):
    with engine.connect() as conn:

        results = semantic_search(
            query,
            conn
        )

        return results.to_dict(
            orient="records"
        )