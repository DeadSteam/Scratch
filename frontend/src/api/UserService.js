/**
 * User Service
 * Single Responsibility: Handle user management API calls
 */

import { httpClient } from './HttpClient';

class UserService {
  /**
   * Get all users (paginated)
   */
  async getAll(params = {}) {
    const { skip = 0, limit = 50 } = params;
    const response = await httpClient.get('/users', { skip, limit });
    return response;
  }

  /**
   * Get user by ID
   */
  async getById(id) {
    const response = await httpClient.get(`/users/${id}`);
    return response.data;
  }

  /**
   * Update user (PUT as required by backend)
   */
  async update(id, updateData) {
    const response = await httpClient.put(`/users/${id}`, updateData);
    return response.data;
  }

  /**
   * Deactivate user
   */
  async deactivate(id) {
    const response = await httpClient.post(`/users/${id}/deactivate`);
    return response;
  }

  /**
   * Activate user
   */
  async activate(id) {
    const response = await httpClient.post(`/users/${id}/activate`);
    return response;
  }

  /**
   * Delete user
   */
  async delete(id) {
    const response = await httpClient.delete(`/users/${id}`);
    return response;
  }
}

export const userService = new UserService();

export default UserService;



