import { request } from '../httpClient';

// Media endpoints
export const getEquipoMedia = (equipoId) => request(`/media/${equipoId}`);

export const uploadEquipoImage = (equipoId, file) => {
  const form = new FormData();
  form.append('file', file);
  return request(`/media/upload/${equipoId}`, {
    method: 'POST',
    body: form,
  });
};
