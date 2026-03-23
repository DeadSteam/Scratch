/**
 * Users Management Component
 */

import { useState, useEffect, useCallback } from 'react';
import { useNotification } from '@context/NotificationContext';
import { userService } from '@api';
import { Button, Spinner, Modal, Input } from '@components/common';
import styles from './Management.module.css';

export function UsersManagement() {
  const [users, setUsers] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedUser, setSelectedUser] = useState(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editForm, setEditForm] = useState({ email: '' });
  const [isSubmitting, setIsSubmitting] = useState(false);

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

  const handleDeactivate = async (userId) => {
    if (!window.confirm('Деактивировать пользователя?')) return;
    try {
      await userService.deactivate(userId);
      success('Пользователь деактивирован');
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

  const handleDelete = async (user) => {
    if (!window.confirm(`Удалить пользователя «${user.username}»? Это действие необратимо.`)) return;
    try {
      await userService.delete(user.id);
      success('Пользователь удалён');
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
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/>
                      </svg>
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
