import json
import os
import re
import unicodedata
from typing import Any, Dict, List, Set

import pandas as pd
import requests
from sqlalchemy import text

from app.database import engine


BASE_URL = "http://127.0.0.1:8000"
K = 10

# Permite ejecutar solo algunas consultas para depuración rápida.
# Ejemplo:
#   EVAL_LIMIT=5 python evaluate_system.py
EVAL_LIMIT = int(os.getenv("EVAL_LIMIT", "0"))


TESTS = [
    # ============================================================
    # Grupo A: consultas con filtros claros
    # Precio, año, popularidad, rating o rango temporal.
    # Estas consultas evalúan donde la búsqueda híbrida debería aportar más.
    # ============================================================

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
        "prompt": "recomiendame juegos tipo Dark Souls de fantasia oscura populares despues de 2015 y menos de 60 dolares",
        "relevant": [
            "ELDEN RING",
            "DARK SOULS III",
            "Sekiro Shadows Die Twice",
            "Lords of the Fallen",
            "Nioh 2",
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
        "prompt": "quiero un rpg de fantasia medieval popular entre 2015 y 2024",
        "relevant": [
            "The Witcher 3 Wild Hunt",
            "Baldur's Gate 3",
            "Divinity Original Sin 2",
            "ELDEN RING",
            "Kingdom Come Deliverance",
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
            "Football Manager 2024",
        ],
    },
    {
        "prompt": "mmorpg de fantasia online masivo populares despues de 2010",
        "relevant": [
            "FINAL FANTASY XIV Online",
            "The Elder Scrolls Online",
            "Lost Ark",
            "New World Aeternum",
            "Black Desert",
        ],
    },
    {
        "prompt": "city builder gestion de recursos y construccion populares entre 2015 y 2024",
        "relevant": [
            "Cities Skylines",
            "Frostpunk",
            "RimWorld",
            "Factorio",
            "Tropico 6",
        ],
    },
    {
        "prompt": "roguelike de accion y mazmorras con muchas reseñas y menos de 40 dolares",
        "relevant": [
            "Hades",
            "Dead Cells",
            "The Binding of Isaac Rebirth",
            "Slay the Spire",
            "Enter the Gungeon",
        ],
    },
    {
        "prompt": "juegos de exploracion espacial ciencia ficcion y supervivencia sandbox",
        "relevant": [
            "No Man's Sky",
            "Kerbal Space Program",
            "Space Engineers",
            "Astroneer",
            "Elite Dangerous",
        ],
    },

    # ============================================================
    # Grupo B: consultas semánticas por género o estilo
    # Estas consultas prueban si el sistema entiende categorías, estilos y géneros.
    # ============================================================

    {
        "prompt": "busco metroidvania de fantasia oscura con plataformas y accion",
        "relevant": [
            "Hollow Knight",
            "Dead Cells",
            "Ori and the Will of the Wisps",
            "ENDER LILIES Quietus of the Knights",
            "Bloodstained Ritual of the Night",
        ],
    },
    {
        "prompt": "juegos cozy relajantes y casuales bien valorados",
        "relevant": [
            "Stardew Valley",
            "Slime Rancher",
            "Unpacking",
            "A Short Hike",
            "Dorfromantik",
        ],
    },
    {
        "prompt": "juegos tranquilos de granja y vida relajante con menos de 40 dolares",
        "relevant": [
            "Stardew Valley",
            "Farming Simulator 22",
            "My Time at Portia",
            "Coral Island",
            "Sun Haven",
        ],
    },
    {
        "prompt": "quiero juegos de estrategia por turnos de civilizaciones e imperios",
        "relevant": [
            "Sid Meier's Civilization VI",
            "HUMANKIND",
            "XCOM 2",
            "Total War WARHAMMER III",
            "Age of Wonders 4",
        ],
    },
    {
        "prompt": "busco juegos de terror psicologico y supervivencia con menos de 60 dolares",
        "relevant": [
            "Resident Evil 2",
            "Resident Evil 4",
            "Outlast",
            "Amnesia The Dark Descent",
            "The Forest",
        ],
    },
    {
        "prompt": "fps multijugador competitivos y tacticos populares con muchas reseñas",
        "relevant": [
            "Counter-Strike 2",
            "Tom Clancy's Rainbow Six Siege",
            "PUBG BATTLEGROUNDS",
            "Team Fortress 2",
            "Squad",
        ],
    },
    {
        "prompt": "juegos de supervivencia en bosque o naturaleza para jugar con amigos",
        "relevant": [
            "The Forest",
            "Sons Of The Forest",
            "Green Hell",
            "Valheim",
            "Don't Starve Together",
        ],
    },
    {
        "prompt": "juegos de cartas estrategia deckbuilding roguelike con menos de 40 dolares",
        "relevant": [
            "Slay the Spire",
            "Balatro",
            "Monster Train",
            "Across the Obelisk",
            "Griftlands",
        ],
    },

    # ============================================================
    # Grupo C: consultas generales de usuario común
    # No todas tienen filtros explícitos. Sirven para evitar que el benchmark
    # sea demasiado favorable a la búsqueda híbrida.
    # ============================================================

    {
        "prompt": "quiero juegos indie bien valorados con pixel art y aventura",
        "relevant": [
            "Undertale",
            "Celeste",
            "Hollow Knight",
            "Dead Cells",
            "Stardew Valley",
        ],
    },
    {
        "prompt": "juegos de mundo abierto para explorar despues de 2015",
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
            "Overcooked 2",
            "Human Fall Flat",
            "Portal 2",
            "Moving Out",
        ],
    },
    {
        "prompt": "juegos casuales populares para pasar el rato",
        "relevant": [
            "Among Us",
            "Fall Guys",
            "Geometry Dash",
            "Vampire Survivors",
            "People Playground",
        ],
    },
    {
        "prompt": "quiero juegos de rol con mucha historia y decisiones",
        "relevant": [
            "Baldur's Gate 3",
            "Disco Elysium",
            "The Witcher 3 Wild Hunt",
            "Divinity Original Sin 2",
            "Pillars of Eternity",
        ],
    },
    {
        "prompt": "busco juegos de simulacion de camiones o manejo tranquilo",
        "relevant": [
            "Euro Truck Simulator 2",
            "American Truck Simulator",
            "SnowRunner",
            "BeamNG.drive",
            "My Summer Car",
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

    # ============================================================
    # Grupo D: consultas difíciles
    # Estas consultas se incluyen intencionalmente para mostrar que el sistema
    # no es perfecto y que el benchmark no fue escogido solo para favorecerlo.
    # ============================================================

    {
        "prompt": "quiero juegos anime de accion y peleas despues de 2015",
        "relevant": [
            "DRAGON BALL FighterZ",
            "GUILTY GEAR STRIVE",
            "NARUTO SHIPPUDEN Ultimate Ninja STORM 4",
            "TEKKEN 8",
            "Street Fighter 6",
        ],
    },
    {
        "prompt": "juegos de investigacion detectives y misterio",
        "relevant": [
            "Disco Elysium",
            "Return of the Obra Dinn",
            "The Case of the Golden Idol",
            "L.A. Noire",
            "Sherlock Holmes Chapter One",
        ],
    },
    {
        "prompt": "quiero juegos de piratas y aventura en mundo abierto",
        "relevant": [
            "Sea of Thieves",
            "Assassin's Creed IV Black Flag",
            "Sid Meier's Pirates",
            "Tempest Pirate Action RPG",
            "King of Seas",
        ],
    },
    {
        "prompt": "juegos de robots o mechas con accion despues de 2015",
        "relevant": [
            "Armored Core VI Fires of Rubicon",
            "Titanfall 2",
            "MechWarrior 5 Mercenaries",
            "Daemon X Machina",
            "Brigador",
        ],
    },
    {
        "prompt": "juegos de vampiros o fantasia oscura con accion",
        "relevant": [
            "V Rising",
            "Vampire Survivors",
            "CODE VEIN",
            "Darkest Dungeon",
            "Castlevania Advance Collection",
        ],
    },
]

def normalize_title(text_value: str) -> str:
    """
    Normaliza títulos únicamente para resolver el ground truth contra la BD.

    La evaluación final NO se hace por texto, sino por appid.
    Esto evita falsos positivos como:
    - Raft = Crafting Block World
    - Cities Skylines = SKY
    - Civilization VI = Civilization V

    También se conservan números y números romanos porque diferencian juegos.
    """
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
    """
    Permite diferencias menores de edición sin confundir juegos distintos.

    Aceptable:
    - Sekiro Shadows Die Twice
    - Sekiro Shadows Die Twice GOTY Edition

    No aceptable:
    - Dark Souls Remastered
    - Dark Souls III

    No aceptable:
    - Cities Skylines
    - Cities Skylines II
    """
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
    """
    Carga el catálogo real desde PostgreSQL.

    Esto sirve para validar que los juegos del ground truth existan dentro de
    la misma base usada por el sistema. Si un juego no está en la BD, no debe
    castigar injustamente el Recall.
    """
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
    """
    Construye un índice por nombre normalizado para resolver ground truth rápido.

    Esto evita recorrer toda la base muchas veces y reduce el tiempo de evaluación.
    """
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
    catalog_index: Dict[str, List[Dict[str, Any]]]
) -> Dict[str, Any]:
    """
    Convierte nombres del ground truth a appid.

    El appid es el identificador único de Steam, por eso es el criterio más
    sólido para contar aciertos en Recall@10.
    """
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
                    row["normalized_name"]
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
    """
    Ejecuta /search como baseline vectorial puro.

    Se usa la consulta interpretada por el NLU para que la comparación sea justa:
    ambos métodos parten del mismo significado semántico.
    """
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


def call_natural_api(prompt: str) -> Dict[str, Any]:
    """
    Ejecuta /natural-search, que representa el sistema final.

    Este endpoint:
    - recibe una consulta en español,
    - interpreta la consulta,
    - extrae filtros,
    - llama internamente a la búsqueda híbrida.
    """
    response = requests.get(
        f"{BASE_URL}/natural-search",
        params={"prompt": prompt},
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


def count_hits_by_appid(
    results: List[Dict[str, Any]],
    resolved_relevant: List[Dict[str, Any]],
    k: int = K
) -> Dict[str, Any]:
    """
    Cuenta aciertos usando appid.

    Esta es la corrección metodológica más importante:
    ya no se considera acierto por parecido textual, sino por coincidencia
    con el identificador único del videojuego.
    """
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
    k: int = K
) -> Dict[str, Any]:
    """
    Calcula Recall@K y Precision@K.

    Recall@K:
    relevantes recuperados en Top-K / relevantes válidos en la BD

    Precision@K:
    relevantes recuperados en Top-K / K
    """
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

        natural_response = call_natural_api(prompt)

        interpreted_query = natural_response["interpreted_query"]
        filters = natural_response.get("filters", {})
        hybrid_results = natural_response.get("results", [])

        vector_results = call_search_api(interpreted_query)

        vector_metrics = metrics(vector_results, resolved_relevant)
        hybrid_metrics = metrics(hybrid_results, resolved_relevant)

        rows.append({
            "query": prompt,
            "interpreted_query": interpreted_query,
            "method": "Vectorial",
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

        rows.append({
            "query": prompt,
            "interpreted_query": interpreted_query,
            "method": "Hibrida",
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

        print_top_results("Hibrida Top 10:", hybrid_results)
        print("Coincidencias hibrida:", hybrid_metrics["matched"])
        print("Recall@10 hibrida:", round(hybrid_metrics["recall"], 3))
        print("Precision@10 hibrida:", round(hybrid_metrics["precision"], 3))

    df = pd.DataFrame(rows)

    print("\nRESULTADOS")
    print("=" * 80)
    print(df[[
        "query",
        "method",
        "hits",
        "valid_relevant_count",
        "unresolved_relevant_count",
        "recall_at_10",
        "precision_at_10",
    ]])

    print("\nPROMEDIOS")
    print("=" * 80)
    print(
        df.groupby("method")[
            [
                "hits",
                "valid_relevant_count",
                "unresolved_relevant_count",
                "recall_at_10",
                "precision_at_10",
            ]
        ].mean()
    )

    df.to_csv(
        "../docs/evaluation_results.csv",
        index=False,
        encoding="utf-8-sig",
    )

    print("\nArchivo guardado en:")
    print("../docs/evaluation_results.csv")


if __name__ == "__main__":
    main()