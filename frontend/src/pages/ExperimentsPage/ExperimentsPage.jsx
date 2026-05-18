/**
 * Experiments Page
 * List of user's experiments
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@context/AuthContext';
import { useNotification } from '@context/NotificationContext';
import { experimentService } from '@api';
import { Layout } from '@components/layout';
import { Button, Card, Spinner, EmptyState, Modal } from '@components/common';
import { ROUTES } from '@utils/constants';
import {
  formatDate,
  formatWeight,
  getScratchQuality,
  formatScratchIndex,
  getKnowledgeQuality,
} from '@utils/formatters';
import {
  Plus,
  WarningCircle,
  Flask,
  Trash,
} from '@phosphor-icons/react';
import { ph } from '@components/icons/phosphor';
import styles from './ExperimentsPage.module.css';

export function ExperimentsPage() {
  const [experiments, setExperiments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deleteConfirm, setDeleteConfirm] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const retryTimerRef = useRef(null);

  const { user } = useAuth();
  const { success, error: showError } = useNotification();
  const navigate = useNavigate();

  const fetchExperiments = useCallback(async ({ silent = false } = {}) => {
    if (!user?.id) return;

    if (!silent) setIsLoading(true);
    setError(null);

    try {
      const response = await experimentService.getByUserId(user.id);
      setExperiments(response.data || []);
      // Clear any pending retry on success
      if (retryTimerRef.current) {
        clearTimeout(retryTimerRef.current);
        retryTimerRef.current = null;
      }
    } catch (err) {
      const isServerDown = err.status === 502 || err.status === 503 || err.status === 504 || !err.status;
      setError(err.message || 'Ошибка загрузки экспериментов');
      if (!silent) showError('Не удалось загрузить эксперименты');
      // Auto-retry every 5s while server is unavailable
      if (isServerDown) {
        retryTimerRef.current = setTimeout(() => fetchExperiments({ silent: true }), 5000);
      }
    } finally {
      setIsLoading(false);
    }
  }, [user?.id, showError]);

  useEffect(() => {
    fetchExperiments();
    return () => {
      if (retryTimerRef.current) clearTimeout(retryTimerRef.current);
    };
  }, [fetchExperiments]);

  const handleCreateExperiment = () => {
    navigate(ROUTES.EXPERIMENT_NEW);
  };

  const handleExperimentClick = (id) => {
    navigate(`/experiments/${id}`);
  };

  const handleDeleteClick = (e, experimentId) => {
    e.stopPropagation(); // Prevent card click
    setDeleteConfirm(experimentId);
  };

  const handleConfirmDelete = async () => {
    if (!deleteConfirm) return;
    
    setIsDeleting(true);
    try {
      await experimentService.delete(deleteConfirm);
      success('Эксперимент удален');
      setExperiments((prev) => prev.filter((exp) => exp.id !== deleteConfirm));
      setDeleteConfirm(null);
    } catch (err) {
      showError(err.message || 'Ошибка удаления эксперимента');
    } finally {
      setIsDeleting(false);
    }
  };

  const handleCancelDelete = () => {
    setDeleteConfirm(null);
  };

  const getLatestScratchResult = (experiment) => {
    const results = experiment.scratch_results;
    if (!results || results.length === 0) return null;
    const scratched = results.filter((r) => (r.passes ?? 0) > 0);
    if (scratched.length === 0) return results[results.length - 1];
    return scratched.reduce((a, b) => ((a.passes ?? 0) > (b.passes ?? 0) ? a : b));
  };

  return (
    <Layout>
      <div className={styles.page}>
        {/* Page header */}
        <div className={styles.header}>
          <div>
            <h1 className={styles.title}>Мои эксперименты</h1>
            <p className={styles.subtitle}>
              Управляйте вашими исследованиями устойчивости к царапинам
            </p>
          </div>
          <Button variant="primary" onClick={handleCreateExperiment}>
            <Plus {...ph(16)} weight="bold" aria-hidden />
            Новый эксперимент
          </Button>
        </div>

        {/* Content */}
        {isLoading ? (
          <div className={styles.loadingContainer}>
            <Spinner size="lg" />
          </div>
        ) : error ? (
          <div className={styles.errorContainer}>
            <Card variant="outlined" padding="lg">
              <div className={styles.errorContent}>
                <WarningCircle className={styles.errorIcon} {...ph(48, { weight: 'fill' })} aria-hidden />
                <p>{error}</p>
                <Button variant="secondary" onClick={() => fetchExperiments()}>
                  Попробовать снова
                </Button>
              </div>
            </Card>
          </div>
        ) : experiments.length === 0 ? (
          <EmptyState
            icon={<Flask {...ph(48)} aria-hidden />}
            title="Нет экспериментов"
            description="Создайте свой первый эксперимент для начала анализа"
            action="Создать эксперимент"
            onAction={handleCreateExperiment}
          />
        ) : (
          <div className={styles.grid}>
            {experiments.map((experiment) => {
              const latestResult = getLatestScratchResult(experiment);
              const scratchIndex = latestResult?.scratch_index ?? null;
              const ks = experiment.knowledge_summary;
              const quality = ks?.situation
                ? getKnowledgeQuality(ks)
                : getScratchQuality(scratchIndex);
              
              return (
                <Card
                  key={experiment.id}
                  variant="default"
                  padding="none"
                  hoverable
                  onClick={() => handleExperimentClick(experiment.id)}
                  className={styles.experimentCard}
                >
                  
                  <div className={styles.cardContent}>
                    {/* Row 1: Name + delete button + date */}
                    <div className={styles.cardHeader}>
                      <h3 className={styles.filmName}>
                        {experiment.name || experiment.film?.name || 'Без названия'}
                      </h3>
                      <button
                        className={styles.deleteButton}
                        onClick={(e) => handleDeleteClick(e, experiment.id)}
                        aria-label="Удалить эксперимент"
                        title="Удалить эксперимент"
                      >
                        <Trash {...ph(16)} aria-hidden />
                      </button>
                      <span className={styles.date}>{formatDate(experiment.date)}</span>
                    </div>

                    {/* Row 2: Film coating info */}
                    {experiment.film?.coating_name && (
                      <div className={styles.filmRow}>
                        <span className={styles.filmTag}>
                          Покрытие: {experiment.film.coating_name}
                        </span>
                        {experiment.film.coating_thickness && (
                          <span className={styles.filmTag}>
                            Толщина: {experiment.film.coating_thickness} мкм
                          </span>
                        )}
                      </div>
                    )}
                    
                    {/* Row 3: Stats + badge */}
                    <div className={styles.stats}>
                      <div className={styles.stat}>
                        <span className={styles.statLabel}>Вес</span>
                        <span className={styles.statValue}>
                          {formatWeight(experiment.weight)}
                        </span>
                      </div>
                      <div className={styles.stat}>
                        <span className={styles.statLabel}>Абразив</span>
                        <span className={styles.statValue}>
                          {experiment.has_fabric ? 'Да' : 'Нет'}
                        </span>
                      </div>
                      <div className={styles.stat}>
                        <span className={styles.statLabel}>Индекс</span>
                        <span className={`${styles.statValue} ${styles[quality.color]}`}>
                          {scratchIndex !== null 
                            ? formatScratchIndex(scratchIndex)
                            : '—'}
                        </span>
                      </div>
                      {scratchIndex !== null && (
                        <div className={`${styles.qualityBadge} ${styles.qualityBadgeLarge} ${styles[quality.color]}`}>
                          {quality.label}
                        </div>
                      )}
                    </div>
                  </div>
                </Card>
              );
            })}
          </div>
        )}

        {/* Delete confirmation modal */}
        <Modal
          isOpen={!!deleteConfirm}
          onClose={handleCancelDelete}
          title="Удалить эксперимент?"
          size="sm"
        >
          <div className={styles.deleteModalContent}>
            <div className={styles.deleteIcon}>
              <Trash {...ph(48)} aria-hidden />
            </div>
            <p className={styles.deleteMessage}>
              Это действие нельзя отменить. Все данные эксперимента будут удалены безвозвратно.
            </p>
            <div className={styles.deleteActions}>
              <Button 
                variant="secondary" 
                onClick={handleCancelDelete}
                disabled={isDeleting}
              >
                Отмена
              </Button>
              <Button 
                variant="danger" 
                onClick={handleConfirmDelete}
                loading={isDeleting}
              >
                Удалить
              </Button>
            </div>
          </div>
        </Modal>
      </div>
    </Layout>
  );
}

export default ExperimentsPage;



