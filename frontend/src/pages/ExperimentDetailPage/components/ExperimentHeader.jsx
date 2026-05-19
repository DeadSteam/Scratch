import { useState } from 'react';
import PropTypes from 'prop-types';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Check, X, PencilSimple, Plus } from '@phosphor-icons/react';
import { ph } from '@components/icons/phosphor';
import { Button, Input } from '@components/common';
import { ROUTES } from '@utils/constants';
import { formatDate } from '@utils/formatters';
import styles from '../ExperimentDetailPage.module.css';

export function ExperimentHeader({
  experiment,
  imagesCount,
  isAnalyzing,
  isUpdatingName,
  onRename,
  onOpenAddImage,
  onRecalculate,
}) {
  const navigate = useNavigate();
  const [isEditing, setIsEditing] = useState(false);
  const [draftName, setDraftName] = useState('');

  const startEditing = () => {
    setDraftName(experiment.name || '');
    setIsEditing(true);
  };

  const confirmEditing = async () => {
    const ok = await onRename(draftName);
    if (ok) setIsEditing(false);
  };

  const cancelEditing = () => {
    setDraftName('');
    setIsEditing(false);
  };

  return (
    <div className={styles.header}>
      <div className={styles.headerInfo}>
        <button className={styles.backButton} onClick={() => navigate(ROUTES.EXPERIMENTS)}>
          <ArrowLeft {...ph(20)} weight="bold" aria-hidden />
          Назад
        </button>

        {isEditing ? (
          <div className={styles.nameEditContainer}>
            <Input
              value={draftName}
              onChange={(e) => setDraftName(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') confirmEditing();
                else if (e.key === 'Escape') cancelEditing();
              }}
              autoFocus
              disabled={isUpdatingName}
              className={styles.nameInput}
              label=""
            />
            <div className={styles.nameEditActions}>
              <button
                className={styles.nameEditButton}
                onClick={confirmEditing}
                disabled={isUpdatingName}
                title="Сохранить"
              >
                <Check {...ph(16)} weight="bold" aria-hidden />
              </button>
              <button
                className={styles.nameEditButton}
                onClick={cancelEditing}
                disabled={isUpdatingName}
                title="Отмена"
              >
                <X {...ph(16)} weight="bold" aria-hidden />
              </button>
            </div>
          </div>
        ) : (
          <div className={styles.titleContainer}>
            <h1 className={styles.title}>
              {experiment.name || experiment.film?.name || 'Эксперимент'}
            </h1>
            <button
              className={styles.editNameButton}
              onClick={startEditing}
              title="Редактировать название"
            >
              <PencilSimple {...ph(16)} aria-hidden />
            </button>
          </div>
        )}

        <span className={styles.experimentDate}>{formatDate(experiment?.date)}</span>
      </div>

      <div className={styles.headerActions}>
        <Button variant="secondary" onClick={onOpenAddImage}>
          <Plus {...ph(16)} weight="bold" aria-hidden />
          Добавить фото
        </Button>
        <Button
          variant="primary"
          onClick={onRecalculate}
          loading={isAnalyzing}
          disabled={imagesCount === 0}
        >
          Пересчитать всё
        </Button>
      </div>
    </div>
  );
}

ExperimentHeader.propTypes = {
  experiment: PropTypes.shape({
    name: PropTypes.string,
    date: PropTypes.string,
    film: PropTypes.shape({ name: PropTypes.string }),
  }).isRequired,
  imagesCount: PropTypes.number.isRequired,
  isAnalyzing: PropTypes.bool,
  isUpdatingName: PropTypes.bool,
  onRename: PropTypes.func.isRequired,
  onOpenAddImage: PropTypes.func.isRequired,
  onRecalculate: PropTypes.func.isRequired,
};

export default ExperimentHeader;
