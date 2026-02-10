/**
 * Experiment Detail Page
 * View experiment details, images, and analysis results
 */

import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useNotification } from '@context/NotificationContext';
import { experimentService, imageService, analysisService } from '@api';
import { Layout } from '@components/layout';
import { Button, Spinner, Modal, Input } from '@components/common';
import { ImageCarousel, ScratchChart, HistogramChart, ROISelector } from '@components/features';
import { formatDate, formatWeight, formatScratchIndex, getScratchQuality } from '@utils/formatters';
import { validateImageFile } from '@utils/validators';
import { ROUTES, IMAGE_CONFIG, API_BASE_URL } from '@utils/constants';
import styles from './ExperimentDetailPage.module.css';

export function ExperimentDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { success, error: showError } = useNotification();

  const [experiment, setExperiment] = useState(null);
  const [images, setImages] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [chartMode, setChartMode] = useState('index'); // 'index' | 'histogram'
  const [histogramData, setHistogramData] = useState([]);
  const [histogramSeries, setHistogramSeries] = useState([]);
  const [isHistogramLoading, setIsHistogramLoading] = useState(false);
  
  // Add image modal state
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [newImageFile, setNewImageFile] = useState(null);
  const [newImagePasses, setNewImagePasses] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [isEditingName, setIsEditingName] = useState(false);
  const [editedName, setEditedName] = useState('');
  const [isUpdatingName, setIsUpdatingName] = useState(false);

  // ROI modal (analysis area)
  const [isRoiModalOpen, setIsRoiModalOpen] = useState(false);
  const [roiCoords, setRoiCoords] = useState(null); // [x, y, w, h] | null
  const [isSavingRoi, setIsSavingRoi] = useState(false);

  const latestImage = images.length > 0
    ? [...images].sort((a, b) => (b.passes ?? 0) - (a.passes ?? 0))[0]
    : null;
  const latestImageUrl = latestImage ? `${API_BASE_URL}/images/${latestImage.id}/data` : null;

  // Fetch experiment data.  `silent` skips the full-page spinner so the
  // UI doesn't flash when refreshing after add/delete/recalculate.
  const fetchExperiment = useCallback(async (silent = false) => {
    if (!silent) setIsLoading(true);
    try {
      const [expData, imagesResponse] = await Promise.all([
        experimentService.getById(id),
        imageService.getByExperimentId(id),
      ]);
      setExperiment(expData);
      setImages(imagesResponse.data || []);
    } catch (err) {
      showError('Ошибка загрузки эксперимента');
      navigate(ROUTES.EXPERIMENTS);
    } finally {
      if (!silent) setIsLoading(false);
    }
  }, [id, navigate, showError]);

  useEffect(() => {
    fetchExperiment();
  }, [fetchExperiment]);

  const loadAllHistograms = useCallback(
    async () => {
      if (!images || images.length === 0) {
        setHistogramData([]);
        setHistogramSeries([]);
        return;
      }

      setIsHistogramLoading(true);
      try {
        const sortedImages = [...images].sort((a, b) => a.passes - b.passes);
        const brightnessMap = new Map();
        const seriesMeta = [];

        // Загружаем гистограммы для всех изображений и собираем общие данные
        // Один brightness (0-255) — несколько линий (по одному на изображение)
        // Y = count_q / total_pixels для каждого изображения отдельно
        for (let index = 0; index < sortedImages.length; index += 1) {
          const image = sortedImages[index];
          const seriesKey = `img_${index}`;
          const label = image.passes === 0 ? 'Эталон' : `${image.passes} проходов`;
          seriesMeta.push({ key: seriesKey, label });

          const response = await analysisService.getImageHistogram(image.id);
          const payload = response?.data || response;
          const histogram = payload.histogram || {};
          const totalPixels = payload.statistics?.total_pixels || 1;

          for (let q = 0; q <= 255; q += 1) {
            const count = histogram[q] ?? histogram[String(q)] ?? 0;
            const ratio = totalPixels > 0 ? count / totalPixels : 0;
            let point = brightnessMap.get(q);
            if (!point) {
              point = { brightness: q };
              brightnessMap.set(q, point);
            }
            point[seriesKey] = ratio;
          }
        }

        const combinedData = Array.from(brightnessMap.values()).sort(
          (a, b) => a.brightness - b.brightness,
        );

        setHistogramData(combinedData);
        setHistogramSeries(seriesMeta);
      } catch (err) {
        showError(err.message || 'Ошибка загрузки гистограмм');
      } finally {
        setIsHistogramLoading(false);
      }
    },
    [images, showError],
  );

  const handleChartModeChange = (mode) => {
    setChartMode(mode);
  };

  // При переключении в режим гистограммы загружаем все гистограммы
  useEffect(() => {
    if (chartMode === 'histogram') {
      loadAllHistograms();
    }
  }, [chartMode, loadAllHistograms]);

  // Handle image upload
  const handleImageChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    const validation = validateImageFile(file);
    if (!validation.isValid) {
      showError(validation.errors[0]);
      return;
    }
    
    setNewImageFile(file);
  };

  // Handle name update
  const handleNameUpdate = async () => {
    const trimmedName = editedName.trim();
    if (trimmedName === (experiment.name || '')) {
      setIsEditingName(false);
      return;
    }

    setIsUpdatingName(true);
    try {
      // Send null if empty, otherwise send the trimmed value
      const updateData = trimmedName === '' ? { name: null } : { name: trimmedName };
      await experimentService.update(id, updateData);
      setExperiment((prev) => ({ ...prev, name: trimmedName === '' ? null : trimmedName }));
      success('Название обновлено');
      setIsEditingName(false);
    } catch (err) {
      showError(err.message || 'Ошибка обновления названия');
    } finally {
      setIsUpdatingName(false);
    }
  };

  const handleNameEdit = () => {
    setEditedName(experiment.name || '');
    setIsEditingName(true);
  };

  const handleNameCancel = () => {
    setEditedName('');
    setIsEditingName(false);
  };

  const handleOpenRoiModal = () => {
    if (!latestImageUrl) {
      showError('Нет изображений для выбора области анализа');
      return;
    }
    setRoiCoords(experiment?.rect_coords ? [...experiment.rect_coords] : null);
    setIsRoiModalOpen(true);
  };

  const handleSaveRoi = async () => {
    if (!roiCoords || roiCoords.length !== 4) {
      showError('Выберите область анализа');
      return;
    }

    setIsSavingRoi(true);
    try {
      await experimentService.update(id, { rect_coords: roiCoords });

      setIsAnalyzing(true);
      try {
        await analysisService.recalculateExperiment(id);
        await fetchExperiment(true);
        success('Область обновлена, пересчёт выполнен');
      } finally {
        setIsAnalyzing(false);
      }

      setIsRoiModalOpen(false);
    } catch (err) {
      showError(err.message || 'Ошибка сохранения области анализа');
    } finally {
      setIsSavingRoi(false);
    }
  };

  // Handle image delete + recalculate so chart stays in sync
  const handleImageDelete = async (imageId) => {
    try {
      await imageService.delete(imageId);
      success('Изображение удалено');
      setImages((prev) => prev.filter((img) => img.id !== imageId));

      // Recalculate experiment so scratch_results stays consistent
      try {
        await analysisService.recalculateExperiment(id);
        await fetchExperiment(true);
      } catch {
        // Recalculation is best-effort after delete
      }
    } catch (err) {
      showError(err.message || 'Ошибка удаления изображения');
    }
  };

  const handleAddImage = async () => {
    if (!newImageFile || !newImagePasses) {
      showError('Заполните все поля');
      return;
    }

    const passes = parseInt(newImagePasses, 10);
    if (isNaN(passes) || passes < 1) {
      showError('Введите корректное количество проходов');
      return;
    }

    setIsUploading(true);
    try {
      // Upload and get the new image object (contains id)
      const uploadedImage = await imageService.upload(newImageFile, id, passes);
      success('Изображение добавлено');
      setIsAddModalOpen(false);
      setNewImageFile(null);
      setNewImagePasses('');

      // Incremental analysis: analyze ONLY the newly uploaded image
      if (uploadedImage?.id) {
        setIsAnalyzing(true);
        try {
          await analysisService.analyzeSingleImage(uploadedImage.id);
          success('Анализ нового изображения выполнен');
        } catch (err) {
          console.error('Ошибка автоматического анализа:', err);
        } finally {
          setIsAnalyzing(false);
        }
      }

      // Single silent refresh after everything is done
      await fetchExperiment(true);
    } catch (err) {
      showError(err.message || 'Ошибка загрузки изображения');
    } finally {
      setIsUploading(false);
    }
  };

  // Handle full recalculation of all images
  const handleRunAnalysis = async () => {
    if (images.length === 0) {
      showError('Добавьте хотя бы одно изображение');
      return;
    }

    setIsAnalyzing(true);
    try {
      await analysisService.recalculateExperiment(id);
      success('Пересчёт завершён');
      await fetchExperiment(true);
    } catch (err) {
      showError(err.message || 'Ошибка пересчёта');
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Prepare chart data — passes is now stored in scratch_results directly
  const chartData = experiment?.scratch_results?.map((result) => {
    const image = images.find((img) => img.id === result.image_id);
    return {
      passes: result.passes ?? image?.passes ?? 0,
      scratch_index: result.scratch_index,
    };
  }) || [];

  // Get latest scratch index (highest passes, excluding reference)
  const latestResult = (() => {
    const results = experiment?.scratch_results;
    if (!results || results.length === 0) return null;
    // Find result with highest passes (most damaged image)
    const scratched = results.filter((r) => r.passes > 0);
    if (scratched.length === 0) return results[results.length - 1]; // only reference
    return scratched.reduce((a, b) => (a.passes > b.passes ? a : b));
  })();
  const quality = getScratchQuality(latestResult?.scratch_index);

  if (isLoading) {
    return (
      <Layout>
        <div className={styles.loadingContainer}>
          <Spinner size="lg" />
        </div>
      </Layout>
    );
  }

  if (!experiment) {
    return (
      <Layout>
        <div className={styles.errorContainer}>
          <p>Эксперимент не найден</p>
          <Button variant="secondary" onClick={() => navigate(ROUTES.EXPERIMENTS)}>
            К списку экспериментов
          </Button>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className={styles.page}>
        {/* Header */}
        <div className={styles.header}>
          <div className={styles.headerInfo}>
            <button 
              className={styles.backButton}
              onClick={() => navigate(ROUTES.EXPERIMENTS)}
            >
              <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M17 10a.75.75 0 01-.75.75H5.612l4.158 3.96a.75.75 0 11-1.04 1.08l-5.5-5.25a.75.75 0 010-1.08l5.5-5.25a.75.75 0 111.04 1.08L5.612 9.25H16.25A.75.75 0 0117 10z" clipRule="evenodd" />
              </svg>
              Назад
            </button>
            {isEditingName ? (
              <div className={styles.nameEditContainer}>
                <Input
                  value={editedName}
                  onChange={(e) => setEditedName(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      handleNameUpdate();
                    } else if (e.key === 'Escape') {
                      handleNameCancel();
                    }
                  }}
                  autoFocus
                  disabled={isUpdatingName}
                  className={styles.nameInput}
                  label=""
                />
                <div className={styles.nameEditActions}>
                  <button
                    className={styles.nameEditButton}
                    onClick={handleNameUpdate}
                    disabled={isUpdatingName}
                    title="Сохранить"
                  >
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                      <path d="M13.78 4.22a.75.75 0 010 1.06l-7.25 7.25a.75.75 0 01-1.06 0L2.22 9.28a.75.75 0 011.06-1.06L6 10.94l6.72-6.72a.75.75 0 011.06 0z" />
                    </svg>
                  </button>
                  <button
                    className={styles.nameEditButton}
                    onClick={handleNameCancel}
                    disabled={isUpdatingName}
                    title="Отмена"
                  >
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                      <path d="M2.22 2.22a.75.75 0 011.06 0L8 6.94l4.72-4.72a.75.75 0 111.06 1.06L9.06 8l4.72 4.72a.75.75 0 11-1.06 1.06L8 9.06l-4.72 4.72a.75.75 0 01-1.06-1.06L6.94 8 2.22 3.28a.75.75 0 010-1.06z" />
                    </svg>
                  </button>
                </div>
              </div>
            ) : (
              <div className={styles.titleContainer}>
                <h1 className={styles.title}>
                  {experiment.name || experiment.film?.name || 'Эксперимент'}
                </h1>
                <button
                  className={styles.editNameButton}
                  onClick={handleNameEdit}
                  title="Редактировать название"
                >
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M11.013 1.427a1.75 1.75 0 012.474 0l1.086 1.086a1.75 1.75 0 010 2.474l-8.61 8.61c-.21.21-.47.364-.756.445l-3.251.93a.75.75 0 01-.927-.928l.929-3.25c.081-.286.235-.547.445-.758l8.61-8.61zm1.414 1.06a.25.25 0 00-.354 0L10.811 3.75l1.439 1.44 1.263-1.263a.25.25 0 000-.354l-1.086-1.086zM11.189 6.25L9.75 4.81l-6.286 6.287a.25.25 0 00-.064.108l-.558 1.953 1.953-.558a.249.249 0 00.108-.064l6.286-6.286z" />
                  </svg>
                </button>
              </div>
            )}
            <span className={styles.experimentDate}>{formatDate(experiment?.date)}</span>
          </div>
          <div className={styles.headerActions}>
            <Button 
              variant="secondary" 
              onClick={() => setIsAddModalOpen(true)}
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                <path d="M8 2a.75.75 0 01.75.75v4.5h4.5a.75.75 0 010 1.5h-4.5v4.5a.75.75 0 01-1.5 0v-4.5h-4.5a.75.75 0 010-1.5h4.5v-4.5A.75.75 0 018 2z" />
              </svg>
              Добавить фото
            </Button>
            <Button 
              variant="primary" 
              onClick={handleRunAnalysis}
              loading={isAnalyzing}
              disabled={images.length === 0}
            >
              Пересчитать всё
            </Button>
          </div>
        </div>

        {/* Main Layout: Carousel Left, Info Right */}
        <div className={styles.mainGrid}>
          {/* Left: Photo Carousel */}
          <div className={styles.carouselSection}>
            <div className={styles.carouselCard}>
              <div className={styles.carouselHeader}>
                <h2 className={styles.sectionTitle}>Изображения</h2>
                <span className={styles.imageCount}>{images.length} шт.</span>
              </div>
              <ImageCarousel images={images} onImageDelete={handleImageDelete} onAddImage={() => setIsAddModalOpen(true)} />
            </div>
          </div>

          {/* Right: Info Cards */}
          <div className={styles.infoSection}>
            {/* Row 1: Film and Config info */}
            <div className={styles.infoRow}>
              {/* Film Info Card */}
              <div className={styles.infoCard}>
                <div className={styles.infoCardHeader}>
                  <div className={styles.infoIcon}>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <rect x="3" y="3" width="18" height="18" rx="2"/>
                      <path d="M3 9h18M9 21V9"/>
                    </svg>
                  </div>
                  <span className={styles.infoCardLabel}>Тип плёнки</span>
                </div>
                <h3 className={styles.infoCardTitle}>{experiment.film?.name || '—'}</h3>
                <div className={styles.infoCardDetails}>
                  {experiment.film?.coating_name && (
                    <div className={styles.infoDetailItem}>
                      <span className={styles.infoDetailLabel}>Покрытие:</span>
                      <span className={styles.infoDetailValue}>{experiment.film.coating_name}</span>
                    </div>
                  )}
                  {experiment.film?.coating_thickness !== null && experiment.film?.coating_thickness !== undefined && (
                    <div className={styles.infoDetailItem}>
                      <span className={styles.infoDetailLabel}>Толщина покрытия:</span>
                      <span className={styles.infoDetailValue}>{experiment.film.coating_thickness} мкм</span>
                    </div>
                  )}
                  {(!experiment.film?.coating_name && (experiment.film?.coating_thickness === null || experiment.film?.coating_thickness === undefined)) && (
                    <p className={styles.infoCardDesc}>Дополнительная информация отсутствует</p>
                  )}
                </div>
              </div>

              {/* Config Info Card */}
              <div className={styles.infoCard}>
                <div className={styles.infoCardHeader}>
                  <div className={styles.infoIcon}>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M12 15a3 3 0 100-6 3 3 0 000 6z"/>
                      <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z"/>
                    </svg>
                  </div>
                  <span className={styles.infoCardLabel}>Конфигурация</span>
                </div>
                <h3 className={styles.infoCardTitle}>{experiment.config?.name || '—'}</h3>
                <div className={styles.infoCardDetails}>
                  {experiment.config?.head_type && (
                    <div className={styles.infoDetailItem}>
                      <span className={styles.infoDetailLabel}>Тип головки:</span>
                      <span className={styles.infoDetailValue}>{experiment.config.head_type}</span>
                    </div>
                  )}
                  {experiment.config?.description && (
                    <div className={styles.infoDetailItem}>
                      <span className={styles.infoDetailLabel}>Описание:</span>
                      <span className={styles.infoDetailValue}>{experiment.config.description}</span>
                    </div>
                  )}
                  {(!experiment.config?.head_type && !experiment.config?.description) && (
                    <p className={styles.infoCardDesc}>Дополнительная информация отсутствует</p>
                  )}
                </div>
              </div>
            </div>

            {/* Row 2: Experiment Parameters */}
            <div className={styles.paramsCard}>
              <h3 className={styles.paramsTitle}>Параметры эксперимента</h3>
              <div className={styles.paramsGrid}>
                <div className={styles.paramItem}>
                  <span className={styles.paramLabel}>Вес груза</span>
                  <span className={styles.paramValue}>{formatWeight(experiment.weight)}</span>
                </div>
                <div className={styles.paramItem}>
                  <span className={styles.paramLabel}>Абразивная ткань</span>
                  <span className={`${styles.paramValue} ${experiment.has_fabric ? styles.paramYes : styles.paramNo}`}>
                    {experiment.has_fabric ? 'Используется' : 'Не используется'}
                  </span>
                </div>
                <div className={styles.paramItem}>
                  <span className={styles.paramLabel}>Текущий индекс</span>
                  <span className={`${styles.paramValue} ${styles.paramIndex} ${styles[quality.color]}`}>
                    {latestResult ? formatScratchIndex(latestResult.scratch_index) : '—'}
                  </span>
                </div>
              </div>
            </div>

            {/* Row 3: Analysis area (compact card) */}
            <div className={styles.analysisCard}>
              <div className={styles.analysisRow}>
                <span className={styles.paramLabel}>Область анализа</span>
                <span className={styles.analysisCoords}>
                  {experiment.rect_coords
                    ? `${experiment.rect_coords[0]}, ${experiment.rect_coords[1]}, ${experiment.rect_coords[2]}×${experiment.rect_coords[3]}`
                    : 'Не задана'}
                </span>
                <button
                  type="button"
                  className={styles.analysisButton}
                  onClick={handleOpenRoiModal}
                  disabled={!latestImageUrl}
                  title={latestImageUrl ? 'Изменить область анализа' : 'Добавьте изображение для выбора области'}
                >
                  Изменить
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Chart Section - Full Width */}
        <div className={styles.chartSection}>
          <div className={styles.chartCard}>
            <div className={styles.chartHeader}>
              <h2 className={styles.sectionTitle}>
                {chartMode === 'index' ? 'График индекса царапины' : 'Гистограмма яркости'}
              </h2>
              <div className={styles.chartHeaderRight}>
                <div className={styles.chartToggle}>
                  <button
                    type="button"
                    className={`${styles.chartToggleButton} ${
                      chartMode === 'index' ? styles.chartToggleButtonActive : ''
                    }`}
                    onClick={() => handleChartModeChange('index')}
                  >
                    Индекс
                  </button>
                  <button
                    type="button"
                    className={`${styles.chartToggleButton} ${
                      chartMode === 'histogram' ? styles.chartToggleButtonActive : ''
                    }`}
                    onClick={() => handleChartModeChange('histogram')}
                  >
                    Гистограмма
                  </button>
                </div>
                {quality && latestResult && (
                  <span className={`${styles.qualityBadge} ${styles[quality.color]}`}>
                    {quality.label}
                  </span>
                )}
              </div>
            </div>

            {chartMode === 'index' && chartData.length > 0 && (
              <div key="chart-index" className={styles.chartWrapper}>
                <ScratchChart data={chartData} title="" />
              </div>
            )}

            {chartMode === 'index' && chartData.length === 0 && (
              <div className={styles.emptyChart}>
                <div className={styles.emptyChartIcon}>
                  <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                    <path d="M3 3v18h18" />
                    <path d="M18 17l-5-5-4 4-4-4" />
                  </svg>
                </div>
                <p>Запустите анализ для отображения графика</p>
                <span>Добавьте изображения и они будут проанализированы автоматически</span>
              </div>
            )}

            {chartMode === 'histogram' && (
              <div key="chart-histogram" className={styles.chartWrapper}>
                {histogramData.length > 0 && histogramSeries.length > 0 && (
                  <HistogramChart data={histogramData} series={histogramSeries} title="" />
                )}
                {histogramData.length === 0 || histogramSeries.length === 0 && (
                  <div className={styles.emptyChart}>
                    <p>Нет данных для отображения гистограммы</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Results Table - if available */}
      {experiment.scratch_results && experiment.scratch_results.length > 0 && (
        <div className={styles.resultsSection}>
          <div className={styles.resultsCard}>
            <h2 className={styles.sectionTitle}>Результаты анализа</h2>
            <div className={styles.resultsTable}>
              <div className={styles.tableHeader}>
                <span>Проходов</span>
                <span>Индекс царапины</span>
                <span>Качество</span>
              </div>
              {experiment.scratch_results.map((result) => {
                const image = images.find((img) => img.id === result.image_id);
                const passes = result.passes ?? image?.passes ?? 0;
                const resultQuality = getScratchQuality(result.scratch_index);
                return (
                  <div key={result.image_id} className={styles.tableRow}>
                    <span className={styles.mono}>{passes === 0 ? 'Эталон' : passes}</span>
                    <span className={styles.mono}>
                      {formatScratchIndex(result.scratch_index)}
                    </span>
                    <span className={`${styles.badge} ${styles[resultQuality.color]}`}>
                      {resultQuality.label}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Add image modal */}
      <Modal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        title="Добавить изображение"
        size="md"
      >
        <div className={styles.modalContent}>
          <div className={styles.uploadArea}>
            <input
              type="file"
              id="addImageUpload"
              accept={IMAGE_CONFIG.ALLOWED_TYPES.join(',')}
              onChange={handleImageChange}
              className={styles.fileInput}
            />
            
            {newImageFile ? (
              <div className={styles.selectedFile}>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M5 21q-.825 0-1.413-.587Q3 19.825 3 19V5q0-.825.587-1.413Q4.175 3 5 3h14q.825 0 1.413.587Q21 4.175 21 5v14q0 .825-.587 1.413Q19.825 21 19 21Zm0-2h14V5H5v14Zm1-2h12l-3.75-5-3 4L9 13Z"/>
                </svg>
                <span>{newImageFile.name}</span>
                <button 
                  type="button"
                  onClick={() => setNewImageFile(null)}
                  className={styles.removeFile}
                >
                  &times;
                </button>
              </div>
            ) : (
              <label htmlFor="addImageUpload" className={styles.uploadLabel}>
                <svg width="32" height="32" viewBox="0 0 32 32" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <rect x="4" y="6" width="24" height="20" rx="3" />
                  <circle cx="12" cy="14" r="3" />
                  <path d="M28 20l-6-6-8 8-4-4-6 6" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                <span>Выберите изображение</span>
              </label>
            )}
          </div>

          <Input
            type="number"
            label="Количество проходов"
            placeholder="Например: 5, 10, 15..."
            value={newImagePasses}
            onChange={(e) => setNewImagePasses(e.target.value)}
            min="1"
          />

          <div className={styles.modalActions}>
            <Button 
              variant="secondary" 
              onClick={() => setIsAddModalOpen(false)}
            >
              Отмена
            </Button>
            <Button 
              variant="primary" 
              onClick={handleAddImage}
              loading={isUploading}
              disabled={!newImageFile || !newImagePasses}
            >
              Добавить
            </Button>
          </div>
        </div>
      </Modal>

      {/* ROI modal */}
      <Modal
        isOpen={isRoiModalOpen}
        onClose={() => setIsRoiModalOpen(false)}
        title="Область анализа"
        size="lg"
      >
        <div className={styles.roiModalContent}>
          {latestImageUrl ? (
            <ROISelector
              imageSrc={latestImageUrl}
              onSelectionChange={setRoiCoords}
              initialSelection={roiCoords ? {
                x: roiCoords[0],
                y: roiCoords[1],
                width: roiCoords[2],
                height: roiCoords[3],
              } : null}
            />
          ) : (
            <div className={styles.emptyChart}>
              <p>Нет изображений для выбора области анализа</p>
            </div>
          )}

          <div className={styles.modalActions}>
            <Button variant="secondary" onClick={() => setIsRoiModalOpen(false)}>
              Отмена
            </Button>
            <Button
              variant="primary"
              onClick={handleSaveRoi}
              loading={isSavingRoi || isAnalyzing}
              disabled={!latestImageUrl || !roiCoords}
            >
              Сохранить и пересчитать
            </Button>
          </div>
        </div>
      </Modal>
    </Layout>
  );
}

export default ExperimentDetailPage;
