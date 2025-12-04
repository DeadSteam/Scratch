# Image Analysis Service - Scratch Resistance Calculation

## Overview
Сервис для анализа стойкости полимерных пленок к царапинам на основе компьютерной обработки фотоизображений.

## Научная основа

### Принцип работы
Исследование стойкости пленки к царапинам проводится на основе разницы яркостей между пленкой без царапин и пленкой с царапинами, рассчитываемой в результате компьютерной обработки фотоизображения.

### Алгоритм анализа

#### 1. Преобразование в Grayscale
```
Grayscale(i,j) = 0.3 * R(i,j) + 0.59 * G(i,j) + 0.11 * B(i,j)
```
где:
- R – яркость красного цвета
- G – яркость зеленого цвета  
- B – яркость синего цвета
- N, M – длина и ширина заданного участка изображения в пикселях

#### 2. Построение гистограммы
Для каждого изображения строится гистограмма распределения яркости пикселей.

#### 3. Определение средней яркости
```
h(q)_cp = P_qmax / P
```
где:
- P_qmax – число пикселей, имеющих преобладающую яркость q
- P – общее число пикселей на изображении

#### 4. Расчет индекса зацарапанности
Используется метод линейной свертки критериев:
```
U(X) = Σ(w_i * x_i)
```
где:
- w_i – вес (важность) i-го критерия
- x_i – оценка альтернативы по i-му критерию

Критерием является совокупность пикселей одного оттенка. Важность критерия определяется тем выше, чем оттенок ближе к белому цвету (коэффициент отражения света).

## API Usage

### Базовый анализ стойкости к царапинам

```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/v1/analysis/scratch-resistance",
        json={
            "experiment_id": "uuid-of-experiment",
            "reference_image_id": "uuid-of-reference-image",
            "scratched_image_ids": [
                "uuid-of-scratched-image-1",
                "uuid-of-scratched-image-2",
                "uuid-of-scratched-image-3"
            ]
        }
    )
    
    result = response.json()
    print(f"Average scratch index: {result['data']['summary']['average_scratch_index']}")
```

### Response Structure

```json
{
  "success": true,
  "message": "Scratch resistance analysis completed successfully",
  "data": {
    "experiment_id": "uuid",
    "reference_image": {
      "image_id": "uuid",
      "analysis": {
        "grayscale_shape": [1080, 1920],
        "dominant_brightness": 128,
        "average_brightness_ratio": 0.15,
        "weighted_average_brightness": 132.5,
        "total_pixels": 2073600,
        "brightness_levels_count": 256
      }
    },
    "scratched_images": [
      {
        "image_id": "uuid",
        "passes": 5,
        "analysis": { /* ... */ },
        "scratch_index": 0.0342,
        "brightness_difference": 12.5
      }
    ],
    "summary": {
      "average_scratch_index": 0.0342,
      "max_scratch_index": 0.0450,
      "min_scratch_index": 0.0234,
      "num_scratched_images": 3
    }
  }
}
```

## Interpretation of Results

### Scratch Index
- **Диапазон**: 0.0 - 1.0
- **Меньше = лучше**: Низкий индекс означает высокую стойкость к царапинам
- **Больше = хуже**: Высокий индекс означает низкую стойкость

### Brightness Difference
Разница в средней яркости между эталоном и поцарапанным образцом:
- **Малая разница** (< 10) - незначительные царапины
- **Средняя разница** (10-30) - заметные царапины
- **Большая разница** (> 30) - сильные повреждения

## Advanced Usage

### Get Histogram for Single Image

```http
GET /api/v1/analysis/histogram/{image_id}
```

Response:
```json
{
  "success": true,
  "data": {
    "image_id": "uuid",
    "histogram": {
      "0": 150,
      "1": 320,
      "128": 45000,
      "255": 200
    },
    "statistics": {
      "dominant_brightness": 128,
      "average_brightness_ratio": 0.15,
      "weighted_average_brightness": 132.5,
      "total_pixels": 2073600
    }
  }
}
```

### Quick Analysis of All Experiment Images

```http
GET /api/v1/analysis/experiment/{experiment_id}/quick-analysis
```

Returns basic statistics for all images without full analysis.

## Service Methods

### `convert_to_grayscale(image_array)`
Converts RGB image to grayscale using the scientific formula.

### `calculate_histogram(grayscale_image)`
Calculates brightness distribution histogram.

### `calculate_average_brightness(histogram)`
Determines dominant brightness level and ratio.

### `calculate_scratch_index(reference_histogram, scratched_histogram)`
Calculates scratch index using linear convolution method.

### `analyze_experiment_images(experiment_id, reference_image_id, scratched_image_ids)`
Full analysis pipeline for experiment.

## Dependencies

```python
numpy>=1.26.2      # Numerical operations
Pillow>=10.1.0     # Image loading and conversion
```

## Data Storage

Analysis results are automatically saved to `experiments.analysis_results` JSON field:

```json
{
  "experiment_id": "uuid",
  "reference_image": { /* ... */ },
  "scratched_images": [ /* ... */ ],
  "summary": {
    "average_scratch_index": 0.0342,
    "max_scratch_index": 0.0450,
    "min_scratch_index": 0.0234
  }
}
```

## Example Workflow

1. **Upload images**:
   ```http
   POST /api/v1/images/upload
   ```

2. **Run analysis**:
   ```http
   POST /api/v1/analysis/scratch-resistance
   ```

3. **Get experiment with results**:
   ```http
   GET /api/v1/experiments/{id}
   ```
   Results are in `analysis_results` field.

4. **Query experiments by scratch index**:
   Filter experiments based on saved analysis results.

## Best Practices

1. **Image Quality**: Use high-resolution images (min 1920x1080)
2. **Lighting**: Ensure consistent lighting between reference and scratched images
3. **Multiple Passes**: Analyze images with different scratch passes (1, 3, 5, 10)
4. **Reference Image**: Always use clean, unscratched sample as reference
5. **ROI**: Use `rect_coords` in experiment to define Region of Interest

## Error Handling

```python
try:
    result = await analysis_service.analyze_experiment_images(...)
except NotFoundError:
    # Image or experiment not found
except ValidationError:
    # Invalid image format or data
```

## Performance Considerations

- Image processing is CPU-intensive
- Large images (> 4K) may take 2-5 seconds per image
- Consider using async processing for batch analysis
- Results are cached in experiment for quick retrieval

## Future Enhancements

- [ ] Multi-threaded image processing
- [ ] GPU acceleration with CUDA
- [ ] Machine learning-based scratch detection
- [ ] Automated ROI detection
- [ ] Export to PDF reports with charts





















