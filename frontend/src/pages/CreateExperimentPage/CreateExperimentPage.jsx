/**
 * Create Experiment Page
 * Multi-step wizard for creating new experiments
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@context/AuthContext';
import { useNotification } from '@context/NotificationContext';
import { experimentService, filmService, configService, imageService, analysisService } from '@api';
import { Layout } from '@components/layout';
import { Button, Input, Select, Checkbox, Card, Spinner } from '@components/common';
import { ROISelector } from '@components/features/ROISelector';
import { validateImageFile } from '@utils/validators';
import { ROUTES, IMAGE_CONFIG, TIMINGS } from '@utils/constants';
import { Check, Images } from '@phosphor-icons/react';
import { ph } from '@components/icons/phosphor';
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
  
  // Form data
  const [films, setFilms] = useState([]);
  const [configs, setConfigs] = useState([]);
  const [formData, setFormData] = useState({
    name: '',
    filmId: '',
    configId: '',
    weight: '',
    hasFabric: false,
  });
  
  // Image data
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [rectCoords, setRectCoords] = useState(null);
  
  // Errors
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
      const isServerDown = err.status === 502 || err.status === 503 || err.status === 504 || !err.status;
      if (!silent) showError('Ошибка загрузки данных');
      if (isServerDown) {
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

  // Handle form input change
  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
    
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: '' }));
    }
  };

  // Handle image file selection
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
    
    // Create preview
    const reader = new FileReader();
    reader.onload = () => {
      setImagePreview(reader.result);
    };
    reader.readAsDataURL(file);
  };

  // Handle ROI selection
  const handleROIChange = useCallback((coords) => {
    setRectCoords(coords);
    if (errors.roi) {
      setErrors((prev) => ({ ...prev, roi: '' }));
    }
  }, [errors.roi]);

  // Validate step
  const validateStep = () => {
    const newErrors = {};
    
    if (currentStep === 1) {
      if (!formData.filmId) newErrors.filmId = 'Выберите тип пленки';
      if (!formData.configId) newErrors.configId = 'Выберите конфигурацию';
      if (!formData.weight || parseFloat(formData.weight) <= 0) {
        newErrors.weight = 'Введите корректный вес';
      }
    }
    
    if (currentStep === 2) {
      if (!imageFile) newErrors.image = 'Загрузите изображение';
    }
    
    if (currentStep === 3) {
      if (!rectCoords) newErrors.roi = 'Выберите область анализа';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle step navigation
  const handleNext = () => {
    if (validateStep()) {
      setCurrentStep((prev) => prev + 1);
    }
  };

  const handleCancel = () => {
    navigate(ROUTES.EXPERIMENTS);
  };

  const handleBack = () => {
    setCurrentStep((prev) => prev - 1);
  };

  // Handle form submission
  const handleSubmit = async () => {
    if (!validateStep()) return;
    
    setIsSubmitting(true);
    
    try {
      // Create experiment
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
      
      // Upload reference image (passes = 0) and analyze it
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

  // Film options for select
  const filmOptions = films.map((film) => ({
    value: film.id,
    label: film.name + (film.coating_name ? ` (${film.coating_name})` : ''),
  }));

  // Config options for select
  const configOptions = configs.map((config) => ({
    value: config.id,
    label: config.name + (config.head_type ? ` - ${config.head_type}` : ''),
  }));

  if (isLoading) {
    return (
      <Layout>
        <div className={styles.loadingContainer}>
          <Spinner size="lg" />
        </div>
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

        {/* Steps indicator */}
        <div className={styles.steps}>
          {STEPS.map((step, index) => (
            <>
              <div
                key={step.id}
                className={`${styles.step} ${currentStep >= step.id ? styles.active : ''} ${currentStep > step.id ? styles.completed : ''}`}
              >
                <div className={styles.stepIndicator}>
                  {currentStep > step.id ? (
                    <Check {...ph(16)} weight="bold" aria-hidden />
                  ) : (
                    step.id
                  )}
                </div>
                <div className={styles.stepText}>
                  <span className={styles.stepTitle}>{step.title}</span>
                </div>
              </div>
              {index < STEPS.length - 1 && <div className={styles.stepLine} key={`line-${step.id}`} />}
            </>
          ))}
        </div>

        {/* Step content */}
        <Card variant="default" padding="lg" className={styles.content}>
          {/* Step 1: Configuration */}
          {currentStep === 1 && (
            <div className={styles.stepContent}>
              <h2 className={styles.stepHeading}>Параметры эксперимента</h2>
              <p className={styles.stepDescription}>
                Выберите тип пленки, конфигурацию оборудования и укажите параметры теста
              </p>
              
              <div className={styles.formGrid}>
                <Input
                  name="name"
                  label="Название эксперимента"
                  placeholder="Введите название"
                  value={formData.name}
                  onChange={handleInputChange}
                  error={errors.name}
                />
                <Select
                  name="filmId"
                  label="Тип пленки"
                  options={filmOptions}
                  value={formData.filmId}
                  onChange={handleInputChange}
                  error={errors.filmId}
                  required
                  placeholder="Выберите тип пленки"
                />
                
                <Select
                  name="configId"
                  label="Конфигурация оборудования"
                  options={configOptions}
                  value={formData.configId}
                  onChange={handleInputChange}
                  error={errors.configId}
                  required
                  placeholder="Выберите конфигурацию"
                />
                
                <Input
                  name="weight"
                  type="number"
                  label="Вес груза (г)"
                  placeholder="Например: 500"
                  value={formData.weight}
                  onChange={handleInputChange}
                  error={errors.weight}
                  required
                  min="0"
                  step="0.1"
                />
                
                <div className={styles.checkboxWrapper}>
                  <Checkbox
                    name="hasFabric"
                    label="Использовать абразивную ткань"
                    checked={formData.hasFabric}
                    onChange={handleInputChange}
                  />
                </div>
              </div>
            </div>
          )}

          {/* Step 2: Image Upload */}
          {currentStep === 2 && (
            <div className={styles.stepContent}>
              <h2 className={styles.stepHeading}>Загрузка эталонного изображения</h2>
              <p className={styles.stepDescription}>
                Загрузите фотографию чистой (незацарапанной) пленки
              </p>
              
              <div className={styles.uploadArea}>
                <input
                  type="file"
                  id="imageUpload"
                  accept={IMAGE_CONFIG.ALLOWED_TYPES.join(',')}
                  onChange={handleImageChange}
                  className={styles.fileInput}
                />
                
                {imagePreview ? (
                  <div className={styles.imagePreview}>
                    <img src={imagePreview} alt="Preview" />
                    <div className={styles.imageOverlay}>
                      <label htmlFor="imageUpload" className={styles.changeButton}>
                        Изменить
                      </label>
                    </div>
                  </div>
                ) : (
                  <label htmlFor="imageUpload" className={styles.uploadLabel}>
                    <Images {...ph(48)} aria-hidden />
                    <span className={styles.uploadText}>
                      Нажмите или перетащите изображение
                    </span>
                    <span className={styles.uploadHint}>
                      JPEG, PNG или WebP до 10 МБ
                    </span>
                  </label>
                )}
                
                {errors.image && (
                  <span className={styles.error}>{errors.image}</span>
                )}
              </div>
            </div>
          )}

          {/* Step 3: ROI Selection */}
          {currentStep === 3 && (
            <div className={styles.stepContent}>
              <h2 className={styles.stepHeading}>Выбор области анализа</h2>
              <p className={styles.stepDescription}>
                Нарисуйте прямоугольник на изображении для определения области анализа
              </p>
              
              {imagePreview && (
                <ROISelector
                  imageSrc={imagePreview}
                  onSelectionChange={handleROIChange}
                  initialSelection={rectCoords ? {
                    x: rectCoords[0],
                    y: rectCoords[1],
                    width: rectCoords[2],
                    height: rectCoords[3],
                  } : null}
                />
              )}
              
              {errors.roi && (
                <span className={styles.error}>{errors.roi}</span>
              )}
            </div>
          )}

          {/* Navigation buttons */}
          <div className={styles.navigation}>
            <div className={styles.navLeft}>
              {currentStep === 1 ? (
                <Button variant="ghost" onClick={handleCancel}>
                  Отмена
                </Button>
              ) : (
                <Button variant="secondary" onClick={handleBack}>
                  Назад
                </Button>
              )}
            </div>
            
            <div className={styles.navRight}>
              {currentStep < STEPS.length ? (
                <Button variant="primary" onClick={handleNext}>
                  Далее
                </Button>
              ) : (
                <Button 
                  variant="primary" 
                  onClick={handleSubmit}
                  loading={isSubmitting}
                >
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



