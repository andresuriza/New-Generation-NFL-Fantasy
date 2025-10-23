// src/utils/leagueNetwork.js
import { saveLeague, addAudit } from './leagueStore'

/**
 * Simula la creación de liga (visual) sin afectar la red real ni auth.
 */
export async function fakeLeagueCreateVisual(payload) {
  await new Promise(r => setTimeout(r, 400))

  if (!payload?.name?.trim()) throw new Error('El nombre es obligatorio.')
  if (![4, 6].includes(Number(payload.playoffs))) throw new Error('Formato de playoffs inválido.')

  const league = saveLeague({
    id: payload.id,
    name: payload.name.trim(),
    description: payload.description?.trim() || '',
    teams: Number(payload.teams),
    registeredTeams: 1,
    status: payload.status,
    season: payload.season,
    commissionerEmail: 'you@local',
    gameScheme: 'Redraft',
    scoringSystem: 'PPR',
    playoffsTeams: Number(payload.playoffs),
    allowDecimals: !!payload.allowDecimals,
    tradeDeadlineActive: !!payload.tradeDeadlineActive,
    tradeDeadlineAt: null,
    maxSeasonTradesPerTeam: payload.maxSeasonTradesPerTeam ?? null,
    maxSeasonFAAddsPerTeam: payload.maxSeasonFAAddsPerTeam ?? null,
    draft: { pending: true, sessionId: `draft_${payload.id}` },
    currentWeek: 1,
    audit: [],
    createdAt: payload.createdAt,
    commishTeamName: payload.commishTeamName,
  })

  addAudit(league.id, {
    action: 'league_create',
    by: 'you@local',
    notes: 'Creación de liga visual',
    fields: [
      { field: 'status', oldValue: null, newValue: league.status },
      { field: 'playoffsTeams', oldValue: null, newValue: league.playoffsTeams },
      { field: 'teams', oldValue: null, newValue: league.teams },
    ],
  })

  const remainingSlots = league.teams - league.registeredTeams

  return {
    ok: true,
    data: {
      id: league.id,
      remainingSlots,
      redirect_to: `/league/${league.id}/admin`,
    },
  }
}
