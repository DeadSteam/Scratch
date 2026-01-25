/**
 * Situation Service (Knowledge Base)
 * API for situations: /api/v1/situations
 */

import { httpClient } from './HttpClient';

class SituationService {
  async getAll(params = {}) {
    const { skip = 0, limit = 100 } = params;
    return httpClient.get('/situations', { skip, limit });
  }

  async getById(id) {
    const res = await httpClient.get(`/situations/${id}`);
    return res.data;
  }

  async create(data) {
    const res = await httpClient.post('/situations', data);
    return res.data;
  }

  async update(id, data) {
    const res = await httpClient.patch(`/situations/${id}`, data);
    return res.data;
  }

  async delete(id) {
    return httpClient.delete(`/situations/${id}`);
  }
}

export const situationService = new SituationService();
export default SituationService;
