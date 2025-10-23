// src/utils/leagueJoinNetwork.js
import { getLeague, saveLeague, addAudit } from './leagueStore';
import { readLeagueLocal } from './leagueSearch';

/**
 * Búsqueda visual (puedes llamar a searchLeaguesLocal directamente desde la página,
 * pero dejo este envoltorio por si luego reemplazan con llamada HTTP real).
 */
export { searchLeaguesLocal } from './leagueSearch';

/**
 * Simula unirse a una liga con alias, nombre de equipo y "password".
 * NOTA: La validación real de password la hará el backend. Aquí solo pedimos que no esté vacío.
 */
export async function fakeJoinLeagueVisual({ leagueId, alias, teamName, password, userEmail = 'you@local' }) {
  await new Promise(r => setTimeout(r, 350));

  if (!password || !password.trim()) throw new Error('Credenciales inválidas.'); // genérico

  const league = getLeague(leagueId) || readLeagueLocal(leagueId);
  if (!league) throw new Error('La liga no existe o está inactiva.');

  if (String(league.status).toLowerCase() !== 'pre-draft' && String(league.status).toLowerCase() !== 'active') {
    throw new Error('La liga no acepta nuevas inscripciones.');
  }

  // Cupos
  const capacity = Number(league.teams) || Number(league.teamsMax) || 0;
  const registered = Number(league.registeredTeams || (league.members?.length || 0));
  if (capacity && registered >= capacity) throw new Error('La liga no tiene cupos disponibles.');

  // Validar unicidad de alias y nombre de equipo dentro de la liga (visual)
  const members = Array.isArray(league.members) ? league.members : [];
  const aliasClash = alias && members.find(m => m.alias?.toLowerCase() === alias.trim().toLowerCase());
  if (aliasClash) throw new Error('El alias ya existe en la liga.');

  const teamClash = teamName && (
    members.find(m => m.teamName?.toLowerCase() === teamName.trim().toLowerCase())
    || (league.commisshTeamName && league.commisshTeamName.toLowerCase() === teamName.trim().toLowerCase())
    || (league.commissionerTeamName && league.commissionerTeamName.toLowerCase() === teamName.trim().toLowerCase())
  );
  if (teamClash) throw new Error('El nombre de equipo ya existe en la liga.');

  // Registrar miembro
  const member = {
    id: `mem_${Date.now()}`,
    email: userEmail,
    alias: alias?.trim() || null,
    teamName: teamName?.trim(),
    joinedAt: new Date().toISOString(),
  };

  league.members = [...members, member];
  league.registeredTeams = (league.registeredTeams || members.length) + 1;

  saveLeague(league);

  addAudit(league.id, {
    action: 'league_join',
    by: userEmail,
    notes: `Usuario se unió a la liga`,
    fields: [{ field: 'registeredTeams', oldValue: registered, newValue: league.registeredTeams }],
  });

  const remaining = capacity ? capacity - league.registeredTeams : 0;

  return {
    ok: true,
    data: {
      leagueId: league.id,
      memberId: member.id,
      remainingSlots: remaining,
      redirect_to: `/league/${league.id}`, // visual, ajústalo si quieres
    },
  };
}
