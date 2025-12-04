/**
 * Configs Management Component
 */

import { useState, useEffect, useCallback } from 'react';
import { useNotification } from '@context/NotificationContext';
import { configService } from '@api';
import { Button, Spinner, Modal, Input } from '@components/common';
import styles from './Management.module.css';

export function ConfigsManagement() {
  const [configs, setConfigs] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedConfig, setSelectedConfig] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [form, setForm] = useState({ name: '', head_type: '', description: '' });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { success, error: showError } = useNotification();

  const fetchConfigs = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await configService.getAll();
      setConfigs(response.data || []);
    } catch (err) {
      showError('Ошибка загрузки конфигураций');
    } finally {
      setIsLoading(false);
    }
  }, [showError]);

  useEffect(() => {
    fetchConfigs();
  }, [fetchConfigs]);

  const handleCreate = () => {
    setSelectedConfig(null);
    setForm({ name: '', head_type: '', description: '' });
    setIsCreating(true);
    setIsModalOpen(true);
  };

  const handleEdit = (config) => {
    setSelectedConfig(config);
    setForm({
      name: config.name,
      head_type: config.head_type || '',
      description: config.description || '',
    });
    setIsCreating(false);
    setIsModalOpen(true);
  };

  const handleSubmit = async () => {
    if (!form.name) {
      showError('Введите название');
      return;
    }

    setIsSubmitting(true);
    try {
      const data = {
        name: form.name,
        head_type: form.head_type || null,
        description: form.description || null,
      };

      if (isCreating) {
        await configService.create(data);
        success('Конфигурация создана');
      } else {
        await configService.update(selectedConfig.id, data);
        success('Конфигурация обновлена');
      }
      setIsModalOpen(false);
      fetchConfigs();
    } catch (err) {
      showError(err.message || 'Ошибка сохранения');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (configId) => {
    if (!window.confirm('Удалить конфигурацию?')) return;
    
    try {
      await configService.delete(configId);
      success('Конфигурация удалена');
      fetchConfigs();
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
          Добавить конфигурацию
        </Button>
      </div>

      <div className={styles.tableWrapper}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>Название</th>
              <th>Тип головки</th>
              <th>Описание</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            {configs.map((config) => (
              <tr key={config.id}>
                <td className={styles.primaryCell}>{config.name}</td>
                <td>{config.head_type || '—'}</td>
                <td className={styles.descriptionCell}>{config.description || '—'}</td>
                <td>
                  <div className={styles.actions}>
                    <Button variant="ghost" size="sm" onClick={() => handleEdit(config)}>
                      Изменить
                    </Button>
                    <Button variant="ghost" size="sm" onClick={() => handleDelete(config.id)}>
                      Удалить
                    </Button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={isCreating ? 'Добавить конфигурацию' : 'Редактировать конфигурацию'}
        size="sm"
      >
        <div className={styles.modalContent}>
          <Input
            label="Название"
            value={form.name}
            onChange={(e) => setForm((prev) => ({ ...prev, name: e.target.value }))}
            required
          />
          <Input
            label="Тип головки"
            value={form.head_type}
            onChange={(e) => setForm((prev) => ({ ...prev, head_type: e.target.value }))}
          />
          <Input
            label="Описание"
            value={form.description}
            onChange={(e) => setForm((prev) => ({ ...prev, description: e.target.value }))}
          />

          <div className={styles.modalActions}>
            <Button variant="secondary" onClick={() => setIsModalOpen(false)}>
              Отмена
            </Button>
            <Button variant="primary" onClick={handleSubmit} loading={isSubmitting}>
              {isCreating ? 'Создать' : 'Сохранить'}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}

export default ConfigsManagement;



