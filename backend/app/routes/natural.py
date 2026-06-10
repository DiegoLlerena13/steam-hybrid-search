import re
from fastapi import APIRouter

from app.routes.hybrid import hybrid_search

router = APIRouter()


def detect_price(text: str):
    text = text.lower()

    soles_match = re.search(r"(\d+)\s*(soles|s/)", text)
    if soles_match:
        soles = float(soles_match.group(1))
        return round(soles / 3.7, 2)

    dollars_match = re.search(r"(\d+)\s*(dolares|dólares|usd|\$)", text)
    if dollars_match:
        return float(dollars_match.group(1))

    return 999


def detect_year(text: str):
    text = text.lower()

    year_match = re.search(r"(20\d{2}|19\d{2})", text)

    if not year_match:
        return "2000-01-01"

    year = year_match.group(1)

    if "antes" in text:
        return "2000-01-01"

    return f"{year}-01-01"


def detect_reviews(text: str):
    text = text.lower()

    if "muy popular" in text or "muy populares" in text:
        return 100000

    if "popular" in text or "populares" in text:
        return 10000

    return 0


def detect_rating(text: str):
    text = text.lower()

    if "muy bien valorado" in text or "muy bien valorados" in text:
        return 90

    if "bien valorado" in text or "bien valorados" in text:
        return 80

    return 0


def detect_query(text: str):
    text_lower = text.lower()

    replacements = {
        "dark souls": "souls-like dark fantasy action rpg difficult boss fights",
        "darksouls": "souls-like dark fantasy action rpg difficult boss fights",
        "elden ring": "souls-like open world dark fantasy action rpg",
        "sekiro": "difficult action combat samurai souls-like",
        "skyrim": "open world fantasy rpg adventure",
        "stardew valley": "farming life simulator relaxing pixel art",
        "terraria": "pixel art sandbox crafting adventure",
        "minecraft": "sandbox crafting survival open world",
        "counter strike": "competitive multiplayer fps tactical shooter",
        "left 4 dead": "zombie survival cooperative multiplayer shooter",
        "hollow knight": "metroidvania dark fantasy platformer action adventure",
        "the witcher": "open world fantasy rpg story rich",
        "zelda": "open world fantasy adventure exploration"
    }

    for key, value in replacements.items():
        if key in text_lower:
            return value

    clean_text = text_lower

    words_to_remove = [
        "juegos",
        "juego",
        "similares",
        "similar",
        "parecidos",
        "parecido",
        "como",
        "que",
        "cuesten",
        "cueste",
        "menos",
        "mas",
        "más",
        "de",
        "del",
        "despues",
        "después",
        "antes",
        "populares",
        "popular",
        "bien",
        "valorados",
        "valorado",
        "soles",
        "dolares",
        "dólares",
        "usd"
    ]

    for word in words_to_remove:
        clean_text = clean_text.replace(word, "")

    clean_text = re.sub(r"\d+", "", clean_text)
    clean_text = re.sub(r"\s+", " ", clean_text).strip()

    if clean_text == "":
        return text

    return clean_text


@router.get("/natural-search")
def natural_search(prompt: str):

    interpreted_query = detect_query(prompt)
    max_price = detect_price(prompt)
    min_date = detect_year(prompt)
    min_reviews = detect_reviews(prompt)
    min_rating = detect_rating(prompt)

    results = hybrid_search(
        query=interpreted_query,
        max_price=max_price,
        min_date=min_date,
        min_reviews=min_reviews,
        min_rating=min_rating
    )

    return {
        "original_prompt": prompt,
        "interpreted_query": interpreted_query,
        "filters": {
            "max_price_usd": max_price,
            "min_date": min_date,
            "min_reviews": min_reviews,
            "min_rating": min_rating
        },
        "results": results
    }