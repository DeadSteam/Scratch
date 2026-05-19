/**
 * HttpClient — тонкая обёртка над fetch.
 * Авторизация и refresh-флоу делегированы AuthInterceptor,
 * хранилище токенов — TokenStorage.
 */

import { authInterceptor } from './AuthInterceptor';

const JSON_HEADERS = { 'Content-Type': 'application/json' };

function buildErrorMessage(response, data) {
  if (data?.errors && Array.isArray(data.errors)) {
    return data.errors
      .map((err) => err.message || err.msg || JSON.stringify(err))
      .join(', ');
  }
  if (Array.isArray(data?.detail)) {
    return data.detail
      .map((err) => err.msg || err.message || JSON.stringify(err))
      .join(', ');
  }
  if (typeof data?.detail === 'string') {
    return data.detail;
  }
  if (response.status === 401) {
    return 'Сессия истекла. Пожалуйста, войдите снова.';
  }
  if (response.status >= 502 && response.status <= 504) {
    return 'Сервис временно недоступен. Повторное подключение...';
  }
  if (response.status === 429) {
    return 'Слишком много запросов. Пожалуйста, подождите немного.';
  }
  if (response.status === 403) {
    return 'Доступ запрещён. У вас недостаточно прав.';
  }
  return data?.message || 'Произошла ошибка';
}

async function parseResponse(response) {
  if (response.status === 204 || response.headers.get('content-length') === '0') {
    return { success: true };
  }

  const contentType = response.headers.get('content-type') || '';
  let data;
  if (contentType.includes('application/json')) {
    try {
      data = await response.json();
    } catch {
      const error = new Error(response.statusText || 'Произошла ошибка');
      error.status = response.status;
      throw error;
    }
  } else {
    data = { message: response.statusText || 'Произошла ошибка' };
  }

  if (!response.ok) {
    const error = new Error(buildErrorMessage(response, data));
    error.status = response.status;
    error.data = data;
    throw error;
  }

  return data;
}

function appendQuery(endpoint, params) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) search.append(key, value);
  });
  const qs = search.toString();
  return qs ? `${endpoint}?${qs}` : endpoint;
}

class HttpClient {
  async _request(endpoint, options) {
    const response = await authInterceptor.fetch(endpoint, options);
    return parseResponse(response);
  }

  get(endpoint, params = {}) {
    return this._request(appendQuery(endpoint, params), { method: 'GET' });
  }

  post(endpoint, body = {}) {
    return this._request(endpoint, {
      method: 'POST',
      headers: JSON_HEADERS,
      body: JSON.stringify(body),
    });
  }

  put(endpoint, body = {}) {
    return this._request(endpoint, {
      method: 'PUT',
      headers: JSON_HEADERS,
      body: JSON.stringify(body),
    });
  }

  patch(endpoint, body = {}) {
    return this._request(endpoint, {
      method: 'PATCH',
      headers: JSON_HEADERS,
      body: JSON.stringify(body),
    });
  }

  async delete(endpoint) {
    const response = await authInterceptor.fetch(endpoint, { method: 'DELETE' });
    if (response.status === 204) return { success: true };
    return parseResponse(response);
  }

  postFormData(endpoint, formData) {
    return this._request(endpoint, { method: 'POST', body: formData });
  }

  async getBlob(endpoint) {
    const response = await authInterceptor.fetch(endpoint, { method: 'GET' });
    if (!response.ok) {
      let message = response.statusText || 'Не удалось загрузить изображение';
      const contentType = response.headers.get('content-type') || '';
      if (contentType.includes('application/json')) {
        try {
          const data = await response.json();
          message = data.message || data.detail || message;
        } catch {
          /* ignore */
        }
      }
      const error = new Error(
        typeof message === 'string' ? message : 'Не удалось загрузить изображение',
      );
      error.status = response.status;
      throw error;
    }
    return response.blob();
  }
}

export const httpClient = new HttpClient();

export default HttpClient;
