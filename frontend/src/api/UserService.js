import { BaseApiService } from './BaseApiService';

class UserService extends BaseApiService {
  constructor() {
    super('/users', 50);
  }

  // Users use PUT (full replace), not PATCH
  async update(id, data) {
    const response = await this.http.put(`${this.basePath}/${id}`, data);
    return response.data;
  }

  async getRoles() {
    const response = await this.http.get(`${this.basePath}/roles`);
    return response.data;
  }

  async setRoles(id, roles) {
    const response = await this.http.put(`${this.basePath}/${id}/roles`, { roles });
    return response.data;
  }

  async deactivate(id) {
    return this.http.post(`${this.basePath}/${id}/deactivate`);
  }

  async activate(id) {
    return this.http.post(`${this.basePath}/${id}/activate`);
  }
}

export const userService = new UserService();
export default UserService;
