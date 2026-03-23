/**
 * HTTP Client - Base API layer
 * Single Responsibility: Handle HTTP requests
 */

import { API_BASE_URL, STORAGE_KEYS } from '@utils/constants';

class HttpClient {
  constructor(baseURL = API_BASE_URL) {
    this.baseURL = baseURL;
    this._isRefreshing = false;
    this._refreshQueue = [];
  }

  getAccessToken() {
    return sessionStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
  }

  getRefreshToken() {
    return sessionStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);
  }

  saveTokens({ access_token, refresh_token, user }) {
    if (access_token) sessionStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, access_token);
    if (refresh_token) sessionStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, refresh_token);
    if (user) sessionStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(user));
  }

  clearSession() {
    sessionStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
    sessionStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
    sessionStorage.removeItem(STORAGE_KEYS.USER);
  }

  getHeaders(customHeaders = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...customHeaders,
    };
    const token = this.getAccessToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;
    return headers;
  }

  /**
   * Attempt to refresh the access token using the refresh token.
   * Returns true if successful, false otherwise.
   */
  async tryRefreshToken() {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) return false;

    try {
      const response = await fetch(`${this.baseURL}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
      if (!response.ok) return false;
      const data = await response.json();
      if (data.success && data.data) {
        this.saveTokens(data.data);
        return true;
      }
      return false;
    } catch {
      return false;
    }
  }

  async handleResponse(response, retryFn = null) {
    // Handle empty responses (204 No Content, etc.)
    if (response.status === 204 || response.headers.get('content-length') === '0') {
      return { success: true };
    }

    let data;
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      try {
        data = await response.json();
      } catch (e) {
        const error = new Error(response.statusText || 'Произошла ошибка');
        error.status = response.status;
        throw error;
      }
    } else {
      const text = await response.text();
      data = { message: text || response.statusText };
    }

    if (!response.ok) {
      let errorMessage = data.message || 'Произошла ошибка';

      if (data.errors && Array.isArray(data.errors)) {
        errorMessage = data.errors.map(err => err.message || err.msg || JSON.stringify(err)).join(', ');
      } else if (data.detail) {
        if (Array.isArray(data.detail)) {
          errorMessage = data.detail.map(err => err.msg || err.message || JSON.stringify(err)).join(', ');
        } else if (typeof data.detail === 'string') {
          errorMessage = data.detail;
        }
      } else if (response.status === 401 && retryFn && !this._isRefreshing) {
        // Try to refresh the token once, then retry
        this._isRefreshing = true;
        const refreshed = await this.tryRefreshToken();
        this._isRefreshing = false;
        if (refreshed) {
          return retryFn();
        }
        // Refresh failed — log out
        errorMessage = 'Сессия истекла. Пожалуйста, войдите снова.';
        this.clearSession();
        setTimeout(() => { window.location.href = '/login'; }, 1500);
      } else if (response.status === 401) {
        errorMessage = 'Сессия истекла. Пожалуйста, войдите снова.';
        this.clearSession();
        setTimeout(() => { window.location.href = '/login'; }, 1500);
      } else if (response.status === 429) {
        errorMessage = 'Слишком много запросов. Пожалуйста, подождите немного.';
      } else if (response.status === 403) {
        errorMessage = 'Доступ запрещён. У вас недостаточно прав.';
      }

      const error = new Error(errorMessage);
      error.status = response.status;
      error.data = data;
      throw error;
    }

    return data;
  }

  async get(endpoint, params = {}) {
    const url = new URL(`${this.baseURL}${endpoint}`, window.location.origin);
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) url.searchParams.append(key, value);
    });
    const doRequest = () =>
      fetch(url.toString(), { method: 'GET', headers: this.getHeaders() })
        .then(r => this.handleResponse(r, doRequest));
    return doRequest();
  }

  async post(endpoint, body = {}) {
    const doRequest = () =>
      fetch(`${this.baseURL}${endpoint}`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(body),
      }).then(r => this.handleResponse(r, doRequest));
    return doRequest();
  }

  async postFormData(endpoint, formData) {
    const headers = {};
    const token = this.getAccessToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'POST',
      headers,
      body: formData,
    });
    return this.handleResponse(response);
  }

  async put(endpoint, body = {}) {
    const doRequest = () =>
      fetch(`${this.baseURL}${endpoint}`, {
        method: 'PUT',
        headers: this.getHeaders(),
        body: JSON.stringify(body),
      }).then(r => this.handleResponse(r, doRequest));
    return doRequest();
  }

  async patch(endpoint, body = {}) {
    const doRequest = () =>
      fetch(`${this.baseURL}${endpoint}`, {
        method: 'PATCH',
        headers: this.getHeaders(),
        body: JSON.stringify(body),
      }).then(r => this.handleResponse(r, doRequest));
    return doRequest();
  }

  async delete(endpoint) {
    const doRequest = () =>
      fetch(`${this.baseURL}${endpoint}`, {
        method: 'DELETE',
        headers: this.getHeaders(),
      }).then(r => {
        if (r.status === 204) return { success: true };
        return this.handleResponse(r, doRequest);
      });
    return doRequest();
  }
}

// Export singleton instance
export const httpClient = new HttpClient();

export default HttpClient;



