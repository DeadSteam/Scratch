/**
 * useCrudResource — обобщённый hook для CRUD-страниц админки.
 *
 * Скрывает повторяющийся каркас: загрузка списка, состояние модалок
 * создания/редактирования, форма, удаление с подтверждением, нотификации.
 *
 * Параметры:
 *   service          — должен соответствовать BaseApiService (getAll, create, update, delete).
 *   emptyForm        — начальное состояние формы (объект).
 *   itemToForm       — (item) => form  — маппинг записи в состояние формы при «Изменить».
 *   formToPayload    — (form) => payload  — что отправить на сервер.
 *   validate         — (form) => string | null  — клиентская валидация (вернёт сообщение об ошибке).
 *   listParams       — параметры getAll (по умолчанию пусто).
 *   messages         — кастомные тексты ('загрузка', 'создано', 'удалено', ...).
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { useNotification } from '@context/NotificationContext';

const DEFAULT_MESSAGES = {
  loadError: 'Ошибка загрузки',
  created: 'Запись создана',
  updated: 'Запись обновлена',
  deleted: 'Запись удалена',
  saveError: 'Ошибка сохранения',
  deleteError: 'Ошибка удаления',
};

export function useCrudResource({
  service,
  emptyForm = {},
  itemToForm = (item) => ({ ...item }),
  formToPayload = (form) => form,
  validate = () => null,
  listParams,
  messages,
}) {
  const { success, error: showError } = useNotification();

  // Стабилизируем «по ссылке» нестабильные аргументы, чтобы вызывающий компонент
  // мог передавать inline-объекты/функции без бесконечного re-fetch.
  const listParamsRef = useRef(listParams);
  listParamsRef.current = listParams;
  const itemToFormRef = useRef(itemToForm);
  itemToFormRef.current = itemToForm;
  const formToPayloadRef = useRef(formToPayload);
  formToPayloadRef.current = formToPayload;
  const validateRef = useRef(validate);
  validateRef.current = validate;
  const text = { ...DEFAULT_MESSAGES, ...(messages || {}) };
  const textRef = useRef(text);
  textRef.current = text;
  const emptyFormRef = useRef(emptyForm);
  emptyFormRef.current = emptyForm;

  const [items, setItems] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selected, setSelected] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState(null);

  const fetchItems = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await service.getAll(listParamsRef.current);
      setItems(response.data || []);
    } catch {
      showError(textRef.current.loadError);
    } finally {
      setIsLoading(false);
    }
  }, [service, showError]);

  useEffect(() => {
    fetchItems();
  }, [fetchItems]);

  const startCreate = useCallback(() => {
    setSelected(null);
    setForm(emptyFormRef.current);
    setIsCreating(true);
    setIsModalOpen(true);
  }, []);

  const startEdit = useCallback((item) => {
    setSelected(item);
    setForm(itemToFormRef.current(item));
    setIsCreating(false);
    setIsModalOpen(true);
  }, []);

  const closeModal = useCallback(() => setIsModalOpen(false), []);

  const submit = useCallback(async () => {
    const validationError = validateRef.current(form);
    if (validationError) {
      showError(validationError);
      return;
    }
    setIsSubmitting(true);
    try {
      const payload = formToPayloadRef.current(form);
      if (isCreating) {
        await service.create(payload);
        success(textRef.current.created);
      } else {
        await service.update(selected.id, payload);
        success(textRef.current.updated);
      }
      setIsModalOpen(false);
      fetchItems();
    } catch (err) {
      showError(err.message || textRef.current.saveError);
    } finally {
      setIsSubmitting(false);
    }
  }, [form, isCreating, selected, service, success, showError, fetchItems]);

  const askDelete = useCallback((target) => setDeleteConfirm(target), []);
  const cancelDelete = useCallback(() => setDeleteConfirm(null), []);

  const confirmDelete = useCallback(async () => {
    if (!deleteConfirm) return;
    const id = typeof deleteConfirm === 'object' ? deleteConfirm.id : deleteConfirm;
    try {
      await service.delete(id);
      success(textRef.current.deleted);
      setDeleteConfirm(null);
      fetchItems();
    } catch (err) {
      showError(err.message || textRef.current.deleteError);
    }
  }, [deleteConfirm, service, success, showError, fetchItems]);

  return {
    items,
    isLoading,
    refetch: fetchItems,

    // form state
    form,
    setForm,
    isModalOpen,
    isCreating,
    isSubmitting,
    selected,

    // actions
    startCreate,
    startEdit,
    closeModal,
    submit,

    // delete flow
    deleteConfirm,
    askDelete,
    cancelDelete,
    confirmDelete,
  };
}

export default useCrudResource;
