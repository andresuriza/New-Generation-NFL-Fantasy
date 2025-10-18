export default function TeamHeader({ team }) {
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
      <img src={team.image} alt={team.name} className="team-logo" />
      <div className="team-info">
        <h1>{team.name}</h1>
        <p className="muted">Manager: {team.manager}</p>
        <p>Liga: {team.league}</p>
        <p>Estado: {team.state}</p>
      </div>
    </div>
  );
}
