/**
 * Experiment Detail Page
 *
 * Тонкая страница-оркестратор: всё состояние данных эксперимента — в useExperimentData,
 * действия (rename / upload / delete / saveRoi / recalc) — в useExperimentActions,
 * UI разнесён по components/*.
 */

import { useState, useCallback, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useExperimentData } from '@hooks/useExperimentData';
import { useHistogramData } from '@hooks/useHistogramData';
import { useExperimentActions } from '@hooks/useExperimentActions';
import { useAuthenticatedImageUrl } from '@hooks/useAuthenticatedImageUrl';
import { useNotification } from '@context/NotificationContext';
import { experimentService } from '@api';
import { Layout } from '@components/layout';
import { Button, Spinner } from '@components/common';
import { ImageCarousel } from '@components/features';
import {
  getKnowledgeQuality,
  getLatestScratchResult,
  getReferenceScratchIndex,
  sortByPasses,
} from '@utils/formatters';
import { ROUTES } from '@utils/constants';

import { ExperimentHeader } from './components/ExperimentHeader';
import { ExperimentInfoCards } from './components/ExperimentInfoCards';
import { ExperimentChartCard } from './components/ExperimentChartCard';
import { ExperimentResultsTable } from './components/ExperimentResultsTable';
import { AddImageModal } from './components/AddImageModal';
import { RoiModal } from './components/RoiModal';
import { KnowledgeModal } from './components/KnowledgeModal';

import styles from './ExperimentDetailPage.module.css';

export function ExperimentDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const {
    experiment, setExperiment,
    images, setImages,
    isLoading,
    knowledgeSituations,
    knowledgeModalAutoOpenRef,
    fetchExperiment,
  } = useExperimentData(id);

  const [chartMode, setChartMode] = useState('index');
  const { histogramData, histogramSeries, isHistogramLoading } = useHistogramData(images, chartMode);

  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isRoiModalOpen, setIsRoiModalOpen] = useState(false);
  const [isKnowledgeModalOpen, setIsKnowledgeModalOpen] = useState(false);
  const [isReportLoading, setIsReportLoading] = useState(false);

  const { success: notifySuccess, error: notifyError } = useNotification();

  const openKnowledge = useCallback(() => setIsKnowledgeModalOpen(true), []);

  const downloadReport = useCallback(async () => {
    setIsReportLoading(true);
    try {
      const blob = await experimentService.downloadReport(id);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      const name = experiment?.name || experiment?.film?.name || id;
      link.download = `report-${name}.xlsx`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      notifySuccess('Отчёт сформирован');
    } catch (err) {
      notifyError(err.message || 'Не удалось сформировать отчёт');
    } finally {
      setIsReportLoading(false);
    }
  }, [id, experiment, notifySuccess, notifyError]);

  const actions = useExperimentActions({
    id,
    experiment,
    setExperiment,
    setImages,
    fetchExperiment,
    knowledgeModalAutoOpenRef,
    onKnowledgeAutoOpen: openKnowledge,
  });

  const latestImage = useMemo(() => {
    if (images.length === 0) return null;
    const sorted = sortByPasses(images);
    return sorted[sorted.length - 1];
  }, [images]);
  const { url: latestImageUrl } = useAuthenticatedImageUrl(latestImage?.id);

  const chartData = useMemo(() => {
    if (!experiment?.scratch_results) return [];
    const imageById = new Map(images.map((img) => [img.id, img]));
    return experiment.scratch_results.map((result) => ({
      passes: result.passes ?? imageById.get(result.image_id)?.passes ?? 0,
      scratch_index: result.scratch_index,
    }));
  }, [experiment?.scratch_results, images]);

  const latestResult = useMemo(() => getLatestScratchResult(experiment), [experiment]);
  const knowledgeSummary = experiment?.knowledge_summary || null;
  const quality = getKnowledgeQuality(knowledgeSummary);
  const referenceScratchIndex = useMemo(
    () => (experiment ? getReferenceScratchIndex(experiment) : null),
    [experiment],
  );

  const initialRoiCoords = useMemo(
    () => (experiment?.rect_coords ? [...experiment.rect_coords] : null),
    [experiment?.rect_coords],
  );

  if (isLoading) {
    return (
      <Layout>
        <div className={styles.loadingContainer}><Spinner size="lg" /></div>
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
        <ExperimentHeader
          experiment={experiment}
          imagesCount={images.length}
          isAnalyzing={actions.isAnalyzing}
          isUpdatingName={actions.isUpdatingName}
          onRename={actions.renameExperiment}
          onOpenAddImage={() => setIsAddModalOpen(true)}
          onRecalculate={actions.recalculateAll}
          onDownloadReport={downloadReport}
          isReportLoading={isReportLoading}
        />

        <div className={styles.mainGrid}>
          <div className={styles.carouselSection}>
            <div className={styles.carouselCard}>
              <div className={styles.carouselHeader}>
                <h2 className={styles.sectionTitle}>Изображения</h2>
                <span className={styles.imageCount}>{images.length} шт.</span>
              </div>
              <ImageCarousel
                images={images}
                onImageDelete={actions.deleteImage}
                onAddImage={() => setIsAddModalOpen(true)}
              />
            </div>
          </div>

          <ExperimentInfoCards
            experiment={experiment}
            latestResult={latestResult}
            knowledgeSummary={knowledgeSummary}
            quality={quality}
            latestImage={latestImage}
            onOpenRoi={() => setIsRoiModalOpen(true)}
            onOpenKnowledge={openKnowledge}
          />
        </div>

        <ExperimentChartCard
          chartMode={chartMode}
          onChartModeChange={setChartMode}
          chartData={chartData}
          histogramData={histogramData}
          histogramSeries={histogramSeries}
          isHistogramLoading={isHistogramLoading}
          latestResult={latestResult}
          quality={quality}
        />
      </div>

      <ExperimentResultsTable
        results={experiment.scratch_results}
        images={images}
        referenceScratchIndex={referenceScratchIndex}
        knowledgeSituations={knowledgeSituations}
      />

      <AddImageModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        onValidate={actions.validateImage}
        onSubmit={async (file, passes) => {
          const ok = await actions.uploadImage(file, passes);
          if (ok) setIsAddModalOpen(false);
          return ok;
        }}
        isUploading={actions.isUploading}
      />

      <RoiModal
        isOpen={isRoiModalOpen}
        onClose={() => setIsRoiModalOpen(false)}
        imageSrc={latestImageUrl}
        initialCoords={initialRoiCoords}
        onSave={actions.saveRoi}
        isSaving={actions.isSavingRoi}
        isAnalyzing={actions.isAnalyzing}
      />

      <KnowledgeModal
        isOpen={isKnowledgeModalOpen}
        onClose={() => setIsKnowledgeModalOpen(false)}
        knowledgeSummary={knowledgeSummary}
        quality={quality}
      />
    </Layout>
  );
}

export default ExperimentDetailPage;
