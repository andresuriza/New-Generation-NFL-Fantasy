// src/utils/seasonNetwork.js
import { saveSeason, listSeasons, getCurrentSeason } from './seasonStore'

function rangesOverlap(aStart, aEnd, bStart, bEnd) {
  return aStart < bEnd && bStart < aEnd
}

/**
 * Crea temporada visualmente: valida traslapes con otras temporadas,
 * unicidad de "actual", y guarda semanas.
 */
export async function fakeSeasonCreateVisual(payload) {
  // pequeña latencia
  await new Promise(r => setTimeout(r, 350))

  const { id, name, weeksCount, startDate, endDate, weeks, isCurrent } = payload
  const s = new Date(startDate).getTime()
  const e = new Date(endDate).getTime()
  if (!name?.trim()) throw new Error('El nombre es obligatorio.')
  if (!weeksCount || weeksCount < 1) throw new Error('Cantidad de semanas inválida.')
  if (!(s < e)) throw new Error('Rango de temporada inválido.')

  // No traslapar con otras temporadas existentes
  const others = listSeasons()
  const clash = others.find(o => rangesOverlap(s, e, new Date(o.startDate).getTime(), new Date(o.endDate).getTime()))
  if (clash) throw new Error(`Las fechas de esta temporada se traslapan con "${clash.name}".`)

  // Solo una temporada "actual"
  if (isCurrent && getCurrentSeason()) {
    throw new Error('Ya existe una temporada marcada como "actual".')
  }

  const season = {
    id,
    name: name.trim(),
    createdAt: new Date().toISOString(),
    weeksCount,
    startDate,
    endDate,
    weeks: weeks.map((w, i) => ({ n: i + 1, start: w.start, end: w.end })),
    isCurrent: !!isCurrent,
  }

  saveSeason(season)

  return {
    ok: true,
    data: {
      id: season.id,
      redirect_to: `/season/${season.id}/overview`, // solo visual
    },
  }
}
