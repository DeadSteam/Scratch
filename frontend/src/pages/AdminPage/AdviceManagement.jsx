/**
 * Advice Management (Knowledge Base)
 * CRUD: cause_id (optional), description (max 50)
 */

import { useState, useEffect, useCallback } from 'react';
import { useNotification } from '@context/NotificationContext';
import { adviceService, causeService } from '@api';
import { Button, Spinner, Modal, Input, Select } from '@components/common';
import styles from './Management.module.css';

const EMPTY_OPTION = { value: '', label: '— Не выбрано' };

export function AdviceManagement() {
  const [items, setItems] = useState([]);
  const [causes, setCauses] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selected, setSelected] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [form, setForm] = useState({ cause_id: '', description: '' });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { success, error: showError } = useNotification();

  const causeOptions = [
    EMPTY_OPTION,
    ...causes.map((c) => ({
      value: c.id,
      label: (c.description || '').trim() || c.id,
    })),
  ];

  const fetchCauses = useCallback(async () => {
    try {
      const res = await causeService.getAll();
      setCauses(res.data || []);
    } catch {
      setCauses([]);
    }
  }, []);

  const fetchItems = useCallback(async () => {
    setIsLoading(true);
    try {
      const res = await adviceService.getAll();
      setItems(res.data || []);
    } catch (err) {
      showError('Ошибка загрузки рекомендаций');
    } finally {
      setIsLoading(false);
    }
  }, [showError]);

  useEffect(() => {
    fetchCauses();
  }, [fetchCauses]);

  useEffect(() => {
    fetchItems();
  }, [fetchItems]);

  const handleCreate = () => {
    setSelected(null);
    setForm({ cause_id: '', description: '' });
    setIsCreating(true);
    setIsModalOpen(true);
  };

  const handleEdit = (row) => {
    setSelected(row);
    setForm({
      cause_id: row.cause_id ?? '',
      description: row.description || '',
    });
    setIsCreating(false);
    setIsModalOpen(true);
  };

  const handleSubmit = async () => {
    if ((form.description || '').length > 50) {
      showError('Описание не более 50 символов');
      return;
    }
    setIsSubmitting(true);
    try {
      const data = {
        cause_id: form.cause_id || null,
        description: form.description || null,
      };

      if (isCreating) {
        await adviceService.create(data);
        success('Рекомендация создана');
      } else {
        await adviceService.update(selected.id, data);
        success('Рекомендация обновлена');
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
    if (!window.confirm('Удалить рекомендацию?')) return;
    try {
      await adviceService.delete(id);
      success('Рекомендация удалена');
      fetchItems();
    } catch (err) {
      showError(err.message || 'Ошибка удаления');
    }
  };

  const getCauseLabel = (causeId) => {
    if (!causeId) return '—';
    const c = causes.find((x) => x.id === causeId);
    return c ? (c.description || causeId) : causeId;
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
          Добавить рекомендацию
        </Button>
      </div>

      <div className={styles.tableWrapper}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>Причина</th>
              <th>Рекомендация</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            {items.map((row) => (
              <tr key={row.id}>
                <td className={styles.primaryCell}>{getCauseLabel(row.cause_id)}</td>
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

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={isCreating ? 'Добавить рекомендацию' : 'Редактировать рекомендацию'}
        size="sm"
      >
        <div className={styles.modalContent}>
          <Select
            label="Причина"
            options={causeOptions}
            value={form.cause_id}
            onChange={(e) => setForm((p) => ({ ...p, cause_id: e.target.value }))}
            placeholder="— Не выбрано"
          />
          <Input
            label="Текст рекомендации (до 50 символов)"
            value={form.description}
            onChange={(e) => setForm((p) => ({ ...p, description: e.target.value }))}
            maxLength={50}
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

export default AdviceManagement;
