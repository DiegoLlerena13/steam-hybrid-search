from app.routes.natural import (
    detect_price,
    detect_year_range,
    detect_reviews,
    detect_rating
)


EXPECTED_FILTERS = [
    {
        "query": "quiero juegos de zombies cooperativos de supervivencia populares con menos de 60 dolares",
        "expected": {
            "max_price_usd": 60,
            "min_date": "2000-01-01",
            "max_date": "2100-01-01",
            "min_reviews": 10000,
            "min_rating": 0
        }
    },
    {
        "query": "juegos tipo Dark Souls de fantasia oscura populares despues de 2015 y menos de 60 dolares",
        "expected": {
            "max_price_usd": 60,
            "min_date": "2015-01-01",
            "max_date": "2100-01-01",
            "min_reviews": 10000,
            "min_rating": 0
        }
    },
    {
        "query": "busco juegos pixel art de aventura metroidvania bien valorados con menos de 40 dolares",
        "expected": {
            "max_price_usd": 40,
            "min_date": "2000-01-01",
            "max_date": "2100-01-01",
            "min_reviews": 0,
            "min_rating": 80
        }
    },
    {
        "query": "rpg de fantasia medieval populares entre 2015 y 2024",
        "expected": {
            "max_price_usd": 999,
            "min_date": "2015-01-01",
            "max_date": "2024-12-31",
            "min_reviews": 10000,
            "min_rating": 0
        }
    },
    {
        "query": "juegos de supervivencia sandbox crafting mundo abierto populares",
        "expected": {
            "max_price_usd": 999,
            "min_date": "2000-01-01",
            "max_date": "2100-01-01",
            "min_reviews": 10000,
            "min_rating": 0
        }
    },
    {
        "query": "juegos de exploracion espacial ciencia ficcion y supervivencia sandbox",
        "expected": {
            "max_price_usd": 999,
            "min_date": "2000-01-01",
            "max_date": "2100-01-01",
            "min_reviews": 0,
            "min_rating": 0
        }
    },
    {
        "query": "simulacion de carreras realista con autos populares y menos de 70 dolares",
        "expected": {
            "max_price_usd": 70,
            "min_date": "2000-01-01",
            "max_date": "2100-01-01",
            "min_reviews": 10000,
            "min_rating": 0
        }
    },
    {
        "query": "juegos de futbol deportes y simulacion populares",
        "expected": {
            "max_price_usd": 999,
            "min_date": "2000-01-01",
            "max_date": "2100-01-01",
            "min_reviews": 10000,
            "min_rating": 0
        }
    },
    {
        "query": "mmorpg de fantasia online masivo populares despues de 2010",
        "expected": {
            "max_price_usd": 999,
            "min_date": "2010-01-01",
            "max_date": "2100-01-01",
            "min_reviews": 10000,
            "min_rating": 0
        }
    },
    {
        "query": "roguelike de accion y mazmorras con muchas reseñas y menos de 40 dolares",
        "expected": {
            "max_price_usd": 40,
            "min_date": "2000-01-01",
            "max_date": "2100-01-01",
            "min_reviews": 10000,
            "min_rating": 0
        }
    },
    {
        "query": "city builder gestion de recursos y construccion populares entre 2015 y 2024",
        "expected": {
            "max_price_usd": 999,
            "min_date": "2015-01-01",
            "max_date": "2024-12-31",
            "min_reviews": 10000,
            "min_rating": 0
        }
    },
    {
        "query": "juegos de terror y supervivencia cooperativos para jugar con amigos con menos de 60 dolares",
        "expected": {
            "max_price_usd": 60,
            "min_date": "2000-01-01",
            "max_date": "2100-01-01",
            "min_reviews": 0,
            "min_rating": 0
        }
    },
    {
        "query": "juegos de cartas estrategia deckbuilding roguelike con menos de 40 dolares",
        "expected": {
            "max_price_usd": 40,
            "min_date": "2000-01-01",
            "max_date": "2100-01-01",
            "min_reviews": 0,
            "min_rating": 0
        }
    },
    {
        "query": "metroidvania y plataformas dificiles bien valorados con menos de 40 dolares",
        "expected": {
            "max_price_usd": 40,
            "min_date": "2000-01-01",
            "max_date": "2100-01-01",
            "min_reviews": 0,
            "min_rating": 80
        }
    },
    {
        "query": "juegos indie bien valorados con pixel art y aventura con menos de 40 dolares",
        "expected": {
            "max_price_usd": 40,
            "min_date": "2000-01-01",
            "max_date": "2100-01-01",
            "min_reviews": 0,
            "min_rating": 80
        }
    },
    {
        "query": "fps multijugador competitivos y tacticos populares con muchas reseñas",
        "expected": {
            "max_price_usd": 999,
            "min_date": "2000-01-01",
            "max_date": "2100-01-01",
            "min_reviews": 10000,
            "min_rating": 0
        }
    },
    {
        "query": "juegos tranquilos de granja simulacion casual y vida relajante con menos de 40 dolares",
        "expected": {
            "max_price_usd": 40,
            "min_date": "2000-01-01",
            "max_date": "2100-01-01",
            "min_reviews": 0,
            "min_rating": 0
        }
    },
    {
        "query": "supervivencia sandbox mundo abierto con crafting exploracion y muchas reseñas",
        "expected": {
            "max_price_usd": 999,
            "min_date": "2000-01-01",
            "max_date": "2100-01-01",
            "min_reviews": 10000,
            "min_rating": 0
        }
    },
    {
        "query": "juegos populares de supervivencia exploracion espacial y construccion tipo sandbox",
        "expected": {
            "max_price_usd": 999,
            "min_date": "2000-01-01",
            "max_date": "2100-01-01",
            "min_reviews": 10000,
            "min_rating": 0
        }
    },
    {
        "query": "juegos de mundo abierto fantasia y exploracion populares despues de 2015",
        "expected": {
            "max_price_usd": 999,
            "min_date": "2015-01-01",
            "max_date": "2100-01-01",
            "min_reviews": 10000,
            "min_rating": 0
        }
    },
    {
        "query": "juegos cooperativos divertidos para jugar con amigos",
        "expected": {
            "max_price_usd": 999,
            "min_date": "2000-01-01",
            "max_date": "2100-01-01",
            "min_reviews": 0,
            "min_rating": 0
        }
    },
    {
        "query": "juegos casuales populares para pasar el rato",
        "expected": {
            "max_price_usd": 999,
            "min_date": "2000-01-01",
            "max_date": "2100-01-01",
            "min_reviews": 10000,
            "min_rating": 0
        }
    },
    {
        "query": "quiero juegos de rol con mucha historia y decisiones",
        "expected": {
            "max_price_usd": 999,
            "min_date": "2000-01-01",
            "max_date": "2100-01-01",
            "min_reviews": 0,
            "min_rating": 0
        }
    },
    {
        "query": "busco juegos de simulacion de camiones o manejo tranquilo",
        "expected": {
            "max_price_usd": 999,
            "min_date": "2000-01-01",
            "max_date": "2100-01-01",
            "min_reviews": 0,
            "min_rating": 0
        }
    },
    {
        "query": "busco juegos de plataformas dificiles y bien valorados",
        "expected": {
            "max_price_usd": 999,
            "min_date": "2000-01-01",
            "max_date": "2100-01-01",
            "min_reviews": 0,
            "min_rating": 80
        }
    },
    {
        "query": "juegos de estrategia por turnos de civilizaciones e imperios populares",
        "expected": {
            "max_price_usd": 999,
            "min_date": "2000-01-01",
            "max_date": "2100-01-01",
            "min_reviews": 10000,
            "min_rating": 0
        }
    },
    {
        "query": "juegos de gestion de colonias y supervivencia populares",
        "expected": {
            "max_price_usd": 999,
            "min_date": "2000-01-01",
            "max_date": "2100-01-01",
            "min_reviews": 10000,
            "min_rating": 0
        }
    },
    {
        "query": "juegos de accion cooperativa contra monstruos con muchas reseñas",
        "expected": {
            "max_price_usd": 999,
            "min_date": "2000-01-01",
            "max_date": "2100-01-01",
            "min_reviews": 10000,
            "min_rating": 0
        }
    },
    {
        "query": "juegos de disparos gratis y populares",
        "expected": {
            "max_price_usd": 999,
            "min_date": "2000-01-01",
            "max_date": "2100-01-01",
            "min_reviews": 10000,
            "min_rating": 0
        }
    },
    {
        "query": "juegos de fantasia online con mucho contenido y muchas reseñas",
        "expected": {
            "max_price_usd": 999,
            "min_date": "2000-01-01",
            "max_date": "2100-01-01",
            "min_reviews": 10000,
            "min_rating": 0
        }
    },
]


def evaluate_query(item):
    query = item["query"]
    expected = item["expected"]

    min_date, max_date = detect_year_range(query)

    predicted = {
        "max_price_usd": detect_price(query),
        "min_date": min_date,
        "max_date": max_date,
        "min_reviews": detect_reviews(query),
        "min_rating": detect_rating(query)
    }

    results = {}

    for field in expected:
        results[field] = predicted[field] == expected[field]

    return {
        "query": query,
        "expected": expected,
        "predicted": predicted,
        "results": results
    }


def main():
    evaluated = [evaluate_query(item) for item in EXPECTED_FILTERS]

    fields = [
        "max_price_usd",
        "min_date",
        "max_date",
        "min_reviews",
        "min_rating"
    ]

    total_by_field = {field: 0 for field in fields}
    correct_by_field = {field: 0 for field in fields}

    print("\nRESULTADOS POR CONSULTA\n")

    for item in evaluated:
        print("Consulta:", item["query"])
        print("Esperado:", item["expected"])
        print("Extraido:", item["predicted"])

        for field in fields:
            total_by_field[field] += 1

            if item["results"][field]:
                correct_by_field[field] += 1

        print("Aciertos:", item["results"])
        print("-" * 80)

    print("\nRESUMEN NLU\n")

    total_correct = 0
    total_fields = 0

    for field in fields:
        correct = correct_by_field[field]
        total = total_by_field[field]
        accuracy = correct / total if total > 0 else 0

        total_correct += correct
        total_fields += total

        print(f"{field}: {correct}/{total} = {accuracy:.3f}")

    overall_accuracy = total_correct / total_fields if total_fields > 0 else 0

    print("-" * 80)
    print(f"Exactitud promedio por campo: {total_correct}/{total_fields} = {overall_accuracy:.3f}")


if __name__ == "__main__":
    main()