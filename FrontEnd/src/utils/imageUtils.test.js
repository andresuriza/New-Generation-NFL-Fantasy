import { getImageUrl, formatPlayerData } from './imageUtils';

// Mock del BASE_URL usado por getImageUrl
jest.mock('./communicationModule/httpClient.js', () => ({
  BASE_URL: 'http://localhost:8000',
}));

describe('imageUtils', () => {
  // Pruebas para getImageUrl
  describe('getImageUrl', () => {
    test('returns empty string for null or undefined', () => {
      // Valores no válidos -> cadena vacía
      expect(getImageUrl(null)).toBe('');
      expect(getImageUrl(undefined)).toBe('');
    });

    test('returns empty string for non-string values', () => {
      // Tipos incorrectos -> cadena vacía
      expect(getImageUrl(123)).toBe('');
      expect(getImageUrl({})).toBe('');
    });

    test('returns full URL as-is when starts with http://', () => {
      // Si ya es URL absoluta, se devuelve igual
      const url = 'http://example.com/image.jpg';
      expect(getImageUrl(url)).toBe(url);
    });

    test('returns full URL as-is when starts with https://', () => {
      // Igual para https
      const url = 'https://example.com/image.jpg';
      expect(getImageUrl(url)).toBe(url);
    });

    test('prepends BASE_URL when path starts with /', () => {
      // Rutas absolutas relativas → se antepone BASE_URL
      expect(getImageUrl('/imgs/player.jpg')).toBe('http://localhost:8000/imgs/player.jpg');
    });

    test('returns data URL as-is', () => {
      // Data URLs deben mantenerse intactas
      const dataUrl = 'data:image/png;base64,iVBORw0KGgoAAAANS';
      expect(getImageUrl(dataUrl)).toBe(dataUrl);
    });

    test('prepends BASE_URL with / for relative paths', () => {
      // Rutas sin "/" inicial → aún así se agrega BASE_URL
      expect(getImageUrl('imgs/player.jpg')).toBe('http://localhost:8000/imgs/player.jpg');
    });
  });

  // Pruebas para formatPlayerData
  describe('formatPlayerData', () => {
    test('formats complete player data correctly', () => {
      // Caso típico: jugador con todos los campos presentes
      const player = {
        id: '123',
        nombre: 'Patrick Mahomes',
        posicion: 'QB',
        equipo_nombre: 'Chiefs',
        imagen_url: '/imgs/mahomes.jpg',
        thumbnail_url: '/imgs/thumbs/mahomes.jpg',
        activo: true,
      };

      const formatted = formatPlayerData(player);

      // Se verifican las transformaciones esperadas
      expect(formatted.id).toBe('123');
      expect(formatted.name).toBe('Patrick Mahomes');
      expect(formatted.position).toBe('QB');
      expect(formatted.team).toBe('Chiefs');
      expect(formatted.image).toBe('http://localhost:8000/imgs/mahomes.jpg');
      expect(formatted.thumbnail).toBe('http://localhost:8000/imgs/thumbs/mahomes.jpg');
      expect(formatted.activo).toBe(true);
    });

    test('handles missing equipo_nombre with nested equipo object', () => {
      // El equipo puede venir anidado en un objeto
      const player = {
        id: '456',
        nombre: 'Travis Kelce',
        posicion: 'TE',
        equipo: { nombre: 'Chiefs' },
        imagen_url: 'https://example.com/kelce.jpg',
        thumbnail_url: null,
        activo: true,
      };

      const formatted = formatPlayerData(player);

      // Se prioriza el objeto equipo.nombre
      expect(formatted.team).toBe('Chiefs');
      expect(formatted.image).toBe('https://example.com/kelce.jpg');
      expect(formatted.thumbnail).toBe('');
    });

    test('defaults to Unknown Team when no team info', () => {
      // Caso sin información del equipo
      const player = {
        id: '789',
        nombre: 'Unknown Player',
        posicion: 'WR',
        imagen_url: null,
        thumbnail_url: null,
        activo: false,
      };

      const formatted = formatPlayerData(player);

      // Se aplican valores por defecto
      expect(formatted.team).toBe('Unknown Team');
      expect(formatted.image).toBe('');
      expect(formatted.thumbnail).toBe('');
    });

    test('preserves additional player fields', () => {
      // Campos extras no deben perderse
      const player = {
        id: '111',
        nombre: 'Test Player',
        posicion: 'RB',
        customField: 'customValue',
        stats: { touchdowns: 10 },
      };

      const formatted = formatPlayerData(player);

      // Se conservan los campos no transformados
      expect(formatted.customField).toBe('customValue');
      expect(formatted.stats).toEqual({ touchdowns: 10 });
    });
  });
});
