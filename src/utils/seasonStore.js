// src/utils/seasonStore.js
const IDX = 'seasons_index' // array de ids
const KEY = (id) => `season_${id}`

function loadIndex() {
  try { return JSON.parse(localStorage.getItem(IDX) || '[]') } catch { return [] }
}
function saveIndex(ids) {
  localStorage.setItem(IDX, JSON.stringify(ids))
}

export function saveSeason(season) {
  const ids = loadIndex()
  if (!ids.includes(season.id)) {
    ids.unshift(season.id)
    saveIndex(ids)
  }
  localStorage.setItem(KEY(season.id), JSON.stringify(season))
  return season
}

export function getSeason(id) {
  try { return JSON.parse(localStorage.getItem(KEY(id)) || 'null') } catch { return null }
}

export function listSeasons() {
  const ids = loadIndex()
  return ids.map(getSeason).filter(Boolean)
}

export function getCurrentSeason() {
  return listSeasons().find(s => s.isCurrent)
}
