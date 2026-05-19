import PropTypes from 'prop-types';
import { FilmStrip, Gear, Info } from '@phosphor-icons/react';
import { ph } from '@components/icons/phosphor';
import {
  formatScratchDelta,
  formatScratchIndex,
} from '@utils/formatters';
import styles from '../ExperimentDetailPage.module.css';

export function ExperimentInfoCards({
  experiment,
  latestResult,
  knowledgeSummary,
  quality,
  latestImage,
  onOpenRoi,
  onOpenKnowledge,
}) {
  return (
    <div className={styles.infoSection}>
      {/* Row 1: Film and Config info */}
      <div className={styles.infoRow}>
        <div className={styles.infoCard}>
          <div className={styles.infoCardHeader}>
            <div className={styles.infoIcon}><FilmStrip {...ph(20)} aria-hidden /></div>
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
            {experiment.film?.coating_thickness != null && (
              <div className={styles.infoDetailItem}>
                <span className={styles.infoDetailLabel}>Толщина покрытия:</span>
                <span className={styles.infoDetailValue}>
                  {experiment.film.coating_thickness} мкм
                </span>
              </div>
            )}
            {!experiment.film?.coating_name && experiment.film?.coating_thickness == null && (
              <p className={styles.infoCardDesc}>Дополнительная информация отсутствует</p>
            )}
          </div>
        </div>

        <div className={styles.infoCard}>
          <div className={styles.infoCardHeader}>
            <div className={styles.infoIcon}><Gear {...ph(20)} aria-hidden /></div>
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
            {!experiment.config?.head_type && !experiment.config?.description && (
              <p className={styles.infoCardDesc}>Дополнительная информация отсутствует</p>
            )}
          </div>
        </div>
      </div>

      <div className={styles.paramsCard}>
        <h3 className={styles.paramsTitle}>Параметры эксперимента</h3>
        <div className={styles.paramsGrid}>
          <div className={styles.paramItem}>
            <span className={styles.paramLabel}>Вес груза</span>
            <span className={styles.paramValue}>
              {experiment.weight != null ? `${experiment.weight} г` : '—'}
            </span>
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
                onClick={onOpenKnowledge}
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
            onClick={onOpenRoi}
            disabled={!latestImage}
            title={latestImage ? 'Изменить область анализа' : 'Добавьте изображение для выбора области'}
          >
            Изменить
          </button>
        </div>
      </div>
    </div>
  );
}

ExperimentInfoCards.propTypes = {
  experiment: PropTypes.object.isRequired,
  latestResult: PropTypes.object,
  knowledgeSummary: PropTypes.object,
  quality: PropTypes.shape({
    label: PropTypes.string,
    color: PropTypes.string,
  }).isRequired,
  latestImage: PropTypes.object,
  onOpenRoi: PropTypes.func.isRequired,
  onOpenKnowledge: PropTypes.func.isRequired,
};

export default ExperimentInfoCards;
