/**
 * Situations Management (Knowledge Base)
 * CRUD: controlled_param, min_value, max_value, description
 */

import { useState, useEffect, useCallback } from 'react';
import { useNotification } from '@context/NotificationContext';
import { situationService } from '@api';
import { Button, Spinner, Modal, Input } from '@components/common';
import styles from './Management.module.css';

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
    description: '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { success, error: showError } = useNotification();

  const fetchItems = useCallback(async () => {
    setIsLoading(true);
    try {
      const res = await situationService.getAll();
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
    setForm({ controlled_param: '', min_value: '', max_value: '', description: '' });
    setIsCreating(true);
    setIsModalOpen(true);
  };

  const handleEdit = (row) => {
    setSelected(row);
    setForm({
      controlled_param: row.controlled_param || '',
      min_value: row.min_value != null ? String(row.min_value) : '',
      max_value: row.max_value != null ? String(row.max_value) : '',
      description: row.description || '',
    });
    setIsCreating(false);
    setIsModalOpen(true);
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      const data = {
        controlled_param: form.controlled_param || null,
        min_value: form.min_value === '' ? null : parseFloat(form.min_value),
        max_value: form.max_value === '' ? null : parseFloat(form.max_value),
        description: form.description || null,
      };

      if (isCreating) {
        await situationService.create(data);
        success('Ситуация создана');
      } else {
        await situationService.update(selected.situation_id, data);
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

  const handleDelete = async (id) => {
    if (!window.confirm('Удалить ситуацию? Связанные причины и рекомендации тоже будут удалены.')) return;
    try {
      await situationService.delete(id);
      success('Ситуация удалена');
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
              <th>Контролируемый параметр</th>
              <th>Мин.</th>
              <th>Макс.</th>
              <th>Описание</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            {items.map((row) => (
              <tr key={row.situation_id}>
                <td className={styles.primaryCell}>{row.controlled_param || '—'}</td>
                <td>{row.min_value != null ? row.min_value : '—'}</td>
                <td>{row.max_value != null ? row.max_value : '—'}</td>
                <td className={styles.descriptionCell}>{row.description || '—'}</td>
                <td>
                  <div className={styles.actions}>
                    <Button variant="ghost" size="sm" onClick={() => handleEdit(row)}>Изменить</Button>
                    <Button variant="ghost" size="sm" onClick={() => handleDelete(row.situation_id)}>Удалить</Button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={isCreating ? 'Добавить ситуацию' : 'Редактировать ситуацию'}
        size="sm"
      >
        <div className={styles.modalContent}>
          <Input
            label="Контролируемый параметр"
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
            label="Описание"
            value={form.description}
            onChange={(e) => setForm((p) => ({ ...p, description: e.target.value }))}
            maxLength={100}
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
