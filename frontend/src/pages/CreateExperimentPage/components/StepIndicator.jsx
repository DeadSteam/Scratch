import { Fragment } from 'react';
import PropTypes from 'prop-types';
import { Check } from '@phosphor-icons/react';
import { ph } from '@components/icons/phosphor';
import styles from '../CreateExperimentPage.module.css';

export function StepIndicator({ steps, currentStep }) {
  return (
    <div className={styles.steps}>
      {steps.map((step, index) => (
        <Fragment key={step.id}>
          <div
            className={`${styles.step} ${currentStep >= step.id ? styles.active : ''} ${currentStep > step.id ? styles.completed : ''}`}
          >
            <div className={styles.stepIndicator}>
              {currentStep > step.id ? <Check {...ph(16)} weight="bold" aria-hidden /> : step.id}
            </div>
            <div className={styles.stepText}>
              <span className={styles.stepTitle}>{step.title}</span>
            </div>
          </div>
          {index < steps.length - 1 && <div className={styles.stepLine} />}
        </Fragment>
      ))}
    </div>
  );
}

StepIndicator.propTypes = {
  steps: PropTypes.arrayOf(PropTypes.shape({
    id: PropTypes.number.isRequired,
    title: PropTypes.string.isRequired,
  })).isRequired,
  currentStep: PropTypes.number.isRequired,
};

export default StepIndicator;
