import json
import os
import re
import unicodedata
from typing import Any, Dict, List, Set

import pandas as pd
import requests
from sqlalchemy import text

from app.database import engine
from app.routes.natural import (
    detect_price,
    detect_year_range,
    detect_reviews,
    detect_rating,
)

BASE_URL = "http://127.0.0.1:8000"
K = 10

EVAL_LIMIT = int(os.getenv("EVAL_LIMIT", "0"))

WEIGHT_CONFIGS = [
    {
        "method": "Hibrida A 0.90/0.10/0.00",
        "similarity_weight": 0.90,
        "popularity_weight": 0.10,
        "rating_weight": 0.00,
    },
    {
        "method": "Hibrida B 0.80/0.15/0.05",
        "similarity_weight": 0.80,
        "popularity_weight": 0.15,
        "rating_weight": 0.05,
    },
    {
        "method": "Hibrida C 0.75/0.20/0.05",
        "similarity_weight": 0.75,
        "popularity_weight": 0.20,
        "rating_weight": 0.05,
    },
    {
        "method": "Hibrida D 0.60/0.30/0.10",
        "similarity_weight": 0.60,
        "popularity_weight": 0.30,
        "rating_weight": 0.10,
    },
    {
        "method": "Hibrida E 0.50/0.30/0.20",
        "similarity_weight": 0.50,
        "popularity_weight": 0.30,
        "rating_weight": 0.20,
    },
]

TESTS = [
    {
        "prompt": "quiero juegos de zombies cooperativos de supervivencia populares con menos de 60 dolares",
        "relevant": [
            "Project Zomboid",
            "DayZ",
            "7 Days to Die",
            "Unturned",
            "Dying Light",
        ],
    },
    {
        "prompt": "juegos tipo Dark Souls de fantasia oscura populares despues de 2015 y menos de 60 dolares",
        "relevant": [
            "ELDEN RING",
            "DARK SOULS III",
            "Sekiro Shadows Die Twice",
            "Hollow Knight",
            "Darkest Dungeon",
        ],
    },
    {
        "prompt": "busco juegos pixel art de aventura metroidvania bien valorados con menos de 40 dolares",
        "relevant": [
            "Hollow Knight",
            "Dead Cells",
            "Celeste",
            "Terraria",
            "Undertale",
        ],
    },
    {
        "prompt": "rpg de fantasia medieval populares entre 2015 y 2024",
        "relevant": [
            "The Witcher 3 Wild Hunt",
            "Baldur's Gate 3",
            "Divinity Original Sin 2",
            "ELDEN RING",
            "Kingdom Come Deliverance",
        ],
    },
    {
        "prompt": "juegos de supervivencia sandbox crafting mundo abierto populares",
        "relevant": [
            "Terraria",
            "Rust",
            "Raft",
            "Don't Starve Together",
            "Subnautica",
        ],
    },
    {
        "prompt": "juegos de exploracion espacial ciencia ficcion y supervivencia sandbox",
        "relevant": [
            "No Man's Sky",
            "Kerbal Space Program",
            "Space Engineers",
            "Astroneer",
            "Subnautica",
        ],
    },
    {
        "prompt": "simulacion de carreras realista con autos populares y menos de 70 dolares",
        "relevant": [
            "BeamNG.drive",
            "Assetto Corsa",
            "Forza Horizon 5",
            "Euro Truck Simulator 2",
            "American Truck Simulator",
        ],
    },
    {
        "prompt": "juegos de futbol deportes y simulacion populares",
        "relevant": [
            "EA SPORTS FC 24",
            "eFootball",
            "Rocket League",
            "FIFA 22",
            "Team Fortress 2",
        ],
    },
    {
        "prompt": "mmorpg de fantasia online masivo populares despues de 2010",
        "relevant": [
            "FINAL FANTASY XIV Online",
            "The Elder Scrolls Online",
            "Lost Ark",
            "New World Aeternum",
            "Path of Exile",
        ],
    },
    {
        "prompt": "roguelike de accion y mazmorras con muchas reseñas y menos de 40 dolares",
        "relevant": [
            "Hades",
            "Dead Cells",
            "The Binding of Isaac Rebirth",
            "Slay the Spire",
            "Balatro",
        ],
    },
    {
        "prompt": "city builder gestion de recursos y construccion populares entre 2015 y 2024",
        "relevant": [
            "Cities Skylines",
            "Frostpunk",
            "Factorio",
            "Satisfactory",
            "RimWorld",
        ],
    },
    {
        "prompt": "juegos de terror y supervivencia cooperativos para jugar con amigos con menos de 60 dolares",
        "relevant": [
            "The Forest",
            "Sons Of The Forest",
            "Phasmophobia",
            "Dead by Daylight",
            "Project Zomboid",
        ],
    },
    {
        "prompt": "juegos de cartas estrategia deckbuilding roguelike con menos de 40 dolares",
        "relevant": [
            "Slay the Spire",
            "Balatro",
            "Darkest Dungeon",
            "Dead Cells",
            "Cult of the Lamb",
        ],
    },
    {
        "prompt": "metroidvania y plataformas dificiles bien valorados con menos de 40 dolares",
        "relevant": [
            "Hollow Knight",
            "Dead Cells",
            "Celeste",
            "Geometry Dash",
            "Ori and the Will of the Wisps",
        ],
    },
    {
        "prompt": "juegos indie bien valorados con pixel art y aventura con menos de 40 dolares",
        "relevant": [
            "Hollow Knight",
            "Dead Cells",
            "Celeste",
            "Terraria",
            "Undertale",
        ],
    },
    {
        "prompt": "fps multijugador competitivos y tacticos populares con muchas reseñas",
        "relevant": [
            "Team Fortress 2",
            "PUBG BATTLEGROUNDS",
            "Titanfall 2",
            "Insurgency Sandstorm",
            "Squad",
        ],
    },
    {
        "prompt": "juegos tranquilos de granja simulacion casual y vida relajante con menos de 40 dolares",
        "relevant": [
            "Stardew Valley",
            "Slime Rancher",
            "The Sims 4",
            "Euro Truck Simulator 2",
            "Oxygen Not Included",
        ],
    },
    {
        "prompt": "supervivencia sandbox mundo abierto con crafting exploracion y muchas reseñas",
        "relevant": [
            "Terraria",
            "Raft",
            "Rust",
            "Subnautica",
            "ARK Survival Evolved",
        ],
    },
    {
        "prompt": "juegos populares de supervivencia exploracion espacial y construccion tipo sandbox",
        "relevant": [
            "Astroneer",
            "Space Engineers",
            "No Man's Sky",
            "Kerbal Space Program",
            "Starbound",
        ],
    },
    {
        "prompt": "juegos de mundo abierto fantasia y exploracion populares despues de 2015",
        "relevant": [
            "The Witcher 3 Wild Hunt",
            "ELDEN RING",
            "Subnautica",
            "Valheim",
            "No Man's Sky",
        ],
    },
    {
        "prompt": "juegos cooperativos divertidos para jugar con amigos",
        "relevant": [
            "It Takes Two",
            "Portal 2",
            "Human Fall Flat",
            "Overcooked 2",
            "Don't Starve Together",
        ],
    },
    {
        "prompt": "juegos casuales populares para pasar el rato",
        "relevant": [
            "Vampire Survivors",
            "Geometry Dash",
            "People Playground",
            "Among Us",
            "Fall Guys",
        ],
    },
    {
        "prompt": "quiero juegos de rol con mucha historia y decisiones",
        "relevant": [
            "Baldur's Gate 3",
            "The Witcher 3 Wild Hunt",
            "Divinity Original Sin 2",
            "Disco Elysium",
            "Pillars of Eternity",
        ],
    },
    {
        "prompt": "busco juegos de simulacion de camiones o manejo tranquilo",
        "relevant": [
            "Euro Truck Simulator 2",
            "American Truck Simulator",
            "BeamNG.drive",
            "My Summer Car",
            "SnowRunner",
        ],
    },
    {
        "prompt": "busco juegos de plataformas dificiles y bien valorados",
        "relevant": [
            "Celeste",
            "Cuphead",
            "Super Meat Boy",
            "Hollow Knight",
            "Geometry Dash",
        ],
    },
    {
        "prompt": "juegos de estrategia por turnos de civilizaciones e imperios populares",
        "relevant": [
            "Sid Meier's Civilization VI",
            "HUMANKIND",
            "Stellaris",
            "Age of Empires II Definitive Edition",
            "Europa Universalis IV",
        ],
    },
    {
        "prompt": "juegos de gestion de colonias y supervivencia populares",
        "relevant": [
            "RimWorld",
            "Oxygen Not Included",
            "Frostpunk",
            "Factorio",
            "Satisfactory",
        ],
    },
    {
        "prompt": "juegos de accion cooperativa contra monstruos con muchas reseñas",
        "relevant": [
            "Deep Rock Galactic",
            "Monster Hunter World",
            "Killing Floor 2",
            "Warhammer Vermintide 2",
            "Risk of Rain 2",
        ],
    },
    {
        "prompt": "juegos de disparos gratis y populares",
        "relevant": [
            "Team Fortress 2",
            "PUBG BATTLEGROUNDS",
            "Warframe",
            "Apex Legends",
            "Counter-Strike 2",
        ],
    },
    {
        "prompt": "juegos de fantasia online con mucho contenido y muchas reseñas",
        "relevant": [
            "FINAL FANTASY XIV Online",
            "The Elder Scrolls Online",
            "Lost Ark",
            "Path of Exile",
            "New World Aeternum",
        ],
    },
]


def normalize_title(text_value: str) -> str:
    text_value = str(text_value).lower()

    replacements = {
        "™": "",
        "®": "",
        "©": "",
        "â„¢": "",
        "â®": "",
        "’": "'",
        "‘": "'",
        "“": '"',
        "”": '"',
        ":": " ",
        "-": " ",
        "_": " ",
        "&": " and ",
    }

    for old, new in replacements.items():
        text_value = text_value.replace(old, new)

    text_value = unicodedata.normalize("NFKD", text_value)
    text_value = "".join(
        char for char in text_value
        if not unicodedata.combining(char)
    )

    text_value = re.sub(r"[^a-z0-9]+", " ", text_value)
    text_value = re.sub(r"\s+", " ", text_value).strip()

    return text_value


def edition_safe_match(expected: str, candidate: str) -> bool:
    expected_tokens = set(expected.split())
    candidate_tokens = set(candidate.split())

    if not expected_tokens or not candidate_tokens:
        return False

    allowed_extra_tokens = {
        "goty",
        "edition",
        "definitive",
        "complete",
        "special",
    }

    if expected_tokens.issubset(candidate_tokens):
        extra_tokens = candidate_tokens - expected_tokens
        return extra_tokens.issubset(allowed_extra_tokens)

    if candidate_tokens.issubset(expected_tokens):
        extra_tokens = expected_tokens - candidate_tokens
        return extra_tokens.issubset(allowed_extra_tokens)

    return False


def load_games_catalog() -> pd.DataFrame:
    sql = text("""
        SELECT
            appid,
            name
        FROM games
    """)

    with engine.connect() as conn:
        catalog = pd.read_sql(sql, conn)

    catalog["normalized_name"] = catalog["name"].apply(normalize_title)

    return catalog


def build_catalog_index(catalog: pd.DataFrame) -> Dict[str, List[Dict[str, Any]]]:
    index: Dict[str, List[Dict[str, Any]]] = {}

    for _, row in catalog.iterrows():
        normalized_name = row["normalized_name"]

        index.setdefault(normalized_name, []).append({
            "appid": int(row["appid"]),
            "name": row["name"],
            "normalized_name": normalized_name,
        })

    return index


def resolve_relevant_games(
    relevant_names: List[str],
    catalog: pd.DataFrame,
    catalog_index: Dict[str, List[Dict[str, Any]]],
) -> Dict[str, Any]:
    resolved = []
    unresolved = []

    for relevant_name in relevant_names:
        normalized_relevant = normalize_title(relevant_name)

        candidates = catalog_index.get(normalized_relevant, [])

        if not candidates:
            candidates = [
                {
                    "appid": int(row["appid"]),
                    "name": row["name"],
                    "normalized_name": row["normalized_name"],
                }
                for _, row in catalog.iterrows()
                if edition_safe_match(
                    normalized_relevant,
                    row["normalized_name"],
                )
            ]

        if candidates:
            resolved.append({
                "expected_name": relevant_name,
                "expected_normalized": normalized_relevant,
                "valid_appids": {
                    int(candidate["appid"])
                    for candidate in candidates
                },
                "database_names": [
                    candidate["name"]
                    for candidate in candidates
                ],
            })
        else:
            unresolved.append(relevant_name)

    return {
        "resolved": resolved,
        "unresolved": unresolved,
    }


def call_search_api(query: str) -> List[Dict[str, Any]]:
    response = requests.get(
        f"{BASE_URL}/search",
        params={"query": query},
        timeout=60,
    )

    if response.status_code != 200:
        print("Error: /search", response.status_code)
        print(response.text)
        return []

    results = response.json()

    for item in results:
        if "appid" not in item:
            raise ValueError(
                "El endpoint /search no devuelve appid. "
                "Corrige backend/app/search.py antes de evaluar."
            )

    return results


def call_natural_api(
    prompt: str,
    similarity_weight: float = 0.75,
    popularity_weight: float = 0.20,
    rating_weight: float = 0.05,
) -> Dict[str, Any]:
    response = requests.get(
        f"{BASE_URL}/natural-search",
        params={
            "prompt": prompt,
            "similarity_weight": similarity_weight,
            "popularity_weight": popularity_weight,
            "rating_weight": rating_weight,
        },
        timeout=60,
    )

    if response.status_code != 200:
        print("Error: /natural-search", response.status_code)
        print(response.text)
        return {
            "interpreted_query": prompt,
            "filters": {},
            "results": [],
        }

    data = response.json()

    for item in data.get("results", []):
        if "appid" not in item:
            raise ValueError(
                "El endpoint /natural-search no devuelve appid en results. "
                "Corrige backend/app/routes/hybrid.py antes de evaluar."
            )

    return data


def relational_baseline_search(prompt: str, limit: int = K) -> List[Dict[str, Any]]:
    max_price = detect_price(prompt)
    min_date, max_date = detect_year_range(prompt)
    min_reviews = detect_reviews(prompt)
    min_rating = detect_rating(prompt)

    sql = text("""
        SELECT
            appid,
            name,
            price,
            release_date,
            pct_pos_total,
            num_reviews_total,

            (
                (LEAST(COALESCE(num_reviews_total, 0), 100000) / 100000.0) * 0.70
                +
                (COALESCE(pct_pos_total, 0) / 100.0) * 0.30
            ) AS relational_score

        FROM games

        WHERE COALESCE(price, 0) <= :max_price
        AND release_date IS NOT NULL
        AND release_date >= CAST(:min_date AS date)
        AND release_date <= CAST(:max_date AS date)
        AND COALESCE(num_reviews_total, 0) >= :min_reviews
        AND COALESCE(pct_pos_total, 0) >= :min_rating

        ORDER BY relational_score DESC

        LIMIT :limit
    """)

    with engine.connect() as conn:
        result = pd.read_sql(
            sql,
            conn,
            params={
                "max_price": max_price,
                "min_date": min_date,
                "max_date": max_date,
                "min_reviews": min_reviews,
                "min_rating": min_rating,
                "limit": limit,
            },
        )

    return result.to_dict("records")


def count_hits_by_appid(
    results: List[Dict[str, Any]],
    resolved_relevant: List[Dict[str, Any]],
    k: int = K,
) -> Dict[str, Any]:
    top_k = results[:k]

    top_results_by_appid = {
        int(item["appid"]): item
        for item in top_k
    }

    hits = 0
    matched = []

    for relevant_item in resolved_relevant:
        valid_appids: Set[int] = relevant_item["valid_appids"]

        matched_appids = valid_appids.intersection(
            set(top_results_by_appid.keys())
        )

        if matched_appids:
            matched_appid = next(iter(matched_appids))
            found_item = top_results_by_appid[matched_appid]

            hits += 1
            matched.append({
                "expected": relevant_item["expected_name"],
                "found": found_item["name"],
                "appid": matched_appid,
            })

    return {
        "hits": hits,
        "matched": matched,
    }


def metrics(
    results: List[Dict[str, Any]],
    resolved_relevant: List[Dict[str, Any]],
    k: int = K,
) -> Dict[str, Any]:
    hit_info = count_hits_by_appid(
        results,
        resolved_relevant,
        k,
    )

    valid_relevant_count = len(resolved_relevant)

    recall = (
        hit_info["hits"] / valid_relevant_count
        if valid_relevant_count > 0
        else 0
    )

    precision = hit_info["hits"] / k

    return {
        "hits": hit_info["hits"],
        "valid_relevant_count": valid_relevant_count,
        "recall": recall,
        "precision": precision,
        "matched": hit_info["matched"],
    }


def print_top_results(title: str, results: List[Dict[str, Any]]) -> None:
    print(f"\n{title}")

    for item in results[:K]:
        print(f"- [{item['appid']}] {item['name']}")


def main() -> None:
    print("\nCARGANDO CATALOGO DESDE POSTGRESQL")
    print("=" * 80)

    catalog = load_games_catalog()
    catalog_index = build_catalog_index(catalog)

    print("Juegos cargados:", len(catalog))

    tests_to_run = TESTS[:EVAL_LIMIT] if EVAL_LIMIT > 0 else TESTS

    rows = []

    print("\nEVALUACION DEL SISTEMA")
    print("=" * 80)

    for test in tests_to_run:
        prompt = test["prompt"]
        relevant_names = test["relevant"]

        resolved_info = resolve_relevant_games(
            relevant_names,
            catalog,
            catalog_index,
        )

        resolved_relevant = resolved_info["resolved"]
        unresolved_relevant = resolved_info["unresolved"]

        base_response = call_natural_api(prompt)

        interpreted_query = base_response["interpreted_query"]
        filters = base_response.get("filters", {})

        vector_results = call_search_api(interpreted_query)
        vector_metrics = metrics(vector_results, resolved_relevant)

        rows.append({
            "query": prompt,
            "interpreted_query": interpreted_query,
            "method": "Vectorial pura",
            "similarity_weight": 1.00,
            "popularity_weight": 0.00,
            "rating_weight": 0.00,
            "hits": vector_metrics["hits"],
            "valid_relevant_count": vector_metrics["valid_relevant_count"],
            "unresolved_relevant_count": len(unresolved_relevant),
            "recall_at_10": round(vector_metrics["recall"], 3),
            "precision_at_10": round(vector_metrics["precision"], 3),
            "filters": json.dumps(filters, ensure_ascii=False),
            "matched": json.dumps(
                vector_metrics["matched"],
                ensure_ascii=False,
            ),
            "unresolved_relevant": json.dumps(
                unresolved_relevant,
                ensure_ascii=False,
            ),
        })

        relational_results = relational_baseline_search(prompt, limit=K)
        relational_metrics = metrics(relational_results, resolved_relevant)

        rows.append({
            "query": prompt,
            "interpreted_query": interpreted_query,
            "method": "Baseline relacional",
            "similarity_weight": 0.00,
            "popularity_weight": 0.70,
            "rating_weight": 0.30,
            "hits": relational_metrics["hits"],
            "valid_relevant_count": relational_metrics["valid_relevant_count"],
            "unresolved_relevant_count": len(unresolved_relevant),
            "recall_at_10": round(relational_metrics["recall"], 3),
            "precision_at_10": round(relational_metrics["precision"], 3),
            "filters": json.dumps(filters, ensure_ascii=False),
            "matched": json.dumps(
                relational_metrics["matched"],
                ensure_ascii=False,
            ),
            "unresolved_relevant": json.dumps(
                unresolved_relevant,
                ensure_ascii=False,
            ),
        })

        for config in WEIGHT_CONFIGS:
            natural_response = call_natural_api(
                prompt,
                similarity_weight=config["similarity_weight"],
                popularity_weight=config["popularity_weight"],
                rating_weight=config["rating_weight"],
            )

            hybrid_results = natural_response.get("results", [])
            hybrid_metrics = metrics(hybrid_results, resolved_relevant)

            rows.append({
                "query": prompt,
                "interpreted_query": interpreted_query,
                "method": config["method"],
                "similarity_weight": config["similarity_weight"],
                "popularity_weight": config["popularity_weight"],
                "rating_weight": config["rating_weight"],
                "hits": hybrid_metrics["hits"],
                "valid_relevant_count": hybrid_metrics["valid_relevant_count"],
                "unresolved_relevant_count": len(unresolved_relevant),
                "recall_at_10": round(hybrid_metrics["recall"], 3),
                "precision_at_10": round(hybrid_metrics["precision"], 3),
                "filters": json.dumps(filters, ensure_ascii=False),
                "matched": json.dumps(
                    hybrid_metrics["matched"],
                    ensure_ascii=False,
                ),
                "unresolved_relevant": json.dumps(
                    unresolved_relevant,
                    ensure_ascii=False,
                ),
            })

        print("\nConsulta original:", prompt)
        print("Consulta interpretada:", interpreted_query)
        print("Filtros detectados:", filters)
        print("Ground truth validado:", len(resolved_relevant))
        print("Ground truth no encontrado en BD:", unresolved_relevant)

        print_top_results("Vectorial Top 10:", vector_results)
        print("Coincidencias vectorial:", vector_metrics["matched"])
        print("Recall@10 vectorial:", round(vector_metrics["recall"], 3))
        print("Precision@10 vectorial:", round(vector_metrics["precision"], 3))

        print_top_results("Baseline relacional Top 10:", relational_results)
        print("Coincidencias baseline relacional:", relational_metrics["matched"])
        print("Recall@10 baseline relacional:", round(relational_metrics["recall"], 3))
        print("Precision@10 baseline relacional:", round(relational_metrics["precision"], 3))

    df = pd.DataFrame(rows)

    print("\nRESULTADOS")
    print("=" * 80)

    print(df[[
        "query",
        "method",
        "similarity_weight",
        "popularity_weight",
        "rating_weight",
        "hits",
        "valid_relevant_count",
        "unresolved_relevant_count",
        "recall_at_10",
        "precision_at_10",
    ]])

    print("\nPROMEDIOS")
    print("=" * 80)

    summary = df.groupby("method")[
        [
            "similarity_weight",
            "popularity_weight",
            "rating_weight",
            "hits",
            "valid_relevant_count",
            "unresolved_relevant_count",
            "recall_at_10",
            "precision_at_10",
        ]
    ].mean()

    print(summary)

    df.to_csv(
        "../docs/evaluation_results.csv",
        index=False,
        encoding="utf-8-sig",
    )

    summary.to_csv(
        "../docs/weight_sensitivity_results.csv",
        encoding="utf-8-sig",
    )

    print("\nArchivos guardados en:")
    print("../docs/evaluation_results.csv")
    print("../docs/weight_sensitivity_results.csv")


if __name__ == "__main__":
    main()