import PlayerCard from "./PlayerCard";

export default function PlayerList({ players }) {
  return (
    <div className="player-list">
      {players.map((player) => (
        <PlayerCard key={player.id} player={player} />
      ))}
    </div>
  );
}
