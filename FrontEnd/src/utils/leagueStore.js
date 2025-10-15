const KEY = (id) => `league_${id}`;

export function getLeague(id) {
  try {
    const raw = localStorage.getItem(KEY(id));
    if (raw) return JSON.parse(raw);
  } catch {}

  // Mock base
  const demo = {
    id,
    name: 'Liga Demo',
    description: 'Liga de ejemplo',
    teams: 10,                    // capacidad máxima configurada
    registeredTeams: 1,           // ya registrados (tu equipo)
    status: 'Pre-Draft',          // 'Pre-Draft' | 'Active' | 'Inactive'
    season: 2025,
    commissionerEmail: 'demo@nfl.com',
    // Configurables en Pre-Draft:
    gameScheme: 'Redraft',        // 'Redraft' | 'Keeper' | 'Dynasty'
    scoringSystem: 'PPR',         // 'Standard' | 'Half-PPR' | 'PPR'
    playoffsTeams: 4,             // 4 | 6
    allowDecimals: true,
    tradeDeadlineActive: false,
    tradeDeadlineAt: null,        // ISO string si activo
    maxSeasonTradesPerTeam: null, // null => sin límite
    maxSeasonFAAddsPerTeam: null, // null => sin límite

    currentWeek: 1,
    draft: { pending: true, sessionId: 'draft_abc' },
    audit: [],
  };
  localStorage.setItem(KEY(id), JSON.stringify(demo));
  return demo;
}

export function saveLeague(league) {
  localStorage.setItem(KEY(league.id), JSON.stringify(league));
  return league;
}

export function addAudit(leagueId, { action, by, notes, fields }) {
  const lg = getLeague(leagueId);
  lg.audit = lg.audit || [];
  lg.audit.unshift({
    id: `aud_${Date.now()}`,
    at: new Date().toISOString(),
    action, // e.g., 'config_update'
    by,
    notes,
    fields: fields || [], // [{field, oldValue, newValue}]
  });
  saveLeague(lg);
  return lg.audit;
}

export function isCommissioner(userEmail, league) {
  return !!userEmail && league?.commissionerEmail?.toLowerCase() === userEmail.toLowerCase();
}
