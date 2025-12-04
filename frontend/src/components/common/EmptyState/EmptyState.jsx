/**
 * Empty State Component
 * Display when no data is available
 */

import PropTypes from 'prop-types';
import { Button } from '../Button/Button';
import styles from './EmptyState.module.css';

export function EmptyState({
  icon,
  title,
  description,
  action,
  onAction,
  className = '',
}) {
  return (
    <div className={`${styles.container} ${className}`}>
      {icon && <div className={styles.icon}>{icon}</div>}
      <h3 className={styles.title}>{title}</h3>
      {description && <p className={styles.description}>{description}</p>}
      {action && onAction && (
        <Button variant="primary" onClick={onAction}>
          {action}
        </Button>
      )}
    </div>
  );
}

EmptyState.propTypes = {
  icon: PropTypes.node,
  title: PropTypes.string.isRequired,
  description: PropTypes.string,
  action: PropTypes.string,
  onAction: PropTypes.func,
  className: PropTypes.string,
};

export default EmptyState;



