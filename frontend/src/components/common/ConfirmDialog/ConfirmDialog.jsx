/**
 * ConfirmDialog
 * Универсальный диалог подтверждения (delete / deactivate / save).
 * Заменяет 8+ копий «Удалить ...?» Modal'ов по проекту.
 */

import PropTypes from 'prop-types';
import { Modal } from '../Modal/Modal';
import { Button } from '../Button/Button';
import styles from './ConfirmDialog.module.css';

export function ConfirmDialog({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  icon,
  confirmText = 'Подтвердить',
  cancelText = 'Отмена',
  tone = 'primary',
  loading = false,
  size = 'sm',
}) {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title={title} size={size}>
      <div className={styles.content}>
        {icon && <div className={styles.icon}>{icon}</div>}
        {message && <p className={styles.message}>{message}</p>}
        <div className={styles.actions}>
          <Button variant="secondary" onClick={onClose} disabled={loading}>
            {cancelText}
          </Button>
          <Button variant={tone} onClick={onConfirm} loading={loading}>
            {confirmText}
          </Button>
        </div>
      </div>
    </Modal>
  );
}

ConfirmDialog.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onConfirm: PropTypes.func.isRequired,
  title: PropTypes.string.isRequired,
  message: PropTypes.node,
  icon: PropTypes.node,
  confirmText: PropTypes.string,
  cancelText: PropTypes.string,
  tone: PropTypes.oneOf(['primary', 'danger', 'secondary']),
  loading: PropTypes.bool,
  size: PropTypes.oneOf(['sm', 'md', 'lg', 'xl', 'full']),
};

export default ConfirmDialog;
