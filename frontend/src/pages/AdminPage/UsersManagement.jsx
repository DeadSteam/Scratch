/**
 * Users Management — на абстракциях useCrudResource + CrudTable.
 *
 * Особенности: правка только email (PUT), отдельный flow деактивации/активации,
 * подтверждение удаления хранит весь объект (для отображения username в заголовке).
 */

import { useCallback, useEffect, useState } from 'react';
import { Users } from '@phosphor-icons/react';
import { ph } from '@components/icons/phosphor';
import { useNotification } from '@context/NotificationContext';
import { Button, Spinner, ConfirmDialog, CrudTable, CrudFormModal } from '@components/common';
import { useCrudResource } from '@hooks/useCrudResource';
import { userService } from '@api';
import { RolesModal } from './RolesModal';
import styles from './Management.module.css';

const EMPTY_FORM = { email: '' };

const FIELDS = [{ name: 'email', label: 'Email', type: 'email' }];

export function UsersManagement() {
  const { success, error: showError } = useNotification();
  const [deactivateConfirm, setDeactivateConfirm] = useState(null);
  const [rolesUser, setRolesUser] = useState(null);
  const [availableRoles, setAvailableRoles] = useState([]);
  const [isLoadingRoles, setIsLoadingRoles] = useState(false);
  const [isSavingRoles, setIsSavingRoles] = useState(false);

  const crud = useCrudResource({
    service: userService,
    emptyForm: EMPTY_FORM,
    itemToForm: (user) => ({ email: user.email }),
    formToPayload: (form) => form,
    messages: {
      loadError: 'Ошибка загрузки пользователей',
      updated: 'Пользователь обновлён',
      deleted: 'Пользователь удалён',
    },
  });

  const handleConfirmDeactivate = useCallback(async () => {
    if (!deactivateConfirm) return;
    try {
      await userService.deactivate(deactivateConfirm);
      success('Пользователь деактивирован');
      setDeactivateConfirm(null);
      crud.refetch();
    } catch (err) {
      showError(err.message || 'Ошибка деактивации');
    }
  }, [deactivateConfirm, success, showError, crud]);

  const handleActivate = useCallback(async (userId) => {
    try {
      await userService.activate(userId);
      success('Пользователь активирован');
      crud.refetch();
    } catch (err) {
      showError(err.message || 'Ошибка активации');
    }
  }, [success, showError, crud]);

  useEffect(() => {
    let cancelled = false;
    setIsLoadingRoles(true);
    userService.getRoles()
      .then((roles) => { if (!cancelled) setAvailableRoles(roles || []); })
      .catch((err) => showError(err.message || 'Ошибка загрузки ролей'))
      .finally(() => { if (!cancelled) setIsLoadingRoles(false); });
    return () => { cancelled = true; };
  }, [showError]);

  const handleSaveRoles = useCallback(async (roles) => {
    if (!rolesUser) return;
    setIsSavingRoles(true);
    try {
      await userService.setRoles(rolesUser.id, roles);
      success('Роли обновлены');
      setRolesUser(null);
      crud.refetch();
    } catch (err) {
      showError(err.message || 'Ошибка сохранения ролей');
    } finally {
      setIsSavingRoles(false);
    }
  }, [rolesUser, success, showError, crud]);

  const columns = [
    { header: 'Имя пользователя', field: 'username' },
    { header: 'Email', field: 'email' },
    {
      header: 'Роли',
      render: (u) => (u.roles || []).map((r) => (
        <span key={r.id} className={styles.badge}>{r.name}</span>
      )),
    },
    {
      header: 'Статус',
      render: (u) => (
        <span className={`${styles.status} ${u.is_active ? styles.active : styles.inactive}`}>
          {u.is_active ? 'Активен' : 'Неактивен'}
        </span>
      ),
    },
  ];

  if (crud.isLoading) {
    return <div className={styles.loading}><Spinner size="lg" /></div>;
  }

  return (
    <div className={styles.container}>
      <CrudTable
        columns={columns}
        items={crud.items}
        onEdit={crud.startEdit}
        onDelete={(user) => crud.askDelete(user)}
        actions={(user) => (
          <>
            <Button variant="ghost" size="sm" onClick={() => setRolesUser(user)}>Роли</Button>
            {user.is_active
              ? <Button variant="ghost" size="sm" onClick={() => setDeactivateConfirm(user.id)}>Деактивировать</Button>
              : <Button variant="ghost" size="sm" onClick={() => handleActivate(user.id)}>Активировать</Button>}
          </>
        )}
        emptyIcon={<Users {...ph(18)} aria-hidden />}
        emptyTitle="Нет пользователей"
        emptyDescription="Пользователи появятся здесь после загрузки данных"
      />

      <ConfirmDialog
        isOpen={!!deactivateConfirm}
        onClose={() => setDeactivateConfirm(null)}
        onConfirm={handleConfirmDeactivate}
        title="Деактивировать пользователя?"
        message="Пользователь потеряет доступ к системе. Это можно отменить."
        confirmText="Деактивировать"
        tone="danger"
      />

      <ConfirmDialog
        isOpen={!!crud.deleteConfirm}
        onClose={crud.cancelDelete}
        onConfirm={crud.confirmDelete}
        title={`Удалить пользователя «${crud.deleteConfirm?.username || crud.deleteConfirm?.email || ''}»?`}
        message="Это действие необратимо."
        confirmText="Удалить"
        tone="danger"
      />

      <CrudFormModal
        isOpen={crud.isModalOpen}
        isCreating={false}
        onClose={crud.closeModal}
        onSubmit={crud.submit}
        isSubmitting={crud.isSubmitting}
        titleCreate=""
        titleEdit="Редактирование пользователя"
        fields={FIELDS}
        form={crud.form}
        setForm={crud.setForm}
      />

      <RolesModal
        isOpen={!!rolesUser}
        user={rolesUser}
        availableRoles={availableRoles}
        isLoadingRoles={isLoadingRoles}
        isSaving={isSavingRoles}
        onClose={() => setRolesUser(null)}
        onSave={handleSaveRoles}
      />
    </div>
  );
}

export default UsersManagement;
