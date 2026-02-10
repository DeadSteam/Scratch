/**
 * Experiment Service
 * Single Responsibility: Handle experiment API calls
 */

import { httpClient } from './HttpClient';

class ExperimentService {
  /**
   * Get all experiments (paginated)
   */
  async getAll(params = {}) {
    const { skip = 0, limit = 50 } = params;
    const response = await httpClient.get('/experiments', { skip, limit });
    return response;
  }

  /**
   * Get experiments by user ID
   */
  async getByUserId(userId, params = {}) {
    const { skip = 0, limit = 50 } = params;
    const response = await httpClient.get(`/experiments/user/${userId}`, { skip, limit });
    return response;
  }

  /**
   * Get experiment by ID
   */
  async getById(id) {
    const response = await httpClient.get(`/experiments/${id}`);
    return response.data;
  }

  /**
   * Get experiment with images
   */
  async getWithImages(id) {
    const response = await httpClient.get(`/experiments/${id}/with-images`);
    return response.data;
  }

  /**
   * Create new experiment
   */
  async create(experimentData) {
    const response = await httpClient.post('/experiments/', experimentData);
    return response.data;
  }

  /**
   * Update experiment
   */
  async update(id, updateData) {
    const response = await httpClient.patch(`/experiments/${id}`, updateData);
    return response.data;
  }

  /**
   * Delete experiment
   */
  async delete(id) {
    const response = await httpClient.delete(`/experiments/${id}`);
    return response;
  }

}

export const experimentService = new ExperimentService();

export default ExperimentService;

