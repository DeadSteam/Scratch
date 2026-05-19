/**
 * Situations Management — на абстракциях useCrudResource + CrudTable + CrudFormModal.
 */

import { ClipboardText } from '@phosphor-icons/react';
import { ph } from '@components/icons/phosphor';
import { Button, Spinner, ConfirmDialog, CrudTable, CrudFormModal, Select } from '@components/common';
import { useCrudResource } from '@hooks/useCrudResource';
import { situationService } from '@api';
import styles from './Management.module.css';

// Отдельное значение, чтобы не конфликтовать с пустым placeholder в Select
const SEVERITY_UNSET = '__severity_unset__';

const SEVERITY_OPTIONS = [
  { value: SEVERITY_UNSET, label: '— не задано (в UI как muted)' },
  { value: 'success', label: 'success' },
  { value: 'warning', label: 'warning' },
  { value: 'error', label: 'error' },
  { value: 'muted', label: 'muted' },
];

const EMPTY_FORM = {
  controlled_param: '',
  min_value: '',
  max_value: '',
  label: '',
  severity: '',
  description: '',
};

const parseNumeric = (v) => (v === '' ? null : parseFloat(v));

const LIST_PARAMS = { skip: 0, limit: 500 };

export function SituationsManagement() {
  const crud = useCrudResource({
    service: situationService,
    emptyForm: EMPTY_FORM,
    listParams: LIST_PARAMS,
    itemToForm: (row) => ({
      controlled_param: row.controlled_param || '',
      min_value: row.min_value != null ? String(row.min_value) : '',
      max_value: row.max_value != null ? String(row.max_value) : '',
      label: row.label || '',
      severity: row.severity || '',
      description: row.description || '',
    }),
    formToPayload: (form) => ({
      controlled_param: form.controlled_param.trim() || null,
      min_value: parseNumeric(form.min_value),
      max_value: parseNumeric(form.max_value),
      label: form.label.trim() === '' ? null : form.label.trim(),
      severity: form.severity === '' ? null : form.severity,
      description: form.description.trim() === '' ? null : form.description.trim(),
    }),
    validate: (form) => {
      const min = parseNumeric(form.min_value);
      const max = parseNumeric(form.max_value);
      if (min !== null && Number.isNaN(min)) return 'Некорректное минимальное значение';
      if (max !== null && Number.isNaN(max)) return 'Некорректное максимальное значение';
      return null;
    },
    messages: {
      loadError: 'Ошибка загрузки ситуаций',
      created: 'Ситуация создана',
      updated: 'Ситуация обновлена',
      deleted: 'Ситуация удалена',
    },
  });

  const columns = [
    { header: 'Параметр', render: (r) => r.controlled_param || '—' },
    { header: 'Мин.', render: (r) => (r.min_value != null ? r.min_value : '—') },
    { header: 'Макс.', render: (r) => (r.max_value != null ? r.max_value : '—') },
    { header: 'Оценка (label)', render: (r) => r.label || '—' },
    { header: 'Уровень', render: (r) => r.severity || '—' },
    { header: 'Описание', render: (r) => r.description || '—', className: styles.descriptionCell },
  ];

  // severity-поле использует UNSET-плейсхолдер вместо пустой строки
  const fields = [
    {
      name: 'controlled_param',
      label: 'Контролируемый параметр',
      hint: 'Произвольная метка для справки. Оценка по дельте индексов задаётся только полями мин./макс.',
      maxLength: 100,
    },
    { name: 'min_value', label: 'Минимальное значение', type: 'number', step: 'any' },
    { name: 'max_value', label: 'Максимальное значение', type: 'number', step: 'any' },
    {
      name: 'label',
      label: 'Краткая оценка для UI (label)',
      maxLength: 50,
      hint: 'Текст в статусе и в таблице «Качество» (например: Хорошо, Средне)',
    },
    {
      name: 'severity',
      render: ({ form, setForm }) => (
        <Select
          label="Уровень серьёзности (severity)"
          hint="Цвет бейджа: success / warning / error / muted"
          options={SEVERITY_OPTIONS}
          value={form.severity ? form.severity : SEVERITY_UNSET}
          onChange={(e) => {
            const v = e.target.value;
            setForm((p) => ({ ...p, severity: v === SEVERITY_UNSET ? '' : v }));
          }}
          placeholder="Выберите уровень"
        />
      ),
    },
    { name: 'description', label: 'Описание ситуации', maxLength: 255 },
  ];

  if (crud.isLoading) {
    return <div className={styles.loading}><Spinner size="lg" /></div>;
  }

  return (
    <div className={styles.container}>
      <div className={styles.toolbar}>
        <Button variant="primary" onClick={crud.startCreate}>
          Добавить ситуацию
        </Button>
      </div>

      <CrudTable
        columns={columns}
        items={crud.items}
        onEdit={crud.startEdit}
        onDelete={(item) => crud.askDelete(item.id)}
        emptyIcon={<ClipboardText {...ph(18)} aria-hidden />}
        emptyTitle="Нет ситуаций"
        emptyDescription="Нажмите «Добавить ситуацию» чтобы создать первую запись"
      />

      <ConfirmDialog
        isOpen={!!crud.deleteConfirm}
        onClose={crud.cancelDelete}
        onConfirm={crud.confirmDelete}
        title="Удалить ситуацию?"
        message="Связанные причины и рекомендации тоже будут удалены. Это действие нельзя отменить."
        confirmText="Удалить"
        tone="danger"
      />

      <CrudFormModal
        isOpen={crud.isModalOpen}
        isCreating={crud.isCreating}
        onClose={crud.closeModal}
        onSubmit={crud.submit}
        isSubmitting={crud.isSubmitting}
        titleCreate="Добавить ситуацию"
        titleEdit="Редактировать ситуацию"
        fields={fields}
        form={crud.form}
        setForm={crud.setForm}
        size="md"
      />
    </div>
  );
}

export default SituationsManagement;
