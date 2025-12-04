/**
 * Header Component
 * Main navigation header
 */

import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '@context/AuthContext';
import { ROUTES } from '@utils/constants';
import styles from './Header.module.css';

export function Header() {
  const { user, isAdmin, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate(ROUTES.LOGIN);
  };

  const isActive = (path) => location.pathname === path;

  return (
    <header className={styles.header}>
      <div className={styles.container}>
        <Link to={ROUTES.EXPERIMENTS} className={styles.logo}>
          <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="2" y="2" width="28" height="28" rx="6" stroke="currentColor" strokeWidth="2"/>
            <path d="M8 16H24M16 8V24M10 10L22 22M22 10L10 22" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" opacity="0.5"/>
            <circle cx="16" cy="16" r="4" stroke="currentColor" strokeWidth="2"/>
          </svg>
          <span className={styles.logoText}>ScratchLab</span>
        </Link>

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

        <div className={styles.userSection}>
          <div className={styles.userInfo}>
            <div className={styles.avatar}>
              {user?.username?.[0]?.toUpperCase() || 'U'}
            </div>
            <div className={styles.userMeta}>
              <span className={styles.userName}>{user?.username}</span>
              <span className={styles.userRole}>
                {isAdmin ? 'Администратор' : 'Пользователь'}
              </span>
            </div>
          </div>
          <button 
            type="button"
            className={styles.logoutButton}
            onClick={handleLogout}
            title="Выйти"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M3 4.25A2.25 2.25 0 015.25 2h5.5A2.25 2.25 0 0113 4.25v2a.75.75 0 01-1.5 0v-2a.75.75 0 00-.75-.75h-5.5a.75.75 0 00-.75.75v11.5c0 .414.336.75.75.75h5.5a.75.75 0 00.75-.75v-2a.75.75 0 011.5 0v2A2.25 2.25 0 0110.75 18h-5.5A2.25 2.25 0 013 15.75V4.25z" clipRule="evenodd" />
              <path fillRule="evenodd" d="M6 10a.75.75 0 01.75-.75h9.546l-1.048-1.048a.75.75 0 111.06-1.06l2.5 2.5a.75.75 0 010 1.06l-2.5 2.5a.75.75 0 11-1.06-1.06l1.048-1.048H6.75A.75.75 0 016 10z" clipRule="evenodd" />
            </svg>
          </button>
        </div>
      </div>
    </header>
  );
}

export default Header;



