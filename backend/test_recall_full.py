import requests

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
    }
]


def search(endpoint, query):
    response = requests.get(
        f"{BASE_URL}/{endpoint}",
        params={
            "query": query,
            "min_reviews": 1000
        }
    )

    if response.status_code != 200:
        print("Error:", response.status_code, response.text)
        return []

    return response.json()


def recall_at_k(results, relevant, k=10):
    top_k = results[:k]

    found_names = [
        item["name"].lower()
        for item in top_k
    ]

    hits = 0

    for rel in relevant:
        rel_lower = rel.lower()

        if any(rel_lower in name or name in rel_lower for name in found_names):
            hits += 1

    return hits / len(relevant), hits


def main():
    total_vector_recall = 0
    total_hybrid_recall = 0

    print("\nEVALUACION RECALL@10")
    print("=" * 60)

    for test in TESTS:
        query = test["query"]
        relevant = test["relevant"]

        vector_results = search(
            "search",
            query
        )

        hybrid_results = search(
            "hybrid-search",
            query
        )

        vector_recall, vector_hits = recall_at_k(
            vector_results,
            relevant
        )

        hybrid_recall, hybrid_hits = recall_at_k(
            hybrid_results,
            relevant
        )

        total_vector_recall += vector_recall
        total_hybrid_recall += hybrid_recall

        print("\nConsulta:", query)
        print("Relevantes:", relevant)

        print("\nVectorial Top 10:")
        for item in vector_results[:10]:
            print("-", item["name"])

        print("Recall Vectorial@10:", round(vector_recall, 2), f"({vector_hits}/{len(relevant)})")

        print("\nHibrida Top 10:")
        for item in hybrid_results[:10]:
            print("-", item["name"])

        print("Recall Hibrida@10:", round(hybrid_recall, 2), f"({hybrid_hits}/{len(relevant)})")

    avg_vector = total_vector_recall / len(TESTS)
    avg_hybrid = total_hybrid_recall / len(TESTS)

    print("\n" + "=" * 60)
    print("PROMEDIO")
    print("Recall Vectorial@10:", round(avg_vector, 2))
    print("Recall Hibrida@10:", round(avg_hybrid, 2))


if __name__ == "__main__":
    main()