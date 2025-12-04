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
  if (!data || data.length === 0 || !series || series.length === 0) {
    return (
      <div className={styles.empty}>
        <p>Нет данных для отображения гистограммы</p>
      </div>
    );
  }

  // Автоматический диапазон по X и Y
  const { xMin, xMax, yMax } = useMemo(() => {
    const seriesKeys = series.map((s) => s.key);

    let minB = 255;
    let maxB = 0;
    let maxRatio = 0;

    data.forEach((point) => {
      const hasValue = seriesKeys.some((key) => (point[key] || 0) > 0);
      if (hasValue) {
        if (point.brightness < minB) minB = point.brightness;
        if (point.brightness > maxB) maxB = point.brightness;
      }

      const localMax = Math.max(...seriesKeys.map((key) => point[key] || 0));
      if (localMax > maxRatio) {
        maxRatio = localMax;
      }
    });

    if (minB > maxB) {
      minB = 0;
      maxB = 255;
    }

    const padding = 5;
    const domainMin = Math.max(0, minB - padding);
    const domainMax = Math.min(255, maxB + padding);

    const safeMaxRatio = maxRatio || 0.001;

    return {
      xMin: domainMin,
      xMax: domainMax,
      yMax: safeMaxRatio * 1.1,
    };
  }, [data, series]);

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


