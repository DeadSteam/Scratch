/**
 * Users Management Component
 */

import { useState, useEffect, useCallback } from 'react';
import { useNotification } from '@context/NotificationContext';
import { userService } from '@api';
import { Users } from '@phosphor-icons/react';
import { ph } from '@components/icons/phosphor';
import { Button, Spinner, Modal, Input } from '@components/common';
import styles from './Management.module.css';

export function UsersManagement() {
  const [users, setUsers] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedUser, setSelectedUser] = useState(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editForm, setEditForm] = useState({ email: '' });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState(null);
  const [deactivateConfirm, setDeactivateConfirm] = useState(null);

  const { success, error: showError } = useNotification();

  const fetchUsers = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await userService.getAll();
      setUsers(response.data || []);
    } catch (err) {
      showError('Ошибка загрузки пользователей');
    } finally {
      setIsLoading(false);
    }
  }, [showError]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  const handleEdit = (user) => {
    setSelectedUser(user);
    setEditForm({ email: user.email });
    setIsEditModalOpen(true);
  };

  const handleUpdateUser = async () => {
    if (!selectedUser) return;

    setIsSubmitting(true);
    try {
      await userService.update(selectedUser.id, editForm);
      success('Пользователь обновлён');
      setIsEditModalOpen(false);
      fetchUsers();
    } catch (err) {
      showError(err.message || 'Ошибка обновления');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeactivate = (userId) => setDeactivateConfirm(userId);

  const handleConfirmDeactivate = async () => {
    try {
      await userService.deactivate(deactivateConfirm);
      success('Пользователь деактивирован');
      setDeactivateConfirm(null);
      fetchUsers();
    } catch (err) {
      showError(err.message || 'Ошибка деактивации');
    }
  };

  const handleActivate = async (userId) => {
    try {
      await userService.activate(userId);
      success('Пользователь активирован');
      fetchUsers();
    } catch (err) {
      showError(err.message || 'Ошибка активации');
    }
  };

  const handleDelete = (user) => setDeleteConfirm(user);

  const handleConfirmDelete = async () => {
    try {
      await userService.delete(deleteConfirm.id);
      success('Пользователь удалён');
      setDeleteConfirm(null);
      fetchUsers();
    } catch (err) {
      showError(err.message || 'Ошибка удаления');
    }
  };

  if (isLoading) {
    return (
      <div className={styles.loading}>
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.tableWrapper}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>Имя пользователя</th>
              <th>Email</th>
              <th>Роли</th>
              <th>Статус</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            {users.length === 0 ? (
              <tr className={styles.emptyRow}>
                <td colSpan={5}>
                  <div className={styles.emptyStateCell}>
                    <div className={styles.emptyIcon}>
                      <Users {...ph(18)} aria-hidden />
                    </div>
                    <p className={styles.emptyTitle}>Нет пользователей</p>
                    <p className={styles.emptyDesc}>Пользователи появятся здесь после загрузки данных</p>
                  </div>
                </td>
              </tr>
            ) : users.map((user) => (
              <tr key={user.id}>
                <td className={styles.primaryCell}>{user.username}</td>
                <td>{user.email}</td>
                <td>
                  {user.roles?.map((role) => (
                    <span key={role.id} className={styles.badge}>
                      {role.name}
                    </span>
                  ))}
                </td>
                <td>
                  <span className={`${styles.status} ${user.is_active ? styles.active : styles.inactive}`}>
                    {user.is_active ? 'Активен' : 'Неактивен'}
                  </span>
                </td>
                <td>
                  <div className={styles.actions}>
                    <Button variant="ghost" size="sm" onClick={() => handleEdit(user)}>
                      Изменить
                    </Button>
                    {user.is_active ? (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDeactivate(user.id)}
                      >
                        Деактивировать
                      </Button>
                    ) : (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleActivate(user.id)}
                      >
                        Активировать
                      </Button>
                    )}
                    <Button
                      variant="ghost"
                      size="sm"
                      className={styles.deleteBtn}
                      onClick={() => handleDelete(user)}
                    >
                      Удалить
                    </Button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Deactivate confirmation */}
      <Modal
        isOpen={!!deactivateConfirm}
        onClose={() => setDeactivateConfirm(null)}
        title="Деактивировать пользователя?"
        size="sm"
      >
        <div className={styles.modalContent}>
          <p>Пользователь потеряет доступ к системе. Это можно отменить.</p>
          <div className={styles.modalActions}>
            <Button variant="secondary" onClick={() => setDeactivateConfirm(null)}>Отмена</Button>
            <Button variant="danger" onClick={handleConfirmDeactivate}>Деактивировать</Button>
          </div>
        </div>
      </Modal>

      {/* Delete confirmation */}
      <Modal
        isOpen={!!deleteConfirm}
        onClose={() => setDeleteConfirm(null)}
        title={`Удалить пользователя «${deleteConfirm?.username || deleteConfirm?.email || ''}»?`}
        size="sm"
      >
        <div className={styles.modalContent}>
          <p>Это действие необратимо.</p>
          <div className={styles.modalActions}>
            <Button variant="secondary" onClick={() => setDeleteConfirm(null)}>Отмена</Button>
            <Button variant="danger" onClick={handleConfirmDelete}>Удалить</Button>
          </div>
        </div>
      </Modal>

      {/* Edit Modal */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        title="Редактирование пользователя"
        size="sm"
      >
        <div className={styles.modalContent}>
          <Input
            label="Email"
            type="email"
            value={editForm.email}
            onChange={(e) => setEditForm((prev) => ({ ...prev, email: e.target.value }))}
          />

          <div className={styles.modalActions}>
            <Button variant="secondary" onClick={() => setIsEditModalOpen(false)}>
              Отмена
            </Button>
            <Button variant="primary" onClick={handleUpdateUser} loading={isSubmitting}>
              Сохранить
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}

export default UsersManagement;
