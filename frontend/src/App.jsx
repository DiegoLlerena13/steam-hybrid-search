import { useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import "./App.css";

function App() {
  const [prompt, setPrompt] = useState("");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const searchGames = async () => {
    if (!prompt.trim()) {
      setError("Ingresa una consulta en lenguaje natural.");
      return;
    }

    try {
      setLoading(true);
      setError("");
      setData(null);

      const url =
        `http://127.0.0.1:8000/natural-search` +
        `?prompt=${encodeURIComponent(prompt)}`;

      const response = await fetch(url);

      if (!response.ok) {
        throw new Error("Error al consultar la API");
      }

      const result = await response.json();
      setData(result);
    } catch (error) {
      setError("No se pudo realizar la búsqueda.");
    } finally {
      setLoading(false);
    }
  };

  const results = data?.results || [];

  return (
    <div className="container">
      <h1>Steam Hybrid Search</h1>

      <textarea
        placeholder="Ej: juegos similares a Dark Souls que cuesten menos de 60 dólares, populares y después del 2020"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        rows={4}
      />

      <button onClick={searchGames} disabled={loading}>
        {loading ? "Buscando..." : "Buscar"}
      </button>

      {error && <p className="error">{error}</p>}

      {data && (
        <div className="transparency">
          <h2>Interpretación de la consulta</h2>

          <p>
            <strong>Consulta original:</strong> {data.original_prompt}
          </p>

          <p>
            <strong>Consulta interpretada:</strong> {data.interpreted_query}
          </p>

          <p>
            <strong>Precio máximo:</strong> {data.filters.max_price_usd} USD
          </p>

          <p>
            <strong>Fecha mínima:</strong> {data.filters.min_date}
          </p>

        <p>
           <strong>Fecha máxima:</strong> {data.filters.max_date}
          </p>
          <p>
            <strong>Reviews mínimas:</strong> {data.filters.min_reviews}
          </p>

          <p>
            <strong>Rating mínimo:</strong> {data.filters.min_rating}%
          </p>
        </div>
      )}

      {results.length > 0 && (
        <div className="chart">
          <h2>Comparación de score final</h2>

          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={results}>
              <XAxis dataKey="name" hide />
              <YAxis />
              <Tooltip />
              <Bar dataKey="final_score" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="results">
        {results.map((game, index) => (
          <div key={index} className="card">
            <h3>{game.name}</h3>
            <p>Precio: ${game.price}</p>
            <p>Fecha: {game.release_date}</p>
            <p>Rating: {game.rating}%</p>
            <p>Reviews: {game.reviews}</p>
            <p>Similarity: {Number(game.similarity).toFixed(3)}</p>
            <p>Final Score: {Number(game.final_score).toFixed(3)}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;