/**
 * Create Experiment Page
 *
 * Тонкая страница-визард: оркестрация useState + handlers; каждый шаг рендерится
 * отдельным компонентом из ./components.
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@context/AuthContext';
import { useNotification } from '@context/NotificationContext';
import { experimentService, filmService, configService, imageService, analysisService } from '@api';
import { Layout } from '@components/layout';
import { Button, Card, Spinner } from '@components/common';
import { useForm } from '@hooks/useForm';
import { validateImageFile } from '@utils/validators';
import { isServerDown } from '@utils/httpStatus';
import { ROUTES, TIMINGS } from '@utils/constants';

import { StepIndicator } from './components/StepIndicator';
import { StepConfig } from './components/StepConfig';
import { StepImage } from './components/StepImage';
import { StepROI } from './components/StepROI';

import styles from './CreateExperimentPage.module.css';

const STEPS = [
  { id: 1, title: 'Конфигурация', description: 'Параметры эксперимента' },
  { id: 2, title: 'Изображение', description: 'Загрузка эталонного снимка' },
  { id: 3, title: 'Область', description: 'Выбор области анализа' },
];

export function CreateExperimentPage() {
  const [currentStep, setCurrentStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [films, setFilms] = useState([]);
  const [configs, setConfigs] = useState([]);
  const { values: formData, handleChange: handleFieldChange } = useForm({
    name: '',
    filmId: '',
    configId: '',
    weight: '',
    hasFabric: false,
  });

  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [rectCoords, setRectCoords] = useState(null);

  const [errors, setErrors] = useState({});

  const { user } = useAuth();
  const { success, error: showError } = useNotification();
  const navigate = useNavigate();
  const retryTimerRef = useRef(null);

  const fetchData = useCallback(async ({ silent = false } = {}) => {
    if (!silent) setIsLoading(true);
    try {
      const [filmsResponse, configsResponse] = await Promise.all([
        filmService.getAll(),
        configService.getAll(),
      ]);
      setFilms(filmsResponse.data || []);
      setConfigs(configsResponse.data || []);
      if (retryTimerRef.current) {
        clearTimeout(retryTimerRef.current);
        retryTimerRef.current = null;
      }
    } catch (err) {
      if (!silent) showError('Ошибка загрузки данных');
      if (isServerDown(err)) {
        retryTimerRef.current = setTimeout(() => fetchData({ silent: true }), TIMINGS.RETRY_INTERVAL_MS);
      }
    } finally {
      if (!silent) setIsLoading(false);
    }
  }, [showError]);

  useEffect(() => {
    fetchData();
    return () => {
      if (retryTimerRef.current) clearTimeout(retryTimerRef.current);
    };
  }, [fetchData]);

  const handleInputChange = (e) => {
    handleFieldChange(e);
    const { name } = e.target;
    if (errors[name]) setErrors((prev) => ({ ...prev, [name]: '' }));
  };

  const handleImageChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const validation = validateImageFile(file);
    if (!validation.isValid) {
      setErrors((prev) => ({ ...prev, image: validation.errors[0] }));
      return;
    }

    setImageFile(file);
    setErrors((prev) => ({ ...prev, image: '' }));

    const reader = new FileReader();
    reader.onload = () => setImagePreview(reader.result);
    reader.readAsDataURL(file);
  };

  const handleROIChange = useCallback((coords) => {
    setRectCoords(coords);
    setErrors((prev) => (prev.roi ? { ...prev, roi: '' } : prev));
  }, []);

  const validateStep = () => {
    const newErrors = {};
    if (currentStep === 1) {
      if (!formData.filmId) newErrors.filmId = 'Выберите тип пленки';
      if (!formData.configId) newErrors.configId = 'Выберите конфигурацию';
      if (!formData.weight || parseFloat(formData.weight) <= 0) {
        newErrors.weight = 'Введите корректный вес';
      }
    }
    if (currentStep === 2 && !imageFile) newErrors.image = 'Загрузите изображение';
    if (currentStep === 3 && !rectCoords) newErrors.roi = 'Выберите область анализа';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => { if (validateStep()) setCurrentStep((p) => p + 1); };
  const handleBack = () => setCurrentStep((p) => p - 1);
  const handleCancel = () => navigate(ROUTES.EXPERIMENTS);

  const handleSubmit = async () => {
    if (!validateStep()) return;
    setIsSubmitting(true);
    try {
      const experimentData = {
        name: formData.name || null,
        film_id: formData.filmId,
        config_id: formData.configId,
        user_id: user.id,
        date: new Date().toISOString(),
        weight: parseFloat(formData.weight),
        has_fabric: formData.hasFabric,
        rect_coords: rectCoords,
      };

      const experiment = await experimentService.create(experimentData);

      const refImage = await imageService.upload(imageFile, experiment.id, 0);
      if (refImage?.id) {
        await analysisService.analyzeSingleImage(refImage.id);
      }

      success('Эксперимент успешно создан');
      navigate(ROUTES.EXPERIMENT_DETAIL.replace(':id', experiment.id));
    } catch (err) {
      showError(err.message || 'Ошибка создания эксперимента');
    } finally {
      setIsSubmitting(false);
    }
  };

  const filmOptions = films.map((film) => ({
    value: film.id,
    label: film.name + (film.coating_name ? ` (${film.coating_name})` : ''),
  }));

  const configOptions = configs.map((config) => ({
    value: config.id,
    label: config.name + (config.head_type ? ` - ${config.head_type}` : ''),
  }));

  if (isLoading) {
    return (
      <Layout>
        <div className={styles.loadingContainer}><Spinner size="lg" /></div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className={styles.page}>
        <div className={styles.header}>
          <h1 className={styles.title}>Создать эксперимент</h1>
          <p className={styles.subtitle}>
            Настройте параметры теста на устойчивость к царапинам
          </p>
        </div>

        <StepIndicator steps={STEPS} currentStep={currentStep} />

        <Card variant="default" padding="lg" className={styles.content}>
          {currentStep === 1 && (
            <StepConfig
              formData={formData}
              errors={errors}
              onChange={handleInputChange}
              filmOptions={filmOptions}
              configOptions={configOptions}
            />
          )}
          {currentStep === 2 && (
            <StepImage
              imagePreview={imagePreview}
              error={errors.image}
              onFileSelect={handleImageChange}
            />
          )}
          {currentStep === 3 && (
            <StepROI
              imagePreview={imagePreview}
              rectCoords={rectCoords}
              onROIChange={handleROIChange}
              error={errors.roi}
            />
          )}

          <div className={styles.navigation}>
            <div className={styles.navLeft}>
              {currentStep === 1 ? (
                <Button variant="ghost" onClick={handleCancel}>Отмена</Button>
              ) : (
                <Button variant="secondary" onClick={handleBack}>Назад</Button>
              )}
            </div>

            <div className={styles.navRight}>
              {currentStep < STEPS.length ? (
                <Button variant="primary" onClick={handleNext}>Далее</Button>
              ) : (
                <Button variant="primary" onClick={handleSubmit} loading={isSubmitting}>
                  Создать эксперимент
                </Button>
              )}
            </div>
          </div>
        </Card>
      </div>
    </Layout>
  );
}

export default CreateExperimentPage;
