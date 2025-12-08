import {
  INACTIVITY_MS,
  getAuthMeta,
  setAuthMeta,
  resetAuthMeta,
  getSession,
  createSession,
  updateActivity,
  clearSession,
  isExpired,
} from '../utils/session';

// Mock de localStorage
const localStorageMock = (() => {
  let store = {};
  return {
    getItem: (key) => store[key] || null,
    setItem: (key, value) => {
      store[key] = value.toString();
    },
    removeItem: (key) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    },
  };
})();

// Reemplaza el localStorage global con el mock
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

describe('session', () => {
  beforeEach(() => {
    // Limpia el localStorage antes de cada test
    localStorage.clear();
    jest.clearAllMocks();
  });

  // ========== Pruebas para isExpired ==========
  describe('isExpired', () => {
    test('returns true for null session', () => {
      // Sesión nula → expirada
      expect(isExpired(null)).toBe(true);
    });

    test('returns true for undefined session', () => {
      // Sesión undefined → expirada
      expect(isExpired(undefined)).toBe(true);
    });

    test('returns false for recent session', () => {
      // Sesión creada hace 1 hora → no expirada
      const recentSession = {
        createdAt: Date.now() - (1 * 60 * 60 * 1000), // 1 hora atrás
        lastActivity: Date.now(),
      };
      expect(isExpired(recentSession)).toBe(false);
    });

    test('returns true for session older than 12 hours', () => {
      // Sesión de hace 13 horas → expirada
      const oldSession = {
        createdAt: Date.now() - (13 * 60 * 60 * 1000), // 13 horas atrás
        lastActivity: Date.now() - (13 * 60 * 60 * 1000),
      };
      expect(isExpired(oldSession)).toBe(true);
    });

    test('returns false for session exactly at 12 hours minus 1ms', () => {
      // Caso límite: justo antes de expirar
      const boundarySession = {
        createdAt: Date.now() - (INACTIVITY_MS - 1),
        lastActivity: Date.now() - (INACTIVITY_MS - 1),
      };
      expect(isExpired(boundarySession)).toBe(false);
    });

    test('returns true for session exactly at 12 hours plus 1ms', () => {
      // Caso límite: justo después de expirar
      const expiredSession = {
        createdAt: Date.now() - (INACTIVITY_MS + 1),
        lastActivity: Date.now() - (INACTIVITY_MS + 1),
      };
      expect(isExpired(expiredSession)).toBe(true);
    });

    test('uses lastActivity if present, ignoring createdAt', () => {
      // Si hay lastActivity reciente, no está expirada aunque createdAt sea viejo
      const session = {
        createdAt: Date.now() - (20 * 60 * 60 * 1000), // 20 horas atrás
        lastActivity: Date.now() - (1 * 60 * 60 * 1000), // 1 hora atrás
      };
      expect(isExpired(session)).toBe(false);
    });

    test('uses createdAt when lastActivity is missing', () => {
      // Sin lastActivity, usa createdAt
      const session = {
        createdAt: Date.now() - (1 * 60 * 60 * 1000), // 1 hora atrás
      };
      expect(isExpired(session)).toBe(false);
    });

    test('returns true when both timestamps are old', () => {
      // Ambos timestamps viejos → expirada
      const session = {
        createdAt: Date.now() - (15 * 60 * 60 * 1000),
        lastActivity: Date.now() - (14 * 60 * 60 * 1000),
      };
      expect(isExpired(session)).toBe(true);
    });
  });

  // ========== Pruebas para getAuthMeta ==========
  describe('getAuthMeta', () => {
    test('returns default meta for non-existent email', () => {
      // Email no registrado → valores por defecto
      const meta = getAuthMeta('test@example.com');
      expect(meta).toEqual({ failedCount: 0, locked: false });
    });

    test('returns stored meta for existing email', () => {
      // Guardar metadata y luego leerla
      setAuthMeta('user@test.com', { failedCount: 3, locked: false });
      const meta = getAuthMeta('user@test.com');
      expect(meta).toEqual({ failedCount: 3, locked: false });
    });

    test('is case-insensitive for email', () => {
      // Minúsculas y mayúsculas deben ser equivalentes
      setAuthMeta('User@Test.COM', { failedCount: 2, locked: true });
      const meta = getAuthMeta('user@test.com');
      expect(meta).toEqual({ failedCount: 2, locked: true });
    });

    test('returns default meta for null email', () => {
      // Email null → valores por defecto
      const meta = getAuthMeta(null);
      expect(meta).toEqual({ failedCount: 0, locked: false });
    });

    test('returns default meta for undefined email', () => {
      // Email undefined → valores por defecto
      const meta = getAuthMeta(undefined);
      expect(meta).toEqual({ failedCount: 0, locked: false });
    });
  });

  // ========== Pruebas para setAuthMeta ==========
  describe('setAuthMeta', () => {
    test('creates new auth meta for email', () => {
      // Crear metadata desde cero
      setAuthMeta('new@test.com', { failedCount: 1, locked: false });
      const meta = getAuthMeta('new@test.com');
      expect(meta).toEqual({ failedCount: 1, locked: false });
    });

    test('updates existing auth meta', () => {
      // Actualizar metadata existente
      setAuthMeta('user@test.com', { failedCount: 1, locked: false });
      setAuthMeta('user@test.com', { failedCount: 2 });
      const meta = getAuthMeta('user@test.com');
      expect(meta.failedCount).toBe(2);
      expect(meta.locked).toBe(false); // Se mantiene
    });

    test('locks account when locked: true', () => {
      // Bloquear cuenta
      setAuthMeta('locked@test.com', { failedCount: 5, locked: true });
      const meta = getAuthMeta('locked@test.com');
      expect(meta.locked).toBe(true);
      expect(meta.failedCount).toBe(5);
    });

    test('handles partial updates', () => {
      // Actualización parcial (solo un campo)
      setAuthMeta('partial@test.com', { failedCount: 3, locked: false });
      setAuthMeta('partial@test.com', { locked: true });
      const meta = getAuthMeta('partial@test.com');
      expect(meta).toEqual({ failedCount: 3, locked: true });
    });

    test('normalizes email to lowercase', () => {
      // Mayúsculas se convierten a minúsculas
      setAuthMeta('User@TEST.com', { failedCount: 1, locked: false });
      const meta = getAuthMeta('user@test.com');
      expect(meta.failedCount).toBe(1);
    });
  });

  // ========== Pruebas para resetAuthMeta ==========
  describe('resetAuthMeta', () => {
    test('resets auth meta to defaults', () => {
      // Resetear después de intentos fallidos
      setAuthMeta('reset@test.com', { failedCount: 4, locked: true });
      resetAuthMeta('reset@test.com');
      const meta = getAuthMeta('reset@test.com');
      expect(meta).toEqual({ failedCount: 0, locked: false });
    });

    test('does nothing for non-existent email', () => {
      // Resetear email que no existe no causa error
      expect(() => resetAuthMeta('nonexistent@test.com')).not.toThrow();
    });

    test('is case-insensitive', () => {
      // Reset con mayúsculas funciona
      setAuthMeta('Reset@TEST.com', { failedCount: 3, locked: true });
      resetAuthMeta('reset@test.com');
      const meta = getAuthMeta('RESET@TEST.COM');
      expect(meta).toEqual({ failedCount: 0, locked: false });
    });
  });

  // ========== Pruebas para createSession ==========
  describe('createSession', () => {
    test('creates session with all fields', () => {
      // Crear sesión completa
      const mockUser = { id: 'user123', nombre: 'John Doe' };
      const session = createSession({
        email: 'user@test.com',
        userId: 'user123',
        accessToken: 'token123',
        refreshToken: 'refresh123',
        user: mockUser,
      });

      expect(session.email).toBe('user@test.com');
      expect(session.userId).toBe('user123');
      expect(session.accessToken).toBe('token123');
      expect(session.refreshToken).toBe('refresh123');
      expect(session.user).toEqual(mockUser);
      expect(session.createdAt).toBeDefined();
      expect(session.lastActivity).toBeDefined();
    });

    test('extracts userId from user object if not provided', () => {
      // Si no se pasa userId pero sí user, extrae el id
      const mockUser = { id: 'extracted123', nombre: 'Jane' };
      const session = createSession({
        email: 'jane@test.com',
        user: mockUser,
      });

      expect(session.userId).toBe('extracted123');
    });

    test('sets userId to null if neither userId nor user.id provided', () => {
      // Sin userId ni user → null
      const session = createSession({
        email: 'minimal@test.com',
      });

      expect(session.userId).toBeNull();
    });

    test('timestamps are numbers', () => {
      // Timestamps deben ser números (milisegundos)
      const session = createSession({ email: 'time@test.com' });
      expect(typeof session.createdAt).toBe('number');
      expect(typeof session.lastActivity).toBe('number');
    });

    test('createdAt and lastActivity are equal on creation', () => {
      // Al crear, ambos timestamps son iguales
      const session = createSession({ email: 'sync@test.com' });
      expect(session.createdAt).toBe(session.lastActivity);
    });
  });

  // ========== Pruebas para getSession ==========
  describe('getSession', () => {
    test('returns null when no session exists', () => {
      // Sin sesión guardada → null
      expect(getSession()).toBeNull();
    });

    test('returns stored session', () => {
      // Guardar y recuperar sesión
      const created = createSession({
        email: 'stored@test.com',
        accessToken: 'token456',
      });
      const retrieved = getSession();

      expect(retrieved.email).toBe('stored@test.com');
      expect(retrieved.accessToken).toBe('token456');
    });

    test('handles corrupted localStorage data', () => {
      // Datos corruptos en localStorage → null
      localStorage.setItem('nfl_session', 'invalid json{');
      expect(getSession()).toBeNull();
    });
  });

  // ========== Pruebas para updateActivity ==========
  describe('updateActivity', () => {
    test('updates lastActivity timestamp', () => {
      // Crear sesión, esperar, actualizar actividad
      const original = createSession({ email: 'active@test.com' });
      const originalTime = original.lastActivity;

      // Simular paso del tiempo
      jest.advanceTimersByTime(5000); // 5 segundos

      updateActivity();
      const updated = getSession();

      expect(updated.lastActivity).toBeGreaterThanOrEqual(originalTime);
    });

    test('does nothing when no session exists', () => {
      // Sin sesión → no hace nada (no debe lanzar error)
      expect(() => updateActivity()).not.toThrow();
    });

    test('preserves other session fields', () => {
      // Actualizar actividad no debe modificar otros campos
      const original = createSession({
        email: 'preserve@test.com',
        accessToken: 'token789',
      });

      updateActivity();
      const updated = getSession();

      expect(updated.email).toBe('preserve@test.com');
      expect(updated.accessToken).toBe('token789');
      expect(updated.createdAt).toBe(original.createdAt);
    });
  });

  // ========== Pruebas para clearSession ==========
  describe('clearSession', () => {
    test('removes session from localStorage', () => {
      // Crear sesión y luego borrarla
      createSession({ email: 'delete@test.com' });
      expect(getSession()).not.toBeNull();

      clearSession();
      expect(getSession()).toBeNull();
    });

    test('does nothing when no session exists', () => {
      // Borrar sin sesión → no debe lanzar error
      expect(() => clearSession()).not.toThrow();
    });

    test('can create new session after clearing', () => {
      // Ciclo completo: crear → borrar → crear nueva
      createSession({ email: 'first@test.com' });
      clearSession();
      const newSession = createSession({ email: 'second@test.com' });

      expect(getSession().email).toBe('second@test.com');
    });
  });
});
