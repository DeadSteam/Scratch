/**
 * Advice Management — на абстракциях useCrudResource + CrudTable + CrudFormModal.
 */

import { useEffect, useMemo, useState, useCallback } from 'react';
import { Button, Spinner, ConfirmDialog, CrudTable, CrudFormModal } from '@components/common';
import { useCrudResource } from '@hooks/useCrudResource';
import { adviceService, causeService } from '@api';
import { EMPTY_SELECT_OPTION } from '@utils/constants';
import styles from './Management.module.css';

const EMPTY_FORM = { cause_id: '', description: '' };

export function AdviceManagement() {
  const [causes, setCauses] = useState([]);

  const fetchCauses = useCallback(async () => {
    try {
      const res = await causeService.getAll();
      setCauses(res.data || []);
    } catch {
      setCauses([]);
    }
  }, []);

  useEffect(() => { fetchCauses(); }, [fetchCauses]);

  const causeOptions = useMemo(
    () => [EMPTY_SELECT_OPTION, ...causes.map((c) => ({ value: c.id, label: (c.description || '').trim() || c.id }))],
    [causes],
  );

  const getCauseLabel = useCallback((id) => {
    if (!id) return '—';
    const c = causes.find((x) => x.id === id);
    return c ? (c.description || id) : id;
  }, [causes]);

  const crud = useCrudResource({
    service: adviceService,
    emptyForm: EMPTY_FORM,
    itemToForm: (row) => ({
      cause_id: row.cause_id ?? '',
      description: row.description || '',
    }),
    formToPayload: (form) => ({
      cause_id: form.cause_id || null,
      description: form.description || null,
    }),
    validate: (form) => ((form.description || '').length > 50 ? 'Описание не более 50 символов' : null),
    messages: {
      loadError: 'Ошибка загрузки рекомендаций',
      created: 'Рекомендация создана',
      updated: 'Рекомендация обновлена',
      deleted: 'Рекомендация удалена',
    },
  });

  const columns = [
    { header: 'Причина', render: (row) => getCauseLabel(row.cause_id) },
    { header: 'Рекомендация', render: (row) => row.description || '—', className: styles.descriptionCell },
  ];

  const fields = [
    { name: 'cause_id', label: 'Причина', type: 'select', options: causeOptions, placeholder: '— Не выбрано' },
    { name: 'description', label: 'Текст рекомендации', maxLength: 50 },
  ];

  if (crud.isLoading) {
    return <div className={styles.loading}><Spinner size="lg" /></div>;
  }

  return (
    <div className={styles.container}>
      <div className={styles.toolbar}>
        <Button variant="primary" onClick={crud.startCreate}>
          Добавить рекомендацию
        </Button>
      </div>

      <CrudTable
        columns={columns}
        items={crud.items}
        onEdit={crud.startEdit}
        onDelete={(item) => crud.askDelete(item.id)}
        emptyTitle="Нет рекомендаций"
        emptyDescription="Нажмите «Добавить рекомендацию» чтобы создать запись"
      />

      <ConfirmDialog
        isOpen={!!crud.deleteConfirm}
        onClose={crud.cancelDelete}
        onConfirm={crud.confirmDelete}
        title="Удалить рекомендацию?"
        message="Это действие нельзя отменить."
        confirmText="Удалить"
        tone="danger"
      />

      <CrudFormModal
        isOpen={crud.isModalOpen}
        isCreating={crud.isCreating}
        onClose={crud.closeModal}
        onSubmit={crud.submit}
        isSubmitting={crud.isSubmitting}
        titleCreate="Добавить рекомендацию"
        titleEdit="Редактировать рекомендацию"
        fields={fields}
        form={crud.form}
        setForm={crud.setForm}
      />
    </div>
  );
}

export default AdviceManagement;
