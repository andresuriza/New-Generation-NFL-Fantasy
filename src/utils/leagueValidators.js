import { validatePassword as validateLeaguePassword } from './validators'

const TEAM_SIZES = [4,6,8,10,12,14,16,18,20]

export function validateLeagueName(name) {
  if (!name || !name.trim()) return 'El nombre es obligatorio.'
  const len = name.trim().length
  if (len < 1 || len > 100) return 'El nombre debe tener entre 1 y 100 caracteres.'
  return null
}

export function validateLeaguePasswordWrapper(pass) {
  // reglas iguales a cuenta: 8–12, alfanumérica, minúscula y mayúscula
  return validateLeaguePassword(pass)
}

export function validateTeamSize(n) {
  if (!TEAM_SIZES.includes(Number(n))) return 'Cantidad de equipos inválida.'
  return null
}

export function validateCommissionerTeamName(teamName) {
  if (!teamName || !teamName.trim()) return 'El nombre de tu equipo es obligatorio.'
  if (teamName.trim().length > 50) return 'El nombre del equipo no puede exceder 50 caracteres.'
  return null
}

export const LEAGUE_TEAM_SIZES = TEAM_SIZES
