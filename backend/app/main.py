from fastapi import FastAPI

from app.database import engine
from app.search import semantic_search

from app.routes.hybrid import router as hybrid_router

app = FastAPI()

app.include_router(hybrid_router)

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