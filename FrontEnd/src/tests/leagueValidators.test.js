import {
  validateLeagueName,
  validateLeaguePasswordWrapper,
  validateTeamSize,
  validateCommissionerTeamName,
  LEAGUE_TEAM_SIZES,
} from '../utils/leagueValidators';

describe('leagueValidators', () => {
  // ========== Pruebas para validateLeagueName ==========
  describe('validateLeagueName', () => {
    test('returns null for valid league name', () => {
      // Nombres válidos de liga
      expect(validateLeagueName('Liga de Amigos')).toBeNull();
      expect(validateLeagueName('NFL Fantasy 2024')).toBeNull();
      expect(validateLeagueName('Mi Primera Liga')).toBeNull();
    });

    test('returns error for empty league name', () => {
      // Nombre vacío → error
      expect(validateLeagueName('')).toBe('El nombre es obligatorio.');
      expect(validateLeagueName('   ')).toBe('El nombre es obligatorio.');
    });

    test('returns error for null or undefined', () => {
      // Valores null/undefined → error
      expect(validateLeagueName(null)).toBe('El nombre es obligatorio.');
      expect(validateLeagueName(undefined)).toBe('El nombre es obligatorio.');
    });

    test('returns null for name at minimum boundary (1 char)', () => {
      // Límite mínimo: 1 carácter (sin espacios)
      expect(validateLeagueName('A')).toBeNull();
    });

    test('returns null for name at maximum boundary (100 chars)', () => {
      // Límite máximo: 100 caracteres
      const maxName = 'a'.repeat(100);
      expect(validateLeagueName(maxName)).toBeNull();
    });

    test('returns error for name exceeding 100 characters', () => {
      // Más de 100 caracteres → error
      const longName = 'a'.repeat(101);
      expect(validateLeagueName(longName)).toBe(
        'El nombre debe tener entre 1 y 100 caracteres.'
      );
    });

    test('trims whitespace before validation', () => {
      // Espacios al inicio/fin se eliminan
      expect(validateLeagueName('  Liga Válida  ')).toBeNull();
    });

    test('returns error for name with only spaces after trim', () => {
      // Solo espacios → vacío después de trim
      expect(validateLeagueName('     ')).toBe('El nombre es obligatorio.');
    });

    test('handles special characters', () => {
      // Caracteres especiales son válidos
      expect(validateLeagueName('Liga #1 - 2024!')).toBeNull();
      expect(validateLeagueName('Ñoños & Friends')).toBeNull();
    });
  });

  // ========== Pruebas para validateLeaguePasswordWrapper ==========
  describe('validateLeaguePasswordWrapper', () => {
    test('returns null for valid password', () => {
      // Contraseñas válidas: 8-12 chars, alfanumérica, mayúscula + minúscula
      expect(validateLeaguePasswordWrapper('Password1')).toBeNull();
      expect(validateLeaguePasswordWrapper('Liga2024')).toBeNull();
      expect(validateLeaguePasswordWrapper('Abc12345')).toBeNull();
    });

    test('returns error for empty password', () => {
      // Contraseña vacía → error
      expect(validateLeaguePasswordWrapper('')).toBe('La contraseña es obligatoria.');
    });

    test('returns error for password without uppercase', () => {
      // Falta mayúscula
      expect(validateLeaguePasswordWrapper('password123')).toContain(
        'al menos una minúscula y una mayúscula'
      );
    });

    test('returns error for password without lowercase', () => {
      // Falta minúscula
      expect(validateLeaguePasswordWrapper('PASSWORD123')).toContain(
        'al menos una minúscula y una mayúscula'
      );
    });

    test('returns error for password too short', () => {
      // Menos de 8 caracteres
      expect(validateLeaguePasswordWrapper('Pass1')).toContain('8–12 caracteres');
    });

    test('returns error for password too long', () => {
      // Más de 12 caracteres
      expect(validateLeaguePasswordWrapper('Password12345')).toContain('8–12 caracteres');
    });

    test('returns error for password with special characters', () => {
      // Solo alfanuméricos permitidos
      expect(validateLeaguePasswordWrapper('Pass@123')).toContain('8–12 caracteres alfanuméricos');
    });

    test('validates at minimum boundary (8 chars)', () => {
      // Exactamente 8 caracteres válidos
      expect(validateLeaguePasswordWrapper('Password')).toBeNull();
    });

    test('validates at maximum boundary (12 chars)', () => {
      // Exactamente 12 caracteres válidos
      expect(validateLeaguePasswordWrapper('Password1234')).toBeNull();
    });
  });

  // ========== Pruebas para validateTeamSize ==========
  describe('validateTeamSize', () => {
    test('returns null for valid team sizes', () => {
      // Todos los tamaños válidos: 4, 6, 8, 10, 12, 14, 16, 18, 20
      const validSizes = [4, 6, 8, 10, 12, 14, 16, 18, 20];
      validSizes.forEach((size) => {
        expect(validateTeamSize(size)).toBeNull();
      });
    });

    test('returns null for valid team sizes as strings', () => {
      // Acepta números como strings (se convierten con Number())
      expect(validateTeamSize('8')).toBeNull();
      expect(validateTeamSize('12')).toBeNull();
      expect(validateTeamSize('20')).toBeNull();
    });

    test('returns error for invalid team size', () => {
      // Tamaños no permitidos
      expect(validateTeamSize(5)).toBe('Cantidad de equipos inválida.');
      expect(validateTeamSize(7)).toBe('Cantidad de equipos inválida.');
      expect(validateTeamSize(22)).toBe('Cantidad de equipos inválida.');
      expect(validateTeamSize(0)).toBe('Cantidad de equipos inválida.');
    });

    test('returns error for negative team size', () => {
      // Números negativos no son válidos
      expect(validateTeamSize(-4)).toBe('Cantidad de equipos inválida.');
    });

    test('returns error for non-numeric values', () => {
      // Valores no numéricos
      expect(validateTeamSize('abc')).toBe('Cantidad de equipos inválida.');
      expect(validateTeamSize(null)).toBe('Cantidad de equipos inválida.');
      expect(validateTeamSize(undefined)).toBe('Cantidad de equipos inválida.');
    });

    test('returns error for decimal numbers', () => {
      // Decimales no son válidos
      expect(validateTeamSize(8.5)).toBe('Cantidad de equipos inválida.');
      expect(validateTeamSize(10.2)).toBe('Cantidad de equipos inválida.');
    });

    test('validates minimum valid size (4)', () => {
      // Tamaño mínimo válido
      expect(validateTeamSize(4)).toBeNull();
    });

    test('validates maximum valid size (20)', () => {
      // Tamaño máximo válido
      expect(validateTeamSize(20)).toBeNull();
    });

    test('returns error for size below minimum (3)', () => {
      // Por debajo del mínimo
      expect(validateTeamSize(3)).toBe('Cantidad de equipos inválida.');
    });

    test('returns error for size above maximum (21)', () => {
      // Por encima del máximo
      expect(validateTeamSize(21)).toBe('Cantidad de equipos inválida.');
    });
  });

  // ========== Pruebas para validateCommissionerTeamName ==========
  describe('validateCommissionerTeamName', () => {
    test('returns null for valid team name', () => {
      // Nombres de equipo válidos
      expect(validateCommissionerTeamName('Los Campeones')).toBeNull();
      expect(validateCommissionerTeamName('Team Alpha')).toBeNull();
      expect(validateCommissionerTeamName('Mi Equipo')).toBeNull();
    });

    test('returns error for empty team name', () => {
      // Nombre vacío → error
      expect(validateCommissionerTeamName('')).toBe(
        'El nombre de tu equipo es obligatorio.'
      );
      expect(validateCommissionerTeamName('   ')).toBe(
        'El nombre de tu equipo es obligatorio.'
      );
    });

    test('returns error for null or undefined', () => {
      // Valores null/undefined → error
      expect(validateCommissionerTeamName(null)).toBe(
        'El nombre de tu equipo es obligatorio.'
      );
      expect(validateCommissionerTeamName(undefined)).toBe(
        'El nombre de tu equipo es obligatorio.'
      );
    });

    test('returns null for name at maximum boundary (50 chars)', () => {
      // Exactamente 50 caracteres
      const maxName = 'a'.repeat(50);
      expect(validateCommissionerTeamName(maxName)).toBeNull();
    });

    test('returns error for name exceeding 50 characters', () => {
      // Más de 50 caracteres → error
      const longName = 'a'.repeat(51);
      expect(validateCommissionerTeamName(longName)).toBe(
        'El nombre del equipo no puede exceder 50 caracteres.'
      );
    });

    test('trims whitespace before validation', () => {
      // Espacios al inicio/fin se eliminan
      expect(validateCommissionerTeamName('  Equipo Válido  ')).toBeNull();
    });

    test('handles special characters', () => {
      // Caracteres especiales son válidos
      expect(validateCommissionerTeamName('Team #1')).toBeNull();
      expect(validateCommissionerTeamName('Ñoños FC')).toBeNull();
      expect(validateCommissionerTeamName("Pat's Team")).toBeNull();
    });

    test('validates single character name', () => {
      // Un solo carácter es válido
      expect(validateCommissionerTeamName('A')).toBeNull();
    });

    test('handles emojis in team name', () => {
      // Emojis cuentan para la longitud
      expect(validateCommissionerTeamName('Team 🏈')).toBeNull();
    });
  });

  // ========== Pruebas para LEAGUE_TEAM_SIZES constante ==========
  describe('LEAGUE_TEAM_SIZES', () => {
    test('exports correct team sizes array', () => {
      // Verifica que la constante exportada tenga los valores correctos
      expect(LEAGUE_TEAM_SIZES).toEqual([4, 6, 8, 10, 12, 14, 16, 18, 20]);
    });

    test('has correct length', () => {
      // 9 tamaños válidos
      expect(LEAGUE_TEAM_SIZES).toHaveLength(9);
    });

    test('contains only even numbers', () => {
      // Todos los tamaños son pares
      LEAGUE_TEAM_SIZES.forEach((size) => {
        expect(size % 2).toBe(0);
      });
    });

    test('is sorted in ascending order', () => {
      // Ordenados de menor a mayor
      const sorted = [...LEAGUE_TEAM_SIZES].sort((a, b) => a - b);
      expect(LEAGUE_TEAM_SIZES).toEqual(sorted);
    });
  });
});
