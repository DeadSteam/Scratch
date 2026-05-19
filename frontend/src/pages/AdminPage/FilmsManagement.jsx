/**
 * Films Management — на абстракциях useCrudResource + CrudTable + CrudFormModal.
 */

import { FilmStrip } from '@phosphor-icons/react';
import { ph } from '@components/icons/phosphor';
import { Button, Spinner, ConfirmDialog, CrudTable, CrudFormModal } from '@components/common';
import { useCrudResource } from '@hooks/useCrudResource';
import { filmService } from '@api';
import { formatThickness } from '@utils/formatters';
import styles from './Management.module.css';

const EMPTY_FORM = { name: '', coating_name: '', coating_thickness: '' };

const FIELDS = [
  { name: 'name', label: 'Название', required: true },
  { name: 'coating_name', label: 'Название покрытия' },
  { name: 'coating_thickness', label: 'Толщина покрытия (мкм)', type: 'number', min: '0', step: '0.1' },
];

export function FilmsManagement() {
  const crud = useCrudResource({
    service: filmService,
    emptyForm: EMPTY_FORM,
    itemToForm: (film) => ({
      name: film.name,
      coating_name: film.coating_name || '',
      coating_thickness: film.coating_thickness ?? '',
    }),
    formToPayload: (form) => ({
      name: form.name,
      coating_name: form.coating_name || null,
      coating_thickness: form.coating_thickness !== '' ? parseFloat(form.coating_thickness) : null,
    }),
    validate: (form) => (!form.name ? 'Введите название' : null),
    messages: {
      loadError: 'Ошибка загрузки типов пленок',
      created: 'Тип пленки создан',
      updated: 'Тип пленки обновлен',
      deleted: 'Тип пленки удален',
    },
  });

  const columns = [
    { header: 'Название', field: 'name' },
    { header: 'Покрытие', render: (item) => item.coating_name || '—' },
    { header: 'Толщина покрытия', render: (item) => formatThickness(item.coating_thickness) },
  ];

  if (crud.isLoading) {
    return <div className={styles.loading}><Spinner size="lg" /></div>;
  }

  return (
    <div className={styles.container}>
      <div className={styles.toolbar}>
        <Button variant="primary" onClick={crud.startCreate}>
          Добавить тип пленки
        </Button>
      </div>

      <CrudTable
        columns={columns}
        items={crud.items}
        onEdit={crud.startEdit}
        onDelete={(item) => crud.askDelete(item.id)}
        emptyIcon={<FilmStrip {...ph(18)} aria-hidden />}
        emptyTitle="Нет типов плёнок"
        emptyDescription="Нажмите «Добавить тип пленки» чтобы создать запись"
      />

      <ConfirmDialog
        isOpen={!!crud.deleteConfirm}
        onClose={crud.cancelDelete}
        onConfirm={crud.confirmDelete}
        title="Удалить тип плёнки?"
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
        titleCreate="Добавить тип пленки"
        titleEdit="Редактировать тип пленки"
        fields={FIELDS}
        form={crud.form}
        setForm={crud.setForm}
      />
    </div>
  );
}

export default FilmsManagement;
