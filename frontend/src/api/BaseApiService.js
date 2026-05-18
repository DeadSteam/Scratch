import { httpClient } from './HttpClient';

export class BaseApiService {
  constructor(basePath, defaultLimit = 50) {
    this.basePath = basePath;
    this.defaultLimit = defaultLimit;
    this.http = httpClient;
  }

  async getAll(params = {}) {
    const { skip = 0, limit = this.defaultLimit } = params;
    return await this.http.get(this.basePath, { skip, limit });
  }

  async getById(id) {
    const response = await this.http.get(`${this.basePath}/${id}`);
    return response.data;
  }

  async create(data) {
    const response = await this.http.post(this.basePath, data);
    return response.data;
  }

  async update(id, data) {
    const response = await this.http.patch(`${this.basePath}/${id}`, data);
    return response.data;
  }

  async delete(id) {
    return this.http.delete(`${this.basePath}/${id}`);
  }
}
