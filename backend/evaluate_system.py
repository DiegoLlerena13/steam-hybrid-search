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
            "DARK SOULS™ III",
            "DARK SOULS™: REMASTERED",
            "Sekiro™: Shadows Die Twice - GOTY Edition",
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
            "The Witcher 3: Wild Hunt",
            "Baldur's Gate 3",
            "Divinity: Original Sin 2 - Definitive Edition",
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
    }
]


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


def normalize(text):
    return text.lower().strip()


def count_hits(results, relevant, k=10):
    top_k = results[:k]

    found_names = [
        normalize(item["name"])
        for item in top_k
    ]

    hits = 0
    matched = []

    for rel in relevant:
        rel_norm = normalize(rel)

        was_found = any(
            rel_norm in found or found in rel_norm
            for found in found_names
        )

        if was_found:
            hits += 1
            matched.append(rel)

    return hits, matched


def metrics(results, relevant, k=10):
    hits, matched = count_hits(results, relevant, k)

    recall = hits / len(relevant)
    precision = hits / k

    return {
        "hits": hits,
        "recall": recall,
        "precision": precision,
        "matched": matched
    }


def main():
    rows = []

    print("\nEVALUACIÓN DEL SISTEMA")
    print("=" * 70)

    for test in TESTS:
        query = test["query"]
        relevant = test["relevant"]

        vector_results = call_api(
            "search",
            query
        )

        hybrid_results = call_api(
            "hybrid-search",
            query
        )

        vector_metrics = metrics(
            vector_results,
            relevant
        )

        hybrid_metrics = metrics(
            hybrid_results,
            relevant
        )

        rows.append({
            "query": query,
            "method": "Vectorial",
            "hits": vector_metrics["hits"],
            "recall_at_10": round(vector_metrics["recall"], 3),
            "precision_at_10": round(vector_metrics["precision"], 3)
        })

        rows.append({
            "query": query,
            "method": "Híbrida",
            "hits": hybrid_metrics["hits"],
            "recall_at_10": round(hybrid_metrics["recall"], 3),
            "precision_at_10": round(hybrid_metrics["precision"], 3)
        })

        print("\nConsulta:", query)

        print("\nVectorial Top 10:")
        for item in vector_results[:10]:
            print("-", item["name"])

        print("Recall@10 vectorial:", round(vector_metrics["recall"], 3))
        print("Precision@10 vectorial:", round(vector_metrics["precision"], 3))

        print("\nHíbrida Top 10:")
        for item in hybrid_results[:10]:
            print("-", item["name"])

        print("Recall@10 híbrida:", round(hybrid_metrics["recall"], 3))
        print("Precision@10 híbrida:", round(hybrid_metrics["precision"], 3))

    df = pd.DataFrame(rows)

    print("\nRESULTADOS")
    print("=" * 70)
    print(df)

    print("\nPROMEDIOS")
    print("=" * 70)
    print(
        df.groupby("method")[
            ["hits", "recall_at_10", "precision_at_10"]
        ].mean()
    )

    df.to_csv(
        "../docs/evaluation_results.csv",
        index=False
    )

    print("\nArchivo guardado en:")
    print("../docs/evaluation_results.csv")


if __name__ == "__main__":
    main()