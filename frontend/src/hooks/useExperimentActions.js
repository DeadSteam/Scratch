/**
 * useExperimentActions — действия страницы ExperimentDetailPage:
 * переименование, загрузка/удаление изображений, сохранение ROI, пересчёт.
 *
 * Принимает id и состояние из useExperimentData; возвращает набор готовых
 * handler-функций и связанные с ними флаги isXxx.
 */

import { useCallback, useState } from 'react';
import { experimentService, imageService, analysisService } from '@api';
import { useNotification } from '@context/NotificationContext';
import { validateImageFile } from '@utils/validators';

export function useExperimentActions({
  id,
  experiment,
  setExperiment,
  setImages,
  fetchExperiment,
  knowledgeModalAutoOpenRef,
  onKnowledgeAutoOpen,
}) {
  const { success, error: showError } = useNotification();

  const [isUpdatingName, setIsUpdatingName] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isSavingRoi, setIsSavingRoi] = useState(false);

  const refreshSilently = useCallback(async () => {
    const { shouldOpenKnowledgeModal } = await fetchExperiment(true);
    if (shouldOpenKnowledgeModal) {
      onKnowledgeAutoOpen?.();
      knowledgeModalAutoOpenRef.current = false;
    }
  }, [fetchExperiment, knowledgeModalAutoOpenRef, onKnowledgeAutoOpen]);

  const renameExperiment = useCallback(async (nextName) => {
    const trimmed = (nextName || '').trim();
    if (trimmed === (experiment?.name || '')) return true;
    setIsUpdatingName(true);
    try {
      const payload = trimmed === '' ? { name: null } : { name: trimmed };
      await experimentService.update(id, payload);
      setExperiment((prev) => ({ ...prev, name: trimmed === '' ? null : trimmed }));
      success('Название обновлено');
      return true;
    } catch (err) {
      showError(err.message || 'Ошибка обновления названия');
      return false;
    } finally {
      setIsUpdatingName(false);
    }
  }, [id, experiment?.name, setExperiment, success, showError]);

  const validateImage = useCallback((file) => {
    const validation = validateImageFile(file);
    if (!validation.isValid) {
      showError(validation.errors[0]);
      return false;
    }
    return true;
  }, [showError]);

  const uploadImage = useCallback(async (file, passesRaw) => {
    const passes = parseInt(passesRaw, 10);
    if (Number.isNaN(passes) || passes < 1) {
      showError('Введите корректное количество проходов');
      return false;
    }

    setIsUploading(true);
    try {
      const uploaded = await imageService.upload(file, id, passes);
      success('Изображение добавлено');

      if (uploaded?.id) {
        setIsAnalyzing(true);
        try {
          knowledgeModalAutoOpenRef.current = true;
          await analysisService.analyzeSingleImage(uploaded.id);
          success('Анализ нового изображения выполнен');
        } catch {
          knowledgeModalAutoOpenRef.current = false;
        } finally {
          setIsAnalyzing(false);
        }
      }
      await refreshSilently();
      return true;
    } catch (err) {
      showError(err.message || 'Ошибка загрузки изображения');
      return false;
    } finally {
      setIsUploading(false);
    }
  }, [id, knowledgeModalAutoOpenRef, refreshSilently, success, showError]);

  const deleteImage = useCallback(async (imageId) => {
    try {
      await imageService.delete(imageId);
      success('Изображение удалено');
      setImages((prev) => prev.filter((img) => img.id !== imageId));
      try {
        await analysisService.recalculateExperiment(id);
        await refreshSilently();
      } catch {
        /* recalculation is best-effort after delete */
      }
    } catch (err) {
      showError(err.message || 'Ошибка удаления изображения');
    }
  }, [id, setImages, refreshSilently, success, showError]);

  const saveRoi = useCallback(async (roiCoords) => {
    if (!roiCoords || roiCoords.length !== 4) {
      showError('Выберите область анализа');
      return false;
    }
    setIsSavingRoi(true);
    try {
      await experimentService.update(id, { rect_coords: roiCoords });
      setIsAnalyzing(true);
      try {
        knowledgeModalAutoOpenRef.current = true;
        await analysisService.recalculateExperiment(id);
        await refreshSilently();
        success('Область обновлена, пересчёт выполнен');
      } finally {
        setIsAnalyzing(false);
      }
      return true;
    } catch (err) {
      knowledgeModalAutoOpenRef.current = false;
      showError(err.message || 'Ошибка сохранения области анализа');
      return false;
    } finally {
      setIsSavingRoi(false);
    }
  }, [id, knowledgeModalAutoOpenRef, refreshSilently, success, showError]);

  const recalculateAll = useCallback(async () => {
    setIsAnalyzing(true);
    try {
      knowledgeModalAutoOpenRef.current = true;
      await analysisService.recalculateExperiment(id);
      success('Пересчёт завершён');
      await refreshSilently();
    } catch (err) {
      knowledgeModalAutoOpenRef.current = false;
      showError(err.message || 'Ошибка пересчёта');
    } finally {
      setIsAnalyzing(false);
    }
  }, [id, knowledgeModalAutoOpenRef, refreshSilently, success, showError]);

  return {
    isUpdatingName,
    isUploading,
    isAnalyzing,
    isSavingRoi,
    renameExperiment,
    validateImage,
    uploadImage,
    deleteImage,
    saveRoi,
    recalculateAll,
  };
}

export default useExperimentActions;
