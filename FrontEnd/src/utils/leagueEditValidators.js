import { LEAGUE_TEAM_SIZES, validateLeagueName as baseName } from './leagueValidators';

export const GAME_SCHEMES = ['Redraft','Keeper','Dynasty'];
export const SCORING = ['Standard','Half-PPR','PPR'];

export function validateLeagueName(name) {
  return baseName(name); // 1–100
}

export function validatePreDraftEditable(leagueStatus) {
  if (leagueStatus !== 'Pre-Draft') {
    return 'Esta configuración solo se puede editar en estado Pre-Draft.';
  }
  return null;
}

export function validateTeamSizeWithRegistered(nextTeams, registered) {
  if (!LEAGUE_TEAM_SIZES.includes(Number(nextTeams))) return 'Cantidad de equipos inválida.';
  if (Number(nextTeams) < Number(registered)) {
    return `No puedes reducir a ${nextTeams}. Ya hay ${registered} equipos registrados.`;
  }
  return null;
}

export function validateGameScheme(s) {
  if (!GAME_SCHEMES.includes(s)) return 'Esquema de juego inválido.';
  return null;
}

export function validateScoringSystem(s) {
  if (!SCORING.includes(s)) return 'Sistema de puntaje inválido.';
  return null;
}

export function validatePlayoffsTeams(n) {
  const ok = Number(n) === 4 || Number(n) === 6;
  return ok ? null : 'Formato de playoffs inválido.';
}

export function validateDecimalsFlag(v) {
  return typeof v === 'boolean' ? null : 'Valor de decimales inválido.';
}

// temporada aprox: Sep 1 (season) a Feb 28 (season+1)
export function seasonRange(season) {
  const start = new Date(`${season}-09-01T00:00:00Z`);
  const end = new Date(`${season + 1}-02-28T23:59:59Z`);
  return [start, end];
}

export function validateTradeDeadline(active, deadlineISO, season) {
  if (!active) return null;
  if (!deadlineISO) return 'Debes indicar una fecha límite de intercambios.';
  const d = new Date(deadlineISO);
  if (isNaN(d.getTime())) return 'Fecha de deadline inválida.';
  const [start, end] = seasonRange(season);
  if (d < start || d > end) return 'La fecha límite debe estar dentro de la temporada.';
  return null;
}

export function validatePositiveLimitOrNull(v) {
  if (v === null || v === '' || v === undefined) return null; // sin límite
  const n = Number(v);
  if (!Number.isInteger(n) || n < 1 || n > 100)
    return 'Debe ser un entero entre 1 y 100 o dejarse vacío para sin límite.';
  return null;
}
