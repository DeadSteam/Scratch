/**
 * Application Constants
 * Following Single Responsibility Principle
 */

export const API_BASE_URL = '/api/v1';

export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'scratchlab_access_token',
  REFRESH_TOKEN: 'scratchlab_refresh_token',
  USER: 'scratchlab_user',
};

export const ROUTES = {
  LOGIN: '/login',
  REGISTER: '/register',
  EXPERIMENTS: '/experiments',
  EXPERIMENT_NEW: '/experiments/new',
  EXPERIMENT_DETAIL: '/experiments/:id',
  ADMIN: '/admin',
  ADMIN_USERS: '/admin/users',
  ADMIN_FILMS: '/admin/films',
  ADMIN_CONFIGS: '/admin/configs',
};

export const SCRATCH_INDEX_THRESHOLDS = {
  EXCELLENT: 0.05,
  GOOD: 0.15,
  FAIR: 0.25,
  POOR: 0.35,
};

export const PAGINATION = {
  DEFAULT_LIMIT: 20,
  MAX_LIMIT: 100,
};

export const IMAGE_CONFIG = {
  MAX_SIZE_MB: 10,
  MAX_SIZE_BYTES: 10 * 1024 * 1024,
  ALLOWED_TYPES: ['image/jpeg', 'image/png', 'image/webp'],
  ALLOWED_EXTENSIONS: ['.jpg', '.jpeg', '.png', '.webp'],
};

export const TOAST_DURATION = {
  SHORT: 3000,
  MEDIUM: 5000,
  LONG: 8000,
};



