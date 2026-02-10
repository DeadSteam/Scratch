/**
 * Film Service
 * Single Responsibility: Handle film API calls
 */

import { httpClient } from './HttpClient';

class FilmService {
  /**
   * Get all films (paginated)
   */
  async getAll(params = {}) {
    const { skip = 0, limit = 100 } = params;
    const response = await httpClient.get('/films', { skip, limit });
    return response;
  }

  /**
   * Get film by ID
   */
  async getById(id) {
    const response = await httpClient.get(`/films/${id}`);
    return response.data;
  }

  /**
   * Create new film
   */
  async create(filmData) {
    const response = await httpClient.post('/films', filmData);
    return response.data;
  }

  /**
   * Update film
   */
  async update(id, updateData) {
    const response = await httpClient.patch(`/films/${id}`, updateData);
    return response.data;
  }

  /**
   * Delete film
   */
  async delete(id) {
    const response = await httpClient.delete(`/films/${id}`);
    return response;
  }
}

export const filmService = new FilmService();

export default FilmService;



