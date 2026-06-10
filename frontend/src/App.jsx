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
  const [query, setQuery] = useState("");
  const [maxPrice, setMaxPrice] = useState("");
  const [minDate, setMinDate] = useState("");
  const [minReviews, setMinReviews] = useState("");
  const [minRating, setMinRating] = useState("");
  const [results, setResults] = useState([]);

  const searchGames = async () => {
    const url =
      `http://127.0.0.1:8000/hybrid-search` +
      `?query=${encodeURIComponent(query)}` +
      `&max_price=${maxPrice || 999}` +
      `&min_date=${minDate || "2000-01-01"}` +
      `&min_reviews=${minReviews || 0}` +
      `&min_rating=${minRating || 0}`;

    const response = await fetch(url);
    const data = await response.json();

    setResults(data);
  };

  return (
    <div className="container">
      <h1>Steam Hybrid Search</h1>

      <input
        type="text"
        placeholder="Ej: souls-like dark fantasy action rpg"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />

      <input
        type="number"
        placeholder="Precio máximo"
        value={maxPrice}
        onChange={(e) => setMaxPrice(e.target.value)}
      />

      <input
        type="date"
        value={minDate}
        onChange={(e) => setMinDate(e.target.value)}
      />

      <input
        type="number"
        placeholder="Reviews mínimas"
        value={minReviews}
        onChange={(e) => setMinReviews(e.target.value)}
      />

      <input
        type="number"
        placeholder="Rating mínimo %"
        value={minRating}
        onChange={(e) => setMinRating(e.target.value)}
      />

      <button onClick={searchGames}>Buscar</button>

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
            <p>💰 Precio: ${game.price}</p>
            <p>📅 Fecha: {game.release_date}</p>
            <p>⭐ Rating: {game.rating}%</p>
            <p>📝 Reviews: {game.reviews}</p>
            <p>🎯 Similarity: {Number(game.similarity).toFixed(3)}</p>
            <p>🏆 Final Score: {Number(game.final_score).toFixed(3)}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;