import json
import re
import unicodedata
from typing import Dict, List, Set, Any

import pandas as pd
import requests
from sqlalchemy import text

from app.database import engine


BASE_URL = "http://127.0.0.1:8000"
K = 10

# Se mantiene este filtro mínimo para la búsqueda híbrida porque forma parte
# del componente relacional usado para reducir resultados poco representativos.
# Debe reportarse en el artículo como parámetro experimental.
HYBRID_MIN_REVIEWS = 1000


TESTS = [
    {
        "query": "zombie survival multiplayer",
        "relevant": [
            "Project Zomboid",
            "DayZ",
            "7 Days to Die",
            "Unturned",
            "Dying Light",
        ],
    },
    {
        "query": "souls-like dark fantasy action rpg",
        "relevant": [
            "ELDEN RING",
            "DARK SOULS III",
            "DARK SOULS REMASTERED",
            "Sekiro Shadows Die Twice",
            "Lords of the Fallen",
        ],
    },
    {
        "query": "pixel art adventure",
        "relevant": [
            "Terraria",
            "Stardew Valley",
            "Undertale",
            "Hollow Knight",
            "Dead Cells",
        ],
    },
    {
        "query": "medieval fantasy rpg",
        "relevant": [
            "The Witcher 3 Wild Hunt",
            "Baldur's Gate 3",
            "Divinity Original Sin 2",
            "ELDEN RING",
            "Dragon's Dogma 2",
        ],
    },
    {
        "query": "farming life simulator",
        "relevant": [
            "Stardew Valley",
            "Farming Simulator 22",
            "My Time at Portia",
            "Coral Island",
            "Sun Haven",
        ],
    },
    {
        "query": "competitive multiplayer fps tactical shooter",
        "relevant": [
            "Counter-Strike 2",
            "Tom Clancy's Rainbow Six Siege",
            "Apex Legends",
            "PUBG BATTLEGROUNDS",
            "Team Fortress 2",
        ],
    },
    {
        "query": "open world fantasy adventure exploration",
        "relevant": [
            "The Elder Scrolls V Skyrim Special Edition",
            "The Witcher 3 Wild Hunt",
            "ELDEN RING",
            "Dragon's Dogma 2",
            "Horizon Zero Dawn Complete Edition",
        ],
    },
    {
        "query": "metroidvania dark fantasy platformer action adventure",
        "relevant": [
            "Hollow Knight",
            "Dead Cells",
            "Blasphemous",
            "Ori and the Blind Forest Definitive Edition",
            "ENDER LILIES Quietus of the Knights",
        ],
    },
    {
        "query": "sandbox crafting survival open world",
        "relevant": [
            "Terraria",
            "Valheim",
            "Rust",
            "Raft",
            "Don't Starve Together",
        ],
    },
    {
        "query": "roguelike action dungeon crawler",
        "relevant": [
            "Hades",
            "The Binding of Isaac Rebirth",
            "Dead Cells",
            "Enter the Gungeon",
            "Risk of Rain 2",
        ],
    },
    {
        "query": "city building management strategy",
        "relevant": [
            "Cities Skylines",
            "Cities Skylines II",
            "Frostpunk",
            "Anno 1800",
            "Tropico 6",
        ],
    },
    {
        "query": "horror survival psychological scary",
        "relevant": [
            "Resident Evil 2",
            "Resident Evil 4",
            "Outlast",
            "Amnesia The Dark Descent",
            "The Forest",
        ],
    },
    {
        "query": "space exploration sci fi survival",
        "relevant": [
            "No Man's Sky",
            "Elite Dangerous",
            "Kerbal Space Program",
            "Space Engineers",
            "Astroneer",
        ],
    },
    {
        "query": "turn based strategy civilization empire",
        "relevant": [
            "Sid Meier's Civilization VI",
            "Total War WARHAMMER III",
            "XCOM 2",
            "Age of Wonders 4",
            "HUMANKIND",
        ],
    },
    {
        "query": "racing simulation realistic cars",
        "relevant": [
            "Assetto Corsa",
            "Forza Horizon 5",
            "F1 23",
            "DiRT Rally 2.0",
            "Project CARS 2",
        ],
    },
    {
        "query": "sports football soccer simulation",
        "relevant": [
            "EA SPORTS FC 24",
            "eFootball",
            "Football Manager 2024",
            "Rocket League",
            "FIFA 23",
        ],
    },
    {
        "query": "anime fighting action adventure",
        "relevant": [
            "NARUTO SHIPPUDEN Ultimate Ninja STORM 4",
            "DRAGON BALL FighterZ",
            "Persona 5 Royal",
            "CODE VEIN",
            "GUILTY GEAR STRIVE",
        ],
    },
    {
        "query": "cozy relaxing casual game",
        "relevant": [
            "Stardew Valley",
            "Unpacking",
            "A Short Hike",
            "Slime Rancher",
            "Dorfromantik",
        ],
    },
    {
        "query": "card strategy roguelike deckbuilding",
        "relevant": [
            "Slay the Spire",
            "Balatro",
            "Monster Train",
            "Inscryption",
            "Across the Obelisk",
        ],
    },
    {
        "query": "massively multiplayer online fantasy rpg",
        "relevant": [
            "FINAL FANTASY XIV Online",
            "The Elder Scrolls Online",
            "Black Desert",
            "Lost Ark",
            "Guild Wars 2",
        ],
    },
]


def normalize_title(text_value: str) -> str:
    """
    Normaliza títulos solo para resolver el ground truth contra la base de datos.
    La evaluación final no se hace por texto, sino por appid.

    Se conservan números y números romanos para no confundir juegos distintos:
    Civilization V != Civilization VI
    Dark Souls III != Dark Souls Remastered
    Cities Skylines != Cities Skylines II
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
    Permite diferencias menores de edición sin crear falsos positivos.

    Ejemplos aceptables:
    - "sekiro shadows die twice" vs
      "sekiro shadows die twice goty edition"

    Ejemplos que NO deben aceptarse:
    - "cities skylines ii" vs "cities skylines"
    - "civilization vi" vs "civilization v"
    - "dark souls remastered" vs "dark souls iii"
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
        "remastered",
    }

    if expected_tokens.issubset(candidate_tokens):
        extra = candidate_tokens - expected_tokens
        return extra.issubset(allowed_extra_tokens)

    if candidate_tokens.issubset(expected_tokens):
        extra = expected_tokens - candidate_tokens
        return extra.issubset(allowed_extra_tokens)

    return False


def load_games_catalog() -> pd.DataFrame:
    """
    Carga appid y name desde PostgreSQL para validar el ground truth.
    Esto evita evaluar contra juegos que no existen en la base usada por el sistema.
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


def resolve_relevant_games(
    relevant_names: List[str],
    catalog: pd.DataFrame
) -> Dict[str, Any]:
    """
    Convierte los nombres del ground truth a appid.

    La evaluación usa appid porque es el identificador único del videojuego en Steam.
    Esto es más sólido que comparar nombres, ya que los títulos pueden contener
    símbolos, marcas, subtítulos o variaciones de edición.
    """
    resolved = []
    unresolved = []

    normalized_groups = (
        catalog
        .groupby("normalized_name")
        .apply(lambda group: group[["appid", "name"]].to_dict("records"))
        .to_dict()
    )

    for relevant_name in relevant_names:
        normalized_relevant = normalize_title(relevant_name)

        candidates = normalized_groups.get(normalized_relevant, [])

        if not candidates:
            safe_candidates = []

            for _, row in catalog.iterrows():
                if edition_safe_match(
                    normalized_relevant,
                    row["normalized_name"]
                ):
                    safe_candidates.append({
                        "appid": int(row["appid"]),
                        "name": row["name"],
                    })

            candidates = safe_candidates

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


def call_api(endpoint: str, query: str) -> List[Dict[str, Any]]:
    """
    Ejecuta el endpoint correspondiente.

    /search se usa como baseline vectorial puro.
    /hybrid-search se usa como método propuesto.
    """
    params = {
        "query": query,
    }

    if endpoint == "hybrid-search":
        params["min_reviews"] = HYBRID_MIN_REVIEWS

    response = requests.get(
        f"{BASE_URL}/{endpoint}",
        params=params,
        timeout=60,
    )

    if response.status_code != 200:
        print("Error:", endpoint, response.status_code)
        print(response.text)
        return []

    results = response.json()

    for item in results:
        if "appid" not in item:
            raise ValueError(
                f"El endpoint /{endpoint} no devuelve appid. "
                "Agrega appid al SELECT y al JSON de respuesta antes de evaluar."
            )

    return results


def count_hits_by_appid(
    results: List[Dict[str, Any]],
    resolved_relevant: List[Dict[str, Any]],
    k: int = K
) -> Dict[str, Any]:
    """
    Calcula hits usando appid.

    Esta es la parte más importante de la corrección:
    ya no se cuenta un acierto porque el nombre se parece,
    sino porque el identificador único del juego coincide.
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
    Recall@K = relevantes recuperados en Top-K / relevantes válidos.
    Precision@K = relevantes recuperados en Top-K / K.

    Se usa como denominador solo el ground truth validado contra la base de datos.
    Si un juego relevante no existe en la base, se reporta como unresolved y no se
    usa para castigar injustamente al sistema.
    """
    hit_info = count_hits_by_appid(results, resolved_relevant, k)

    valid_relevant_count = len(resolved_relevant)

    if valid_relevant_count == 0:
        recall = 0
    else:
        recall = hit_info["hits"] / valid_relevant_count

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

    print("Juegos cargados:", len(catalog))

    rows = []

    print("\nEVALUACION DEL SISTEMA")
    print("=" * 80)

    for test in TESTS:
        query = test["query"]
        relevant_names = test["relevant"]

        resolved_info = resolve_relevant_games(
            relevant_names,
            catalog,
        )

        resolved_relevant = resolved_info["resolved"]
        unresolved_relevant = resolved_info["unresolved"]

        vector_results = call_api("search", query)
        hybrid_results = call_api("hybrid-search", query)

        vector_metrics = metrics(vector_results, resolved_relevant)
        hybrid_metrics = metrics(hybrid_results, resolved_relevant)

        rows.append({
            "query": query,
            "method": "Vectorial",
            "hits": vector_metrics["hits"],
            "valid_relevant_count": vector_metrics["valid_relevant_count"],
            "unresolved_relevant_count": len(unresolved_relevant),
            "recall_at_10": round(vector_metrics["recall"], 3),
            "precision_at_10": round(vector_metrics["precision"], 3),
            "matched": json.dumps(
                vector_metrics["matched"],
                ensure_ascii=False
            ),
            "unresolved_relevant": json.dumps(
                unresolved_relevant,
                ensure_ascii=False
            ),
        })

        rows.append({
            "query": query,
            "method": "Hibrida",
            "hits": hybrid_metrics["hits"],
            "valid_relevant_count": hybrid_metrics["valid_relevant_count"],
            "unresolved_relevant_count": len(unresolved_relevant),
            "recall_at_10": round(hybrid_metrics["recall"], 3),
            "precision_at_10": round(hybrid_metrics["precision"], 3),
            "matched": json.dumps(
                hybrid_metrics["matched"],
                ensure_ascii=False
            ),
            "unresolved_relevant": json.dumps(
                unresolved_relevant,
                ensure_ascii=False
            ),
        })

        print("\nConsulta:", query)
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