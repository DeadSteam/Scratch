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
 * Format delta between latest and reference scratch indices
 */
export const formatScratchDelta = (value, decimals = 4) => {
  if (value === null || value === undefined) return '-';
  const sign = value > 0 ? '+' : '';
  return `${sign}${value.toFixed(decimals)}`;
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
 * Resolve knowledge-driven quality badge from backend summary
 */
export const getKnowledgeQuality = (knowledgeSummary) => {
  const situation = knowledgeSummary?.situation;
  if (!situation) {
    return { label: 'Нет данных', color: 'muted' };
  }

  return {
    label: situation.label || 'Без оценки',
    color: situation.severity || 'muted',
  };
};

/**
 * Индекс царапины эталона: из knowledge_summary или первый результат с passes === 0.
 */
export const getReferenceScratchIndex = (experiment) => {
  const fromSummary = experiment?.knowledge_summary?.reference_result?.scratch_index;
  if (fromSummary !== null && fromSummary !== undefined) {
    return fromSummary;
  }
  const results = experiment?.scratch_results;
  if (!results?.length) return null;
  const ref = results.find((r) => (r.passes ?? 0) === 0);
  return ref?.scratch_index ?? null;
};

const situationHasNumericBounds = (s) =>
  s &&
  ((s.min_value !== null && s.min_value !== undefined) ||
    (s.max_value !== null && s.max_value !== undefined));

/**
 * Подбор ситуации по значению дельты — только min/max, имя параметра не учитывается.
 * Порядок как в SituationRepository.find_by_value_in_ranges.
 */
export const findSituationForDelta = (delta, situations) => {
  if (delta === null || delta === undefined || !Array.isArray(situations)) {
    return null;
  }
  const filtered = situations.filter(
    (s) =>
      situationHasNumericBounds(s) &&
      (s.min_value === null ||
        s.min_value === undefined ||
        Number(s.min_value) <= delta) &&
      (s.max_value === null ||
        s.max_value === undefined ||
        Number(s.max_value) >= delta),
  );
  if (!filtered.length) return null;

  filtered.sort((a, b) => {
    const aMin = a.min_value;
    const bMin = b.min_value;
    const rankMinDescNullsLast = (v) => (v === null || v === undefined ? -Infinity : Number(v));
    const ar = rankMinDescNullsLast(aMin);
    const br = rankMinDescNullsLast(bMin);
    if (br !== ar) return br - ar;

    const aMax = a.max_value;
    const bMax = b.max_value;
    const rankMaxAscNullsFirst = (v) =>
      v === null || v === undefined ? -Infinity : Number(v);
    const ax = rankMaxAscNullsFirst(aMax);
    const bx = rankMaxAscNullsFirst(bMax);
    if (ax !== bx) return ax - bx;

    return String(a.id).localeCompare(String(b.id));
  });

  return filtered[0];
};

/**
 * Оценка по шкале базы знаний для конкретной дельты (индекс этапа минус эталон).
 * @param {Array|null} situations null — шкала ещё не загружена
 */
export const getKnowledgeQualityFromDelta = (delta, situations) => {
  if (situations === null) {
    return { label: '…', color: 'muted' };
  }
  if (delta === null || delta === undefined) {
    return { label: 'Нет данных', color: 'muted' };
  }
  const situation = findSituationForDelta(delta, situations);
  if (!situation) {
    if (!situations.length) {
      return { label: 'Нет шкалы', color: 'muted' };
    }
    return { label: 'Вне диапазона', color: 'muted' };
  }
  return {
    label: situation.label || 'Без оценки',
    color: situation.severity || 'muted',
  };
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



