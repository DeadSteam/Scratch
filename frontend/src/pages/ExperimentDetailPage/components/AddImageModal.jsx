import { useState } from 'react';
import PropTypes from 'prop-types';
import { Image as ImageIcon, Images, X } from '@phosphor-icons/react';
import { ph } from '@components/icons/phosphor';
import { Button, Modal, Input } from '@components/common';
import { IMAGE_CONFIG } from '@utils/constants';
import styles from '../ExperimentDetailPage.module.css';

export function AddImageModal({
  isOpen,
  onClose,
  onValidate,
  onSubmit,
  isUploading,
}) {
  const [file, setFile] = useState(null);
  const [passes, setPasses] = useState('');

  const handleFileChange = (e) => {
    const selected = e.target.files?.[0];
    if (!selected) return;
    if (!onValidate(selected)) return;
    setFile(selected);
  };

  const reset = () => {
    setFile(null);
    setPasses('');
  };

  const handleClose = () => {
    reset();
    onClose();
  };

  const handleSubmit = async () => {
    if (!file || !passes) return;
    const ok = await onSubmit(file, passes);
    if (ok) {
      reset();
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Добавить изображение" size="md">
      <div className={styles.modalContent}>
        <div className={styles.uploadArea}>
          <input
            type="file"
            id="addImageUpload"
            accept={IMAGE_CONFIG.ALLOWED_TYPES.join(',')}
            onChange={handleFileChange}
            className={styles.fileInput}
          />

          {file ? (
            <div className={styles.selectedFile}>
              <ImageIcon {...ph(24)} aria-hidden />
              <span>{file.name}</span>
              <button
                type="button"
                onClick={() => setFile(null)}
                className={styles.removeFile}
                aria-label="Убрать файл"
              >
                <X {...ph(20)} weight="bold" aria-hidden />
              </button>
            </div>
          ) : (
            <label htmlFor="addImageUpload" className={styles.uploadLabel}>
              <Images {...ph(32)} aria-hidden />
              <span>Выберите изображение</span>
            </label>
          )}
        </div>

        <Input
          type="number"
          label="Количество проходов"
          placeholder="Например: 5, 10, 15..."
          value={passes}
          onChange={(e) => setPasses(e.target.value)}
          min="1"
        />

        <div className={styles.modalActions}>
          <Button variant="secondary" onClick={handleClose}>Отмена</Button>
          <Button
            variant="primary"
            onClick={handleSubmit}
            loading={isUploading}
            disabled={!file || !passes}
          >
            Добавить
          </Button>
        </div>
      </div>
    </Modal>
  );
}

AddImageModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onValidate: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
  isUploading: PropTypes.bool,
};

export default AddImageModal;
