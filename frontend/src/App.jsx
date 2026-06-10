import { useState } from "react";
import "./App.css";

function App() {
  const [query, setQuery] = useState("");
  const [maxPrice, setMaxPrice] = useState("");
const [minReviews, setMinReviews] = useState("");
  const [results, setResults] = useState([]);

  const searchGames = async () => {
   const url =
  `http://127.0.0.1:8000/hybrid-search` +
  `?query=${encodeURIComponent(query)}` +
  `&max_price=${maxPrice || 999}` +
  `&min_reviews=${minReviews || 0}`;

    const response = await fetch(url);

    const data = await response.json();

    setResults(data);
  };

  return (
    <div className="container">
      <h1>Steam Hybrid Search</h1>

      <input
        type="text"
        placeholder="Buscar videojuegos..."
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
  type="number"
  placeholder="Reviews mínimas"
  value={minReviews}
  onChange={(e) => setMinReviews(e.target.value)}
/>

      <button onClick={searchGames}>
        Buscar
      </button>

      <div className="results">
        {results.map((game, index) => (
          <div key={index} className="card">
            <h3>{game.name}</h3>

            <p>💰 ${game.price}</p>

            <p>⭐ Rating: {game.rating}%</p>

            <p>📝 Reviews: {game.reviews}</p>

            <p>🎯 Similarity: {Number(game.similarity ?? 0).toFixed(3)}</p>
<p>🏆 Score: {Number(game.final_score ?? 0).toFixed(3)}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;