/**
 * ThemeToggle
 * Переключатель светлой/тёмной темы
 */

import { useTheme } from '@context/ThemeContext';
import { Sun, Moon } from '@phosphor-icons/react';
import { ph } from '@components/icons/phosphor';
import styles from './ThemeToggle.module.css';

export function ThemeToggle({ className = '' }) {
  const { theme, toggleTheme } = useTheme();
  const isDark = theme === 'dark';

  return (
    <button
      type="button"
      className={`${styles.btn} ${className}`}
      onClick={toggleTheme}
      title={isDark ? 'Светлая тема' : 'Тёмная тема'}
      aria-label={isDark ? 'Включить светлую тему' : 'Включить тёмную тему'}
    >
      {isDark ? (
        <Sun {...ph(20)} aria-hidden />
      ) : (
        <Moon {...ph(20)} aria-hidden />
      )}
    </button>
  );
}

export default ThemeToggle;
