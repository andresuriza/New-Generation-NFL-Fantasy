import {
  validateName,
  validateAlias,
  validateEmail,
  validatePassword,
  validateConfirm,
} from './validators';

describe('validators', () => {
  // Pruebas para validateName
  describe('validateName', () => {
    test('returns null for valid name', () => {
      // Nombre válido → no debe dar error
      expect(validateName('John Doe')).toBeNull();
    });

    test('returns error for empty name', () => {
      // Cadenas vacías o espacios deben marcar error
      expect(validateName('')).toBe('El nombre es obligatorio.');
      expect(validateName('   ')).toBe('El nombre es obligatorio.');
    });

    test('returns error for name exceeding 50 characters', () => {
      // Se sobrepasa el límite de longitud
      const longName = 'a'.repeat(51);
      expect(validateName(longName)).toBe('El nombre no puede exceder 50 caracteres.');
    });

    test('returns null for name at boundary (50 chars)', () => {
      // Límite exacto permitido
      const boundaryName = 'a'.repeat(50);
      expect(validateName(boundaryName)).toBeNull();
    });
  });

  // Pruebas para validateAlias
  describe('validateAlias', () => {
    test('returns null for valid alias', () => {
      // Alias correcto
      expect(validateAlias('player123')).toBeNull();
    });

    test('returns error for empty alias', () => {
      // Alias vacío → error
      expect(validateAlias('')).toBe('El alias es obligatorio.');
    });

    test('returns error for alias exceeding 50 characters', () => {
      // Longitud máxima excedida
      const longAlias = 'a'.repeat(51);
      expect(validateAlias(longAlias)).toBe('El alias no puede exceder 50 caracteres.');
    });
  });

  // Pruebas para validateEmail
  describe('validateEmail', () => {
    test('returns null for valid email', () => {
      // Formatos de correo válidos
      expect(validateEmail('test@example.com')).toBeNull();
      expect(validateEmail('user.name+tag@domain.co.uk')).toBeNull();
    });

    test('returns error for empty email', () => {
      // Falta el correo
      expect(validateEmail('')).toBe('El correo es obligatorio.');
    });

    test('returns error for invalid email format', () => {
      // Correo sin formato correcto
      expect(validateEmail('notanemail')).toBe('Formato de correo inválido.');
      expect(validateEmail('missing@domain')).toBe('Formato de correo inválido.');
      expect(validateEmail('@domain.com')).toBe('Formato de correo inválido.');
    });

    test('returns error for email exceeding 50 characters', () => {
      // Rebasar límite de longitud
      const longEmail = 'a'.repeat(45) + '@test.com';
      expect(validateEmail(longEmail)).toBe('El correo no puede exceder 50 caracteres.');
    });
  });

  // Pruebas para validatePassword
  describe('validatePassword', () => {
    test('returns null for valid password', () => {
      // Contraseñas válidas (mayúsculas, minúsculas, números)
      expect(validatePassword('Password1')).toBeNull();
      expect(validatePassword('Abc12345')).toBeNull();
    });

    test('returns error for empty password', () => {
      // Falta la contraseña
      expect(validatePassword('')).toBe('La contraseña es obligatoria.');
    });

    test('returns error for password without uppercase', () => {
      // Falta mayúscula
      expect(validatePassword('password123')).toContain('al menos una minúscula y una mayúscula');
    });

    test('returns error for password without lowercase', () => {
      // Falta minúscula
      expect(validatePassword('PASSWORD123')).toContain('al menos una minúscula y una mayúscula');
    });

    test('returns error for password too short', () => {
      // Menos de 8 chars
      expect(validatePassword('Pass1')).toContain('8–12 caracteres');
    });

    test('returns error for password too long', () => {
      // Más de 12 chars
      expect(validatePassword('Password12345')).toContain('8–12 caracteres');
    });

    test('returns error for password with special characters', () => {
      // Solo caracteres alfanuméricos permitidos
      expect(validatePassword('Pass@123')).toContain('8–12 caracteres alfanuméricos');
    });
  });

  // Pruebas para validateConfirm
  describe('validateConfirm', () => {
    test('returns null when passwords match', () => {
      // Las contraseñas coinciden
      expect(validateConfirm('Password1', 'Password1')).toBeNull();
    });

    test('returns error for empty confirmation', () => {
      // Falta la confirmación
      expect(validateConfirm('Password1', '')).toBe('Debes confirmar la contraseña.');
    });

    test('returns error when passwords do not match', () => {
      // Contraseñas distintas
      expect(validateConfirm('Password1', 'Password2')).toBe('La confirmación no coincide.');
    });
  });
});
