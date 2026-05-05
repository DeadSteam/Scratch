/**
 * Modal Component
 * Reusable modal dialog
 */

import { useEffect, useCallback } from 'react';
import { createPortal } from 'react-dom';
import PropTypes from 'prop-types';
import { X } from '@phosphor-icons/react';
import { ph } from '@components/icons/phosphor';
import styles from './Modal.module.css';

export function Modal({
  isOpen,
  onClose,
  title,
  children,
  size = 'md',
  closeOnOverlay = true,
  closeOnEsc = true,
  showCloseButton = true,
  className = '',
}) {
  // Handle escape key
  const handleEscape = useCallback((event) => {
    if (event.key === 'Escape' && closeOnEsc) {
      onClose();
    }
  }, [closeOnEsc, onClose]);

  // Handle overlay click
  const handleOverlayClick = (event) => {
    if (event.target === event.currentTarget && closeOnOverlay) {
      onClose();
    }
  };

  // Add/remove escape listener
  useEffect(() => {
    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = '';
    };
  }, [isOpen, handleEscape]);

  if (!isOpen) return null;

  const modalClasses = [
    styles.modal,
    styles[size],
    className,
  ].filter(Boolean).join(' ');

  return createPortal(
    <div className={styles.overlay} onClick={handleOverlayClick}>
      <div className={modalClasses} role="dialog" aria-modal="true" aria-labelledby="modal-title">
        <div className={styles.header}>
          {title && <h2 id="modal-title" className={styles.title}>{title}</h2>}
          {showCloseButton && (
            <button 
              type="button"
              className={styles.closeButton} 
              onClick={onClose}
              aria-label="Закрыть"
            >
              <X {...ph(20)} aria-hidden />
            </button>
          )}
        </div>
        <div className={styles.content}>
          {children}
        </div>
      </div>
    </div>,
    document.body,
  );
}

Modal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  title: PropTypes.string,
  children: PropTypes.node.isRequired,
  size: PropTypes.oneOf(['sm', 'md', 'lg', 'xl', 'full']),
  closeOnOverlay: PropTypes.bool,
  closeOnEsc: PropTypes.bool,
  showCloseButton: PropTypes.bool,
  className: PropTypes.string,
};

export default Modal;



