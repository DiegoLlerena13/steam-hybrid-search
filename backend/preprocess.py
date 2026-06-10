import pandas as pd

# Cargar dataset original
df = pd.read_csv("../dataset/games_march2025_cleaned.csv")

print("Dataset cargado")
print(df.shape)

# Crear texto semántico mejorado
# Ahora incluye genres y tags, que son claves para búsquedas como:
# souls-like, pixel art, roguelike, survival, open world, etc.
df["semantic_text"] = (
    df["name"].fillna("") + " " +
    df["genres"].fillna("").astype(str) + " " +
    df["tags"].fillna("").astype(str) + " " +
    df["tags"].fillna("").astype(str) + " " +  # repetimos tags para darles más peso
    df["short_description"].fillna("") + " " +
    df["about_the_game"].fillna("") + " " +
    df["detailed_description"].fillna("")
)

# Guardar dataset procesado
df.to_csv(
    "../dataset/games_processed.csv",
    index=False
)

print("Archivo guardado")
print("\nTexto semántico generado")

# Verificar Counter Strike
print(df["semantic_text"].iloc[0][:500])

# Verificar Elden Ring
elden = df[df["name"].str.contains("ELDEN RING", case=False, na=False)]

print("\nTexto semántico de ELDEN RING:")
print(elden["semantic_text"].iloc[0][:1000])