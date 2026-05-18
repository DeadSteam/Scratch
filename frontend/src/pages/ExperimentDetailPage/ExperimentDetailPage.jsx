/**
 * Experiment Detail Page
 * View experiment details, images, and analysis results
 */

import { useState, useCallback, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useNotification } from '@context/NotificationContext';
import { experimentService, imageService, analysisService } from '@api';
import { useExperimentData } from '@hooks/useExperimentData';
import { useHistogramData } from '@hooks/useHistogramData';
import { useAuthenticatedImageUrl } from '@hooks/useAuthenticatedImageUrl';
import { Layout } from '@components/layout';
import { Button, Spinner, Modal, Input } from '@components/common';
import { ImageCarousel, ScratchChart, HistogramChart, ROISelector } from '@components/features';
import {
  formatDate,
  formatWeight,
  formatScratchDelta,
  formatScratchIndex,
  getKnowledgeQuality,
  getKnowledgeQualityFromDelta,
  getReferenceScratchIndex,
} from '@utils/formatters';
import { validateImageFile } from '@utils/validators';
import { ROUTES, IMAGE_CONFIG } from '@utils/constants';
import {
  ArrowLeft,
  Check,
  X,
  PencilSimple,
  FilmStrip,
  Gear,
  Info,
  ChartLine,
  Plus,
  Image as ImageIcon,
  Images,
} from '@phosphor-icons/react';
import { ph } from '@components/icons/phosphor';
import styles from './ExperimentDetailPage.module.css';

export function ExperimentDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { success, error: showError } = useNotification();

  const {
    experiment, setExperiment,
    images, setImages,
    isLoading,
    knowledgeSituations,
    knowledgeModalAutoOpenRef,
    fetchExperiment,
  } = useExperimentData(id);

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [chartMode, setChartMode] = useState('index');
  const { histogramData, histogramSeries, isHistogramLoading } = useHistogramData(images, chartMode);

  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [newImageFile, setNewImageFile] = useState(null);
  const [newImagePasses, setNewImagePasses] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [isEditingName, setIsEditingName] = useState(false);
  const [editedName, setEditedName] = useState('');
  const [isUpdatingName, setIsUpdatingName] = useState(false);
  const [isKnowledgeModalOpen, setIsKnowledgeModalOpen] = useState(false);

  const [isRoiModalOpen, setIsRoiModalOpen] = useState(false);
  const [roiCoords, setRoiCoords] = useState(null);
  const [isSavingRoi, setIsSavingRoi] = useState(false);

  const latestImage = images.length > 0
    ? [...images].sort((a, b) => (b.passes ?? 0) - (a.passes ?? 0))[0]
    : null;
  const { url: latestImageUrl } = useAuthenticatedImageUrl(latestImage?.id);

  const wrappedFetchExperiment = useCallback(async (silent = false) => {
    const { shouldOpenKnowledgeModal } = await fetchExperiment(silent);
    if (shouldOpenKnowledgeModal) {
      setIsKnowledgeModalOpen(true);
      knowledgeModalAutoOpenRef.current = false;
    }
  }, [fetchExperiment, knowledgeModalAutoOpenRef]);

  const handleChartModeChange = (mode) => setChartMode(mode);

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
    if (!latestImage) {
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
        knowledgeModalAutoOpenRef.current = true;
        await analysisService.recalculateExperiment(id);
        await wrappedFetchExperiment(true);
        success('Область обновлена, пересчёт выполнен');
      } finally {
        setIsAnalyzing(false);
      }

      setIsRoiModalOpen(false);
    } catch (err) {
      knowledgeModalAutoOpenRef.current = false;
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
        await wrappedFetchExperiment(true);
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
          knowledgeModalAutoOpenRef.current = true;
          await analysisService.analyzeSingleImage(uploadedImage.id);
          success('Анализ нового изображения выполнен');
        } catch {
          knowledgeModalAutoOpenRef.current = false;
        } finally {
          setIsAnalyzing(false);
        }
      }

      // Single silent refresh after everything is done
      await wrappedFetchExperiment(true);
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
      knowledgeModalAutoOpenRef.current = true;
      await analysisService.recalculateExperiment(id);
      success('Пересчёт завершён');
      await wrappedFetchExperiment(true);
    } catch (err) {
      knowledgeModalAutoOpenRef.current = false;
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
  const knowledgeSummary = experiment?.knowledge_summary || null;
  const quality = getKnowledgeQuality(knowledgeSummary);
  const referenceScratchIndex = useMemo(
    () => (experiment ? getReferenceScratchIndex(experiment) : null),
    [experiment],
  );

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
              <ArrowLeft {...ph(20)} weight="bold" aria-hidden />
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
                    <Check {...ph(16)} weight="bold" aria-hidden />
                  </button>
                  <button
                    className={styles.nameEditButton}
                    onClick={handleNameCancel}
                    disabled={isUpdatingName}
                    title="Отмена"
                  >
                    <X {...ph(16)} weight="bold" aria-hidden />
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
                  <PencilSimple {...ph(16)} aria-hidden />
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
              <Plus {...ph(16)} weight="bold" aria-hidden />
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
                    <FilmStrip {...ph(20)} aria-hidden />
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
                    <Gear {...ph(20)} aria-hidden />
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
                <div className={styles.paramItem}>
                  <span className={styles.paramLabel}>Статус</span>
                  <span className={`${styles.paramValue} ${styles.paramStatusLarge} ${styles[quality.color]}`}>
                    {quality.label}
                  </span>
                </div>
                <div className={styles.paramItem}>
                  <span className={styles.paramLabel}>Дельта к эталону</span>
                  <span className={`${styles.paramValue} ${styles[quality.color]}`}>
                    {formatScratchDelta(knowledgeSummary?.delta)}
                  </span>
                </div>
                <div className={styles.paramItem}>
                  <span className={styles.paramLabel}>Ситуация</span>
                  <div className={styles.situationRow}>
                    <span className={styles.paramValue}>
                      {knowledgeSummary?.situation?.description || 'Не определена'}
                    </span>
                    <button
                      type="button"
                      className={styles.situationKnowledgeIconButton}
                      onClick={() => setIsKnowledgeModalOpen(true)}
                      disabled={!knowledgeSummary}
                      title="База знаний по результату"
                      aria-label="Открыть базу знаний по результату"
                    >
                      <Info {...ph(18)} weight="bold" aria-hidden />
                    </button>
                  </div>
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
                  disabled={!latestImage}
                  title={
                    latestImage
                      ? 'Изменить область анализа'
                      : 'Добавьте изображение для выбора области'
                  }
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
                {latestResult && (
                  <span className={`${styles.qualityBadge} ${styles.qualityBadgeLarge} ${styles[quality.color]}`}>
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
                  <ChartLine {...ph(48)} aria-hidden />
                </div>
                <p>Запустите анализ для отображения графика</p>
                <span>Добавьте изображения и они будут проанализированы автоматически</span>
              </div>
            )}

            {chartMode === 'histogram' && (
              <div key="chart-histogram" className={styles.chartWrapper}>
                {isHistogramLoading && (
                  <div className={styles.emptyChart}>
                    <Spinner size="lg" />
                    <p>Загрузка гистограмм...</p>
                  </div>
                )}
                {!isHistogramLoading && histogramData.length > 0 && histogramSeries.length > 0 && (
                  <HistogramChart data={histogramData} series={histogramSeries} title="" />
                )}
                {!isHistogramLoading && (histogramData.length === 0 || histogramSeries.length === 0) && (
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
                const deltaForRow =
                  passes > 0 &&
                  referenceScratchIndex !== null &&
                  referenceScratchIndex !== undefined
                    ? result.scratch_index - referenceScratchIndex
                    : null;
                const resultBadge =
                  passes === 0
                    ? { label: 'Эталон', color: 'muted' }
                    : getKnowledgeQualityFromDelta(deltaForRow, knowledgeSituations);
                return (
                  <div key={result.image_id} className={styles.tableRow}>
                    <span className={styles.mono}>{passes === 0 ? 'Эталон' : passes}</span>
                    <span className={styles.mono}>
                      {formatScratchIndex(result.scratch_index)}
                    </span>
                    <span className={`${styles.badge} ${styles.resultsQualityBadge} ${styles[resultBadge.color]}`}>
                      {resultBadge.label}
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
                <ImageIcon {...ph(24)} aria-hidden />
                <span>{newImageFile.name}</span>
                <button 
                  type="button"
                  onClick={() => setNewImageFile(null)}
                  className={styles.removeFile}
                  aria-label="Убрать файл"
                >
                  <X {...ph(20)} weight="bold" aria-hidden />
                </button>
              </div>
            ) : (
              <label htmlFor="addImageUpload" className={styles.uploadLabel}>
                <Images {...ph(32)} aria-hidden />
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

      <Modal
        isOpen={isKnowledgeModalOpen}
        onClose={() => setIsKnowledgeModalOpen(false)}
        title="База знаний по результату"
        size="lg"
      >
        <div className={styles.knowledgeModalContent}>
          <div className={styles.knowledgeSummaryCard}>
            <div className={styles.knowledgeSummaryHeader}>
              <span className={styles.knowledgeLabel}>Итоговая оценка</span>
              <span className={`${styles.qualityBadge} ${styles[quality.color]}`}>
                {quality.label}
              </span>
            </div>
            <p className={styles.knowledgeDescription}>
              {knowledgeSummary?.situation?.description || 'Для текущего результата ситуация в базе знаний не найдена.'}
            </p>
            <div className={styles.knowledgeMetrics}>
              <div className={styles.knowledgeMetric}>
                <span className={styles.paramLabel}>Эталон</span>
                <span className={styles.paramValue}>
                  {formatScratchIndex(knowledgeSummary?.reference_result?.scratch_index)}
                </span>
              </div>
              <div className={styles.knowledgeMetric}>
                <span className={styles.paramLabel}>Последний снимок</span>
                <span className={styles.paramValue}>
                  {formatScratchIndex(knowledgeSummary?.latest_result?.scratch_index)}
                </span>
              </div>
              <div className={styles.knowledgeMetric}>
                <span className={styles.paramLabel}>Дельта</span>
                <span className={`${styles.paramValue} ${styles[quality.color]}`}>
                  {formatScratchDelta(knowledgeSummary?.delta)}
                </span>
              </div>
            </div>
          </div>

          {knowledgeSummary?.causes?.length > 0 ? (
            <div className={styles.knowledgeList}>
              {knowledgeSummary.causes.map((cause) => (
                <div key={cause.id} className={styles.knowledgeCauseCard}>
                  <h3 className={styles.knowledgeCauseTitle}>{cause.description}</h3>
                  {cause.advices?.length > 0 ? (
                    <ul className={styles.knowledgeAdviceList}>
                      {cause.advices.map((advice) => (
                        <li key={advice.id} className={styles.knowledgeAdviceItem}>
                          {advice.description}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className={styles.knowledgeEmptyText}>Рекомендации пока не заполнены.</p>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p className={styles.knowledgeEmptyText}>
              Для найденной ситуации причины и рекомендации пока не заполнены.
            </p>
          )}

          <div className={styles.modalActions}>
            <Button variant="primary" onClick={() => setIsKnowledgeModalOpen(false)}>
              Понятно
            </Button>
          </div>
        </div>
      </Modal>
    </Layout>
  );
}

export default ExperimentDetailPage;
