/**
 * Authentication Service
 * Single Responsibility: Handle authentication API calls
 */

import { httpClient } from './HttpClient';
import { STORAGE_KEYS } from '@utils/constants';

class AuthService {
  /**
   * Register new user
   */
  async register(userData) {
    const response = await httpClient.post('/auth/register', userData);
    return response.data;
  }

  /**
   * Login user
   */
  async login(credentials) {
    const response = await httpClient.post('/auth/login', credentials);
    
    if (response.success && response.data) {
      this.saveTokens(response.data);
    }
    
    return response.data;
  }

  /**
   * Logout user
   */
  logout() {
    sessionStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
    sessionStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
    sessionStorage.removeItem(STORAGE_KEYS.USER);
  }

  /**
   * Get current user
   */
  async getCurrentUser() {
    const response = await httpClient.get('/auth/me');
    return response.data;
  }

  /**
   * Save tokens to session storage
   */
  saveTokens(authData) {
    if (authData.access_token) {
      sessionStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, authData.access_token);
    }
    if (authData.refresh_token) {
      sessionStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, authData.refresh_token);
    }
    if (authData.user) {
      sessionStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(authData.user));
    }
  }

  /**
   * Get stored user from session
   */
  getStoredUser() {
    const userData = sessionStorage.getItem(STORAGE_KEYS.USER);
    return userData ? JSON.parse(userData) : null;
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated() {
    return !!sessionStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
  }

  /**
   * Check if user has admin role
   */
  isAdmin() {
    const user = this.getStoredUser();
    if (!user || !user.roles) return false;
    return user.roles.some(role => role.name === 'admin');
  }
}

export const authService = new AuthService();

export default AuthService;



