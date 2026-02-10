/**
 * HTTP Client - Base API layer
 * Single Responsibility: Handle HTTP requests
 */

import { API_BASE_URL, STORAGE_KEYS } from '@utils/constants';

class HttpClient {
  constructor(baseURL = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  /**
   * Get access token from session storage
   */
  getAccessToken() {
    return sessionStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
  }

  /**
   * Get default headers
   */
  getHeaders(customHeaders = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...customHeaders,
    };

    const token = this.getAccessToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    return headers;
  }

  /**
   * Handle response
   */
  async handleResponse(response) {
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
        // If JSON parsing fails, create error from status text
        const error = new Error(response.statusText || 'Произошла ошибка');
        error.status = response.status;
        throw error;
      }
    } else {
      // Non-JSON response
      const text = await response.text();
      data = { message: text || response.statusText };
    }

    if (!response.ok) {
      // Extract error message from validation errors if present
      let errorMessage = data.message || 'Произошла ошибка';

      // Handle FastAPI validation errors (errors array)
      if (data.errors && Array.isArray(data.errors)) {
        errorMessage = data.errors.map(err => err.message || err.msg || JSON.stringify(err)).join(', ');
      }
      // Handle Pydantic validation errors (detail array)
      else if (data.detail) {
        if (Array.isArray(data.detail)) {
          errorMessage = data.detail.map(err => err.msg || err.message || JSON.stringify(err)).join(', ');
        } else if (typeof data.detail === 'string') {
          errorMessage = data.detail;
        }
      } else if (response.status === 401) {
        errorMessage = 'Сессия истекла. Пожалуйста, войдите снова.';
        // Auto-logout on 401
        sessionStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
        sessionStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
        sessionStorage.removeItem(STORAGE_KEYS.USER);
        // Redirect to login after a short delay
        setTimeout(() => {
          window.location.href = '/login';
        }, 1500);
      } else if (response.status === 429) {
        errorMessage = 'Слишком много запросов. Пожалуйста, подождите немного.';
      } else if (response.status === 403) {
        errorMessage = 'Доступ запрещен. У вас недостаточно прав для выполнения этого действия.';
      }

      const error = new Error(errorMessage);
      error.status = response.status;
      error.data = data;
      throw error;
    }

    return data;
  }

  /**
   * GET request
   */
  async get(endpoint, params = {}) {
    const url = new URL(`${this.baseURL}${endpoint}`, window.location.origin);
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        url.searchParams.append(key, value);
      }
    });

    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: this.getHeaders(),
    });

    return this.handleResponse(response);
  }

  /**
   * POST request
   */
  async post(endpoint, body = {}) {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(body),
    });

    return this.handleResponse(response);
  }

  /**
   * POST multipart form data (for file uploads)
   */
  async postFormData(endpoint, formData) {
    const headers = {};
    const token = this.getAccessToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'POST',
      headers,
      body: formData,
    });

    return this.handleResponse(response);
  }

  /**
   * PATCH request
   */
  async patch(endpoint, body = {}) {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'PATCH',
      headers: this.getHeaders(),
      body: JSON.stringify(body),
    });

    return this.handleResponse(response);
  }

  /**
   * DELETE request
   */
  async delete(endpoint) {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'DELETE',
      headers: this.getHeaders(),
    });

    // Handle 204 No Content
    if (response.status === 204) {
      return { success: true };
    }

    return this.handleResponse(response);
  }
}

// Export singleton instance
export const httpClient = new HttpClient();

export default HttpClient;



