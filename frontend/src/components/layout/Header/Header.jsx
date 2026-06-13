/**
 * Header Component
 * Main navigation header
 */

import { useCallback, useState, useRef } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '@context/AuthContext';
import { useTheme } from '@context/ThemeContext';
import { useClickOutside } from '@hooks/useClickOutside';
import { ROUTES } from '@utils/constants';
import { Flask, Sun, Moon, SignOut } from '@phosphor-icons/react';
import { ph } from '@components/icons/phosphor';
import styles from './Header.module.css';

export function Header() {
  const { user, isAdmin, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef(null);
  const closeDropdown = useCallback(() => setIsOpen(false), []);
  useClickOutside(containerRef, closeDropdown, isOpen);

  const handleLogout = () => {
    logout();
    navigate(ROUTES.LOGIN);
  };

  const isActive = (path) => location.pathname === path;
  const isDark = theme === 'dark';

  return (
    <header className={styles.header}>
      <div className={styles.container}>
        <div className={styles.brandGroup}>
          <Link to={ROUTES.EXPERIMENTS} className={styles.logo}>
            <Flask {...ph(24)} aria-hidden className={styles.logoIcon} />
            <span className={styles.logoText}>ScratchLab</span>
          </Link>
          <div className={styles.systemStatus}>
            <span className="status-dot status-dot-ok" aria-hidden />
            <span>Система активна</span>
          </div>
        </div>

        <nav className={styles.nav}>
          <Link 
            to={ROUTES.EXPERIMENTS} 
            className={`${styles.navLink} ${isActive(ROUTES.EXPERIMENTS) ? styles.active : ''}`}
          >
            Эксперименты
          </Link>
          {isAdmin && (
            <Link 
              to={ROUTES.ADMIN} 
              className={`${styles.navLink} ${location.pathname.startsWith('/admin') ? styles.active : ''}`}
            >
              Админ-панель
            </Link>
          )}
        </nav>

        <div className={styles.userSection} ref={containerRef}>
          <button
            type="button"
            className={`${styles.userTrigger} ${isOpen ? styles.active : ''}`}
            onClick={() => setIsOpen((o) => !o)}
            aria-expanded={isOpen}
            aria-haspopup="true"
          >
            <div className={styles.avatar}>
              {user?.username?.[0]?.toUpperCase() || 'U'}
            </div>
            <div className={styles.userMeta}>
              <span className={styles.userName}>{user?.username}</span>
              <span className={styles.userRole}>
                {isAdmin ? 'Администратор' : 'Пользователь'}
              </span>
            </div>
          </button>

          {isOpen && (
            <div className={styles.dropdown}>
              <button
                type="button"
                className={styles.dropdownItem}
                onClick={() => { toggleTheme(); setIsOpen(false); }}
              >
                {isDark ? (
                  <Sun {...ph(18)} aria-hidden />
                ) : (
                  <Moon {...ph(18)} aria-hidden />
                )}
                <span>{isDark ? 'Светлая тема' : 'Тёмная тема'}</span>
              </button>
              <button
                type="button"
                className={`${styles.dropdownItem} ${styles.danger}`}
                onClick={handleLogout}
              >
                <SignOut {...ph(18)} aria-hidden />
                <span>Выйти</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

export default Header;



