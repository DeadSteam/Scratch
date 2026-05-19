import PropTypes from 'prop-types';
import { Button, Modal } from '@components/common';
import { formatScratchDelta, formatScratchIndex } from '@utils/formatters';
import styles from '../ExperimentDetailPage.module.css';

export function KnowledgeModal({ isOpen, onClose, knowledgeSummary, quality }) {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title="База знаний по результату" size="lg">
      <div className={styles.knowledgeModalContent}>
        <div className={styles.knowledgeSummaryCard}>
          <div className={styles.knowledgeSummaryHeader}>
            <span className={styles.knowledgeLabel}>Итоговая оценка</span>
            <span className={`${styles.qualityBadge} ${styles[quality.color]}`}>
              {quality.label}
            </span>
          </div>
          <p className={styles.knowledgeDescription}>
            {knowledgeSummary?.situation?.description
              || 'Для текущего результата ситуация в базе знаний не найдена.'}
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
                  <p className={styles.knowledgeEmptyText}>
                    Рекомендации пока не заполнены.
                  </p>
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
          <Button variant="primary" onClick={onClose}>Понятно</Button>
        </div>
      </div>
    </Modal>
  );
}

KnowledgeModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  knowledgeSummary: PropTypes.object,
  quality: PropTypes.shape({
    label: PropTypes.string,
    color: PropTypes.string,
  }).isRequired,
};

export default KnowledgeModal;
