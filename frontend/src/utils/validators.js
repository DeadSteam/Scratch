/**
 * Validation Utilities
 */

import { IMAGE_CONFIG } from './constants';

/**
 * Validate email format
 */
export const isValidEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Validate password strength
 */
export const validatePassword = (password) => {
  const errors = [];
  
  if (password.length < 8) {
    errors.push('Минимум 8 символов');
  }
  if (!/[A-Z]/.test(password)) {
    errors.push('Минимум одна заглавная буква');
  }
  if (!/[a-z]/.test(password)) {
    errors.push('Минимум одна строчная буква');
  }
  if (!/[0-9]/.test(password)) {
    errors.push('Минимум одна цифра');
  }
  
  return {
    isValid: errors.length === 0,
    errors,
  };
};

/**
 * Validate username
 */
export const validateUsername = (username) => {
  const errors = [];
  
  if (username.length < 3) {
    errors.push('Минимум 3 символа');
  }
  if (username.length > 50) {
    errors.push('Максимум 50 символов');
  }
  if (!/^[a-zA-Z0-9_]+$/.test(username)) {
    errors.push('Только буквы, цифры и подчеркивания');
  }
  
  return {
    isValid: errors.length === 0,
    errors,
  };
};

/**
 * Validate image file
 */
export const validateImageFile = (file) => {
  const errors = [];

  if (!file) {
    errors.push('Файл не выбран');
    return { isValid: false, errors };
  }

  if (file.size > IMAGE_CONFIG.MAX_SIZE_BYTES) {
    errors.push(`Размер файла не должен превышать ${IMAGE_CONFIG.MAX_SIZE_MB} МБ`);
  }

  if (!IMAGE_CONFIG.ALLOWED_TYPES.includes(file.type)) {
    errors.push('Допустимые форматы: JPEG, PNG, WebP');
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
};



