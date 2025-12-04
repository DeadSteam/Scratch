/**
 * Films Management Component
 */

import { useState, useEffect, useCallback } from 'react';
import { useNotification } from '@context/NotificationContext';
import { filmService } from '@api';
import { Button, Spinner, Modal, Input } from '@components/common';
import { formatThickness } from '@utils/formatters';
import styles from './Management.module.css';

export function FilmsManagement() {
  const [films, setFilms] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedFilm, setSelectedFilm] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [form, setForm] = useState({ name: '', coating_name: '', coating_thickness: '' });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { success, error: showError } = useNotification();

  const fetchFilms = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await filmService.getAll();
      setFilms(response.data || []);
    } catch (err) {
      showError('Ошибка загрузки типов пленок');
    } finally {
      setIsLoading(false);
    }
  }, [showError]);

  useEffect(() => {
    fetchFilms();
  }, [fetchFilms]);

  const handleCreate = () => {
    setSelectedFilm(null);
    setForm({ name: '', coating_name: '', coating_thickness: '' });
    setIsCreating(true);
    setIsModalOpen(true);
  };

  const handleEdit = (film) => {
    setSelectedFilm(film);
    setForm({
      name: film.name,
      coating_name: film.coating_name || '',
      coating_thickness: film.coating_thickness || '',
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
        coating_name: form.coating_name || null,
        coating_thickness: form.coating_thickness ? parseFloat(form.coating_thickness) : null,
      };

      if (isCreating) {
        await filmService.create(data);
        success('Тип пленки создан');
      } else {
        await filmService.update(selectedFilm.id, data);
        success('Тип пленки обновлен');
      }
      setIsModalOpen(false);
      fetchFilms();
    } catch (err) {
      showError(err.message || 'Ошибка сохранения');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (filmId) => {
    if (!window.confirm('Удалить тип пленки?')) return;
    
    try {
      await filmService.delete(filmId);
      success('Тип пленки удален');
      fetchFilms();
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
          Добавить тип пленки
        </Button>
      </div>

      <div className={styles.tableWrapper}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>Название</th>
              <th>Покрытие</th>
              <th>Толщина покрытия</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            {films.map((film) => (
              <tr key={film.id}>
                <td className={styles.primaryCell}>{film.name}</td>
                <td>{film.coating_name || '—'}</td>
                <td>{formatThickness(film.coating_thickness)}</td>
                <td>
                  <div className={styles.actions}>
                    <Button variant="ghost" size="sm" onClick={() => handleEdit(film)}>
                      Изменить
                    </Button>
                    <Button variant="ghost" size="sm" onClick={() => handleDelete(film.id)}>
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
        title={isCreating ? 'Добавить тип пленки' : 'Редактировать тип пленки'}
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
            label="Название покрытия"
            value={form.coating_name}
            onChange={(e) => setForm((prev) => ({ ...prev, coating_name: e.target.value }))}
          />
          <Input
            label="Толщина покрытия (мкм)"
            type="number"
            value={form.coating_thickness}
            onChange={(e) => setForm((prev) => ({ ...prev, coating_thickness: e.target.value }))}
            min="0"
            step="0.1"
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

export default FilmsManagement;



