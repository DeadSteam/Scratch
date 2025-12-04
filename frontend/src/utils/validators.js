/**
 * Validation Utilities
 */

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
 * Validate required field
 */
export const isRequired = (value) => {
  if (value === null || value === undefined) return false;
  if (typeof value === 'string') return value.trim().length > 0;
  return true;
};

/**
 * Validate image file
 */
export const validateImageFile = (file) => {
  const errors = [];
  const maxSize = 10 * 1024 * 1024; // 10MB
  const allowedTypes = ['image/jpeg', 'image/png', 'image/webp'];
  
  if (!file) {
    errors.push('Файл не выбран');
    return { isValid: false, errors };
  }
  
  if (file.size > maxSize) {
    errors.push('Размер файла не должен превышать 10 МБ');
  }
  
  if (!allowedTypes.includes(file.type)) {
    errors.push('Допустимые форматы: JPEG, PNG, WebP');
  }
  
  return {
    isValid: errors.length === 0,
    errors,
  };
};

/**
 * Validate rectangle coordinates
 */
export const validateRectCoords = (coords) => {
  if (!Array.isArray(coords) || coords.length !== 4) {
    return { isValid: false, error: 'Координаты должны содержать 4 значения' };
  }
  
  const [x, y, width, height] = coords;
  
  if (x < 0 || y < 0 || width <= 0 || height <= 0) {
    return { isValid: false, error: 'Недопустимые координаты области' };
  }
  
  return { isValid: true, error: null };
};

/**
 * Validate positive number
 */
export const isPositiveNumber = (value) => {
  const num = parseFloat(value);
  return !isNaN(num) && num > 0;
};



