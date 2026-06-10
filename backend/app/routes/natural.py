import re

from fastapi import APIRouter

from app.routes.hybrid import hybrid_search

router = APIRouter()


@router.get("/natural-search")
def natural_search(prompt: str):

    max_price = 999

    min_reviews = 0

    min_rating = 0

    min_date = "2000-01-01"

    query = prompt

    # -----------------------
    # Precio
    # -----------------------

    price_match = re.search(
        r"(\d+)\s*(dolares|dólares|usd|\$)",
        prompt.lower()
    )

    if price_match:
        max_price = float(
            price_match.group(1)
        )

    # -----------------------
    # Año
    # -----------------------

    year_match = re.search(
        r"(20\d{2})",
        prompt
    )

    if year_match:
        min_date = (
            f"{year_match.group(1)}-01-01"
        )

    # -----------------------
    # Popular
    # -----------------------

    if (
        "popular" in prompt.lower()
        or
        "populares" in prompt.lower()
    ):
        min_reviews = 10000

    # -----------------------
    # Muy popular
    # -----------------------

    if (
        "muy popular" in prompt.lower()
        or
        "muy populares" in prompt.lower()
    ):
        min_reviews = 100000

    # -----------------------
    # Bien valorado
    # -----------------------

    if (
        "bien valorado" in prompt.lower()
        or
        "bien valorados" in prompt.lower()
    ):
        min_rating = 80

    # -----------------------
    # Consulta semántica
    # -----------------------

    replacements = {
        "dark souls": "souls-like dark fantasy action rpg",
        "elden ring": "souls-like open world dark fantasy action rpg",
        "skyrim": "open world fantasy rpg",
        "stardew valley": "farming life simulator",
        "counter strike": "competitive multiplayer fps",
        "minecraft": "sandbox crafting survival",
        "terraria": "pixel art sandbox adventure",
        "zelda": "open world fantasy adventure"
    }

    query_lower = prompt.lower()

    for key, value in replacements.items():

        if key in query_lower:
            query = value
            break

    return hybrid_search(
        query=query,
        max_price=max_price,
        min_date=min_date,
        min_reviews=min_reviews,
        min_rating=min_rating
    )