import requests

queries = {
    "zombie survival multiplayer": [
        "Project Zomboid",
        "DayZ",
        "Unturned",
        "7 Days to Die",
        "State of Decay 2: Juggernaut Edition"
    ],

    "pixel art adventure": [
        "Terraria",
        "Stardew Valley",
        "Undertale",
        "Core Keeper",
        "OneShot"
    ],

    "medieval fantasy rpg": [
        "Baldur's Gate 3",
        "The Witcher 3: Wild Hunt",
        "Kingdom Come: Deliverance",
        "Dragon's Dogma 2",
        "Divinity: Original Sin 2 - Definitive Edition"
    ],

    "souls like": [
        "ELDEN RING",
        "Lords of the Fallen",
        "Dark Souls",
        "Lies of P",
        "Black Myth: Wukong"
    ]
}

total_recall = 0

for query, relevant_games in queries.items():

    response = requests.get(
        "http://127.0.0.1:8000/search",
        params={
            "query": query
        }
    )

    results = response.json()

    found_games = [
        game["name"]
        for game in results
    ]

    hits = 0

    for game in relevant_games:

        if any(
            game.lower() in result.lower()
            for result in found_games
        ):
            hits += 1

    recall = hits / len(relevant_games)

    total_recall += recall

    print("\n" + "="*50)
    print("Consulta:", query)

    print("\nEncontrados:")

    for game in found_games:
        print("-", game)

    print("\nHits:", hits)
    print("Recall:", round(recall, 2))

average_recall = (
    total_recall /
    len(queries)
)

print("\n" + "="*50)
print("RECALL PROMEDIO")
print(round(average_recall, 2))