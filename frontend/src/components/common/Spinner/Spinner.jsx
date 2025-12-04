/**
 * Spinner Component
 * Loading indicator
 */

import PropTypes from 'prop-types';
import styles from './Spinner.module.css';

export function Spinner({
  size = 'md',
  className = '',
}) {
  const spinnerClasses = [
    styles.spinner,
    styles[size],
    className,
  ].filter(Boolean).join(' ');

  return (
    <div className={spinnerClasses} role="status" aria-label="Загрузка">
      <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle 
          cx="12" 
          cy="12" 
          r="10" 
          stroke="currentColor" 
          strokeWidth="3"
          className={styles.track}
        />
        <path 
          d="M12 2C6.47715 2 2 6.47715 2 12" 
          stroke="currentColor" 
          strokeWidth="3"
          strokeLinecap="round"
          className={styles.progress}
        />
      </svg>
      <span className="sr-only">Загрузка...</span>
    </div>
  );
}

Spinner.propTypes = {
  size: PropTypes.oneOf(['sm', 'md', 'lg', 'xl']),
  className: PropTypes.string,
};

export default Spinner;



