/**
 * Cause Service (Knowledge Base)
 * API for causes: /api/v1/causes, /api/v1/situations/{id}/causes
 */

import { httpClient } from './HttpClient';

class CauseService {
  async getAll(params = {}) {
    const { skip = 0, limit = 100 } = params;
    return httpClient.get('/causes', { skip, limit });
  }

  async getById(id) {
    const res = await httpClient.get(`/causes/${id}`);
    return res.data;
  }

  async create(data) {
    const res = await httpClient.post('/causes', data);
    return res.data;
  }

  async update(id, data) {
    const res = await httpClient.patch(`/causes/${id}`, data);
    return res.data;
  }

  async delete(id) {
    return httpClient.delete(`/causes/${id}`);
  }
}

export const causeService = new CauseService();
export default CauseService;
