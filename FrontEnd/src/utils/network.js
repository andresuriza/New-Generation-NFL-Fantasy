// Legacy demo network helpers kept for reference; not used for auth anymore.
// You can remove this file if no longer used elsewhere.
const FAIL_RATE = 0.2; // 20% de probabilidad de fallo
export function fakeCreateLeagueRequest(payload, { failRate = 0.15, latency = [500, 1200] } = {}) {
  return new Promise((resolve, reject) => {
    const [min, max] = latency
    const wait = Math.floor(min + Math.random() * (max - min))
    setTimeout(() => {
      if (Math.random() < failRate) reject(new Error('Fallo de red o base de datos.'))
      else resolve({ ok: true })
    }, wait)
  })
}
export function fakeToggleLeagueStateRequest({ leagueId, to }, { failRate = 0.15, latency = [400, 1000] } = {}) {
  return new Promise((resolve, reject) => {
    const [min, max] = latency;
    const wait = Math.floor(min + Math.random() * (max - min));
    setTimeout(() => {
      if (Math.random() < failRate) reject(new Error('Fallo de red o base de datos.'));
      else resolve({ ok: true, leagueId, to });
    }, wait);
  });
}
export function fakeUpdateLeagueConfigRequest(payload, { failRate = 0.15, latency = [500, 1200] } = {}) {
  return new Promise((resolve, reject) => {
    const [min, max] = latency;
    const wait = Math.floor(min + Math.random() * (max - min));
    setTimeout(() => {
      if (Math.random() < failRate) reject(new Error('Fallo de red o validación.'));
      else resolve({ ok: true });
    }, wait);
  });
}
