import { useState, useCallback, useEffect } from 'react';
import { analysisService } from '@api';
import { useNotification } from '@context/NotificationContext';

/**
 * Loads and aggregates histogram data for all images in an experiment.
 * Triggers automatically when chartMode switches to 'histogram'.
 */
export function useHistogramData(images, chartMode) {
  const { error: showError } = useNotification();
  const [histogramData, setHistogramData] = useState([]);
  const [histogramSeries, setHistogramSeries] = useState([]);
  const [isHistogramLoading, setIsHistogramLoading] = useState(false);

  const loadHistograms = useCallback(async () => {
    if (!images || images.length === 0) {
      setHistogramData([]);
      setHistogramSeries([]);
      return;
    }

    setIsHistogramLoading(true);
    try {
      const sorted = [...images].sort((a, b) => a.passes - b.passes);
      const brightnessMap = new Map();
      const seriesMeta = [];

      for (let i = 0; i < sorted.length; i++) {
        const image = sorted[i];
        const key = `img_${i}`;
        seriesMeta.push({ key, label: image.passes === 0 ? 'Эталон' : `${image.passes} проходов` });

        const payload = await analysisService.getImageHistogram(image.id);
        const histogram = payload?.histogram || {};
        const totalPixels = payload?.statistics?.total_pixels || 1;

        for (let q = 0; q <= 255; q++) {
          const count = histogram[q] ?? histogram[String(q)] ?? 0;
          let point = brightnessMap.get(q);
          if (!point) { point = { brightness: q }; brightnessMap.set(q, point); }
          point[key] = totalPixels > 0 ? count / totalPixels : 0;
        }
      }

      setHistogramData(Array.from(brightnessMap.values()).sort((a, b) => a.brightness - b.brightness));
      setHistogramSeries(seriesMeta);
    } catch (err) {
      showError(err.message || 'Ошибка загрузки гистограмм');
    } finally {
      setIsHistogramLoading(false);
    }
  }, [images, showError]);

  useEffect(() => {
    if (chartMode === 'histogram') loadHistograms();
  }, [chartMode, loadHistograms]);

  return { histogramData, histogramSeries, isHistogramLoading };
}
