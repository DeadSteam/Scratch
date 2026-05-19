import PropTypes from 'prop-types';
import { CrudTable } from '@components/common';
import {
  formatScratchIndex,
  getKnowledgeQualityFromDelta,
} from '@utils/formatters';
import styles from '../ExperimentDetailPage.module.css';

export function ExperimentResultsTable({
  results,
  images,
  referenceScratchIndex,
  knowledgeSituations,
}) {
  if (!results || results.length === 0) return null;

  const imageById = new Map(images.map((img) => [img.id, img]));

  const rows = results.map((result) => {
    const passes = result.passes ?? imageById.get(result.image_id)?.passes ?? 0;
    const delta =
      passes > 0 && referenceScratchIndex != null
        ? result.scratch_index - referenceScratchIndex
        : null;
    const badge =
      passes === 0
        ? { label: 'Эталон', color: 'muted' }
        : getKnowledgeQualityFromDelta(delta, knowledgeSituations);
    return {
      id: result.image_id,
      passes,
      scratchIndex: result.scratch_index,
      badge,
    };
  });

  const columns = [
    {
      header: 'Проходов',
      render: (row) => (
        <span className={styles.mono}>{row.passes === 0 ? 'Эталон' : row.passes}</span>
      ),
    },
    {
      header: 'Индекс царапины',
      render: (row) => (
        <span className={styles.mono}>{formatScratchIndex(row.scratchIndex)}</span>
      ),
    },
    {
      header: 'Качество',
      render: (row) => (
        <span className={`${styles.badge} ${styles.resultsQualityBadge} ${styles[row.badge.color]}`}>
          {row.badge.label}
        </span>
      ),
    },
  ];

  return (
    <div className={styles.resultsSection}>
      <div className={styles.resultsCard}>
        <h2 className={styles.sectionTitle}>Результаты анализа</h2>
        <CrudTable
          columns={columns}
          items={rows}
          actions={false}
        />
      </div>
    </div>
  );
}

ExperimentResultsTable.propTypes = {
  results: PropTypes.array,
  images: PropTypes.array.isRequired,
  referenceScratchIndex: PropTypes.number,
  knowledgeSituations: PropTypes.array,
};

export default ExperimentResultsTable;
