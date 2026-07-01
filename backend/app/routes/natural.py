import re
import unicodedata
from fastapi import APIRouter

from app.routes.hybrid import hybrid_search

router = APIRouter()


def normalize_text(text: str) -> str:
    """
    Normaliza el texto ingresado por el usuario.

    Se eliminan tildes y se pasa todo a minúsculas para que expresiones como
    'dólares', 'dolares', 'después' o 'despues' sean interpretadas de la misma forma.
    """
    text = text.lower()

    text = unicodedata.normalize("NFKD", text)
    text = "".join(
        char for char in text
        if not unicodedata.combining(char)
    )

    return text


def detect_price(text: str):
    """
    Detecta restricciones de precio desde lenguaje natural.

    Ejemplos:
    - "menos de 60 dólares" -> 60
    - "menos de 200 soles" -> conversión aproximada a dólares
    - Si no se detecta precio, se usa 999 como valor amplio por defecto.
    """
    text = normalize_text(text)

    soles_match = re.search(r"(\d+)\s*(soles|s/)", text)
    if soles_match:
        soles = float(soles_match.group(1))
        return round(soles / 3.7, 2)

    dollars_match = re.search(
        r"(\d+)\s*(dolares|usd|\$)",
        text
    )
    if dollars_match:
        return float(dollars_match.group(1))

    return 999


def detect_year_range(text: str):
    """
    Detecta rango de fechas desde lenguaje natural.

    Ejemplos:
    - "entre 2015 y 2024" -> 2015-01-01 a 2024-12-31
    - "después de 2020" -> 2020-01-01 a 2100-01-01
    - "antes de 2018" -> 2000-01-01 a 2018-12-31

    Esto permite que la búsqueda híbrida aproveche filtros relacionales.
    """
    text = normalize_text(text)

    range_match = re.search(
        r"entre\s+(20\d{2}|19\d{2})\s+y\s+(20\d{2}|19\d{2})",
        text
    )

    if range_match:
        start_year = range_match.group(1)
        end_year = range_match.group(2)
        return f"{start_year}-01-01", f"{end_year}-12-31"

    after_match = re.search(
        r"(despues de|desde|posterior a|a partir de)\s+(20\d{2}|19\d{2})",
        text
    )

    if after_match:
        year = after_match.group(2)
        return f"{year}-01-01", "2100-01-01"

    before_match = re.search(
        r"(antes de|hasta)\s+(20\d{2}|19\d{2})",
        text
    )

    if before_match:
        year = before_match.group(2)
        return "2000-01-01", f"{year}-12-31"

    year_match = re.search(r"(20\d{2}|19\d{2})", text)

    if year_match:
        year = year_match.group(1)
        return f"{year}-01-01", "2100-01-01"

    return "2000-01-01", "2100-01-01"


def detect_reviews(text: str):
    """
    Detecta restricciones de popularidad a partir de reseñas.

    Ejemplos:
    - "más de 10000 reseñas" -> 10000
    - "populares" -> 10000
    - "muy populares" -> 100000
    """
    text = normalize_text(text)

    explicit_reviews = re.search(
        r"(mas de|al menos|minimo)\s+(\d+)\s*(resenas|reviews)",
        text
    )

    if explicit_reviews:
        return int(explicit_reviews.group(2))

    if "muy popular" in text or "muy populares" in text:
        return 100000

    if (
        "popular" in text
        or "populares" in text
        or "muchas resenas" in text
    ):
        return 10000

    return 0


def detect_rating(text: str):
    """
    Detecta restricciones de valoración positiva.

    Ejemplos:
    - "al menos 80%" -> 80
    - "bien valorados" -> 80
    - "muy bien valorados" -> 90
    """
    text = normalize_text(text)

    explicit_rating = re.search(
        r"(mas de|al menos|minimo)\s+(\d+)\s*%",
        text
    )

    if explicit_rating:
        return float(explicit_rating.group(2))

    if "muy bien valorado" in text or "muy bien valorados" in text:
        return 90

    if "bien valorado" in text or "bien valorados" in text:
        return 80

    if "valoraciones positivas" in text:
        return 80

    return 0


def detect_query(text: str):
    """
    Convierte una consulta en español a una consulta semántica más útil
    para el modelo de embeddings.

    Esta parte no reemplaza la búsqueda vectorial; la guía. Por ejemplo,
    si el usuario escribe "juegos tipo Dark Souls", el sistema interpreta
    conceptos como souls-like, fantasía oscura, acción, RPG y jefes difíciles.
    """
    text_lower = normalize_text(text)

    replacements = {
        "dark souls": "souls-like dark fantasy action rpg difficult boss fights",
        "darksouls": "souls-like dark fantasy action rpg difficult boss fights",
        "elden ring": "souls-like open world dark fantasy action rpg",
        "sekiro": "difficult action combat samurai souls-like",

        "zombies": "zombie survival cooperative multiplayer shooter",
        "zombie": "zombie survival cooperative multiplayer shooter",

        "pixel art": "pixel art adventure indie platformer metroidvania",
        "metroidvania": "metroidvania dark fantasy platformer action adventure",
        "mundo abierto": "open world fantasy adventure exploration",
        "fantasia medieval": "medieval fantasy rpg open world story rich",

        "granja": "farming life simulator relaxing cozy",
        "vida relajante": "cozy relaxing casual farming life simulation",
        "cozy": "cozy relaxing casual farming wholesome life simulation",
        "relajantes": "cozy relaxing casual wholesome life simulation",
        "relajante": "cozy relaxing casual wholesome life simulation",

        "sandbox": "sandbox crafting survival open world",
        "supervivencia": "survival crafting open world multiplayer",
        "crafting": "sandbox crafting survival open world",

        "roguelike": "roguelike action dungeon crawler",
        "mazmorras": "roguelike action dungeon crawler",
        "deckbuilding": "card strategy roguelike deckbuilding tactical cards",
        "cartas": "card strategy roguelike deckbuilding tactical cards",

        "city builder": "city builder management strategy construction simulation",
        "construccion de ciudades": "city builder management strategy construction simulation",

        "terror psicologico": "psychological horror survival scary",
        "horror": "horror survival psychological scary",

        "espacial": "space exploration sci fi survival sandbox",
        "ciencia ficcion": "space exploration sci fi survival sandbox",

        "estrategia por turnos": "turn based strategy civilization empire",
        "civilizacion": "turn based strategy civilization empire",

        "carreras": "realistic racing driving simulation cars motorsport",
        "autos": "realistic racing driving simulation cars motorsport",
        "futbol": "football soccer sports simulation competitive",
        "deportes": "sports football soccer simulation",

        "anime": "anime fighting action jrpg visual style character combat adventure",
        "peleas": "fighting action combat arena martial arts multiplayer",
        "lucha": "fighting action combat arena martial arts multiplayer",

        "mmorpg": "massively multiplayer online fantasy rpg",
        "online masivo": "massively multiplayer online fantasy rpg",
        
        "shooters": "competitive multiplayer fps tactical shooter",
        "shooter": "competitive multiplayer fps tactical shooter",
        "fps": "competitive multiplayer fps tactical shooter",
        "competitivos": "competitive multiplayer fps tactical shooter",
        "multijugador": "multiplayer online competitive",

        "mundo abierto": "open world exploration adventure rpg",
        "exploracion": "exploration adventure open world",
        "exploración": "exploration adventure open world",

        "terror psicologico": "psychological horror survival scary",
        "terror": "psychological horror survival scary",
        "psicologico": "psychological horror survival scary",
        "psicológico": "psychological horror survival scary",

        "anime": "anime fighting action jrpg visual novel character combat",
        "jrpg": "anime jrpg story rich action adventure",
        "peleas": "fighting action combat anime arena",
        "lucha": "fighting action combat anime arena",
    }

    interpreted_terms = []

    for key, value in replacements.items():
        if key in text_lower:
            interpreted_terms.append(value)

    if interpreted_terms:
        joined_terms = " ".join(interpreted_terms)
        unique_terms = dict.fromkeys(joined_terms.split())
        return " ".join(unique_terms)

    clean_text = text_lower

    words_to_remove = [
        "juegos", "juego", "similares", "similar", "parecidos", "parecido",
        "como", "que", "cuesten", "cueste", "menos", "mas",
        "de", "del", "despues", "antes", "entre", "hasta",
        "desde", "populares", "popular", "bien", "valorados", "valorado",
        "soles", "dolares", "usd", "a", "y", "con",
        "precio", "resenas", "reviews"
    ]

    for word in words_to_remove:
        clean_text = re.sub(rf"\b{re.escape(word)}\b", " ", clean_text)

    clean_text = re.sub(r"\d+", "", clean_text)
    clean_text = re.sub(r"\s+", " ", clean_text).strip()

    if clean_text == "":
        return text

    return clean_text


@router.get("/natural-search")
def natural_search(prompt: str):
    """
    Endpoint principal para consultas en lenguaje natural.

    El usuario solo escribe una consulta en una caja de texto.
    El sistema extrae internamente:
    - consulta semántica
    - precio máximo
    - fecha mínima y máxima
    - popularidad por reseñas
    - rating mínimo

    Luego llama a la búsqueda híbrida, que combina embeddings + filtros SQL.
    """
    interpreted_query = detect_query(prompt)
    max_price = detect_price(prompt)
    min_date, max_date = detect_year_range(prompt)
    min_reviews = detect_reviews(prompt)
    min_rating = detect_rating(prompt)

    results = hybrid_search(
        query=interpreted_query,
        max_price=max_price,
        min_date=min_date,
        max_date=max_date,
        min_reviews=min_reviews,
        min_rating=min_rating
    )

    semantic_tags = interpreted_query.split()

    return {
        "original_prompt": prompt,
        "interpreted_query": interpreted_query,
        "extracted_tags": semantic_tags,
        "filters": {
            "max_price_usd": max_price,
            "min_date": min_date,
            "max_date": max_date,
            "min_reviews": min_reviews,
            "min_rating": min_rating
        },
        "transparency": {
            "semantic_tags": semantic_tags,
            "recognized_filters": {
                "price": f"price <= {max_price}",
                "release_date_min": f"release_date >= {min_date}",
                "release_date_max": f"release_date <= {max_date}",
                "reviews": f"num_reviews_total >= {min_reviews}",
                "rating": f"pct_pos_total >= {min_rating}"
            },
            "vector_part": "La consulta interpretada se transforma en un embedding y pgvector compara ese vector contra los embeddings almacenados.",
            "sql_part": "SQL filtra videojuegos por precio, rango de fecha, cantidad de reseñas y rating positivo.",
            "ranking_formula": "final_score = 0.75 * semantic_similarity + 0.20 * normalized_popularity + 0.05 * positive_rating",
            "ranking_weights": {
                "semantic_similarity": 0.75,
                "normalized_popularity": 0.20,
                "positive_rating": 0.05
            }
        },
        "results": results
    }