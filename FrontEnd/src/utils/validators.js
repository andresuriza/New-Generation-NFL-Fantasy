const EMAIL_RX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const PASS_RX = /^(?=.*[a-z])(?=.*[A-Z])[A-Za-z0-9]{8,12}$/;

export function validateName(name) {
  if (!name || name.trim().length < 1) return 'El nombre es obligatorio.';
  if (name.trim().length > 50) return 'El nombre no puede exceder 50 caracteres.';
  return null;
}

export function validateAlias(alias) {
  if (!alias) return null; // opcional
  if (alias.trim().length > 50) return 'El alias no puede exceder 50 caracteres.';
  return null;
}

export function validateEmail(email) {
  if (!email) return 'El correo es obligatorio.';
  if (email.length > 50) return 'El correo no puede exceder 50 caracteres.';
  if (!EMAIL_RX.test(email)) return 'Formato de correo inválido.';
  return null;
}

export function validatePassword(pass) {
  if (!pass) return 'La contraseña es obligatoria.';
  if (!PASS_RX.test(pass)) {
    return 'La contraseña debe tener 8–12 caracteres alfanuméricos, con al menos una minúscula y una mayúscula.';
  }
  return null;
}

export function validateConfirm(pass, confirm) {
  if (!confirm) return 'Debes confirmar la contraseña.';
  if (pass !== confirm) return 'La confirmación no coincide.';
  return null;
}

