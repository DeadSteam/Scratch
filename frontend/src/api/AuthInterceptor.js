/**
 * AuthInterceptor — fetch-обёртка с Bearer-авторизацией и шейрингом refresh-флоу.
 *
 * Решает race-condition: при N параллельных 401 ответах refresh-токен дёргается
 * один раз (через общий promise), остальные ждут результат и переигрывают свой
 * запрос. Раньше в HttpClient второй 401 сразу чистил сессию и редиректил.
 */

import { API_BASE_URL, TIMINGS } from '@utils/constants';
import { tokenStorage } from './TokenStorage';

class AuthInterceptor {
  constructor(baseURL = API_BASE_URL) {
    this.baseURL = baseURL;
    this._refreshPromise = null;
    this._sessionExpiredHandled = false;
  }

  _refresh() {
    if (this._refreshPromise) return this._refreshPromise;

    const refreshToken = tokenStorage.getRefresh();
    if (!refreshToken) {
      return Promise.resolve(false);
    }

    this._refreshPromise = (async () => {
      try {
        const response = await fetch(`${this.baseURL}/auth/refresh`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh_token: refreshToken }),
        });
        if (!response.ok) return false;
        const data = await response.json();
        if (data.success && data.data) {
          tokenStorage.save(data.data);
          return true;
        }
        return false;
      } catch {
        return false;
      } finally {
        this._refreshPromise = null;
      }
    })();

    return this._refreshPromise;
  }

  _handleSessionExpired() {
    if (this._sessionExpiredHandled) return;
    this._sessionExpiredHandled = true;
    tokenStorage.clear();
    setTimeout(() => {
      window.location.href = '/login';
    }, TIMINGS.REDIRECT_DELAY_MS);
  }

  /**
   * Выполняет fetch с Bearer-токеном. При 401 однократно пытается обновить
   * токен (общий promise на все параллельные запросы) и повторяет запрос.
   */
  async fetch(endpoint, options = {}) {
    const url = endpoint.startsWith('http') ? endpoint : `${this.baseURL}${endpoint}`;
    const initialAccess = tokenStorage.getAccess();

    const buildOptions = () => {
      const headers = { ...(options.headers || {}) };
      const token = tokenStorage.getAccess();
      if (token) headers.Authorization = `Bearer ${token}`;
      return { ...options, headers };
    };

    let response = await fetch(url, buildOptions());

    if (response.status !== 401 || !initialAccess) {
      return response;
    }

    // Был залогинен и получил 401 — пробуем обновить токен.
    if (tokenStorage.getRefresh()) {
      const refreshed = await this._refresh();
      if (refreshed) {
        return fetch(url, buildOptions());
      }
    }

    this._handleSessionExpired();
    return response;
  }
}

export const authInterceptor = new AuthInterceptor();

export default AuthInterceptor;
