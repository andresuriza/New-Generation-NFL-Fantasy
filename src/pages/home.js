export default function Home() {
  return (
    <div className="container" style={{ paddingTop: 24, paddingBottom: 48 }}>
      {/* Hero */}
      <section className="hero" style={{ marginBottom: 24 }}>
        <div className="card" style={{ padding: 20 }}>
          <h1 style={{ margin: 0, fontSize: 28, letterSpacing: .5 }}>
            Construye tu <span style={{ color: 'var(--accent-1)' }}>Fantasy</span> ganador
          </h1>
          <p style={{ marginTop: 8, color: 'var(--muted)' }}>
            Gestiona tu roster, analiza proyecciones y simula picks. Todo en un mismo lugar.
          </p>

          <div className="hero__field" style={{ marginTop: 16 }} />

          <div style={{ marginTop: 16, display: 'flex', gap: 12, flexWrap: 'wrap' }}>
            <input className="input" placeholder="Buscar jugador (QB, RB, WR...)" style={{ flex: 1, minWidth: 240 }} />
            <button className="button">Explorar Jugadores</button>
          </div>
        </div>
      </section>

      {/* Bloques iniciales */}
      <section className="grid grid-3">
        <div className="card">
          <h3>Mi Equipo</h3>
          <p>Resumen del roster actual, titulares y banca.</p>
          <div style={{ marginTop: 12, display: 'flex', gap: 8 }}>
            <span className="badge">QB</span>
            <span className="badge">RB</span>
            <span className="badge">WR</span>
            <span className="badge">TE</span>
            <span className="badge">FLEX</span>
            <span className="badge">DST</span>
            <span className="badge">K</span>
          </div>
          <button className="button" style={{ marginTop: 14 }}>Ver Mi Equipo</button>
        </div>

        <div className="card">
          <h3>Jugadores</h3>
          <p>Explora el pool con filtros por posición y bye week.</p>
          <button className="button" style={{ marginTop: 14 }}>Abrir Explorador</button>
        </div>

        <div className="card">
          <h3>Draft Room</h3>
          <p>Simula picks y practica estrategias (Zero-RB, Hero-RB, etc.).</p>
          <button className="button" style={{ marginTop: 14 }}>Entrar al Draft</button>
        </div>
      </section>
    </div>
  )
}
