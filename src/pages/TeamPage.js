import { useState } from "react";
import TeamHeader from "../components/TeamHeader";
import PlayerFilter from "../components/PlayerFilter";
import PlayerList from "../components/PlayerList";
import AcquisitionChart from "../components/AcquisitionChart";
import EmptyState from "../components/EmptyState";
import { teamData } from "../mock/teamData";
import "../styles/global.css";

export default function TeamPage() {
  const [filter, setFilter] = useState({ position: "ALL", search: "" });

  const filteredPlayers = teamData.players.filter((player) => {
    const matchPosition =
      filter.position === "ALL" || player.position === filter.position;
    const matchSearch = player.name
      .toLowerCase()
      .includes(filter.search.toLowerCase());
    return matchPosition && matchSearch;
  });

  return (
    <div className="page-container">
      <div className="content-container">
        <TeamHeader team={teamData} />

        <div className="filter-container">
          <PlayerFilter filter={filter} onChange={setFilter} />
        </div>

        <div className="card">
          <h2 className="section-title">Roster de equipo</h2>
          {filteredPlayers.length > 0 ? (
            <PlayerList players={filteredPlayers} />
          ) : (
            <EmptyState message="No hay jugadores asignados a este equipo." />
          )}
        </div>

        <div className="card">
          <h2 className="section-title">Distribución de adquisición</h2>
          <AcquisitionChart players={teamData.players} />
        </div>
      </div>
    </div>
  );
}
