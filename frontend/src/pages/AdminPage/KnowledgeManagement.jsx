/**
 * Knowledge Management
 * Блок «База знаний»: три плашки сверху, контент выбранного раздела — ниже
 */

import { useState } from 'react';
import { SituationsManagement } from './SituationsManagement';
import { CausesManagement } from './CausesManagement';
import { AdviceManagement } from './AdviceManagement';
import styles from './KnowledgeManagement.module.css';

const SECTIONS = [
  { id: 'situations', label: 'Ситуации', desc: 'Настройка ситуаций (контролируемый параметр, диапазон, описание)', Component: SituationsManagement },
  { id: 'causes', label: 'Причины', desc: 'Настройка причин с привязкой к ситуациям', Component: CausesManagement },
  { id: 'advices', label: 'Рекомендации', desc: 'Настройка рекомендаций с привязкой к причинам', Component: AdviceManagement },
];

export function KnowledgeManagement() {
  const [active, setActive] = useState(null);
  const activeSection = active ? SECTIONS.find((s) => s.id === active) : null;
  const ActiveComponent = activeSection?.Component;

  return (
    <div className={styles.wrapper}>
      <div className={styles.cardsGrid}>
        {SECTIONS.map((s) => (
          <button
            key={s.id}
            type="button"
            className={`${styles.card} ${active === s.id ? styles.active : ''}`}
            onClick={() => setActive(s.id)}
          >
            <span className={styles.cardTitle}>{s.label}</span>
            <span className={styles.cardDesc}>{s.desc}</span>
          </button>
        ))}
      </div>

      {ActiveComponent && (
        <div className={styles.sectionContent}>
          <ActiveComponent />
        </div>
      )}
    </div>
  );
}

export default KnowledgeManagement;
