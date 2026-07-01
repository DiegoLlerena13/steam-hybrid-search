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
  const [results, setResults] = useState([]);
  const [interpretedQuery, setInterpretedQuery] = useState("");
  const [filters, setFilters] = useState(null);
  const [transparency, setTransparency] = useState(null);

  const searchGames = async () => {
    const url =
      `http://127.0.0.1:8000/natural-search` +
      `?prompt=${encodeURIComponent(prompt)}`;

    const response = await fetch(url);
    const data = await response.json();

    setInterpretedQuery(data.interpreted_query);
    setFilters(data.filters);
    setTransparency(data.transparency);
    setResults(data.results);
  };

  return (
    <div className="container">
      <h1>Steam Hybrid Search</h1>

      <p className="subtitle">
        Busca videojuegos usando lenguaje natural.
      </p>

      <textarea
        placeholder="Ej: juegos parecidos a dark souls populares después del 2020 y menos de 50 dólares"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
      />

      <button onClick={searchGames}>
        Buscar
      </button>

      {filters && (
        <div className="interpretation">
          <h2>Transparencia del sistema</h2>

          <p>
            <strong>Consulta original:</strong> {prompt}
          </p>

          <p>
            <strong>Consulta interpretada para embeddings:</strong>{" "}
            {interpretedQuery}
          </p>

          {transparency && (
            <>
              <p>
                <strong>🏷️ Conceptos semánticos extraídos:</strong>{" "}
                {transparency.semantic_tags.join(", ")}
              </p>

              <p>
                <strong>🧠 Parte vectorial:</strong>{" "}
                {transparency.vector_part}
              </p>

              <p>
                <strong>🗄️ Parte SQL:</strong>{" "}
                {transparency.sql_part}
              </p>

              <p>
                <strong>📊 Fórmula de ranking:</strong>{" "}
                {transparency.ranking_formula}
              </p>
            </>
          )}

          <div className="filters">
            <span>💰 Precio máximo: ${filters.max_price_usd}</span>
            <span>📅 Fecha mínima: {filters.min_date}</span>
            <span>📝 Reviews mínimas: {filters.min_reviews}</span>
            <span>⭐ Rating mínimo: {filters.min_rating}%</span>
          </div>

          {transparency && (
            <div className="filters">
              <span>{transparency.recognized_filters.price}</span>
              <span>{transparency.recognized_filters.release_date}</span>
              <span>{transparency.recognized_filters.reviews}</span>
              <span>{transparency.recognized_filters.rating}</span>
            </div>
          )}
        </div>
      )}

      {results.length > 0 && (
        <div className="chart">
          <h2>Comparación de score final por videojuego</h2>

          <ResponsiveContainer width="100%" height={420}>
            <BarChart data={results}>
              <XAxis
                dataKey="name"
                angle={-25}
                textAnchor="end"
                height={120}
                interval={0}
              />
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
            <h3>
              {index + 1}. {game.name}
            </h3>

            <p>💰 Precio: ${game.price}</p>
            <p>📅 Fecha de lanzamiento: {game.release_date}</p>
            <p>⭐ Rating positivo: {game.rating}%</p>
            <p>📝 Reviews totales: {game.reviews}</p>

            <p>
              🎯 Similitud semántica:{" "}
              {Number(game.similarity).toFixed(3)}
            </p>

            <p>
              🏆 Score final híbrido:{" "}
              {Number(game.final_score).toFixed(3)}
            </p>

            {game.genres && (
              <p>
                <strong>🎮 Géneros:</strong>{" "}
                {Array.isArray(game.genres)
                  ? game.genres.join(", ")
                  : game.genres}
              </p>
            )}

            {game.tags && (
              <p>
                <strong>🏷️ Tags:</strong>{" "}
                {Array.isArray(game.tags)
                  ? game.tags.join(", ")
                  : game.tags}
              </p>
            )}

            {game.description && (
              <div className="description">
                <strong>📌 Presentación:</strong>
                <p>{game.description}</p>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;