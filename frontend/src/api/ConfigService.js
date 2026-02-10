/**
 * Equipment Config Service
 * Single Responsibility: Handle equipment configuration API calls
 */

import { httpClient } from './HttpClient';

class ConfigService {
  /**
   * Get all configs (paginated)
   */
  async getAll(params = {}) {
    const { skip = 0, limit = 100 } = params;
    const response = await httpClient.get('/equipment-configs', { skip, limit });
    return response;
  }

  /**
   * Get config by ID
   */
  async getById(id) {
    const response = await httpClient.get(`/equipment-configs/${id}`);
    return response.data;
  }

  /**
   * Create new config
   */
  async create(configData) {
    const response = await httpClient.post('/equipment-configs', configData);
    return response.data;
  }

  /**
   * Update config
   */
  async update(id, updateData) {
    const response = await httpClient.patch(`/equipment-configs/${id}`, updateData);
    return response.data;
  }

  /**
   * Delete config
   */
  async delete(id) {
    const response = await httpClient.delete(`/equipment-configs/${id}`);
    return response;
  }
}

export const configService = new ConfigService();

export default ConfigService;



