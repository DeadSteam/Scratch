/**
 * ThemeToggle
 * Переключатель светлой/тёмной темы
 */

import { useTheme } from '@context/ThemeContext';
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
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="5"/>
          <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
        </svg>
      ) : (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
        </svg>
      )}
    </button>
  );
}

export default ThemeToggle;
