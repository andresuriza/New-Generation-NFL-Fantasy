import { BASE_URL } from "./communicationModule/httpClient.js";

/**
 * Converts a backend image path to a full URL
 * @param {string} imagePath - The image path from the backend (can be relative path, full URL, or null/undefined)
 * @returns {string} - The full image URL or empty string if invalid
 */
export const getImageUrl = (imagePath) => {
  if (!imagePath || typeof imagePath !== 'string') {
    return '';
  }

  // If it's already a full URL (http/https), return as is
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
    return imagePath;
  }

  // If it's a relative path from backend (starts with /), prepend backend URL
  if (imagePath.startsWith('/')) {
    return `${BASE_URL}${imagePath}`;
  }

  // If it's base64 data, return as is
  if (imagePath.startsWith('data:')) {
    return imagePath;
  }

  // Default case: treat as relative path
  return `${BASE_URL}/${imagePath}`;
};

/**
 * Converts backend player data to frontend format with proper image URLs
 * @param {Object} player - Player object from backend
 * @returns {Object} - Player object with proper image URLs
 */
export const formatPlayerData = (player) => ({
  id: player.id,
  name: player.nombre,
  position: player.posicion,
  team: player.equipo_nombre || player.equipo?.nombre || 'Unknown Team',
  image: getImageUrl(player.imagen_url),
  thumbnail: getImageUrl(player.thumbnail_url),
  activo: player.activo,
  // Include any other fields that might be needed
  ...player
});