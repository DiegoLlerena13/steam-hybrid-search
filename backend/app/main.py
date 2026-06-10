from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from app.search import semantic_search
from app.routes.hybrid import router as hybrid_router
from app.routes.natural import router as natural_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(hybrid_router)
app.include_router(natural_router)

@app.get("/")
def home():
    return {
        "message": "Steam Hybrid Search API"
    }

@app.get("/search")
def search_games(query: str):
    with engine.connect() as conn:
        results = semantic_search(query, conn)

        return results.to_dict(
            orient="records"
        )