/**
 * Layout Component
 * Main application layout wrapper
 */

import PropTypes from 'prop-types';
import { Header } from '../Header/Header';
import styles from './Layout.module.css';

export function Layout({ children }) {
  return (
    <div className={styles.layout}>
      <Header />
      <main className={styles.main}>
        {children}
      </main>
    </div>
  );
}

Layout.propTypes = {
  children: PropTypes.node.isRequired,
};

export default Layout;



