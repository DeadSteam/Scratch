/**
 * Layout Component
 * Main application layout wrapper
 */

import PropTypes from 'prop-types';
import { useLocation } from 'react-router-dom';
import { Header } from '../Header/Header';
import styles from './Layout.module.css';

export function Layout({ children }) {
  const location = useLocation();

  return (
    <div className={styles.layout}>
      <Header />
      <main className={styles.main}>
        {children}
      </main>
      <footer className={styles.statusbar}>
        <div className={styles.statusbarGroup}>
          <span className="status-dot status-dot-ok" aria-hidden />
          <span>ScratchLab / v4.0.0</span>
        </div>
        <div className={styles.statusbarGroup}>
          <span className={styles.statusbarPath}>{location.pathname}</span>
        </div>
      </footer>
    </div>
  );
}

Layout.propTypes = {
  children: PropTypes.node.isRequired,
};

export default Layout;
