/**
 * Experiments Page
 * List of user's experiments
 */

import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@context/AuthContext';
import { useNotification } from '@context/NotificationContext';
import { experimentService } from '@api';
import { Layout } from '@components/layout';
import { Button, Card, Spinner, EmptyState, Modal } from '@components/common';
import { ROUTES } from '@utils/constants';
import { formatDate, formatWeight, getScratchQuality, formatScratchIndex } from '@utils/formatters';
import styles from './ExperimentsPage.module.css';

export function ExperimentsPage() {
  const [experiments, setExperiments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deleteConfirm, setDeleteConfirm] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);
  
  const { user } = useAuth();
  const { success, error: showError } = useNotification();
  const navigate = useNavigate();

  const fetchExperiments = useCallback(async () => {
    if (!user?.id) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await experimentService.getByUserId(user.id);
      setExperiments(response.data || []);
    } catch (err) {
      setError(err.message || 'Ошибка загрузки экспериментов');
      showError('Не удалось загрузить эксперименты');
    } finally {
      setIsLoading(false);
    }
  }, [user?.id, showError]);

  useEffect(() => {
    fetchExperiments();
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

  const getLatestScratchIndex = (experiment) => {
    if (!experiment.scratch_results || experiment.scratch_results.length === 0) {
      return null;
    }
    const lastResult = experiment.scratch_results[experiment.scratch_results.length - 1];
    return lastResult?.scratch_index;
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
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
              <path d="M8 2a.75.75 0 01.75.75v4.5h4.5a.75.75 0 010 1.5h-4.5v4.5a.75.75 0 01-1.5 0v-4.5h-4.5a.75.75 0 010-1.5h4.5v-4.5A.75.75 0 018 2z" />
            </svg>
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
                <svg width="48" height="48" viewBox="0 0 48 48" fill="currentColor" className={styles.errorIcon}>
                  <path fillRule="evenodd" d="M24 4C12.954 4 4 12.954 4 24s8.954 20 20 20 20-8.954 20-20S35.046 4 24 4zm-1.5 10a1.5 1.5 0 013 0v12a1.5 1.5 0 01-3 0V14zm1.5 20a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
                </svg>
                <p>{error}</p>
                <Button variant="secondary" onClick={fetchExperiments}>
                  Попробовать снова
                </Button>
              </div>
            </Card>
          </div>
        ) : experiments.length === 0 ? (
          <EmptyState
            icon={
              <svg viewBox="0 0 48 48" fill="none" stroke="currentColor" strokeWidth="1.5">
                <circle cx="24" cy="24" r="20" />
                <path d="M16 20h16M16 28h10M24 14v20" strokeLinecap="round" />
              </svg>
            }
            title="Нет экспериментов"
            description="Создайте свой первый эксперимент для начала анализа"
            action="Создать эксперимент"
            onAction={handleCreateExperiment}
          />
        ) : (
          <div className={styles.grid}>
            {experiments.map((experiment) => {
              const scratchIndex = getLatestScratchIndex(experiment);
              const quality = getScratchQuality(scratchIndex);
              
              return (
                <Card
                  key={experiment.id}
                  variant="default"
                  padding="none"
                  hoverable
                  onClick={() => handleExperimentClick(experiment.id)}
                  className={styles.experimentCard}
                >
                  {/* Card indicator */}
                  <div className={`${styles.cardIndicator} ${styles[quality.color]}`} />
                  
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
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
                        </svg>
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
                        <div className={`${styles.qualityBadge} ${styles[quality.color]}`}>
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
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
                <line x1="10" y1="11" x2="10" y2="17"/>
                <line x1="14" y1="11" x2="14" y2="17"/>
              </svg>
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



