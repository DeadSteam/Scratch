/**
 * Configs Management — на абстракциях useCrudResource + CrudTable + CrudFormModal.
 */

import { SlidersHorizontal } from '@phosphor-icons/react';
import { ph } from '@components/icons/phosphor';
import { Button, Spinner, ConfirmDialog, CrudTable, CrudFormModal } from '@components/common';
import { useCrudResource } from '@hooks/useCrudResource';
import { configService } from '@api';
import styles from './Management.module.css';

const EMPTY_FORM = { name: '', head_type: '', description: '' };

const FIELDS = [
  { name: 'name', label: 'Название', required: true },
  { name: 'head_type', label: 'Тип головки' },
  { name: 'description', label: 'Описание' },
];

export function ConfigsManagement() {
  const crud = useCrudResource({
    service: configService,
    emptyForm: EMPTY_FORM,
    itemToForm: (config) => ({
      name: config.name,
      head_type: config.head_type || '',
      description: config.description || '',
    }),
    formToPayload: (form) => ({
      name: form.name,
      head_type: form.head_type || null,
      description: form.description || null,
    }),
    validate: (form) => (!form.name ? 'Введите название' : null),
    messages: {
      loadError: 'Ошибка загрузки конфигураций',
      created: 'Конфигурация создана',
      updated: 'Конфигурация обновлена',
      deleted: 'Конфигурация удалена',
    },
  });

  const columns = [
    { header: 'Название', field: 'name' },
    { header: 'Тип головки', render: (item) => item.head_type || '—' },
    { header: 'Описание', render: (item) => item.description || '—', className: styles.descriptionCell },
  ];

  if (crud.isLoading) {
    return <div className={styles.loading}><Spinner size="lg" /></div>;
  }

  return (
    <div className={styles.container}>
      <div className={styles.toolbar}>
        <Button variant="primary" onClick={crud.startCreate}>
          Добавить конфигурацию
        </Button>
      </div>

      <CrudTable
        columns={columns}
        items={crud.items}
        onEdit={crud.startEdit}
        onDelete={(item) => crud.askDelete(item.id)}
        emptyIcon={<SlidersHorizontal {...ph(18)} aria-hidden />}
        emptyTitle="Нет конфигураций"
        emptyDescription="Нажмите «Добавить конфигурацию» чтобы создать запись"
      />

      <ConfirmDialog
        isOpen={!!crud.deleteConfirm}
        onClose={crud.cancelDelete}
        onConfirm={crud.confirmDelete}
        title="Удалить конфигурацию?"
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
        titleCreate="Добавить конфигурацию"
        titleEdit="Редактировать конфигурацию"
        fields={FIELDS}
        form={crud.form}
        setForm={crud.setForm}
      />
    </div>
  );
}

export default ConfigsManagement;
