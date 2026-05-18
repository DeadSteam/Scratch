/**
 * Situations Management (Knowledge Base)
 * CRUD: controlled_param, min_value, max_value, label, severity, description
 */

import { useState, useEffect, useCallback } from 'react';
import { useNotification } from '@context/NotificationContext';
import { situationService } from '@api';
import { ClipboardText } from '@phosphor-icons/react';
import { ph } from '@components/icons/phosphor';
import { Button, Spinner, Modal, Input, Select } from '@components/common';
import styles from './Management.module.css';

/** Отдельное значение, чтобы не конфликтовать с пустым placeholder в Select */
const SEVERITY_UNSET = '__severity_unset__';

const SEVERITY_OPTIONS = [
  { value: SEVERITY_UNSET, label: '— не задано (в UI как muted)' },
  { value: 'success', label: 'success' },
  { value: 'warning', label: 'warning' },
  { value: 'error', label: 'error' },
  { value: 'muted', label: 'muted' },
];

export function SituationsManagement() {
  const [items, setItems] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selected, setSelected] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [form, setForm] = useState({
    controlled_param: '',
    min_value: '',
    max_value: '',
    label: '',
    severity: '',
    description: '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState(null);

  const { success, error: showError } = useNotification();

  const fetchItems = useCallback(async () => {
    setIsLoading(true);
    try {
      const res = await situationService.getAll({ skip: 0, limit: 500 });
      setItems(res.data || []);
    } catch (err) {
      showError('Ошибка загрузки ситуаций');
    } finally {
      setIsLoading(false);
    }
  }, [showError]);

  useEffect(() => {
    fetchItems();
  }, [fetchItems]);

  const handleCreate = () => {
    setSelected(null);
    setForm({
      controlled_param: '',
      min_value: '',
      max_value: '',
      label: '',
      severity: '',
      description: '',
    });
    setIsCreating(true);
    setIsModalOpen(true);
  };

  const handleEdit = (row) => {
    setSelected(row);
    setForm({
      controlled_param: row.controlled_param || '',
      min_value: row.min_value != null ? String(row.min_value) : '',
      max_value: row.max_value != null ? String(row.max_value) : '',
      label: row.label || '',
      severity: row.severity || '',
      description: row.description || '',
    });
    setIsCreating(false);
    setIsModalOpen(true);
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      const minParsed = form.min_value === '' ? null : parseFloat(form.min_value);
      const maxParsed = form.max_value === '' ? null : parseFloat(form.max_value);
      if (minParsed !== null && Number.isNaN(minParsed)) {
        showError('Некорректное минимальное значение');
        return;
      }
      if (maxParsed !== null && Number.isNaN(maxParsed)) {
        showError('Некорректное максимальное значение');
        return;
      }
      const data = {
        controlled_param: form.controlled_param.trim() || null,
        min_value: minParsed,
        max_value: maxParsed,
        label: form.label.trim() === '' ? null : form.label.trim(),
        severity: form.severity === '' ? null : form.severity,
        description: form.description.trim() === '' ? null : form.description.trim(),
      };

      if (isCreating) {
        await situationService.create(data);
        success('Ситуация создана');
      } else {
        await situationService.update(selected.id, data);
        success('Ситуация обновлена');
      }
      setIsModalOpen(false);
      fetchItems();
    } catch (err) {
      showError(err.message || 'Ошибка сохранения');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = (id) => setDeleteConfirm(id);

  const handleConfirmDelete = async () => {
    try {
      await situationService.delete(deleteConfirm);
      success('Ситуация удалена');
      setDeleteConfirm(null);
      fetchItems();
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
      <div className={styles.toolbar}>
        <Button variant="primary" onClick={handleCreate}>
          Добавить ситуацию
        </Button>
      </div>

      <div className={styles.tableWrapper}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>Параметр</th>
              <th>Мин.</th>
              <th>Макс.</th>
              <th>Оценка (label)</th>
              <th>Уровень</th>
              <th>Описание</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            {items.length === 0 ? (
              <tr className={styles.emptyRow}>
                <td colSpan={7}>
                  <div className={styles.emptyStateCell}>
                    <div className={styles.emptyIcon}>
                      <ClipboardText {...ph(18)} aria-hidden />
                    </div>
                    <p className={styles.emptyTitle}>Нет ситуаций</p>
                    <p className={styles.emptyDesc}>Нажмите «Добавить ситуацию» чтобы создать первую запись</p>
                  </div>
                </td>
              </tr>
            ) : items.map((row) => (
              <tr key={row.id}>
                <td className={styles.primaryCell}>{row.controlled_param || '—'}</td>
                <td>{row.min_value != null ? row.min_value : '—'}</td>
                <td>{row.max_value != null ? row.max_value : '—'}</td>
                <td>{row.label || '—'}</td>
                <td>{row.severity || '—'}</td>
                <td className={styles.descriptionCell}>{row.description || '—'}</td>
                <td>
                  <div className={styles.actions}>
                    <Button variant="ghost" size="sm" onClick={() => handleEdit(row)}>Изменить</Button>
                    <Button variant="ghost" size="sm" onClick={() => handleDelete(row.id)}>Удалить</Button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Delete confirmation */}
      <Modal
        isOpen={!!deleteConfirm}
        onClose={() => setDeleteConfirm(null)}
        title="Удалить ситуацию?"
        size="sm"
      >
        <div className={styles.modalContent}>
          <p>Связанные причины и рекомендации тоже будут удалены. Это действие нельзя отменить.</p>
          <div className={styles.modalActions}>
            <Button variant="secondary" onClick={() => setDeleteConfirm(null)}>Отмена</Button>
            <Button variant="danger" onClick={handleConfirmDelete}>Удалить</Button>
          </div>
        </div>
      </Modal>

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={isCreating ? 'Добавить ситуацию' : 'Редактировать ситуацию'}
        size="md"
      >
        <div className={styles.modalContent}>
          <Input
            label="Контролируемый параметр"
            hint="Произвольная метка для справки. Оценка по дельте индексов задаётся только полями мин./макс."
            value={form.controlled_param}
            onChange={(e) => setForm((p) => ({ ...p, controlled_param: e.target.value }))}
            maxLength={100}
          />
          <Input
            label="Минимальное значение"
            type="number"
            value={form.min_value}
            onChange={(e) => setForm((p) => ({ ...p, min_value: e.target.value }))}
            step="any"
          />
          <Input
            label="Максимальное значение"
            type="number"
            value={form.max_value}
            onChange={(e) => setForm((p) => ({ ...p, max_value: e.target.value }))}
            step="any"
          />
          <Input
            label="Краткая оценка для UI (label)"
            value={form.label}
            onChange={(e) => setForm((p) => ({ ...p, label: e.target.value }))}
            maxLength={50}
            hint="Текст в статусе и в таблице «Качество» (например: Хорошо, Средне)"
          />
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
          <Input
            label="Описание ситуации"
            value={form.description}
            onChange={(e) => setForm((p) => ({ ...p, description: e.target.value }))}
            maxLength={255}
          />
          <div className={styles.modalActions}>
            <Button variant="secondary" onClick={() => setIsModalOpen(false)}>Отмена</Button>
            <Button variant="primary" onClick={handleSubmit} loading={isSubmitting}>
              {isCreating ? 'Создать' : 'Сохранить'}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}

export default SituationsManagement;
