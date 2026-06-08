import pandas as pd

# Cargar dataset
df = pd.read_csv("../dataset/games_march2025_cleaned.csv")

print("Dataset cargado")
print(df.shape)

# Crear texto semántico
df["semantic_text"] = (
    df["name"].fillna("") + " " +
    df["short_description"].fillna("") + " " +
    df["about_the_game"].fillna("") + " " +
    df["detailed_description"].fillna("")
)
df.to_csv(
    "../dataset/games_processed.csv",
    index=False
)

print("Archivo guardado")
print("\nTexto semántico generado")

print(df["semantic_text"].iloc[0][:500])