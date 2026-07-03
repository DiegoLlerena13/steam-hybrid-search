import re
import unicodedata
from fastapi import APIRouter

from app.routes.hybrid import hybrid_search

router = APIRouter()


def normalize_text(text: str) -> str:
    text = text.lower()

    text = unicodedata.normalize("NFKD", text)
    text = "".join(
        char for char in text
        if not unicodedata.combining(char)
    )

    return text


def compact_title_text(text: str) -> str:
    text = normalize_text(text)
    return re.sub(r"[^a-z0-9]+", "", text)


def clean_possible_title_query(text: str) -> str:
    text = normalize_text(text)

    filler_words = [
        "busco", "buscar", "quiero", "dame", "muestrame", "mostrar",
        "recomiendame", "recomendar", "juego", "juegos", "videojuego",
        "videojuegos", "steam", "pc", "el", "la", "los", "las",
        "un", "una"
    ]

    for word in filler_words:
        text = re.sub(rf"\b{re.escape(word)}\b", " ", text)

    text = re.sub(r"\s+", " ", text).strip()

    return text


def is_direct_title_query(text: str) -> bool:
    text_normalized = normalize_text(text)

    semantic_markers = [
        "similar", "similares", "parecido", "parecidos", "tipo", "estilo",
        "como", "menos", "hasta", "maximo", "maxima", "despues", "antes",
        "entre", "popular", "populares", "bien valorado", "bien valorados",
        "zombie", "zombies", "terror", "supervivencia", "sandbox",
        "multijugador", "cooperativo", "cooperativos", "rpg", "fps",
        "mmorpg", "roguelike", "metroidvania", "carreras", "deportes",
        "futbol", "accion", "aventura", "fantasia", "estrategia",
        "simulacion", "plataformas", "casuales", "casual", "cartas",
        "mundo abierto", "exploracion", "granja", "espacial",
        "ciencia ficcion", "shooter", "shooters", "gratis", "baratos",
        "barato", "caros", "caro", "reseñas", "resenas", "rating"
    ]

    for marker in semantic_markers:
        if marker in text_normalized:
            return False

    cleaned_title = clean_possible_title_query(text_normalized)

    if cleaned_title == "":
        return False

    if len(cleaned_title.split()) > 5:
        return False

    compact_title = compact_title_text(cleaned_title)

    if len(compact_title) < 4:
        return False

    return True


def detect_title_query_compact(text: str) -> str:
    if not is_direct_title_query(text):
        return ""

    cleaned_title = clean_possible_title_query(text)
    return compact_title_text(cleaned_title)


def detect_price(text: str):
    text = normalize_text(text)

    soles_match = re.search(
        r"(menos de|menor a|hasta|maximo|maxima|por debajo de)\s+(\d+)\s*(soles|s/)",
        text
    )

    if soles_match:
        soles = float(soles_match.group(2))
        return round(soles / 3.7, 2)

    dollars_match = re.search(
        r"(menos de|menor a|hasta|maximo|maxima|por debajo de)\s+(\d+)\s*(dolares|usd|\$)",
        text
    )

    if dollars_match:
        return float(dollars_match.group(2))

    return 999


def detect_year_range(text: str):
    text = normalize_text(text)

    range_match = re.search(
        r"entre\s+(20\d{2}|19\d{2})\s+y\s+(20\d{2}|19\d{2})",
        text
    )

    if range_match:
        start_year = range_match.group(1)
        end_year = range_match.group(2)
        return f"{start_year}-01-01", f"{end_year}-12-31"

    before_match = re.search(
        r"(antes de|antes del|anteriores a|anterior a|previos a|previo a)\s+(20\d{2}|19\d{2})",
        text
    )

    if before_match:
        year = int(before_match.group(2))
        end_year = year - 1
        return "2000-01-01", f"{end_year}-12-31"

    until_match = re.search(
        r"(hasta)\s+(20\d{2}|19\d{2})",
        text
    )

    if until_match:
        year = until_match.group(2)
        return "2000-01-01", f"{year}-12-31"

    after_match = re.search(
        r"(despues de|despues del|desde|posterior a|posteriores a|a partir de)\s+(20\d{2}|19\d{2})",
        text
    )

    if after_match:
        year = after_match.group(2)
        return f"{year}-01-01", "2100-01-01"

    year_match = re.search(r"(20\d{2}|19\d{2})", text)

    if year_match:
        year = year_match.group(1)
        return f"{year}-01-01", "2100-01-01"

    return "2000-01-01", "2100-01-01"


def detect_reviews(text: str):
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
    text_lower = normalize_text(text)

    replacements = {
        "dark souls iii": "DARK SOULS III souls-like dark fantasy action rpg difficult boss fights",
        "dark souls 3": "DARK SOULS III souls-like dark fantasy action rpg difficult boss fights",
        "dark souls": "DARK SOULS souls-like dark fantasy action rpg difficult boss fights",
        "darksouls": "DARK SOULS souls-like dark fantasy action rpg difficult boss fights",
        "elden ring": "ELDEN RING souls-like open world dark fantasy action rpg",
        "sekiro": "SEKIRO Shadows Die Twice difficult action combat samurai souls-like",

        "zombies": "zombie survival cooperative multiplayer shooter",
        "zombie": "zombie survival cooperative multiplayer shooter",

        "pixel art": "pixel art adventure indie platformer metroidvania",
        "metroidvania": "metroidvania dark fantasy platformer action adventure",
        "fantasia medieval": "medieval fantasy rpg open world story rich",
        "fantasia": "fantasy adventure rpg",

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
        "terror": "psychological horror survival scary",
        "horror": "horror survival psychological scary",
        "psicologico": "psychological horror survival scary",

        "espacial": "space exploration sci fi survival sandbox",
        "ciencia ficcion": "space exploration sci fi survival sandbox",

        "estrategia por turnos": "turn based strategy civilization empire",
        "civilizacion": "turn based strategy civilization empire",
        "gestion de colonias": "colony management survival strategy simulation",

        "carreras": "realistic racing driving simulation cars motorsport",
        "autos": "realistic racing driving simulation cars motorsport",
        "futbol": "football soccer sports simulation competitive",
        "deportes": "sports football soccer simulation",

        "anime": "anime fighting action jrpg visual novel character combat",
        "jrpg": "anime jrpg story rich action adventure",
        "peleas": "fighting action combat anime arena",
        "lucha": "fighting action combat anime arena",

        "mmorpg": "massively multiplayer online fantasy rpg",
        "online masivo": "massively multiplayer online fantasy rpg",

        "shooters": "competitive multiplayer fps tactical shooter",
        "shooter": "competitive multiplayer fps tactical shooter",
        "fps": "competitive multiplayer fps tactical shooter",
        "competitivos": "competitive multiplayer fps tactical shooter",
        "multijugador": "multiplayer online competitive",

        "mundo abierto": "open world exploration adventure rpg",
        "exploracion": "exploration adventure open world",
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
        "juegos", "juego", "videojuegos", "videojuego",
        "similares", "similar", "parecidos", "parecido",
        "como", "que", "cuesten", "cueste", "menos", "mas",
        "de", "del", "despues", "antes", "entre", "hasta",
        "desde", "populares", "popular", "bien", "valorados", "valorado",
        "soles", "dolares", "usd", "a", "y", "con",
        "precio", "resenas", "reviews", "maximo", "maxima",
        "minimo", "al", "por"
    ]

    for word in words_to_remove:
        clean_text = re.sub(rf"\b{re.escape(word)}\b", " ", clean_text)

    clean_text = re.sub(r"\d+", "", clean_text)
    clean_text = re.sub(r"\s+", " ", clean_text).strip()

    if clean_text == "":
        return text

    return clean_text


@router.get("/natural-search")
def natural_search(
    prompt: str,
    similarity_weight: float = 0.75,
    popularity_weight: float = 0.20,
    rating_weight: float = 0.05
):
    interpreted_query = detect_query(prompt)
    title_query_compact = detect_title_query_compact(prompt)

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
        min_rating=min_rating,
        similarity_weight=similarity_weight,
        popularity_weight=popularity_weight,
        rating_weight=rating_weight,
        title_query_compact=title_query_compact
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
            "title_query_compact": title_query_compact,
            "recognized_filters": {
                "price": f"price <= {max_price}",
                "release_date_min": f"release_date >= {min_date}",
                "release_date_max": f"release_date <= {max_date}",
                "reviews": f"num_reviews_total >= {min_reviews}",
                "rating": f"pct_pos_total >= {min_rating}"
            },
            "vector_part": "La consulta interpretada se transforma en un embedding y pgvector compara ese vector contra los embeddings almacenados.",
            "sql_part": "SQL filtra videojuegos por precio máximo, rango de fecha, cantidad de reseñas y rating positivo.",
            "ranking_formula": (
                f"final_score = {similarity_weight} * semantic_similarity "
                f"+ {popularity_weight} * normalized_popularity "
                f"+ {rating_weight} * positive_rating"
            ),
            "ranking_weights": {
                "semantic_similarity": similarity_weight,
                "normalized_popularity": popularity_weight,
                "positive_rating": rating_weight
            }
        },
        "results": results
    }