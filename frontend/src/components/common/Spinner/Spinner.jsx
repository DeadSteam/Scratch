/**
 * Spinner Component
 * Loading indicator
 */

import PropTypes from 'prop-types';
import { CircleNotch } from '@phosphor-icons/react';
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
      <CircleNotch weight="bold" aria-hidden />
      <span className="sr-only">Загрузка...</span>
    </div>
  );
}

Spinner.propTypes = {
  size: PropTypes.oneOf(['sm', 'md', 'lg', 'xl']),
  className: PropTypes.string,
};

export default Spinner;



