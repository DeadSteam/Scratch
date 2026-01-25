/**
 * Advice Service (Knowledge Base)
 * API for advices: /api/v1/advices, /api/v1/causes/{id}/advices
 */

import { httpClient } from './HttpClient';

class AdviceService {
  async getAll(params = {}) {
    const { skip = 0, limit = 100 } = params;
    return httpClient.get('/advices', { skip, limit });
  }

  async getById(id) {
    const res = await httpClient.get(`/advices/${id}`);
    return res.data;
  }

  async getByCauseId(causeId, params = {}) {
    const { skip = 0, limit = 100 } = params;
    return httpClient.get(`/causes/${causeId}/advices`, { skip, limit });
  }

  async create(data) {
    const res = await httpClient.post('/advices', data);
    return res.data;
  }

  async update(id, data) {
    const res = await httpClient.patch(`/advices/${id}`, data);
    return res.data;
  }

  async delete(id) {
    return httpClient.delete(`/advices/${id}`);
  }
}

export const adviceService = new AdviceService();
export default AdviceService;
