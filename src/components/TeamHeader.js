import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

export default function TeamHeader({ teamId: propTeamId }) {
  const { id: routeId } = useParams();
  const [team, setTeam] = useState(null);

  useEffect(() => {
    const teams = JSON.parse(localStorage.getItem("fantasy_teams") || "[]");
    const targetId = propTeamId || routeId;
    if (targetId) {
      const found = teams.find((t) => t.id === targetId);
      setTeam(found || null);
    }
  }, [propTeamId, routeId]);

  if (!team) {
    return (
      <div className="card">
        <h2>Equipo no encontrado</h2>
        <p className="muted">No existe equipo con ese ID.</p>
      </div>
    );
  }

  return (
    <div className="card team-header">
      <div className="team-header__info">
        <img src={team.image} alt={team.name} className="team-header__img" />
        <div>
          <h2 className="team-header__name">{team.name}</h2>
          <p className="muted">Manager: {team.manager}</p>
          <p>League: {team.league}</p>
          <p>Estado: {team.state}</p>
        </div>
      </div>
    </div>
  );
}
