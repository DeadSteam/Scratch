/**
 * Toast Component
 * Notification toast messages
 */

import { useNotification } from '@context/NotificationContext';
import { CheckCircle, XCircle, Warning, Info, X } from '@phosphor-icons/react';
import { ph } from '@components/icons/phosphor';
import styles from './Toast.module.css';

const iconProps = ph(20, { weight: 'fill' });

const icons = {
  success: <CheckCircle {...iconProps} aria-hidden />,
  error: <XCircle {...iconProps} aria-hidden />,
  warning: <Warning {...iconProps} aria-hidden />,
  info: <Info {...iconProps} aria-hidden />,
};

export function ToastContainer() {
  const { notifications, removeNotification } = useNotification();

  if (notifications.length === 0) return null;

  return (
    <div className={styles.container}>
      {notifications.map((notification) => (
        <div
          key={notification.id}
          className={`${styles.toast} ${styles[notification.type]}`}
          role="alert"
        >
          <span className={styles.icon}>
            {icons[notification.type]}
          </span>
          <span className={styles.message}>{notification.message}</span>
          <button
            type="button"
            className={styles.closeButton}
            onClick={() => removeNotification(notification.id)}
            aria-label="Закрыть"
          >
            <X {...ph(16)} weight="bold" aria-hidden />
          </button>
        </div>
      ))}
    </div>
  );
}

export default ToastContainer;



