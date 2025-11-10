// src/pages/administrator/seasonCreate.js
import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  validateSeasonName,
  validateWeeksCount,
  validateSeasonDates,
  validateWeeksInRange,
} from "../../utils/seasonValidators";
import { fakeSeasonCreateVisual } from "../../utils/seasonNetwork";
import {
  GetTemporada,
  CrearTemporada,
} from "../../utils/communicationModule/resources/temporadas";

const PASS_NOTE =
  "Solo visual: la unicidad de nombre la valida el backend real.";

export default function SeasonCreate() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    name: "",
    weeksCount: 18,
    startDate: "",
    endDate: "",
    autoDistribute: true,
    isCurrent: false,
  });
  const [weeks, setWeeks] = useState([]); // [{start,end}]
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [toast, setToast] = useState({ type: null, message: "" });

  function setField(name, value) {
    setForm((f) => ({ ...f, [name]: value }));
    setToast({ type: null, message: "" });
  }

  // Autogenerar semanas equidistantes dentro del rango (si está activado)
  useMemo(() => {
    const { startDate, endDate, weeksCount, autoDistribute } = form;
    if (!autoDistribute || !startDate || !endDate) return;
    const s = new Date(startDate).getTime();
    const e = new Date(endDate).getTime();
    if (!(s < e) || !weeksCount) return;
    const span = e - s;
    const slots = weeksCount;
    const size = Math.floor(span / slots);
    const gen = [];
    let cur = s;
    for (let i = 0; i < slots; i++) {
      const wStart = cur;
      // última semana llega hasta el final
      const wEnd = i === slots - 1 ? e : Math.min(e, cur + size);
      gen.push({
        start: new Date(wStart).toISOString().slice(0, 10),
        end: new Date(wEnd).toISOString().slice(0, 10),
      });
      cur = wEnd;
    }
    setWeeks(gen);
  }, [form.startDate, form.endDate, form.weeksCount, form.autoDistribute]);

  function setWeek(i, key, val) {
    setWeeks((ws) =>
      ws.map((w, idx) => (idx === i ? { ...w, [key]: val } : w))
    );
    setToast({ type: null, message: "" });
  }

  function validateAll() {
    const e = {};
    const eName = validateSeasonName(form.name);
    if (eName) e.name = eName;
    const eCnt = validateWeeksCount(form.weeksCount);
    if (eCnt) e.weeksCount = eCnt;
    const eDates = validateSeasonDates(form.startDate, form.endDate);
    if (eDates) e.dates = eDates;
    const eWeeks = validateWeeksInRange(weeks, form.startDate, form.endDate);
    if (eWeeks) e.weeks = eWeeks;
    setErrors(e);
    return Object.keys(e).length === 0;
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setToast({ type: null, message: "" });
    if (!validateAll()) return;
    setSubmitting(true);

    const generated = {
      id: crypto.randomUUID ? crypto.randomUUID() : `season_${Date.now()}`,
      createdAt: new Date().toISOString(),
    };

    try {
      const created = await CrearTemporada({
        nombre: form.name.trim(),
        semanas: Number(form.weeksCount),
        fecha_inicio: form.startDate,
        fecha_fin: form.endDate,
        es_actual: !!form.isCurrent,
      });

      setSubmitting(false);
      setToast({
        type: "ok",
        message: `Temporada creada: ${form.name}. Semanas: ${form.weeksCount}.`,
      });
      // No dependemos de página admin real; si quieres, quédate aquí:
      // return
      setTimeout(() => navigate("/"), 900);
    } catch (err) {
      setSubmitting(false);
      setToast({
        type: "err",
        message: err?.message || "No se pudo crear la temporada.",
      });
    }
  }

  return (
    <div className="container" style={{ paddingTop: 24, paddingBottom: 48 }}>
      <div className="card" style={{ maxWidth: 900, margin: "0 auto" }}>
        <h2 style={{ marginTop: 0 }}>Crear temporada</h2>
        <p className="help">{PASS_NOTE}</p>

        <form className="form" onSubmit={handleSubmit} noValidate>
          <div
            className="grid"
            style={{
              gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
              gap: 16,
            }}
          >
            <div className="form__group">
              <label>Nombre *</label>
              <input
                className={`input ${errors.name ? "input--invalid" : ""}`}
                value={form.name}
                onChange={(e) => setField("name", e.target.value)}
                maxLength={100}
                placeholder="Temporada 2025"
              />
              {errors.name && <div className="error">{errors.name}</div>}
            </div>

            <div className="form__group">
              <label>Cantidad de semanas *</label>
              <input
                className={`input ${errors.weeksCount ? "input--invalid" : ""}`}
                type="number"
                min={1}
                max={18}
                value={form.weeksCount}
                onChange={(e) => setField("weeksCount", Number(e.target.value))}
              />
              {errors.weeksCount && (
                <div className="error">{errors.weeksCount}</div>
              )}
            </div>

            <div className="form__group">
              <label>Inicio de temporada *</label>
              <input
                type="date"
                className={`input ${errors.dates ? "input--invalid" : ""}`}
                value={form.startDate}
                onChange={(e) => setField("startDate", e.target.value)}
              />
            </div>

            <div className="form__group">
              <label>Fin de temporada *</label>
              <input
                type="date"
                className={`input ${errors.dates ? "input--invalid" : ""}`}
                value={form.endDate}
                onChange={(e) => setField("endDate", e.target.value)}
              />
              {errors.dates && <div className="error">{errors.dates}</div>}
            </div>

            <div className="form__group" style={{ gridColumn: "1 / -1" }}>
              <label
                style={{ display: "inline-flex", alignItems: "center", gap: 8 }}
              >
                <input
                  type="checkbox"
                  checked={form.autoDistribute}
                  onChange={(e) => setField("autoDistribute", e.target.checked)}
                />
                Autogenerar semanas consecutivas dentro del rango
              </label>
            </div>

            <div className="form__group" style={{ gridColumn: "1 / -1" }}>
              <label
                style={{ display: "inline-flex", alignItems: "center", gap: 8 }}
              >
                <input
                  type="checkbox"
                  checked={form.isCurrent}
                  onChange={(e) => setField("isCurrent", e.target.checked)}
                />
                Marcar como temporada actual
              </label>
            </div>
          </div>

          {/* Editor de semanas */}
          <div className="card" style={{ marginTop: 12 }}>
            <h3 style={{ marginTop: 0 }}>Semanas ({weeks.length})</h3>
            {errors.weeks && (
              <div className="error" style={{ marginBottom: 8 }}>
                {errors.weeks}
              </div>
            )}
            <div
              className="grid"
              style={{ gridTemplateColumns: "repeat(3, 1fr)", gap: 8 }}
            >
              {weeks.map((w, i) => (
                <div key={i} className="card" style={{ padding: 8 }}>
                  <div className="help" style={{ marginBottom: 4 }}>
                    Semana {i + 1}
                  </div>
                  <label style={{ display: "block" }}>
                    Inicio
                    <input
                      type="date"
                      className="input"
                      value={w.start}
                      onChange={(e) => setWeek(i, "start", e.target.value)}
                    />
                  </label>
                  <label style={{ display: "block", marginTop: 6 }}>
                    Fin
                    <input
                      type="date"
                      className="input"
                      value={w.end}
                      onChange={(e) => setWeek(i, "end", e.target.value)}
                    />
                  </label>
                </div>
              ))}
            </div>
          </div>

          <div style={{ display: "flex", gap: 12, marginTop: 12 }}>
            <button className="button button--accent" disabled={submitting}>
              {submitting ? "Creando…" : "Crear temporada"}
            </button>
            <button
              type="button"
              className="button button--ghost"
              onClick={() => navigate(-1)}
              disabled={submitting}
            >
              Cancelar
            </button>
          </div>

          {toast.message && (
            <div
              className={`toast ${
                toast.type === "ok" ? "toast--ok" : "toast--err"
              }`}
              style={{ marginTop: 12 }}
            >
              {toast.message}
            </div>
          )}
        </form>
      </div>
    </div>
  );
}
