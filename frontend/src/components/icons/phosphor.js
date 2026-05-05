/**
 * Общие настройки иконок Phosphor по всему приложению.
 * @see https://phosphoricons.com/
 */

export const PHOSPHOR_WEIGHT = 'regular';

/** Удобная обёртка: размер + вес по умолчанию */
export function ph(size, overrides = {}) {
  return { size, weight: PHOSPHOR_WEIGHT, ...overrides };
}
