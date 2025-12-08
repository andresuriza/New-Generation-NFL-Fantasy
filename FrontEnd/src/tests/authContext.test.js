import { renderHook, act } from '@testing-library/react';
import { AuthProvider, useAuth } from '../context/authContext';
import * as sessionUtils from '../utils/session';
import * as usuariosApi from '../utils/communicationModule/resources/usuarios';

// Mock de módulos externos
jest.mock('../utils/session');
jest.mock('../utils/communicationModule/resources/usuarios');

// Mock de localStorage
const localStorageMock = (() => {
  let store = {};
  return {
    getItem: jest.fn((key) => store[key] || null),
    setItem: jest.fn((key, value) => {
      store[key] = value.toString();
    }),
    removeItem: jest.fn((key) => {
      delete store[key];
    }),
    clear: jest.fn(() => {
      store = {};
    }),
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Mock de timers
jest.useFakeTimers();

describe('authContext', () => {
  beforeEach(() => {
    // Limpiar todos los mocks antes de cada test
    jest.clearAllMocks();
    localStorage.clear();
    sessionUtils.getSession.mockReturnValue(null);
    sessionUtils.isExpired.mockReturnValue(false);
    sessionUtils.createSession.mockImplementation((data) => ({
      ...data,
      createdAt: Date.now(),
      lastActivity: Date.now(),
    }));
    sessionUtils.clearSession.mockImplementation(() => {});
    sessionUtils.updateActivity.mockImplementation(() => {});
  });

  afterEach(() => {
    // Limpiar event listeners
    jest.clearAllTimers();
  });

  // ========== Pruebas para inicialización ==========
  describe('initialization', () => {
    test('initializes with no session when localStorage is empty', () => {
      // Sin sesión en localStorage → estado inicial null
      sessionUtils.getSession.mockReturnValue(null);
      sessionUtils.isExpired.mockReturnValue(true);

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      expect(result.current.session).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.user).toBeNull();
      expect(result.current.accessToken).toBeNull();
    });

    test('initializes with valid session from localStorage', () => {
      // Sesión válida en localStorage → se carga al inicializar
      const mockSession = {
        email: 'user@test.com',
        userId: 'user123',
        accessToken: 'token123',
        user: { id: 'user123', nombre: 'Test User' },
        createdAt: Date.now(),
        lastActivity: Date.now(),
      };
      sessionUtils.getSession.mockReturnValue(mockSession);
      sessionUtils.isExpired.mockReturnValue(false);

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      expect(result.current.session).toEqual(mockSession);
      expect(result.current.isAuthenticated).toBe(true);
      expect(result.current.user).toEqual(mockSession.user);
      expect(result.current.accessToken).toBe('token123');
    });

    test('initializes with null session when stored session is expired', () => {
      // Sesión expirada → no se carga
      const expiredSession = {
        email: 'user@test.com',
        createdAt: Date.now() - 13 * 60 * 60 * 1000, // 13 horas atrás
        lastActivity: Date.now() - 13 * 60 * 60 * 1000,
      };
      sessionUtils.getSession.mockReturnValue(expiredSession);
      sessionUtils.isExpired.mockReturnValue(true);

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      expect(result.current.session).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
    });
  });

  // ========== Pruebas para loginAsync ==========
  describe('loginAsync', () => {
    test('creates session on successful login', async () => {
      // Login exitoso → crea sesión y actualiza estado
      const mockUser = {
        id: 'user123',
        correo: 'user@test.com',
        nombre: 'Test User',
      };
      const mockTokens = {
        access_token: 'token123',
        refresh_token: 'refresh123',
      };
      const mockResponse = {
        user: mockUser,
        tokens: mockTokens,
      };

      usuariosApi.login.mockResolvedValue(mockResponse);
      sessionUtils.createSession.mockReturnValue({
        email: 'user@test.com',
        userId: 'user123',
        accessToken: 'token123',
        refreshToken: 'refresh123',
        user: mockUser,
        createdAt: Date.now(),
        lastActivity: Date.now(),
      });

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      let loginResult;
      await act(async () => {
        loginResult = await result.current.loginAsync({
          correo: 'user@test.com',
          contrasena: 'Password1',
        });
      });

      expect(loginResult.ok).toBe(true);
      expect(loginResult.data).toEqual(mockResponse);
      expect(usuariosApi.login).toHaveBeenCalledWith({
        correo: 'user@test.com',
        contrasena: 'Password1',
      });
      expect(sessionUtils.createSession).toHaveBeenCalledWith({
        email: 'user@test.com',
        userId: 'user123',
        accessToken: 'token123',
        refreshToken: 'refresh123',
        user: mockUser,
      });
      expect(result.current.isAuthenticated).toBe(true);
    });

    test('handles login failure with error status', async () => {
      // Login fallido → retorna error sin crear sesión
      const mockError = new Error('Credenciales inválidas');
      mockError.status = 401;
      usuariosApi.login.mockRejectedValue(mockError);

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      let loginResult;
      await act(async () => {
        loginResult = await result.current.loginAsync({
          correo: 'user@test.com',
          contrasena: 'WrongPassword',
        });
      });

      expect(loginResult.ok).toBe(false);
      expect(loginResult.status).toBe(401);
      expect(loginResult.message).toBe('Credenciales inválidas');
      expect(sessionUtils.createSession).not.toHaveBeenCalled();
      expect(result.current.isAuthenticated).toBe(false);
    });

    test('handles login failure with 423 status (locked account)', async () => {
      // Cuenta bloqueada → error específico
      const mockError = new Error('Cuenta bloqueada');
      mockError.status = 423;
      usuariosApi.login.mockRejectedValue(mockError);

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      let loginResult;
      await act(async () => {
        loginResult = await result.current.loginAsync({
          correo: 'locked@test.com',
          contrasena: 'Password1',
        });
      });

      expect(loginResult.ok).toBe(false);
      expect(loginResult.status).toBe(423);
      expect(loginResult.message).toBe('Cuenta bloqueada');
    });

    test('handles login failure without error message', async () => {
      // Error sin mensaje → mensaje por defecto
      const mockError = new Error();
      mockError.status = 500;
      usuariosApi.login.mockRejectedValue(mockError);

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      let loginResult;
      await act(async () => {
        loginResult = await result.current.loginAsync({
          correo: 'user@test.com',
          contrasena: 'Password1',
        });
      });

      expect(loginResult.ok).toBe(false);
      expect(loginResult.status).toBe(500);
      expect(loginResult.message).toBe('No se pudo iniciar sesión');
    });

    test('extracts userId from user object when not provided separately', async () => {
      // Si userId no viene explícito, se extrae de user.id
      const mockUser = { id: 'extracted123', correo: 'user@test.com' };
      const mockResponse = {
        user: mockUser,
        tokens: { access_token: 'token123' },
      };
      usuariosApi.login.mockResolvedValue(mockResponse);

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      await act(async () => {
        await result.current.loginAsync({
          correo: 'user@test.com',
          contrasena: 'Password1',
        });
      });

      expect(sessionUtils.createSession).toHaveBeenCalledWith(
        expect.objectContaining({
          userId: 'extracted123',
        })
      );
    });
  });

  // ========== Pruebas para logoutAsync ==========
  describe('logoutAsync', () => {
    test('clears session and updates state on logout', async () => {
      // Logout → limpia sesión y actualiza estado
      const mockSession = {
        email: 'user@test.com',
        userId: 'user123',
        accessToken: 'token123',
      };
      sessionUtils.getSession.mockReturnValue(mockSession);
      sessionUtils.isExpired.mockReturnValue(false);

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      // Primero hacer login para tener sesión
      const mockUser = { id: 'user123', correo: 'user@test.com' };
      usuariosApi.login.mockResolvedValue({
        user: mockUser,
        tokens: { access_token: 'token123' },
      });

      await act(async () => {
        await result.current.loginAsync({
          correo: 'user@test.com',
          contrasena: 'Password1',
        });
      });

      expect(result.current.isAuthenticated).toBe(true);

      // Ahora hacer logout
      let logoutResult;
      await act(async () => {
        logoutResult = await result.current.logoutAsync();
      });

      expect(logoutResult.ok).toBe(true);
      expect(sessionUtils.clearSession).toHaveBeenCalled();
      expect(result.current.session).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
    });

    test('logout works even when no session exists', async () => {
      // Logout sin sesión → no debe lanzar error
      sessionUtils.getSession.mockReturnValue(null);

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      let logoutResult;
      await act(async () => {
        logoutResult = await result.current.logoutAsync();
      });

      expect(logoutResult.ok).toBe(true);
      expect(sessionUtils.clearSession).toHaveBeenCalled();
    });
  });

  // ========== Pruebas para logout síncrono ==========
  describe('logout (synchronous)', () => {
    test('clears session synchronously', () => {
      // Logout síncrono → limpia inmediatamente
      const mockSession = {
        email: 'user@test.com',
        userId: 'user123',
      };
      sessionUtils.getSession.mockReturnValue(mockSession);
      sessionUtils.isExpired.mockReturnValue(false);

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      act(() => {
        result.current.logout();
      });

      expect(sessionUtils.clearSession).toHaveBeenCalled();
      expect(result.current.session).toBeNull();
    });
  });

  // ========== Pruebas para updateUser ==========
  describe('updateUser', () => {
    test('updates user info in session and persists to localStorage', () => {
      // Actualizar usuario → modifica sesión y localStorage
      const initialSession = {
        email: 'user@test.com',
        userId: 'user123',
        user: { id: 'user123', nombre: 'Old Name' },
        createdAt: Date.now(),
        lastActivity: Date.now(),
      };
      sessionUtils.getSession.mockReturnValue(initialSession);
      sessionUtils.isExpired.mockReturnValue(false);

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      act(() => {
        result.current.updateUser({ nombre: 'New Name', rol: 'administrador' });
      });

      expect(localStorage.setItem).toHaveBeenCalled();
      const updatedSession = JSON.parse(localStorage.setItem.mock.calls[0][1]);
      expect(updatedSession.user.nombre).toBe('New Name');
      expect(updatedSession.user.rol).toBe('administrador');
      expect(updatedSession.user.id).toBe('user123'); // Se preserva
    });

    test('does nothing when no session exists', () => {
      // Sin sesión → updateUser no hace nada
      sessionUtils.getSession.mockReturnValue(null);

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      act(() => {
        result.current.updateUser({ nombre: 'New Name' });
      });

      expect(localStorage.setItem).not.toHaveBeenCalled();
    });

    test('merges partial updates with existing user data', () => {
      // Actualización parcial → merge con datos existentes
      const initialSession = {
        email: 'user@test.com',
        user: {
          id: 'user123',
          nombre: 'Old Name',
          correo: 'user@test.com',
          alias: 'oldalias',
        },
        createdAt: Date.now(),
        lastActivity: Date.now(),
      };
      sessionUtils.getSession.mockReturnValue(initialSession);
      sessionUtils.isExpired.mockReturnValue(false);

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      act(() => {
        result.current.updateUser({ nombre: 'New Name' });
      });

      const updatedSession = JSON.parse(localStorage.setItem.mock.calls[0][1]);
      expect(updatedSession.user.nombre).toBe('New Name');
      expect(updatedSession.user.correo).toBe('user@test.com'); // Se preserva
      expect(updatedSession.user.alias).toBe('oldalias'); // Se preserva
    });
  });

  // ========== Pruebas para storage events ==========
  describe('storage events', () => {
    test('updates session when storage event fires for nfl_session', () => {
      // Storage event → sincroniza sesión entre tabs
      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      const newSession = {
        email: 'newuser@test.com',
        userId: 'newuser123',
        createdAt: Date.now(),
        lastActivity: Date.now(),
      };
      sessionUtils.getSession.mockReturnValue(newSession);
      sessionUtils.isExpired.mockReturnValue(false);

      act(() => {
        const event = new StorageEvent('storage', {
          key: 'nfl_session',
          newValue: JSON.stringify(newSession),
        });
        window.dispatchEvent(event);
      });

      expect(result.current.session).toEqual(newSession);
    });

    test('ignores storage events for other keys', () => {
      // Storage event de otra clave → se ignora
      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      const initialSession = result.current.session;

      act(() => {
        const event = new StorageEvent('storage', {
          key: 'other_key',
          newValue: 'some value',
        });
        window.dispatchEvent(event);
      });

      expect(result.current.session).toBe(initialSession);
    });

    test('clears session when storage event contains expired session', () => {
      // Storage event con sesión expirada → limpia sesión
      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      const expiredSession = {
        email: 'user@test.com',
        createdAt: Date.now() - 13 * 60 * 60 * 1000,
        lastActivity: Date.now() - 13 * 60 * 60 * 1000,
      };
      sessionUtils.getSession.mockReturnValue(expiredSession);
      sessionUtils.isExpired.mockReturnValue(true);

      act(() => {
        const event = new StorageEvent('storage', {
          key: 'nfl_session',
        });
        window.dispatchEvent(event);
      });

      expect(result.current.session).toBeNull();
    });
  });

  // ========== Pruebas para expiración periódica ==========
  describe('periodic expiration check', () => {
    test('clears expired session after interval', () => {
      // Intervalo de verificación → limpia sesiones expiradas
      const validSession = {
        email: 'user@test.com',
        createdAt: Date.now(),
        lastActivity: Date.now(),
      };
      sessionUtils.getSession.mockReturnValue(validSession);
      sessionUtils.isExpired.mockReturnValue(false);

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      expect(result.current.session).toEqual(validSession);

      // Simular expiración después de 1 minuto
      sessionUtils.isExpired.mockReturnValue(true);
      sessionUtils.getSession.mockReturnValue(validSession);

      act(() => {
        jest.advanceTimersByTime(60 * 1000); // 1 minuto
      });

      expect(sessionUtils.clearSession).toHaveBeenCalled();
      expect(result.current.session).toBeNull();
    });

    test('does not clear valid session during interval check', () => {
      // Sesión válida → no se limpia en verificación
      const validSession = {
        email: 'user@test.com',
        createdAt: Date.now(),
        lastActivity: Date.now(),
      };
      sessionUtils.getSession.mockReturnValue(validSession);
      sessionUtils.isExpired.mockReturnValue(false);

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      act(() => {
        jest.advanceTimersByTime(60 * 1000);
      });

      expect(sessionUtils.clearSession).not.toHaveBeenCalled();
      expect(result.current.session).toEqual(validSession);
    });
  });

  // ========== Pruebas para activity tracking ==========
  describe('activity tracking', () => {
    test('updates activity on click events with throttling', async () => {
      // Click events → actualiza actividad con throttling
      const session = {
        email: 'user@test.com',
        createdAt: Date.now(),
        lastActivity: Date.now(),
      };
      sessionUtils.getSession.mockReturnValue(session);
      sessionUtils.isExpired.mockReturnValue(false);

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      // Primero hacer login para activar tracking
      usuariosApi.login.mockResolvedValue({
        user: { id: 'user123', correo: 'user@test.com' },
        tokens: { access_token: 'token123' },
      });

      await act(async () => {
        await result.current.loginAsync({
          correo: 'user@test.com',
          contrasena: 'Password1',
        });
      });

      // Simular múltiples clicks rápidos
      act(() => {
        const clickEvent = new MouseEvent('click', { bubbles: true });
        window.dispatchEvent(clickEvent);
        window.dispatchEvent(clickEvent);
        window.dispatchEvent(clickEvent);
      });

      // Con throttling de 15s, solo debería actualizar una vez
      expect(sessionUtils.updateActivity).toHaveBeenCalled();
    });

    test('updates activity on keydown events', async () => {
      // Keydown events → actualiza actividad
      const session = {
        email: 'user@test.com',
        createdAt: Date.now(),
        lastActivity: Date.now(),
      };
      sessionUtils.getSession.mockReturnValue(session);
      sessionUtils.isExpired.mockReturnValue(false);

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      usuariosApi.login.mockResolvedValue({
        user: { id: 'user123', correo: 'user@test.com' },
        tokens: { access_token: 'token123' },
      });

      await act(async () => {
        await result.current.loginAsync({
          correo: 'user@test.com',
          contrasena: 'Password1',
        });
      });

      act(() => {
        const keyEvent = new KeyboardEvent('keydown', { bubbles: true });
        window.dispatchEvent(keyEvent);
      });

      expect(sessionUtils.updateActivity).toHaveBeenCalled();
    });

    test('updates activity on visibility change when tab becomes visible', async () => {
      // Visibility change → actualiza cuando tab se hace visible
      const session = {
        email: 'user@test.com',
        createdAt: Date.now(),
        lastActivity: Date.now(),
      };
      sessionUtils.getSession.mockReturnValue(session);
      sessionUtils.isExpired.mockReturnValue(false);

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      usuariosApi.login.mockResolvedValue({
        user: { id: 'user123', correo: 'user@test.com' },
        tokens: { access_token: 'token123' },
      });

      await act(async () => {
        await result.current.loginAsync({
          correo: 'user@test.com',
          contrasena: 'Password1',
        });
      });

      // Simular que el tab se hace visible
      Object.defineProperty(document, 'hidden', {
        writable: true,
        configurable: true,
        value: false,
      });

      act(() => {
        const visibilityEvent = new Event('visibilitychange');
        document.dispatchEvent(visibilityEvent);
      });

      expect(sessionUtils.updateActivity).toHaveBeenCalled();
    });

    test('does not track activity when no session exists', () => {
      // Sin sesión → no se registra actividad
      sessionUtils.getSession.mockReturnValue(null);

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      act(() => {
        const clickEvent = new MouseEvent('click', { bubbles: true });
        window.dispatchEvent(clickEvent);
      });

      expect(sessionUtils.updateActivity).not.toHaveBeenCalled();
    });
  });

  // ========== Pruebas para context value memoization ==========
  describe('context value memoization', () => {
    test('memoizes context value based on session', () => {
      // Memoización → mismo objeto cuando session no cambia
      const session = {
        email: 'user@test.com',
        userId: 'user123',
        user: { id: 'user123' },
        accessToken: 'token123',
        createdAt: Date.now(),
        lastActivity: Date.now(),
      };
      sessionUtils.getSession.mockReturnValue(session);
      sessionUtils.isExpired.mockReturnValue(false);

      const { result, rerender } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      const firstValue = result.current;

      // Rerender sin cambiar session
      rerender();

      // Debería ser el mismo objeto (memoizado)
      expect(result.current).toBe(firstValue);
    });

    test('provides correct derived values', () => {
      // Valores derivados → isAuthenticated, user, accessToken
      const session = {
        email: 'user@test.com',
        userId: 'user123',
        user: { id: 'user123', nombre: 'Test User' },
        accessToken: 'token123',
        createdAt: Date.now(),
        lastActivity: Date.now(),
      };
      sessionUtils.getSession.mockReturnValue(session);
      sessionUtils.isExpired.mockReturnValue(false);

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      expect(result.current.isAuthenticated).toBe(true);
      expect(result.current.user).toEqual(session.user);
      expect(result.current.accessToken).toBe('token123');
      expect(result.current.session).toEqual(session);
    });

    test('provides null derived values when no session', () => {
      // Sin sesión → valores derivados son null/false
      sessionUtils.getSession.mockReturnValue(null);

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.user).toBeNull();
      expect(result.current.accessToken).toBeNull();
      expect(result.current.session).toBeNull();
    });
  });

  // ========== Pruebas para login síncrono (legacy) ==========
  describe('login (synchronous legacy)', () => {
    test('creates session with email only', () => {
      // Login síncrono legacy → crea sesión básica
      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      const mockSession = {
        email: 'demo@test.com',
        createdAt: Date.now(),
        lastActivity: Date.now(),
      };
      sessionUtils.createSession.mockReturnValue(mockSession);

      act(() => {
        result.current.login({ email: 'demo@test.com' });
      });

      expect(sessionUtils.createSession).toHaveBeenCalledWith({
        email: 'demo@test.com',
      });
      expect(result.current.session).toEqual(mockSession);
    });
  });
});

