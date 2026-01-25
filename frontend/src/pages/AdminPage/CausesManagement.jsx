/**
 * Causes Management (Knowledge Base)
 * CRUD: situation_id (optional), description
 */

import { useState, useEffect, useCallback } from 'react';
import { useNotification } from '@context/NotificationContext';
import { causeService, situationService } from '@api';
import { Button, Spinner, Modal, Input, Select } from '@components/common';
import styles from './Management.module.css';

const EMPTY_OPTION = { value: '', label: '— Не выбрано' };

export function CausesManagement() {
  const [items, setItems] = useState([]);
  const [situations, setSituations] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selected, setSelected] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [form, setForm] = useState({ situation_id: '', description: '' });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { success, error: showError } = useNotification();

  const situationOptions = [
    EMPTY_OPTION,
    ...situations.map((s) => ({
      value: s.situation_id,
      label: [s.controlled_param, s.description].filter(Boolean).join(' — ') || s.situation_id,
    })),
  ];

  const fetchSituations = useCallback(async () => {
    try {
      const res = await situationService.getAll();
      setSituations(res.data || []);
    } catch {
      setSituations([]);
    }
  }, []);

  const fetchItems = useCallback(async () => {
    setIsLoading(true);
    try {
      const res = await causeService.getAll();
      setItems(res.data || []);
    } catch (err) {
      showError('Ошибка загрузки причин');
    } finally {
      setIsLoading(false);
    }
  }, [showError]);

  useEffect(() => {
    fetchSituations();
  }, [fetchSituations]);

  useEffect(() => {
    fetchItems();
  }, [fetchItems]);

  const handleCreate = () => {
    setSelected(null);
    setForm({ situation_id: '', description: '' });
    setIsCreating(true);
    setIsModalOpen(true);
  };

  const handleEdit = (row) => {
    setSelected(row);
    setForm({
      situation_id: row.situation_id ?? '',
      description: row.description || '',
    });
    setIsCreating(false);
    setIsModalOpen(true);
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      const data = {
        situation_id: form.situation_id || null,
        description: form.description || null,
      };

      if (isCreating) {
        await causeService.create(data);
        success('Причина создана');
      } else {
        await causeService.update(selected.cause_id, data);
        success('Причина обновлена');
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
    if (!window.confirm('Удалить причину? Связанные рекомендации тоже будут удалены.')) return;
    try {
      await causeService.delete(id);
      success('Причина удалена');
      fetchItems();
    } catch (err) {
      showError(err.message || 'Ошибка удаления');
    }
  };

  const getSituationLabel = (situationId) => {
    if (!situationId) return '—';
    const s = situations.find((x) => x.situation_id === situationId);
    if (!s) return situationId;
    return [s.controlled_param, s.description].filter(Boolean).join(' — ') || situationId;
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
          Добавить причину
        </Button>
      </div>

      <div className={styles.tableWrapper}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>Ситуация</th>
              <th>Описание</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            {items.map((row) => (
              <tr key={row.cause_id}>
                <td className={styles.primaryCell}>{getSituationLabel(row.situation_id)}</td>
                <td className={styles.descriptionCell}>{row.description || '—'}</td>
                <td>
                  <div className={styles.actions}>
                    <Button variant="ghost" size="sm" onClick={() => handleEdit(row)}>Изменить</Button>
                    <Button variant="ghost" size="sm" onClick={() => handleDelete(row.cause_id)}>Удалить</Button>
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
        title={isCreating ? 'Добавить причину' : 'Редактировать причину'}
        size="sm"
      >
        <div className={styles.modalContent}>
          <Select
            label="Ситуация"
            options={situationOptions}
            value={form.situation_id}
            onChange={(e) => setForm((p) => ({ ...p, situation_id: e.target.value }))}
            placeholder="— Не выбрано"
          />
          <Input
            label="Описание причины"
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

export default CausesManagement;
