import PropTypes from 'prop-types';
import { Input, Select, Checkbox } from '@components/common';
import styles from '../CreateExperimentPage.module.css';

export function StepConfig({ formData, errors, onChange, filmOptions, configOptions }) {
  return (
    <div className={styles.stepContent}>
      <h2 className={styles.stepHeading}>Параметры эксперимента</h2>
      <p className={styles.stepDescription}>
        Выберите тип пленки, конфигурацию оборудования и укажите параметры теста
      </p>

      <div className={styles.formGrid}>
        <Input
          name="name"
          label="Название эксперимента"
          placeholder="Введите название"
          value={formData.name}
          onChange={onChange}
          error={errors.name}
        />
        <Select
          name="filmId"
          label="Тип пленки"
          options={filmOptions}
          value={formData.filmId}
          onChange={onChange}
          error={errors.filmId}
          required
          placeholder="Выберите тип пленки"
        />
        <Select
          name="configId"
          label="Конфигурация оборудования"
          options={configOptions}
          value={formData.configId}
          onChange={onChange}
          error={errors.configId}
          required
          placeholder="Выберите конфигурацию"
        />
        <Input
          name="weight"
          type="number"
          label="Вес груза (г)"
          placeholder="Например: 500"
          value={formData.weight}
          onChange={onChange}
          error={errors.weight}
          required
          min="0"
          step="0.1"
        />
        <div className={styles.checkboxWrapper}>
          <Checkbox
            name="hasFabric"
            label="Использовать абразивную ткань"
            checked={formData.hasFabric}
            onChange={onChange}
          />
        </div>
      </div>
    </div>
  );
}

StepConfig.propTypes = {
  formData: PropTypes.object.isRequired,
  errors: PropTypes.object.isRequired,
  onChange: PropTypes.func.isRequired,
  filmOptions: PropTypes.array.isRequired,
  configOptions: PropTypes.array.isRequired,
};

export default StepConfig;
