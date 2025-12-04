/**
 * Data Formatters
 */

/**
 * Format date to Russian locale string
 */
export const formatDate = (dateString, options = {}) => {
  if (!dateString) return '-';
  
  const defaultOptions = {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
    ...options,
  };
  
  return new Date(dateString).toLocaleDateString('ru-RU', defaultOptions);
};

/**
 * Format date with time
 */
export const formatDateTime = (dateString) => {
  if (!dateString) return '-';
  
  return new Date(dateString).toLocaleString('ru-RU', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

/**
 * Format scratch index as raw value 0..1
 */
export const formatScratchIndex = (value, decimals = 4) => {
  if (value === null || value === undefined) return '-';
  return value.toFixed(decimals);
};

/**
 * Format scratch index with quality label
 */
export const getScratchQuality = (index) => {
  if (index === null || index === undefined) return { label: 'Нет данных', color: 'muted' };
  
  if (index < 0.05) return { label: 'Отлично', color: 'success' };
  if (index < 0.15) return { label: 'Хорошо', color: 'success' };
  if (index < 0.25) return { label: 'Удовлетворительно', color: 'warning' };
  if (index < 0.35) return { label: 'Плохо', color: 'warning' };
  return { label: 'Критично', color: 'error' };
};

/**
 * Format file size
 */
export const formatFileSize = (bytes) => {
  if (!bytes) return '0 B';
  
  const units = ['B', 'KB', 'MB', 'GB'];
  let unitIndex = 0;
  let size = bytes;
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }
  
  return `${size.toFixed(1)} ${units[unitIndex]}`;
};

/**
 * Format weight (grams)
 */
export const formatWeight = (grams) => {
  if (!grams) return '-';
  return `${grams} г`;
};

/**
 * Format coating thickness (micrometers)
 */
export const formatThickness = (micrometers) => {
  if (!micrometers) return '-';
  return `${micrometers} мкм`;
};

/**
 * Truncate text with ellipsis
 */
export const truncate = (text, maxLength = 50) => {
  if (!text || text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
};



