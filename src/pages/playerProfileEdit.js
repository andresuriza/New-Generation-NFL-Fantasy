import { useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/authContext'
import { getProfile, saveProfile, addHistory, DEFAULTS} from '../../utils/profileData'
import { getById as apiGetUsuario, update as apiUpdateUsuario } from '../../utils/communicationModule/resources/usuarios'
import { validateProfileName, validateProfileAlias, validateLanguage } from '../../utils/profileValidators'

const MAX_IMG_MB = 5
const MIN_DIM = 300
const MAX_DIM = 1024
const ACCEPT_TYPES = ['image/jpeg', 'image/png']

export default function PlayerProfileEdit() {
  const { session, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const email = session?.email

  const initialProfile = useMemo(() => (email ? getProfile(email) : null), [email])

  const [form, setForm] = useState(() => ({
    name: initialProfile?.name || '',
    alias: initialProfile?.alias || '',
    language: initialProfile?.language || 'en',
    // no editables (solo lectura)
    id: initialProfile?.id || '',
    email: initialProfile?.email || '',
    role: initialProfile?.role || '',
    status: initialProfile?.status || '',
    createdAt: initialProfile?.createdAt || '',
  }))

  const [photoPreview, setPhotoPreview] = useState(initialProfile?.profileImage || DEFAULTS.DEFAULT_AVATAR)
  const [photoFile, setPhotoFile] = useState(null)
  const [errors, setErrors] = useState({})
  const [imgError, setImgError] = useState('')
  const [saving, setSaving] = useState(false)
  const fileInputRef = useRef(null)

  useEffect(() => {
    if (!isAuthenticated) navigate('/login')
  }, [isAuthenticated, navigate])

  function handleChange(e) {
    const { name, value } = e.target
    setForm(f => ({ ...f, [name]: value }))
  }

  function validateAll() {
    const errs = {}
    const eName = validateProfileName(form.name); if (eName) errs.name = eName
    const eAlias = validateProfileAlias(form.alias); if (eAlias) errs.alias = eAlias
    const eLang = validateLanguage(form.language); if (eLang) errs.language = eLang
    setErrors(errs)
    return Object.keys(errs).length === 0
  }

  // Validación completa de imagen
  function validateImageFile(file) {
    if (!file) return null
    if (!ACCEPT_TYPES.includes(file.type)) return 'Formato no permitido. Solo JPEG o PNG.'
    const sizeMB = file.size / (1024 * 1024)
    if (sizeMB > MAX_IMG_MB) return `El archivo excede ${MAX_IMG_MB} MB.`
    return null
  }

  function handlePhotoChange(e) {
    setImgError('')
    const file = e.target.files?.[0]
    if (!file) return

    const basicErr = validateImageFile(file)
    if (basicErr) { setImgError(basicErr); setPhotoFile(null); return }

    // Validar dimensiones cargando la imagen en memoria
    const url = URL.createObjectURL(file)
    const img = new Image()
    img.onload = () => {
      const { width, height } = img
      URL.revokeObjectURL(url)
      if (width < MIN_DIM || height < MIN_DIM || width > MAX_DIM || height > MAX_DIM) {
        setImgError(`Dimensiones inválidas: ${width}x${height}. Deben ser entre ${MIN_DIM}x${MIN_DIM} y ${MAX_DIM}x${MAX_DIM}px.`)
        setPhotoFile(null)
        return
      }
      setPhotoFile(file)
      setPhotoPreview(url) // preview inmediata
    }
    img.onerror = () => {
      URL.revokeObjectURL(url)
      setImgError('No se pudo leer la imagen.')
      setPhotoFile(null)
    }
    img.src = url
  }

  async function handleSave(e) {
    e.preventDefault()
    setImgError('')
    if (!validateAll()) return

    setSaving(true)
    try {
      // Preparar cambios: compara contra perfil actual
      const current = getProfile(email)
      const changes = []

      if (current.name !== form.name) changes.push({ field: 'name', oldValue: current.name, newValue: form.name })
      if ((current.alias || '') !== (form.alias || '')) changes.push({ field: 'alias', oldValue: current.alias || '', newValue: form.alias || '' })
      if (current.language !== form.language) changes.push({ field: 'language', oldValue: current.language, newValue: form.language })

      // Foto: si hay file, convertir a dataURL para “guardar” visualmente
      let newProfileImage = current.profileImage || null
      if (photoFile) {
        const dataUrl = await fileToDataURL(photoFile)
        newProfileImage = dataUrl
        changes.push({ field: 'profileImage', oldValue: current.profileImage ? '[set]' : '[none]', newValue: '[set]' })
      }

      if (changes.length === 0) {
        setSaving(false)
        return // nada que guardar
      }

      // Guardar perfil y registrar historial (visual/local)
      saveProfile(email, { name: form.name, alias: form.alias || null, language: form.language, profileImage: newProfileImage })
      addHistory(email, changes)

      setSaving(false)
      // volver a la vista de perfil
      navigate('/player/profile')
    } catch (err) {
      setSaving(false)
      // Como es visual, solo mostramos un mensaje genérico de validación/foto
      alert('No se pudieron guardar los cambios. Revisa los campos e intenta de nuevo.')
    }
  }

  if (!initialProfile) return null

  return (
    <div className="container" style={{ paddingTop: 24, paddingBottom: 48 }}>
      <div className="card" style={{ maxWidth: 800, margin: '0 auto' }}>
        <h2 style={{ marginTop: 0 }}>Editar perfil</h2>
        <p style={{ color: 'var(--muted)' }}>Solo puedes editar <strong>nombre</strong>, <strong>alias</strong>, <strong>idioma</strong> y <strong>foto</strong>. El resto es de solo lectura.</p>

        <form className="form" noValidate onSubmit={handleSave}>
          {/* Foto */}
          <div style={{ display: 'flex', gap: 16, alignItems: 'center', flexWrap: 'wrap' }}>
            <img
              src={photoPreview || DEFAULTS.DEFAULT_AVATAR}
              alt="Foto de perfil"
              width={96}
              height={96}
              style={{ width: 96, height: 96, borderRadius: 16, objectFit: 'cover', border: '1px solid var(--border)' }}
              onError={(e) => { e.currentTarget.src = DEFAULTS.DEFAULT_AVATAR }}
            />
            <div style={{ display: 'grid', gap: 8 }}>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/jpeg,image/png"
                onChange={handlePhotoChange}
              />
              <small className="help">JPEG/PNG • ≤ 5 MB • {MIN_DIM}–{MAX_DIM}px</small>
              {imgError && <div className="error">{imgError}</div>}
            </div>
          </div>

          {/* Editables */}
          <div className="form__group">
            <label htmlFor="name">Nombre *</label>
            <input
              id="name"
              name="name"
              className={`input ${errors.name ? 'input--invalid' : ''}`}
              value={form.name}
              onChange={handleChange}
              maxLength={50}
              placeholder="Tu nombre"
            />
            {errors.name && <div className="error">{errors.name}</div>}
          </div>

          <div className="form__group">
            <label htmlFor="alias">Alias (opcional)</label>
            <input
              id="alias"
              name="alias"
              className={`input ${errors.alias ? 'input--invalid' : ''}`}
              value={form.alias}
              onChange={handleChange}
              maxLength={50}
              placeholder="Tu apodo"
            />
            {errors.alias && <div className="error">{errors.alias}</div>}
          </div>

          <div className="form__group">
            <label htmlFor="language">Idioma *</label>
            <select
              id="language"
              name="language"
              className={`input ${errors.language ? 'input--invalid' : ''}`}
              value={form.language}
              onChange={handleChange}
            >
              <option value="en">English (en)</option>
              <option value="es">Español (es)</option>
              <option value="pt">Português (pt)</option>
            </select>
            {errors.language && <div className="error">{errors.language}</div>}
          </div>

          {/* No editables */}
          <fieldset className="card" style={{ borderColor: 'var(--border)' }}>
            <legend style={{ color: 'var(--muted)' }}>Solo lectura</legend>
            <ReadOnly label="ID" value={form.id} />
            <ReadOnly label="Correo" value={form.email} />
            <ReadOnly label="Rol" value={form.role} />
            <ReadOnly label="Estado" value={form.status} />
            <ReadOnly label="Fecha de creación" value={new Date(form.createdAt).toLocaleString()} />
          </fieldset>

          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
            <button className="button button--accent" disabled={saving}>
              {saving ? 'Guardando…' : 'Guardar cambios'}
            </button>
            <button
              type="button"
              className="button button--ghost"
              onClick={() => navigate('/player/profile')}
              disabled={saving}
            >
              Cancelar
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

function ReadOnly({ label, value }) {
  return (
    <div className="form__group">
      <label>{label}</label>
      <input className="input" value={value || '—'} readOnly />
    </div>
  )
}

function fileToDataURL(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result)
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}
