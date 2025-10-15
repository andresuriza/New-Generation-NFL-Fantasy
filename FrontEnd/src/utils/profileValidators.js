import { validateName as baseName, validateAlias as baseAlias } from './validators'

export function validateProfileName(name) {
  return baseName(name)
}
export function validateProfileAlias(alias) {
  // opcional
  return baseAlias(alias)
}
export function validateLanguage(lang) {
  // minimal: en / es / pt (ajústalo si quieres más)
  const ALLOWED = ['en', 'es', 'pt']
  if (!lang) return 'El idioma es obligatorio.'
  if (!ALLOWED.includes(lang)) return 'Idioma no válido.'
  return null
}
