import { useEffect, useMemo, useRef, useState } from 'react'
import {
  validateName, validateEmail, validatePassword, validateConfirm, validateAlias
} from '../utils/validators'

const MAX50 = 50
const MAX12 = 12

export default function Register() {
  const [form, setForm] = useState({ name: '', email: '', password: '', confirm: '', alias: '' })
  const [errors, setErrors] = useState({})
  const [touched, setTouched] = useState({})        // para no mostrar errores hasta interactuar
  const [toast, setToast] = useState({ type: null, message: '' })
  const [submitting, setSubmitting] = useState(false)

  const [showPass, setShowPass] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)
  const [capsPass, setCapsPass] = useState(false)
  const [capsConfirm, setCapsConfirm] = useState(false)

  // refs para enfocar el primer error al enviar
  const refs = {
    name: useRef(null),
    email: useRef(null),
    password: useRef(null),
    confirm: useRef(null),
    alias: useRef(null),
  }

  function handleChange(e) {
    setForm(f => ({ ...f, [e.target.name]: e.target.value }))
    setToast({ type: null, message: '' })
  }
  function handleBlur(e) {
    setTouched(t => ({ ...t, [e.target.name]: true }))
  }

  // Validación reactiva
  useEffect(() => {
    const errs = {}
    const eName = validateName(form.name); if (eName) errs.name = eName
    const eEmail = validateEmail(form.email); if (eEmail) errs.email = eEmail
    const ePass = validatePassword(form.password); if (ePass) errs.password = ePass
    const eConfirm = validateConfirm(form.password, form.confirm); if (eConfirm) errs.confirm = eConfirm
    const eAlias = validateAlias(form.alias); if (eAlias) errs.alias = eAlias
    setErrors(errs)
  }, [form])

  const isValid = useMemo(() =>
    Object.keys(errors).length === 0 &&
    form.name && form.email && form.password && form.confirm
  , [errors, form])

  function fieldClass(name) {
    return `input ${showError(name) ? 'input--invalid' : ''}`
  }
  function showError(name) {
    // Muestra error si ya se tocó el campo o si intentamos enviar
    return errors[name] && (touched[name] || submitting)
  }

  function focusFirstError() {
    for (const key of ['name','email','password','confirm','alias']) {
      if (errors[key]) { refs[key].current?.focus(); break }
    }
  }

  // Indicadores de reglas / “fuerza” (según tus reglas exactas)
  const passRules = useMemo(() => {
    const p = form.password || ''
    const hasLower = /[a-z]/.test(p)
    const hasUpper = /[A-Z]/.test(p)
    const lenOk = p.length >= 8 && p.length <= 12
    const onlyAlnum = /^[A-Za-z0-9]*$/.test(p) // solo alfanumérica
    const checks = { lenOk, hasLower, hasUpper, onlyAlnum }
    const score = [lenOk, hasLower, hasUpper, onlyAlnum].filter(Boolean).length
    const percent = (score / 4) * 100
    let label = 'Incompleta'
    if (score === 2) label = 'Básica'
    if (score === 3) label = 'Correcta'
    if (score === 4) label = 'Válida'
    return { ...checks, score, percent, label }
  }, [form.password])

  function handleSubmit(e) {
    e.preventDefault()
    setSubmitting(true)

    if (!isValid) {
      // marca todos como tocados para mostrar errores
      setTouched({ name: true, email: true, password: true, confirm: true, alias: !!form.alias })
      // enfoca el primero
      focusFirstError()
      // no seguimos (visual)
      setSubmitting(false)
      return
    }

    // Solo visual: no guardamos, no llamamos API.
    setTimeout(() => {
      setSubmitting(false)
      setToast({
        type: 'ok',
        message:
          'Formulario válido. La cuenta quedaría activa inmediatamente. ' +
          'En el backend se generará: ID único, fecha de creación, rol "manager", ' +
          'estado "active", imagen e idioma "en".'
      })
    }, 400)
  }

  return (
    <div className="container" style={{ paddingTop: 24, paddingBottom: 48 }}>
      <div className="card" style={{ maxWidth: 600, margin: '0 auto' }}>
        <h2 style={{ marginTop: 0 }}>Crear cuenta</h2>
        <p style={{ color: 'var(--muted)' }}>
          Vista previa <strong>sin backend</strong>. Regla de contraseña: 8–12, alfanumérica, con al menos una minúscula y una mayúscula.
        </p>

        <form className="form" noValidate onSubmit={handleSubmit}>
          {/* Nombre */}
          <div className="form__group">
            <div className="label-row">
              <label htmlFor="name">Nombre *</label>
              <span className="counter">{form.name.length}/{MAX50}</span>
            </div>
            <input
              ref={refs.name}
              id="name"
              className={fieldClass('name')}
              name="name"
              value={form.name}
              onChange={handleChange}
              onBlur={handleBlur}
              placeholder="Tu nombre"
              maxLength={MAX50}
              aria-invalid={!!showError('name')}
              aria-describedby={showError('name') ? 'err-name' : undefined}
            />
            {showError('name') && <div id="err-name" className="error">{errors.name}</div>}
          </div>

          {/* Correo */}
          <div className="form__group">
            <div className="label-row">
              <label htmlFor="email">Correo *</label>
              <span className="counter">{form.email.length}/{MAX50}</span>
            </div>
            <input
              ref={refs.email}
              id="email"
              className={fieldClass('email')}
              name="email"
              value={form.email}
              onChange={handleChange}
              onBlur={handleBlur}
              placeholder="tucorreo@ejemplo.com"
              maxLength={MAX50}
              inputMode="email"
              aria-invalid={!!showError('email')}
              aria-describedby={showError('email') ? 'err-email help-email' : 'help-email'}
            />
            {showError('email') && <div id="err-email" className="error">{errors.email}</div>}
            <div id="help-email" className="help">El correo debe ser único (se validará en el backend).</div>
          </div>

          {/* Contraseña */}
          <div className="form__group">
            <label htmlFor="password">Contraseña *</label>
            <div className="input-group">
              <input
                ref={refs.password}
                id="password"
                className={fieldClass('password')}
                type={showPass ? 'text' : 'password'}
                name="password"
                value={form.password}
                onChange={handleChange}
                onBlur={handleBlur}
                onKeyUp={(e) => setCapsPass(e.getModifierState && e.getModifierState('CapsLock'))}
                placeholder="8–12, alfanumérica, mayúsc./minúsc."
                maxLength={MAX12}
                aria-invalid={!!showError('password')}
                aria-describedby={`req-pass ${showError('password') ? 'err-password' : ''}`}
              />
              <button type="button" className="button button--ghost" onClick={() => setShowPass(p => !p)}>
                {showPass ? 'Ocultar' : 'Ver'}
              </button>
            </div>

            {/* Indicadores */}
            {capsPass && <div className="help" role="status">Bloq Mayús activado</div>}
            <div className="meter" aria-hidden="true">
              <div className="meter__bar" style={{ width: `${passRules.percent}%` }} />
            </div>
            <div className="help">Estado: <strong>{passRules.label}</strong></div>

            <ul id="req-pass" className="requirements">
              <li className={passRules.lenOk ? 'ok' : 'bad'}>8–12 caracteres</li>
              <li className={passRules.hasLower ? 'ok' : 'bad'}>Al menos una minúscula</li>
              <li className={passRules.hasUpper ? 'ok' : 'bad'}>Al menos una mayúscula</li>
              <li className={passRules.onlyAlnum ? 'ok' : 'bad'}>Solo letras y números</li>
            </ul>

            {showError('password') && <div id="err-password" className="error">{errors.password}</div>}
          </div>

          {/* Confirmar contraseña */}
          <div className="form__group">
            <label htmlFor="confirm">Confirmar contraseña *</label>
            <div className="input-group">
              <input
                ref={refs.confirm}
                id="confirm"
                className={fieldClass('confirm')}
                type={showConfirm ? 'text' : 'password'}
                name="confirm"
                value={form.confirm}
                onChange={handleChange}
                onBlur={handleBlur}
                onKeyUp={(e) => setCapsConfirm(e.getModifierState && e.getModifierState('CapsLock'))}
                placeholder="Repite tu contraseña"
                maxLength={MAX12}
                aria-invalid={!!showError('confirm')}
                aria-describedby={showError('confirm') ? 'err-confirm' : undefined}
                onPaste={(e) => e.preventDefault()} // opcional: evita pegar, fomenta escribirla
              />
              <button type="button" className="button button--ghost" onClick={() => setShowConfirm(p => !p)}>
                {showConfirm ? 'Ocultar' : 'Ver'}
              </button>
            </div>
            {capsConfirm && <div className="help" role="status">Bloq Mayús activado</div>}
            {showError('confirm') && <div id="err-confirm" className="error">{errors.confirm}</div>}
          </div>

          {/* Alias */}
          <div className="form__group">
            <div className="label-row">
              <label htmlFor="alias">Alias (opcional)</label>
              <span className="counter">{form.alias.length}/{MAX50}</span>
            </div>
            <input
              ref={refs.alias}
              id="alias"
              className={fieldClass('alias')}
              name="alias"
              value={form.alias}
              onChange={handleChange}
              onBlur={handleBlur}
              placeholder="Tu apodo en la liga"
              maxLength={MAX50}
              aria-invalid={!!showError('alias')}
              aria-describedby={showError('alias') ? 'err-alias' : undefined}
            />
            {showError('alias') && <div id="err-alias" className="error">{errors.alias}</div>}
          </div>

          <button className="button button--accent" disabled={!isValid || submitting}>
            {submitting ? 'Validando…' : 'Crear cuenta'}
          </button>

          {toast.message && (
            <div className={`toast ${toast.type === 'ok' ? 'toast--ok' : 'toast--err'}`}>
              {toast.message}
            </div>
          )}
        </form>
      </div>
    </div>
  )
}
