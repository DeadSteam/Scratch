/**
 * Knowledge Management
 * Блок «База знаний»: три плашки сверху, контент выбранного раздела — ниже
 */

import { useState } from 'react';
import { ClipboardText, GitBranch, ChatTeardropText } from '@phosphor-icons/react';
import { ph } from '@components/icons/phosphor';
import { SituationsManagement } from './SituationsManagement';
import { CausesManagement } from './CausesManagement';
import { AdviceManagement } from './AdviceManagement';
import styles from './KnowledgeManagement.module.css';

const IconSituations = () => <ClipboardText {...ph(18)} aria-hidden />;
const IconCauses = () => <GitBranch {...ph(18)} aria-hidden />;
const IconAdvice = () => <ChatTeardropText {...ph(18)} aria-hidden />;

const SECTIONS = [
  {
    id: 'situations',
    label: 'Ситуации',
    desc: 'Параметр, диапазон, оценка (label), уровень (severity), описание',
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
