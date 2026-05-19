import PropTypes from 'prop-types';
import { ROISelector } from '@components/features/ROISelector';
import styles from '../CreateExperimentPage.module.css';

const coordsToInitial = (coords) =>
  coords ? { x: coords[0], y: coords[1], width: coords[2], height: coords[3] } : null;

export function StepROI({ imagePreview, rectCoords, onROIChange, error }) {
  return (
    <div className={styles.stepContent}>
      <h2 className={styles.stepHeading}>Выбор области анализа</h2>
      <p className={styles.stepDescription}>
        Нарисуйте прямоугольник на изображении для определения области анализа
      </p>

      {imagePreview && (
        <ROISelector
          imageSrc={imagePreview}
          onSelectionChange={onROIChange}
          initialSelection={coordsToInitial(rectCoords)}
        />
      )}

      {error && <span className={styles.error}>{error}</span>}
    </div>
  );
}

StepROI.propTypes = {
  imagePreview: PropTypes.string,
  rectCoords: PropTypes.arrayOf(PropTypes.number),
  onROIChange: PropTypes.func.isRequired,
  error: PropTypes.string,
};

export default StepROI;
