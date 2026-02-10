/**
 * Data Formatters
 */

import { SCRATCH_INDEX_THRESHOLDS } from './constants';

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

  const { EXCELLENT, GOOD, FAIR, POOR } = SCRATCH_INDEX_THRESHOLDS;
  if (index < EXCELLENT) return { label: 'Отлично', color: 'success' };
  if (index < GOOD) return { label: 'Хорошо', color: 'success' };
  if (index < FAIR) return { label: 'Удовлетворительно', color: 'warning' };
  if (index < POOR) return { label: 'Плохо', color: 'warning' };
  return { label: 'Критично', color: 'error' };
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



