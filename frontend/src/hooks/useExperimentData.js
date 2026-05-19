import { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { experimentService, imageService, situationService } from '@api';
import { useNotification } from '@context/NotificationContext';
import { ROUTES } from '@utils/constants';

/**
 * Manages experiment + images loading and knowledge situations for ExperimentDetailPage.
 * Extracted from the God Component to follow SRP.
 */
export function useExperimentData(id) {
  const navigate = useNavigate();
  const { error: showError } = useNotification();

  const [experiment, setExperiment] = useState(null);
  const [images, setImages] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [knowledgeSituations, setKnowledgeSituations] = useState(null);

  // Signals that the knowledge modal should auto-open after the next fetch
  const knowledgeModalAutoOpenRef = useRef(false);

  const fetchExperiment = useCallback(async (silent = false) => {
    if (!silent) setIsLoading(true);
    try {
      const [expData, imagesResponse] = await Promise.all([
        experimentService.getById(id),
        imageService.getByExperimentId(id),
      ]);
      setExperiment(expData);
      setImages(imagesResponse.data || []);
      return { shouldOpenKnowledgeModal: knowledgeModalAutoOpenRef.current };
    } catch {
      showError('Ошибка загрузки эксперимента');
      navigate(ROUTES.EXPERIMENTS);
      return { shouldOpenKnowledgeModal: false };
    } finally {
      if (!silent) setIsLoading(false);
    }
  }, [id, navigate, showError]);

  // Initial load
  useEffect(() => {
    fetchExperiment();
  }, [fetchExperiment]);

  // Load knowledge situations once on mount — situationService is a stable singleton import.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await situationService.getAll({ skip: 0, limit: 500 });
        if (!cancelled) setKnowledgeSituations(Array.isArray(res?.data) ? res.data : []);
      } catch {
        if (!cancelled) setKnowledgeSituations([]);
      }
    })();
    return () => { cancelled = true; };
  }, []);

  return {
    experiment,
    setExperiment,
    images,
    setImages,
    isLoading,
    knowledgeSituations,
    knowledgeModalAutoOpenRef,
    fetchExperiment,
  };
}
