import PropTypes from 'prop-types';
import { Images } from '@phosphor-icons/react';
import { ph } from '@components/icons/phosphor';
import { IMAGE_CONFIG } from '@utils/constants';
import styles from '../CreateExperimentPage.module.css';

export function StepImage({ imagePreview, error, onFileSelect }) {
  return (
    <div className={styles.stepContent}>
      <h2 className={styles.stepHeading}>Загрузка эталонного изображения</h2>
      <p className={styles.stepDescription}>
        Загрузите фотографию чистой (незацарапанной) пленки
      </p>

      <div className={styles.uploadArea}>
        <input
          type="file"
          id="imageUpload"
          accept={IMAGE_CONFIG.ALLOWED_TYPES.join(',')}
          onChange={onFileSelect}
          className={styles.fileInput}
        />

        {imagePreview ? (
          <div className={styles.imagePreview}>
            <img src={imagePreview} alt="Preview" />
            <div className={styles.imageOverlay}>
              <label htmlFor="imageUpload" className={styles.changeButton}>
                Изменить
              </label>
            </div>
          </div>
        ) : (
          <label htmlFor="imageUpload" className={styles.uploadLabel}>
            <Images {...ph(48)} aria-hidden />
            <span className={styles.uploadText}>
              Нажмите или перетащите изображение
            </span>
            <span className={styles.uploadHint}>JPEG, PNG или WebP до 10 МБ</span>
          </label>
        )}

        {error && <span className={styles.error}>{error}</span>}
      </div>
    </div>
  );
}

StepImage.propTypes = {
  imagePreview: PropTypes.string,
  error: PropTypes.string,
  onFileSelect: PropTypes.func.isRequired,
};

export default StepImage;
