/**
 * AuthService — REST-обёртка для эндпоинтов авторизации.
 * Источник истины о токенах/пользователе — TokenStorage; admin-флаг — AuthContext.
 */

import { httpClient } from './HttpClient';
import { imageService } from './ImageService';
import { tokenStorage } from './TokenStorage';

class AuthService {
  async register(userData) {
    const response = await httpClient.post('/auth/register', userData);
    return response.data;
  }

  async login(credentials) {
    const response = await httpClient.post('/auth/login', credentials);
    if (response.success && response.data) {
      tokenStorage.save(response.data);
    }
    return response.data;
  }

  logout() {
    imageService.revokeAllBlobUrls();
    tokenStorage.clear();
  }

  getStoredUser() {
    return tokenStorage.getUser();
  }

  isAuthenticated() {
    return tokenStorage.hasAccess();
  }
}

export const authService = new AuthService();

export default AuthService;
