/**
 * Scratch Chart Component
 * Line chart showing scratch index progression
 * Using Recharts for better React integration
 */

import { useMemo } from 'react';
import PropTypes from 'prop-types';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import styles from './ScratchChart.module.css';

export function ScratchChart({ data, title = 'Индекс царапины' }) {
  const { chartData, maxValue } = useMemo(() => {
    if (!data || data.length === 0) {
      return { chartData: null, maxValue: 1 };
    }

    const sortedData = [...data].sort((a, b) => a.passes - b.passes);
    
    const mapped = sortedData.map((item) => ({
      passes: item.passes,
      label: item.passes === 0 ? 'Эталон' : `${item.passes} прох.`,
      scratchIndex: item.scratch_index, // raw value 0..1
    }));
    
    // Calculate max value for Y-axis (add 10% padding, but cap at 1.0)
    const maxIndex = Math.max(...mapped.map((item) => item.scratchIndex));
    const maxValue = Math.min(maxIndex * 1.1, 1);
    
    return { chartData: mapped, maxValue };
  }, [data]);

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className={styles.tooltip}>
          <p className={styles.tooltipTitle}>
            {data.passes === 0 ? 'Эталон' : `Проходов: ${data.passes}`}
          </p>
          <p className={styles.tooltipLabel}>
            Индекс: {data.scratchIndex.toFixed(4)}
          </p>
        </div>
      );
    }
    return null;
  };

  if (!chartData || chartData.length === 0) {
    return (
      <div className={styles.empty}>
        <p>Нет данных для отображения</p>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      {title && <h3 className={styles.title}>{title}</h3>}
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={chartData}
          margin={{ top: 5, right: 20, left: 10, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(51, 65, 85, 0.5)" />
          <XAxis
            dataKey="label"
            stroke="#94a3b8"
            style={{ fontFamily: "'Inter', sans-serif", fontSize: '12px' }}
          />
          <YAxis
            stroke="#94a3b8"
            style={{ fontFamily: "'Inter', sans-serif", fontSize: '12px' }}
            domain={[0, maxValue]}
            tickFormatter={(value) => value.toFixed(2)}
          />
          <Tooltip content={<CustomTooltip />} />
          <Line
            type="monotone"
            dataKey="scratchIndex"
            stroke="#00d4ff"
            strokeWidth={2}
            dot={{ 
              r: 6, 
              fill: '#00d4ff',
              stroke: '#0a1628',
              strokeWidth: 2,
            }}
            activeDot={{ 
              r: 8,
              fill: '#00d4ff',
              stroke: '#0a1628',
              strokeWidth: 2,
            }}
            fill="rgba(0, 212, 255, 0.1)"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

ScratchChart.propTypes = {
  data: PropTypes.arrayOf(PropTypes.shape({
    passes: PropTypes.number.isRequired,
    scratch_index: PropTypes.number.isRequired,
  })),
  title: PropTypes.string,
};

export default ScratchChart;
