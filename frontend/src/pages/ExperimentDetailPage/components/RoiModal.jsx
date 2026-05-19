import { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import { Button, Modal } from '@components/common';
import { ROISelector } from '@components/features';
import styles from '../ExperimentDetailPage.module.css';

const coordsToInitial = (coords) =>
  coords ? { x: coords[0], y: coords[1], width: coords[2], height: coords[3] } : null;

export function RoiModal({
  isOpen,
  onClose,
  imageSrc,
  initialCoords,
  onSave,
  isSaving,
  isAnalyzing,
}) {
  const [coords, setCoords] = useState(initialCoords);

  useEffect(() => {
    if (isOpen) setCoords(initialCoords);
  }, [isOpen, initialCoords]);

  const handleSave = async () => {
    const ok = await onSave(coords);
    if (ok) onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Область анализа" size="lg">
      <div className={styles.roiModalContent}>
        {imageSrc ? (
          <ROISelector
            imageSrc={imageSrc}
            onSelectionChange={setCoords}
            initialSelection={coordsToInitial(coords)}
          />
        ) : (
          <div className={styles.emptyChart}>
            <p>Нет изображений для выбора области анализа</p>
          </div>
        )}

        <div className={styles.modalActions}>
          <Button variant="secondary" onClick={onClose}>Отмена</Button>
          <Button
            variant="primary"
            onClick={handleSave}
            loading={isSaving || isAnalyzing}
            disabled={!imageSrc || !coords}
          >
            Сохранить и пересчитать
          </Button>
        </div>
      </div>
    </Modal>
  );
}

RoiModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  imageSrc: PropTypes.string,
  initialCoords: PropTypes.arrayOf(PropTypes.number),
  onSave: PropTypes.func.isRequired,
  isSaving: PropTypes.bool,
  isAnalyzing: PropTypes.bool,
};

export default RoiModal;
