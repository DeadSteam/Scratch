/**
 * Causes Management — на абстракциях useCrudResource + CrudTable + CrudFormModal.
 */

import { useEffect, useMemo, useState, useCallback } from 'react';
import { Button, Spinner, ConfirmDialog, CrudTable, CrudFormModal } from '@components/common';
import { useCrudResource } from '@hooks/useCrudResource';
import { causeService, situationService } from '@api';
import { EMPTY_SELECT_OPTION } from '@utils/constants';
import styles from './Management.module.css';

const EMPTY_FORM = { situation_id: '', description: '' };

const situationLabel = (s) =>
  [s.label, s.controlled_param, s.description].filter(Boolean).join(' — ') || s.id;

export function CausesManagement() {
  const [situations, setSituations] = useState([]);

  const fetchSituations = useCallback(async () => {
    try {
      const res = await situationService.getAll({ skip: 0, limit: 500 });
      setSituations(res.data || []);
    } catch {
      setSituations([]);
    }
  }, []);

  useEffect(() => { fetchSituations(); }, [fetchSituations]);

  const situationOptions = useMemo(
    () => [EMPTY_SELECT_OPTION, ...situations.map((s) => ({ value: s.id, label: situationLabel(s) }))],
    [situations],
  );

  const getSituationLabel = useCallback((id) => {
    if (!id) return '—';
    const s = situations.find((x) => x.id === id);
    return s ? situationLabel(s) : id;
  }, [situations]);

  const crud = useCrudResource({
    service: causeService,
    emptyForm: EMPTY_FORM,
    itemToForm: (row) => ({
      situation_id: row.situation_id ?? '',
      description: row.description || '',
    }),
    formToPayload: (form) => ({
      situation_id: form.situation_id || null,
      description: form.description || null,
    }),
    messages: {
      loadError: 'Ошибка загрузки причин',
      created: 'Причина создана',
      updated: 'Причина обновлена',
      deleted: 'Причина удалена',
    },
  });

  const columns = [
    { header: 'Ситуация', render: (row) => getSituationLabel(row.situation_id) },
    { header: 'Описание', render: (row) => row.description || '—', className: styles.descriptionCell },
  ];

  const fields = [
    { name: 'situation_id', label: 'Ситуация', type: 'select', options: situationOptions, placeholder: '— Не выбрано' },
    { name: 'description', label: 'Описание причины', maxLength: 255 },
  ];

  if (crud.isLoading) {
    return <div className={styles.loading}><Spinner size="lg" /></div>;
  }

  return (
    <div className={styles.container}>
      <div className={styles.toolbar}>
        <Button variant="primary" onClick={crud.startCreate}>
          Добавить причину
        </Button>
      </div>

      <CrudTable
        columns={columns}
        items={crud.items}
        onEdit={crud.startEdit}
        onDelete={(item) => crud.askDelete(item.id)}
        emptyTitle="Нет причин"
        emptyDescription="Нажмите «Добавить причину» чтобы создать запись"
      />

      <ConfirmDialog
        isOpen={!!crud.deleteConfirm}
        onClose={crud.cancelDelete}
        onConfirm={crud.confirmDelete}
        title="Удалить причину?"
        message="Связанные рекомендации тоже будут удалены. Это действие нельзя отменить."
        confirmText="Удалить"
        tone="danger"
      />

      <CrudFormModal
        isOpen={crud.isModalOpen}
        isCreating={crud.isCreating}
        onClose={crud.closeModal}
        onSubmit={crud.submit}
        isSubmitting={crud.isSubmitting}
        titleCreate="Добавить причину"
        titleEdit="Редактировать причину"
        fields={fields}
        form={crud.form}
        setForm={crud.setForm}
      />
    </div>
  );
}

export default CausesManagement;
