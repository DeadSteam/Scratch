/**
 * Checkbox Component
 */

import { forwardRef } from 'react';
import PropTypes from 'prop-types';
import { Check } from '@phosphor-icons/react';
import styles from './Checkbox.module.css';

export const Checkbox = forwardRef(function Checkbox({
  label,
  disabled = false,
  className = '',
  id,
  ...props
}, ref) {
  const checkboxId = id || `checkbox-${Math.random().toString(36).substr(2, 9)}`;

  return (
    <label 
      htmlFor={checkboxId} 
      className={`${styles.wrapper} ${disabled ? styles.disabled : ''} ${className}`}
    >
      <input
        ref={ref}
        type="checkbox"
        id={checkboxId}
        className={styles.input}
        disabled={disabled}
        {...props}
      />
      <span className={styles.checkmark}>
        <Check size={12} weight="bold" aria-hidden />
      </span>
      {label && <span className={styles.label}>{label}</span>}
    </label>
  );
});

Checkbox.propTypes = {
  label: PropTypes.string,
  disabled: PropTypes.bool,
  className: PropTypes.string,
  id: PropTypes.string,
};

export default Checkbox;



