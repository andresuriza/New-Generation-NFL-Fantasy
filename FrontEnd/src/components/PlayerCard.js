export default function PlayerCard({ player }) {
  return (
    <div className="player-card">
      <img src={player.image} alt={player.name} className="player-photo" />
      <h3>{player.name}</h3>
      <p className="player-details">
        {player.position} — {player.team}
      </p>
      {player.injury && <p className="injury-badge">{player.injury}</p>}
    </div>
  );
}
