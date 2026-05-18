/**
 * Select Component
 * Reusable dropdown select
 */

import { forwardRef } from 'react';
import PropTypes from 'prop-types';
import { CaretDown } from '@phosphor-icons/react';
import { useGeneratedId } from '@hooks/useGeneratedId';
import styles from './Select.module.css';

export const Select = forwardRef(function Select({
  label,
  options = [],
  error,
  hint,
  disabled = false,
  required = false,
  fullWidth = true,
  placeholder = 'Выберите...',
  className = '',
  id,
  ...props
}, ref) {
  const selectId = useGeneratedId(id);

  const wrapperClasses = [
    styles.wrapper,
    fullWidth && styles.fullWidth,
    error && styles.hasError,
    disabled && styles.disabled,
    className,
  ].filter(Boolean).join(' ');

  return (
    <div className={wrapperClasses}>
      {label && (
        <label htmlFor={selectId} className={styles.label}>
          {label}
          {required && <span className={styles.required}>*</span>}
        </label>
      )}
      <div className={styles.selectWrapper}>
        <select
          ref={ref}
          id={selectId}
          className={styles.select}
          disabled={disabled}
          aria-invalid={!!error}
          aria-describedby={error ? `${selectId}-error` : hint ? `${selectId}-hint` : undefined}
          {...props}
        >
          <option value="" disabled>
            {placeholder}
          </option>
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        <span className={styles.arrow}>
          <CaretDown size={12} weight="bold" aria-hidden />
        </span>
      </div>
      {error && (
        <span id={`${selectId}-error`} className={styles.error} role="alert">
          {error}
        </span>
      )}
      {hint && !error && (
        <span id={`${selectId}-hint`} className={styles.hint}>
          {hint}
        </span>
      )}
    </div>
  );
});

Select.propTypes = {
  label: PropTypes.string,
  options: PropTypes.arrayOf(PropTypes.shape({
    value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
    label: PropTypes.string.isRequired,
  })),
  error: PropTypes.string,
  hint: PropTypes.string,
  disabled: PropTypes.bool,
  required: PropTypes.bool,
  fullWidth: PropTypes.bool,
  placeholder: PropTypes.string,
  className: PropTypes.string,
  id: PropTypes.string,
};

export default Select;



