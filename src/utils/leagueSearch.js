// src/utils/leagueSearch.js
const KEY_PREFIX = 'league_';

function readLeague(id) {
  try { return JSON.parse(localStorage.getItem(`${KEY_PREFIX}${id}`) || 'null'); }
  catch { return null; }
}

export function listAllLeaguesLocal() {
  const leagues = [];
  for (let i = 0; i < localStorage.length; i++) {
    const k = localStorage.key(i);
    if (k && k.startsWith(KEY_PREFIX)) {
      try {
        const lg = JSON.parse(localStorage.getItem(k));
        if (lg && lg.id) leagues.push(lg);
      } catch {}
    }
  }
  // ordenar por fecha de creación desc si existe
  leagues.sort((a, b) => (new Date(b.createdAt) - new Date(a.createdAt)));
  return leagues;
}

/**
 * Filtro visual: por nombre (contiene), temporada (season) y estado (status)
 */
export function searchLeaguesLocal({ q = '', season, status } = {}) {
  const all = listAllLeaguesLocal();
  const qnorm = q.trim().toLowerCase();
  return all.filter(lg => {
    const byQ = !qnorm || (lg.name || '').toLowerCase().includes(qnorm);
    const bySeason = !season || Number(lg.season) === Number(season);
    const byStatus = !status || (lg.status || '').toLowerCase() === String(status).toLowerCase();
    return byQ && bySeason && byStatus;
  });
}

export { readLeague as readLeagueLocal };
