import React, { useEffect, useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/authContext";
import "../../styles/global.css";
import PlayerList from "../../components/PlayerList";
import PlayerFilter from "../../components/PlayerFilter";
import { getPlayers } from "../../utils/communicationModule/resources/players.js";
import { list as getTeams } from "../../utils/communicationModule/resources/equipos.js";

function PlayerManagement() {
  const { session } = useAuth();
  const navigate = useNavigate();

  const [players, setPlayers] = useState([]);
  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [totalPlayers, setTotalPlayers] = useState(0);
  const [currentPage, setCurrentPage] = useState(0);
  const [filter, setFilter] = useState({
    position: "ALL",
    team: "",
    search: "",
  });

  const PLAYERS_PER_PAGE = 100;

  // Fetch players and teams from API
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [playersResponse, teamsResponse] = await Promise.all([
          getPlayers({
            skip: currentPage * PLAYERS_PER_PAGE,
            limit: PLAYERS_PER_PAGE,
            activo: true, // Only show active players
          }),
          getTeams()
        ]);

        setPlayers(playersResponse || []);
        setTeams(teamsResponse || []);
        // For now, we'll assume we have all players if we get less than the limit
        // In a real implementation, you'd want to get the total count from the API
        setTotalPlayers(playersResponse ? playersResponse.length : 0);
      } catch (error) {
        console.error("Error fetching data:", error);
        setPlayers([]);
        setTeams([]);
        setTotalPlayers(0);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [currentPage]);

  const filteredPlayers = useMemo(() => {
    // Create team mapping for quick lookup
    const teamMap = teams.reduce((acc, team) => {
      acc[team.id] = team.nombre;
      return acc;
    }, {});

    // Transform API data to match PlayerCard expectations
    const transformedPlayers = players.map(player => ({
      id: player.id,
      name: player.nombre,
      position: player.posicion,
      team: teamMap[player.equipo_id] || 'Unknown Team',
      image: player.imagen_url,
      activo: player.activo,
    }));

    // Apply filters
    return transformedPlayers.filter((player) => {
      const matchesPosition = !filter.position || filter.position === "ALL" || player.position === filter.position;
      const matchesTeam = !filter.team || player.team.toLowerCase().includes(filter.team.toLowerCase());
      const matchesSearch = !filter.search ||
        player.name.toLowerCase().includes(filter.search.toLowerCase());

      return matchesPosition && matchesTeam && matchesSearch && player.activo;
    });
  }, [players, teams, filter]);

  // Check if user is admin
  const isAdmin = session?.user?.rol === "administrador";
  if (!isAdmin) {
    navigate("/");
    return null;
  }

  if (loading) {
    return (
      <div className="container" style={{ paddingTop: 24 }}>
        <div className="card">
          <p>Cargando jugadores...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container" style={{ paddingTop: 24 }}>
      <div className="card">
        <h1 className="section-title">Gestión de Jugadores NFL</h1>
        <p className="section-subtitle">
          Como administrador puedes gestionar todos los jugadores NFL y agregar noticias sobre ellos.
        </p>

        <div style={{ marginTop: 24 }}>
          <PlayerFilter filter={filter} onChange={setFilter} />
        </div>

        <div style={{ marginTop: 24 }}>
          {filteredPlayers.length > 0 ? (
            <PlayerList players={filteredPlayers} />
          ) : (
            <div className="empty-state">
              <h3>No se encontraron jugadores</h3>
              <p>Intenta ajustar los filtros de búsqueda.</p>
            </div>
          )}
        </div>

        {/* Pagination */}
        {totalPlayers > PLAYERS_PER_PAGE && (
          <div style={{ marginTop: 24, display: "flex", justifyContent: "center", gap: 8 }}>
            <button
              className="button"
              onClick={() => setCurrentPage(prev => Math.max(0, prev - 1))}
              disabled={currentPage === 0}
            >
              Anterior
            </button>
            <span style={{ alignSelf: "center", padding: "0 16px" }}>
              Página {currentPage + 1}
            </span>
            <button
              className="button"
              onClick={() => setCurrentPage(prev => prev + 1)}
              disabled={players.length < PLAYERS_PER_PAGE}
            >
              Siguiente
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default PlayerManagement;