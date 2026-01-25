/**
 * Admin Page
 * Administration panel for managing users, films, and configurations
 */

import { useState } from 'react';
import { Layout } from '@components/layout';
// Button and Card imports available if needed
import { UsersManagement } from './UsersManagement';
import { FilmsManagement } from './FilmsManagement';
import { ConfigsManagement } from './ConfigsManagement';
import { KnowledgeManagement } from './KnowledgeManagement';
import styles from './AdminPage.module.css';

const TABS = [
  { id: 'users', label: 'Пользователи' },
  { id: 'films', label: 'Типы пленок' },
  { id: 'configs', label: 'Конфигурации' },
  { id: 'knowledge', label: 'База знаний' },
];

export function AdminPage() {
  const [activeTab, setActiveTab] = useState('users');

  const renderContent = () => {
    switch (activeTab) {
      case 'users':
        return <UsersManagement />;
      case 'films':
        return <FilmsManagement />;
      case 'configs':
        return <ConfigsManagement />;
      case 'knowledge':
        return <KnowledgeManagement />;
      default:
        return null;
    }
  };

  return (
    <Layout>
      <div className={styles.page}>
        <div className={styles.header}>
          <h1 className={styles.title}>Админ-панель</h1>
          <p className={styles.subtitle}>
            Управление пользователями, типами пленок и конфигурациями оборудования
          </p>
        </div>

        {/* Tabs */}
        <div className={styles.tabs}>
          {TABS.map((tab) => (
            <button
              key={tab.id}
              className={`${styles.tab} ${activeTab === tab.id ? styles.active : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className={styles.content}>
          {renderContent()}
        </div>
      </div>
    </Layout>
  );
}

export default AdminPage;

