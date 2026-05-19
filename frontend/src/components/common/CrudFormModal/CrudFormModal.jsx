/**
 * CrudFormModal — модалка create/edit с полями, описанными декларативно.
 *
 * Поддерживает поля типа input, number, select. Кастомные виджеты — через field.render.
 */

import PropTypes from 'prop-types';
import { Modal } from '../Modal/Modal';
import { Button } from '../Button/Button';
import { Input } from '../Input/Input';
import { Select } from '../Select/Select';
import styles from './CrudFormModal.module.css';

export function CrudFormModal({
  isOpen,
  isCreating,
  onClose,
  onSubmit,
  isSubmitting,
  titleCreate,
  titleEdit,
  fields,
  form,
  setForm,
  size = 'sm',
}) {
  const handleField = (name, value) => setForm((prev) => ({ ...prev, [name]: value }));

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isCreating ? titleCreate : titleEdit}
      size={size}
    >
      <div className={styles.modalContent}>
        {fields.map((field) => {
          if (field.render) {
            return (
              <div key={field.name}>
                {field.render({ value: form[field.name], onChange: (v) => handleField(field.name, v), form, setForm })}
              </div>
            );
          }

          const commonProps = {
            label: field.label,
            value: form[field.name] ?? '',
            required: field.required,
            hint: field.hint,
            disabled: field.disabled,
          };

          if (field.type === 'select') {
            return (
              <Select
                key={field.name}
                {...commonProps}
                options={field.options}
                placeholder={field.placeholder}
                onChange={(e) => handleField(field.name, e.target.value)}
              />
            );
          }

          return (
            <Input
              key={field.name}
              {...commonProps}
              type={field.type || 'text'}
              placeholder={field.placeholder}
              maxLength={field.maxLength}
              min={field.min}
              step={field.step}
              onChange={(e) => handleField(field.name, e.target.value)}
            />
          );
        })}

        <div className={styles.modalActions}>
          <Button variant="secondary" onClick={onClose} disabled={isSubmitting}>
            Отмена
          </Button>
          <Button variant="primary" onClick={onSubmit} loading={isSubmitting}>
            {isCreating ? 'Создать' : 'Сохранить'}
          </Button>
        </div>
      </div>
    </Modal>
  );
}

CrudFormModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  isCreating: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
  isSubmitting: PropTypes.bool,
  titleCreate: PropTypes.string.isRequired,
  titleEdit: PropTypes.string.isRequired,
  fields: PropTypes.array.isRequired,
  form: PropTypes.object.isRequired,
  setForm: PropTypes.func.isRequired,
  size: PropTypes.oneOf(['sm', 'md', 'lg', 'xl', 'full']),
};

export default CrudFormModal;
