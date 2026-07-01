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
    {
        "prompt": "quiero juegos de zombies para jugar con amigos, populares y que cuesten menos de 60 dolares",
        "relevant": [
            "Project Zomboid",
            "DayZ",
            "7 Days to Die",
            "Unturned",
            "Dying Light",
        ],
    },
    {
        "prompt": "recomiendame juegos parecidos a Dark Souls de fantasia oscura despues de 2015",
        "relevant": [
            "ELDEN RING",
            "DARK SOULS III",
            "DARK SOULS REMASTERED",
            "Sekiro Shadows Die Twice",
            "Lords of the Fallen",
        ],
    },
    {
        "prompt": "busco juegos pixel art de aventura que sean buenos y baratos",
        "relevant": [
            "Terraria",
            "Stardew Valley",
            "Undertale",
            "Hollow Knight",
            "Dead Cells",
        ],
    },
    {
        "prompt": "quiero un rpg de fantasia medieval popular entre 2015 y 2024",
        "relevant": [
            "The Witcher 3 Wild Hunt",
            "Baldur's Gate 3",
            "Divinity Original Sin 2",
            "ELDEN RING",
            "Dragon's Dogma 2",
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
        "prompt": "quiero shooters competitivos multijugador con muchas reseñas",
        "relevant": [
            "Counter-Strike 2",
            "Tom Clancy's Rainbow Six Siege",
            "Apex Legends",
            "PUBG BATTLEGROUNDS",
            "Team Fortress 2",
        ],
    },
    {
        "prompt": "juegos de mundo abierto para explorar despues de 2015",
        "relevant": [
            "The Elder Scrolls V Skyrim Special Edition",
            "The Witcher 3 Wild Hunt",
            "ELDEN RING",
            "Dragon's Dogma 2",
            "Horizon Zero Dawn Complete Edition",
        ],
    },
    {
        "prompt": "busco metroidvania de fantasia oscura con menos de 40 dolares",
        "relevant": [
            "Hollow Knight",
            "Dead Cells",
            "Blasphemous",
            "Ori and the Blind Forest Definitive Edition",
            "ENDER LILIES Quietus of the Knights",
        ],
    },
    {
        "prompt": "quiero juegos de supervivencia sandbox crafting populares",
        "relevant": [
            "Terraria",
            "Valheim",
            "Rust",
            "Raft",
            "Don't Starve Together",
        ],
    },
    {
        "prompt": "recomiendame roguelikes de accion con mazmorras y muchas reseñas",
        "relevant": [
            "Hades",
            "The Binding of Isaac Rebirth",
            "Dead Cells",
            "Enter the Gungeon",
            "Risk of Rain 2",
        ],
    },
    {
        "prompt": "quiero juegos de construir ciudades y gestionar recursos",
        "relevant": [
            "Cities Skylines",
            "Cities Skylines II",
            "Frostpunk",
            "Anno 1800",
            "Tropico 6",
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
        "prompt": "juegos de exploracion espacial y ciencia ficcion tipo sandbox",
        "relevant": [
            "No Man's Sky",
            "Elite Dangerous",
            "Kerbal Space Program",
            "Space Engineers",
            "Astroneer",
        ],
    },
    {
        "prompt": "quiero juegos de estrategia por turnos de civilizaciones e imperios",
        "relevant": [
            "Sid Meier's Civilization VI",
            "Total War WARHAMMER III",
            "XCOM 2",
            "Age of Wonders 4",
            "HUMANKIND",
        ],
    },
    {
        "prompt": "busco juegos de carreras realistas con autos populares",
        "relevant": [
            "Assetto Corsa",
            "Forza Horizon 5",
            "F1 23",
            "DiRT Rally 2.0",
            "Project CARS 2",
        ],
    },
    {
        "prompt": "juegos de futbol y deportes populares para pc",
        "relevant": [
            "EA SPORTS FC 24",
            "eFootball",
            "Football Manager 2024",
            "Rocket League",
            "FIFA 23",
        ],
    },
    {
        "prompt": "quiero juegos anime de accion y peleas despues de 2015",
        "relevant": [
            "NARUTO SHIPPUDEN Ultimate Ninja STORM 4",
            "DRAGON BALL FighterZ",
            "Persona 5 Royal",
            "CODE VEIN",
            "GUILTY GEAR STRIVE",
        ],
    },
    {
        "prompt": "juegos cozy relajantes y casuales bien valorados",
        "relevant": [
            "Stardew Valley",
            "Unpacking",
            "A Short Hike",
            "Slime Rancher",
            "Dorfromantik",
        ],
    },
    {
        "prompt": "quiero juegos de cartas tipo deckbuilding roguelike",
        "relevant": [
            "Slay the Spire",
            "Balatro",
            "Monster Train",
            "Inscryption",
            "Across the Obelisk",
        ],
    },
    {
        "prompt": "busco mmorpg de fantasia online populares despues de 2010",
        "relevant": [
            "FINAL FANTASY XIV Online",
            "The Elder Scrolls Online",
            "Black Desert",
            "Lost Ark",
            "Guild Wars 2",
        ],
    },
    {
        "prompt": "quiero juegos parecidos a Minecraft de construccion y supervivencia",
        "relevant": [
            "Terraria",
            "Valheim",
            "Starbound",
            "Creativerse",
            "Scrap Mechanic",
        ],
    },
    {
        "prompt": "juegos tipo Stardew Valley relajantes y de granja",
        "relevant": [
            "Stardew Valley",
            "My Time at Portia",
            "Coral Island",
            "Sun Haven",
            "Harvest Moon The Winds of Anthos",
        ],
    },
    {
        "prompt": "quiero juegos de estrategia en tiempo real populares",
        "relevant": [
            "Age of Empires II Definitive Edition",
            "Age of Empires IV",
            "Total War WARHAMMER III",
            "Company of Heroes 2",
            "Northgard",
        ],
    },
    {
        "prompt": "juegos de guerra tactica y disparos realistas con muchas reseñas",
        "relevant": [
            "Squad",
            "Arma 3",
            "Insurgency Sandstorm",
            "Ready or Not",
            "Hell Let Loose",
        ],
    },
    {
        "prompt": "quiero juegos de mundo abierto con crimen y accion",
        "relevant": [
            "Grand Theft Auto V",
            "Cyberpunk 2077",
            "Mafia Definitive Edition",
            "Sleeping Dogs Definitive Edition",
            "Watch Dogs 2",
        ],
    },
    {
        "prompt": "recomiendame juegos de pelea populares para jugar con amigos",
        "relevant": [
            "TEKKEN 8",
            "Street Fighter 6",
            "Mortal Kombat 11",
            "DRAGON BALL FighterZ",
            "GUILTY GEAR STRIVE",
        ],
    },
    {
        "prompt": "busco juegos de plataformas dificiles y bien valorados",
        "relevant": [
            "Celeste",
            "Hollow Knight",
            "Super Meat Boy",
            "Ori and the Blind Forest Definitive Edition",
            "Cuphead",
        ],
    },
    {
        "prompt": "quiero juegos de puzzles tranquilos y bonitos con menos de 30 dolares",
        "relevant": [
            "Portal 2",
            "The Witness",
            "Baba Is You",
            "Unpacking",
            "Dorfromantik",
        ],
    },
    {
        "prompt": "juegos cooperativos divertidos para jugar en pareja o con amigos",
        "relevant": [
            "It Takes Two",
            "Overcooked 2",
            "Human Fall Flat",
            "Moving Out",
            "Portal 2",
        ],
    },
    {
        "prompt": "quiero juegos de supervivencia en bosque o naturaleza",
        "relevant": [
            "The Forest",
            "Sons Of The Forest",
            "Green Hell",
            "Valheim",
            "Don't Starve Together",
        ],
    },
    {
        "prompt": "juegos de gestion de colonias y supervivencia populares",
        "relevant": [
            "RimWorld",
            "Oxygen Not Included",
            "Frostpunk",
            "Dwarf Fortress",
            "Going Medieval",
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
        "prompt": "juegos de vampiros o fantasia oscura con accion",
        "relevant": [
            "V Rising",
            "Castlevania Advance Collection",
            "CODE VEIN",
            "Darkest Dungeon",
            "Vampire Survivors",
        ],
    },
    {
        "prompt": "quiero juegos baratos de estrategia y cartas",
        "relevant": [
            "Slay the Spire",
            "Balatro",
            "Monster Train",
            "Inscryption",
            "Griftlands",
        ],
    },
    {
        "prompt": "juegos de robots o mechas con accion despues de 2015",
        "relevant": [
            "Armored Core VI Fires of Rubicon",
            "Titanfall 2",
            "MechWarrior 5 Mercenaries",
            "Daemon X Machina",
            "GUNDAM EVOLUTION",
        ],
    },
    {
        "prompt": "quiero juegos de estrategia espacial y gestion de imperios",
        "relevant": [
            "Stellaris",
            "Endless Space 2",
            "Galactic Civilizations III",
            "Sins of a Solar Empire Rebellion",
            "Distant Worlds 2",
        ],
    },
    {
        "prompt": "juegos de dinosaurios supervivencia y mundo abierto",
        "relevant": [
            "ARK Survival Evolved",
            "ARK Survival Ascended",
            "The Isle",
            "Jurassic World Evolution 2",
            "Path of Titans",
        ],
    },
    {
        "prompt": "quiero juegos de parkour y accion en primera persona",
        "relevant": [
            "Dying Light",
            "Dying Light 2 Stay Human",
            "Mirror's Edge Catalyst",
            "Ghostrunner",
            "Titanfall 2",
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
        "prompt": "quiero juegos de pelea medieval con espadas populares",
        "relevant": [
            "Mount & Blade II Bannerlord",
            "Chivalry 2",
            "Mordhau",
            "FOR HONOR",
            "Kingdom Come Deliverance",
        ],
    },
    {
        "prompt": "juegos de construccion de fabricas y automatizacion",
        "relevant": [
            "Factorio",
            "Satisfactory",
            "Dyson Sphere Program",
            "Shapez",
            "Mindustry",
        ],
    },
    {
        "prompt": "busco juegos de accion cooperativa contra monstruos",
        "relevant": [
            "Monster Hunter World",
            "Monster Hunter Rise",
            "Deep Rock Galactic",
            "Warhammer Vermintide 2",
            "Killing Floor 2",
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
        "prompt": "juegos de supervivencia bajo el agua o en el oceano",
        "relevant": [
            "Subnautica",
            "Subnautica Below Zero",
            "Raft",
            "Stranded Deep",
            "ABZU",
        ],
    },
    {
        "prompt": "quiero juegos de terror cooperativo para jugar con amigos",
        "relevant": [
            "Phasmophobia",
            "Dead by Daylight",
            "The Forest",
            "Sons Of The Forest",
            "Lethal Company",
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
        "prompt": "quiero juegos de disparos gratis y populares",
        "relevant": [
            "Counter-Strike 2",
            "Team Fortress 2",
            "Apex Legends",
            "PUBG BATTLEGROUNDS",
            "Warframe",
        ],
    },
    {
        "prompt": "juegos de fantasia online con mucho contenido y muchas reseñas",
        "relevant": [
            "FINAL FANTASY XIV Online",
            "The Elder Scrolls Online",
            "Lost Ark",
            "Black Desert",
            "Path of Exile",
        ],
    },
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