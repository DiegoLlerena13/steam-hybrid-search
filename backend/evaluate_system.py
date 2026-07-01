import re
import unicodedata
import requests
import pandas as pd

BASE_URL = "http://127.0.0.1:8000"

TESTS = [
    {
        "query": "zombie survival multiplayer",
        "relevant": [
            "Project Zomboid",
            "DayZ",
            "7 Days to Die",
            "Unturned",
            "Dying Light"
        ]
    },
    {
        "query": "souls-like dark fantasy action rpg",
        "relevant": [
            "ELDEN RING",
            "DARK SOULS III",
            "DARK SOULS REMASTERED",
            "Sekiro Shadows Die Twice",
            "Lords of the Fallen"
        ]
    },
    {
        "query": "pixel art adventure",
        "relevant": [
            "Terraria",
            "Stardew Valley",
            "Undertale",
            "Hollow Knight",
            "Dead Cells"
        ]
    },
    {
        "query": "medieval fantasy rpg",
        "relevant": [
            "The Witcher 3 Wild Hunt",
            "Baldur's Gate 3",
            "Divinity Original Sin 2",
            "ELDEN RING",
            "Dragon's Dogma 2"
        ]
    },
    {
        "query": "farming life simulator",
        "relevant": [
            "Stardew Valley",
            "Farming Simulator 22",
            "My Time at Portia",
            "Coral Island",
            "Sun Haven"
        ]
    },
    {
        "query": "competitive multiplayer fps tactical shooter",
        "relevant": [
            "Counter-Strike 2",
            "Tom Clancy's Rainbow Six Siege",
            "Apex Legends",
            "PUBG BATTLEGROUNDS",
            "Team Fortress 2"
        ]
    },
    {
        "query": "open world fantasy adventure exploration",
        "relevant": [
            "The Elder Scrolls V Skyrim Special Edition",
            "The Witcher 3 Wild Hunt",
            "ELDEN RING",
            "Dragon's Dogma 2",
            "Horizon Zero Dawn Complete Edition"
        ]
    },
    {
        "query": "metroidvania dark fantasy platformer action adventure",
        "relevant": [
            "Hollow Knight",
            "Dead Cells",
            "Blasphemous",
            "Ori and the Blind Forest Definitive Edition",
            "ENDER LILIES Quietus of the Knights"
        ]
    },
    {
        "query": "sandbox crafting survival open world",
        "relevant": [
            "Terraria",
            "Valheim",
            "Rust",
            "Raft",
            "Don't Starve Together"
        ]
    },
    {
        "query": "roguelike action dungeon crawler",
        "relevant": [
            "Hades",
            "The Binding of Isaac Rebirth",
            "Dead Cells",
            "Enter the Gungeon",
            "Risk of Rain 2"
        ]
    },
    {
        "query": "city building management strategy",
        "relevant": [
            "Cities Skylines",
            "Cities Skylines II",
            "Frostpunk",
            "Anno 1800",
            "Tropico 6"
        ]
    },
    {
        "query": "horror survival psychological scary",
        "relevant": [
            "Resident Evil 2",
            "Resident Evil 4",
            "Outlast",
            "Amnesia The Dark Descent",
            "The Forest"
        ]
    },
    {
        "query": "space exploration sci fi survival",
        "relevant": [
            "No Man's Sky",
            "Elite Dangerous",
            "Kerbal Space Program",
            "Space Engineers",
            "Astroneer"
        ]
    },
    {
        "query": "turn based strategy civilization empire",
        "relevant": [
            "Sid Meier's Civilization VI",
            "Total War WARHAMMER III",
            "XCOM 2",
            "Age of Wonders 4",
            "HUMANKIND"
        ]
    },
    {
        "query": "racing simulation realistic cars",
        "relevant": [
            "Assetto Corsa",
            "Forza Horizon 5",
            "F1 23",
            "DiRT Rally 2.0",
            "Project CARS 2"
        ]
    },
    {
        "query": "sports football soccer simulation",
        "relevant": [
            "EA SPORTS FC 24",
            "eFootball",
            "Football Manager 2024",
            "Rocket League",
            "FIFA 23"
        ]
    },
    {
        "query": "anime fighting action adventure",
        "relevant": [
            "NARUTO SHIPPUDEN Ultimate Ninja STORM 4",
            "DRAGON BALL FighterZ",
            "Persona 5 Royal",
            "CODE VEIN",
            "GUILTY GEAR STRIVE"
        ]
    },
    {
        "query": "cozy relaxing casual game",
        "relevant": [
            "Stardew Valley",
            "Unpacking",
            "A Short Hike",
            "Slime Rancher",
            "Dorfromantik"
        ]
    },
    {
        "query": "card strategy roguelike deckbuilding",
        "relevant": [
            "Slay the Spire",
            "Balatro",
            "Monster Train",
            "Inscryption",
            "Across the Obelisk"
        ]
    },
    {
        "query": "massively multiplayer online fantasy rpg",
        "relevant": [
            "FINAL FANTASY XIV Online",
            "The Elder Scrolls Online",
            "Black Desert",
            "Lost Ark",
            "Guild Wars 2"
        ]
    }
]


def normalize(text):
    text = str(text).lower()

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
        "_": " "
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = unicodedata.normalize("NFKD", text)
    text = "".join(
        ch for ch in text
        if not unicodedata.combining(ch)
    )

    text = re.sub(r"[^a-z0-9]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    words_to_remove = {
        "goty",
        "edition",
        "definitive",
        "remastered",
        "complete",
        "special",
        "game",
        "of",
        "the"
    }

    tokens = [
        token for token in text.split()
        if token not in words_to_remove
    ]

    return " ".join(tokens)


def is_match(found_name, relevant_name):
    found = normalize(found_name)
    relevant = normalize(relevant_name)

    if not found or not relevant:
        return False

    if found == relevant:
        return True

    if relevant in found or found in relevant:
        return True

    found_tokens = set(found.split())
    relevant_tokens = set(relevant.split())

    if not found_tokens or not relevant_tokens:
        return False

    overlap = found_tokens.intersection(relevant_tokens)
    ratio = len(overlap) / len(relevant_tokens)

    return ratio >= 0.70


def call_api(endpoint, query):
    params = {
        "query": query,
        "min_reviews": 1000
    }

    response = requests.get(
        f"{BASE_URL}/{endpoint}",
        params=params,
        timeout=60
    )

    if response.status_code != 200:
        print("Error:", endpoint, response.status_code)
        print(response.text)
        return []

    return response.json()


def count_hits(results, relevant, k=10):
    top_k = results[:k]
    hits = 0
    matched = []

    for rel in relevant:
        for item in top_k:
            if is_match(item["name"], rel):
                hits += 1
                matched.append({
                    "relevant": rel,
                    "found": item["name"]
                })
                break

    return hits, matched


def metrics(results, relevant, k=10):
    hits, matched = count_hits(results, relevant, k)

    return {
        "hits": hits,
        "recall": hits / len(relevant),
        "precision": hits / k,
        "matched": matched
    }


def main():
    rows = []

    print("\nEVALUACION DEL SISTEMA")
    print("=" * 80)

    for test in TESTS:
        query = test["query"]
        relevant = test["relevant"]

        vector_results = call_api("search", query)
        hybrid_results = call_api("hybrid-search", query)

        vector_metrics = metrics(vector_results, relevant)
        hybrid_metrics = metrics(hybrid_results, relevant)

        rows.append({
            "query": query,
            "method": "Vectorial",
            "hits": vector_metrics["hits"],
            "recall_at_10": round(vector_metrics["recall"], 3),
            "precision_at_10": round(vector_metrics["precision"], 3),
            "matched": vector_metrics["matched"]
        })

        rows.append({
            "query": query,
            "method": "Hibrida",
            "hits": hybrid_metrics["hits"],
            "recall_at_10": round(hybrid_metrics["recall"], 3),
            "precision_at_10": round(hybrid_metrics["precision"], 3),
            "matched": hybrid_metrics["matched"]
        })

        print("\nConsulta:", query)

        print("\nVectorial Top 10:")
        for item in vector_results[:10]:
            print("-", item["name"])

        print("Coincidencias vectorial:", vector_metrics["matched"])
        print("Recall@10 vectorial:", round(vector_metrics["recall"], 3))
        print("Precision@10 vectorial:", round(vector_metrics["precision"], 3))

        print("\nHibrida Top 10:")
        for item in hybrid_results[:10]:
            print("-", item["name"])

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
        "recall_at_10",
        "precision_at_10"
    ]])

    print("\nPROMEDIOS")
    print("=" * 80)
    print(
        df.groupby("method")[
            ["hits", "recall_at_10", "precision_at_10"]
        ].mean()
    )

    df.to_csv(
        "../docs/evaluation_results.csv",
        index=False,
        encoding="utf-8-sig"
    )

    print("\nArchivo guardado en:")
    print("../docs/evaluation_results.csv")


if __name__ == "__main__":
    main()