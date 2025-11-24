import { useAuth } from "../context/authContext";
import { useNavigate } from "react-router-dom";

export default function PlayerCard({ player }) {
  const { session } = useAuth();
  const navigate = useNavigate();
  const isAdmin = session?.user?.rol === "administrador";

  const handleAddNews = () => {
    navigate(`/player/${player.id}/add-news`);
  };

  return (
    <div className="player-card">
      <img src={player.image} alt={player.name} className="player-photo" />
      <h3>{player.name}</h3>
      <p className="player-details">
        {player.position} — {player.team}
      </p>
      {player.injury && <p className="injury-badge">{player.injury}</p>}
      {isAdmin && (
        <button
          className="button button--small"
          onClick={handleAddNews}
          style={{ marginTop: 8 }}
        >
          Agregar Noticia
        </button>
      )}
    </div>
  );
}
