/**
 * RolesModal — админ выбирает роли пользователя чекбоксами и сохраняет.
 */

import { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import { Modal, Button, Checkbox, Spinner } from '@components/common';
import styles from './Management.module.css';

export function RolesModal({
  isOpen,
  user,
  availableRoles,
  isLoadingRoles,
  isSaving,
  onClose,
  onSave,
}) {
  const [selected, setSelected] = useState([]);

  useEffect(() => {
    if (user) {
      setSelected((user.roles || []).map((r) => r.name));
    }
  }, [user]);

  const toggle = (name) => {
    setSelected((prev) =>
      prev.includes(name) ? prev.filter((n) => n !== name) : [...prev, name],
    );
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`Роли пользователя «${user?.username || ''}»`}
      size="sm"
    >
      {isLoadingRoles ? (
        <div className={styles.loading}><Spinner size="md" /></div>
      ) : (
        <div className={styles.rolesList}>
          {availableRoles.length === 0 ? (
            <p>Нет доступных ролей</p>
          ) : (
            availableRoles.map((role) => (
              <Checkbox
                key={role.id}
                label={role.name}
                checked={selected.includes(role.name)}
                onChange={() => toggle(role.name)}
                disabled={isSaving}
              />
            ))
          )}
        </div>
      )}

      <div className={styles.modalActions}>
        <Button variant="secondary" onClick={onClose} disabled={isSaving}>
          Отмена
        </Button>
        <Button
          variant="primary"
          onClick={() => onSave(selected)}
          loading={isSaving}
        >
          Сохранить
        </Button>
      </div>
    </Modal>
  );
}

RolesModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  user: PropTypes.shape({
    id: PropTypes.string,
    username: PropTypes.string,
    roles: PropTypes.array,
  }),
  availableRoles: PropTypes.array.isRequired,
  isLoadingRoles: PropTypes.bool,
  isSaving: PropTypes.bool,
  onClose: PropTypes.func.isRequired,
  onSave: PropTypes.func.isRequired,
};

export default RolesModal;
