import defaultTeamImage from "../imgs/default-team.png";

export default function TeamHeader({ team }) {
  return (
    <div className="team-header card">
      <img
        src={team.image || defaultTeamImage}
        alt="Team Logo"
        className="team-logo"
      />
      <div className="team-info">
        <h1>{team.name}</h1>
        <p>
          <strong>Manager:</strong> {team.manager}
        </p>
        <p>
          <strong>State:</strong> {team.state}
        </p>
        <p>
          <strong>League:</strong> {team.league}
        </p>
      </div>
    </div>
  );
}
