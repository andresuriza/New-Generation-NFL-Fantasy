// src/utils/seasonValidators.js
export function validateSeasonName(name) {
  if (!name || !name.trim()) return 'El nombre es obligatorio.'
  const len = name.trim().length
  if (len < 1 || len > 100) return 'El nombre debe tener entre 1 y 100 caracteres.'
  return null
}

export function validateWeeksCount(n) {
  const num = Number(n)
  if (!Number.isInteger(num) || num < 1 || num > 30) {
    return 'La cantidad de semanas debe ser un entero entre 1 y 30.'
  }
  return null
}

export function validateSeasonDates(startISO, endISO) {
  const start = new Date(startISO)
  const end = new Date(endISO)
  if (Number.isNaN(+start) || Number.isNaN(+end)) return 'Fechas de temporada inválidas.'
  if (end <= start) return 'La fecha de fin debe ser posterior a la de inicio.'
  return null
}

/** Cada semana: dentro del rango de temporada, fin>inicio y sin traslapes */
export function validateWeeksInRange(weeks, seasonStartISO, seasonEndISO) {
  const s0 = new Date(seasonStartISO).getTime()
  const e0 = new Date(seasonEndISO).getTime()
  if (!Array.isArray(weeks) || weeks.length === 0) return 'Debes definir al menos una semana.'

  const norm = weeks.map((w, i) => {
    const s = new Date(w.start).getTime()
    const e = new Date(w.end).getTime()
    if (Number.isNaN(s) || Number.isNaN(e)) return { i, error: `Semana ${i + 1}: fechas inválidas.` }
    if (e <= s) return { i, error: `Semana ${i + 1}: la fecha fin debe ser posterior a inicio.` }
    if (s < s0 || e > e0) return { i, error: `Semana ${i + 1}: fuera del rango de la temporada.` }
    return { i, s, e }
  })

  const bad = norm.find(n => n.error)
  if (bad) return bad.error

  // sin traslapes
  norm.sort((a, b) => a.s - b.s)
  for (let i = 1; i < norm.length; i++) {
    if (norm[i].s < norm[i - 1].e) {
      return `Semanas ${norm[i - 1].i + 1} y ${norm[i].i + 1} se traslapan.`
    }
  }
  return null
}
