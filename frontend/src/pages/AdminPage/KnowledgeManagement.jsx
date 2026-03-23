/**
 * Knowledge Management
 * Блок «База знаний»: три плашки сверху, контент выбранного раздела — ниже
 */

import { useState } from 'react';
import { SituationsManagement } from './SituationsManagement';
import { CausesManagement } from './CausesManagement';
import { AdviceManagement } from './AdviceManagement';
import styles from './KnowledgeManagement.module.css';

/* SVG icons for each section */
const IconSituations = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
    <rect x="2" y="3" width="20" height="14" rx="2"/>
    <path d="M8 21h8M12 17v4"/>
    <path d="M7 7h10M7 11h6"/>
  </svg>
);

const IconCauses = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 3v3M6.3 6.3l2.1 2.1M3 12h3M6.3 17.7l2.1-2.1M12 21v-3M17.7 17.7l-2.1-2.1M21 12h-3M17.7 6.3l-2.1 2.1"/>
    <circle cx="12" cy="12" r="3"/>
  </svg>
);

const IconAdvice = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 2a7 7 0 0 1 7 7c0 2.38-1.19 4.47-3 5.74V17a1 1 0 0 1-1 1H9a1 1 0 0 1-1-1v-2.26C6.19 13.47 5 11.38 5 9a7 7 0 0 1 7-7z"/>
    <path d="M9 21h6M10 17v1M14 17v1"/>
  </svg>
);

const SECTIONS = [
  {
    id: 'situations',
    label: 'Ситуации',
    desc: 'Контролируемый параметр, диапазон, описание',
    Icon: IconSituations,
    Component: SituationsManagement,
  },
  {
    id: 'causes',
    label: 'Причины',
    desc: 'Привязка причин к ситуациям',
    Icon: IconCauses,
    Component: CausesManagement,
  },
  {
    id: 'advices',
    label: 'Рекомендации',
    desc: 'Привязка рекомендаций к причинам',
    Icon: IconAdvice,
    Component: AdviceManagement,
  },
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
            {/* Corner accents — visible on hover/active (21st.dev Dark Grid pattern) */}
            <span className={styles.cornerTL} aria-hidden="true" />
            <span className={styles.cornerBR} aria-hidden="true" />

            <span className={styles.cardIconWrap}>
              <s.Icon />
            </span>
            <span className={styles.cardText}>
              <span className={styles.cardTitle}>{s.label}</span>
              <span className={styles.cardDesc}>{s.desc}</span>
            </span>
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
