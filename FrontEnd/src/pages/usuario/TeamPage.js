import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import TeamHeader from "../../components/TeamHeader";
import PlayerFilter from "../../components/PlayerFilter";
import PlayerList from "../../components/PlayerList";
import AcquisitionChart from "../../components/AcquisitionChart";
import EmptyState from "../../components/EmptyState";
import { getById as apiGetEquipo } from "../../utils/communicationModule/resources/equipos";
import { getEquipoMedia as apiGetEquipoMedia } from "../../utils/communicationModule/resources/media";
import { getById as apiGetLiga } from "../../utils/communicationModule/resources/ligas";
import { getById as apiGetUsuario } from "../../utils/communicationModule/resources/usuarios";
import { teamData } from "../../mock/teamData";
import "../../styles/global.css";

export default function TeamPage() {
  const { id } = useParams();
  const [filter, setFilter] = useState({ position: "ALL", search: "" });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [team, setTeam] = useState(null);
  // Roster and distribution use mock data per requirement
  const players = teamData.players;

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        // Fetch team basic data
        const equipo = await apiGetEquipo(id);
        // Optionally fetch league name and team media
        let leagueName = equipo.liga_id;
        try {
          const liga = await apiGetLiga(equipo.liga_id);
          leagueName = liga.nombre || leagueName;
        } catch {}
        // Get manager (usuario) display name
        let managerName = equipo.usuario_id;
        try {
          if (equipo.usuario_id != null) {
            const usuario = await apiGetUsuario(equipo.usuario_id);
            managerName = usuario.alias || usuario.nombre || usuario.correo || managerName;
          }
        } catch {}
        let image = undefined;
        try {
          const media = await apiGetEquipoMedia(equipo.id);
          image = media?.url;
        } catch {}

        // Map backend equipo to TeamHeader shape
        const teamHeader = {
          id: equipo.id,
          name: equipo.nombre,
          manager: managerName,
          image: image || "/imgs/XNFL.png",
          state: "Active",
          league: leagueName,
        };

        if (!cancelled) {
          setTeam(teamHeader);
        }
      } catch (e) {
        if (!cancelled) setError(e?.message || "No se pudo cargar el equipo");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    if (id) load();
    return () => {
      cancelled = true;
    };
  }, [id]);

  const filteredPlayers = useMemo(() => {
    return players.filter((player) => {
      const matchPosition =
        filter.position === "ALL" || player.position === filter.position;
      const matchSearch = player.name
        .toLowerCase()
        .includes(filter.search.toLowerCase());
      return matchPosition && matchSearch;
    });
  }, [players, filter]);

  return (
    <div className="page-container">
      <div className="content-container">
        {loading ? (
          <div className="card"><p className="muted">Cargando equipo…</p></div>
        ) : error ? (
          <div className="card"><p className="error">{error}</p></div>
        ) : (
          <TeamHeader team={team} />
        )}

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
          <AcquisitionChart players={players} />
        </div>
      </div>
    </div>
  );
}
