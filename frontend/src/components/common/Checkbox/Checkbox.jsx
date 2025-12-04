/**
 * Checkbox Component
 */

import { forwardRef } from 'react';
import PropTypes from 'prop-types';
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
        <svg viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path 
            d="M2.5 6L5 8.5L9.5 3.5" 
            stroke="currentColor" 
            strokeWidth="2" 
            strokeLinecap="round" 
            strokeLinejoin="round"
          />
        </svg>
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



