/**
 * TokenStorage — единственный источник истины о токенах и пользователе в sessionStorage.
 * HttpClient/AuthInterceptor/AuthService зависят только от этого модуля.
 */

import { STORAGE_KEYS } from '@utils/constants';

export const tokenStorage = {
  getAccess() {
    return sessionStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
  },

  getRefresh() {
    return sessionStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);
  },

  getUser() {
    const raw = sessionStorage.getItem(STORAGE_KEYS.USER);
    if (!raw) return null;
    try {
      return JSON.parse(raw);
    } catch {
      sessionStorage.removeItem(STORAGE_KEYS.USER);
      return null;
    }
  },

  save({ access_token, refresh_token, user } = {}) {
    if (access_token) sessionStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, access_token);
    if (refresh_token) sessionStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, refresh_token);
    if (user) sessionStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(user));
  },

  clear() {
    sessionStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
    sessionStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
    sessionStorage.removeItem(STORAGE_KEYS.USER);
  },

  hasAccess() {
    return Boolean(this.getAccess());
  },
};

export default tokenStorage;
