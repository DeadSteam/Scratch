/**
 * Histogram Chart Component
 * Показывает гистограмму яркости: X = 0..255, Y = доля пикселей этого уровня (0..1)
 */

import PropTypes from 'prop-types';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { useMemo } from 'react';
import styles from './HistogramChart.module.css';

// Цвета для разных изображений
const SERIES_COLORS = [
  '#22c55e',
  '#0ea5e9',
  '#f97316',
  '#a855f7',
  '#e11d48',
  '#14b8a6',
  '#facc15',
  '#6366f1',
];

export function HistogramChart({ data, series, title = 'Гистограмма яркости' }) {
  // Рассчитываем полезный диапазон по X и Y на основе реальных данных
  const { xMin, xMax, yMax, hasData } = useMemo(() => {
    if (!data || data.length === 0 || !series || series.length === 0) {
      return {
        xMin: 0,
        xMax: 255,
        yMax: 1,
        hasData: false,
      };
    }

    const seriesKeys = series.map((s) => s.key);

    let localXMin = 255;
    let localXMax = 0;
    let maxRatioLocal = 0;

    data.forEach((d) => {
      const hasValue = seriesKeys.some((key) => (d[key] || 0) > 0);
      const localMaxForPoint = Math.max(...seriesKeys.map((key) => d[key] || 0));

      if (hasValue) {
        if (d.brightness < localXMin) localXMin = d.brightness;
        if (d.brightness > localXMax) localXMax = d.brightness;
      }

      if (localMaxForPoint > maxRatioLocal) {
        maxRatioLocal = localMaxForPoint;
      }
    });

    // Если все значения нули — используем полный диапазон
    let xDomainMin = localXMin;
    let xDomainMax = localXMax;
    if (localXMin > localXMax) {
      xDomainMin = 0;
      xDomainMax = 255;
    }
    
    const maxRatioSafe = maxRatioLocal || 1;

    return {
      xMin: xDomainMin,
      xMax: xDomainMax,
      yMax: maxRatioSafe,
      hasData: true,
    };
  }, [data, series]);

  if (!hasData) {
    return (
      <div className={styles.empty}>
        <p>Нет данных для отображения гистограммы</p>
      </div>
    );
  }

  const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload || payload.length === 0) return null;

    const d = payload[0].payload;
    return (
      <div className={styles.tooltip}>
        <p className={styles.tooltipTitle}>Яркость: {d.brightness}</p>
        {series.map((s, index) => {
          const value = d[s.key] ?? 0;
          if (!value) return null;
          return (
            <p
              key={s.key}
              className={styles.tooltipValue}
              style={{ color: SERIES_COLORS[index % SERIES_COLORS.length] }}
            >
              {s.label}: {value.toFixed(4)}
            </p>
          );
        })}
      </div>
    );
  };

  return (
    <div className={styles.container}>
      {title && <h3 className={styles.title}>{title}</h3>}
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={data}
          margin={{ top: 5, right: 20, left: 10, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(51, 65, 85, 0.5)" />
          <XAxis
            dataKey="brightness"
            stroke="#94a3b8"
            tickCount={8}
            domain={[xMin, xMax]}
            type="number"
            allowDecimals={false}
            style={{ fontFamily: "'Inter', sans-serif", fontSize: '12px' }}
          />
          <YAxis
            stroke="#94a3b8"
            domain={[0, yMax]}
            tickFormatter={(value) => value.toFixed(3)}
            style={{ fontFamily: "'Inter', sans-serif", fontSize: '12px' }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          {series.map((s, index) => (
            <Line
              key={s.key}
              type="monotone"
              dataKey={s.key}
              name={s.label}
              stroke={SERIES_COLORS[index % SERIES_COLORS.length]}
              strokeWidth={2}
              dot={false}
              isAnimationActive={false}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

HistogramChart.propTypes = {
  data: PropTypes.arrayOf(
    PropTypes.shape({
      brightness: PropTypes.number.isRequired,
    }),
  ),
  series: PropTypes.arrayOf(
    PropTypes.shape({
      key: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
    }),
  ),
  title: PropTypes.string,
};

export default HistogramChart;


