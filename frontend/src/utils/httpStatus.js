/**
 * HTTP status helpers.
 */

const SERVER_DOWN_STATUSES = new Set([502, 503, 504]);

/**
 * Backend недоступен (gateway-ошибка либо запрос даже не дошёл — нет err.status).
 */
export const isServerDown = (err) =>
  !err?.status || SERVER_DOWN_STATUSES.has(err.status);
