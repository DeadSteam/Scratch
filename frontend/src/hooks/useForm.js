/**
 * useForm — лёгкий hook для обработки полей формы.
 *
 *   const form = useForm({ name: '', email: '' });
 *   <Input name="name" value={form.values.name} onChange={form.handleChange} />
 *
 * `handleChange` берёт `name` и тип (`checkbox` / остальные) из target — поэтому
 * для большинства полей не нужно писать `setForm((p) => ({ ...p, ... }))` руками.
 * Для произвольных значений есть `setField(name, value)`.
 */

import { useCallback, useState } from 'react';

export function useForm(initial = {}) {
  const [values, setValues] = useState(initial);

  const setField = useCallback((name, value) => {
    setValues((prev) => ({ ...prev, [name]: value }));
  }, []);

  const handleChange = useCallback((e) => {
    const { name, value, type, checked } = e.target;
    setValues((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  }, []);

  const reset = useCallback((next = initial) => {
    setValues(next);
  }, [initial]);

  return { values, setValues, setField, handleChange, reset };
}

export default useForm;
