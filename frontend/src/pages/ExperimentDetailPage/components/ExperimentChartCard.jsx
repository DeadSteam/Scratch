import PropTypes from 'prop-types';
import { ChartLine } from '@phosphor-icons/react';
import { ph } from '@components/icons/phosphor';
import { Spinner } from '@components/common';
import { ScratchChart, HistogramChart } from '@components/features';
import styles from '../ExperimentDetailPage.module.css';

export function ExperimentChartCard({
  chartMode,
  onChartModeChange,
  chartData,
  histogramData,
  histogramSeries,
  isHistogramLoading,
  latestResult,
  quality,
}) {
  return (
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
                className={`${styles.chartToggleButton} ${chartMode === 'index' ? styles.chartToggleButtonActive : ''}`}
                onClick={() => onChartModeChange('index')}
              >
                Индекс
              </button>
              <button
                type="button"
                className={`${styles.chartToggleButton} ${chartMode === 'histogram' ? styles.chartToggleButtonActive : ''}`}
                onClick={() => onChartModeChange('histogram')}
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
  );
}

ExperimentChartCard.propTypes = {
  chartMode: PropTypes.oneOf(['index', 'histogram']).isRequired,
  onChartModeChange: PropTypes.func.isRequired,
  chartData: PropTypes.array.isRequired,
  histogramData: PropTypes.array.isRequired,
  histogramSeries: PropTypes.array.isRequired,
  isHistogramLoading: PropTypes.bool,
  latestResult: PropTypes.object,
  quality: PropTypes.shape({
    label: PropTypes.string,
    color: PropTypes.string,
  }).isRequired,
};

export default ExperimentChartCard;
