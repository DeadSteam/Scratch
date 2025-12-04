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
  const [editForm, setEditForm] = useState({ email: '', is_active: true });
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
    setEditForm({ email: user.email, is_active: user.is_active });
    setIsEditModalOpen(true);
  };

  const handleUpdateUser = async () => {
    if (!selectedUser) return;
    
    setIsSubmitting(true);
    try {
      await userService.update(selectedUser.id, editForm);
      success('Пользователь обновлен');
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
            {users.map((user) => (
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
                    {user.is_active && (
                      <Button 
                        variant="ghost" 
                        size="sm" 
                        onClick={() => handleDeactivate(user.id)}
                      >
                        Деактивировать
                      </Button>
                    )}
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
          
          <label className={styles.checkboxLabel}>
            <input
              type="checkbox"
              checked={editForm.is_active}
              onChange={(e) => setEditForm((prev) => ({ ...prev, is_active: e.target.checked }))}
            />
            <span>Активен</span>
          </label>

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

