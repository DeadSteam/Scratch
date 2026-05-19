/**
 * CrudTable — таблица CRUD-страницы админки.
 *
 * Декларативно описывает колонки и empty-state. Колонка «Действия»
 * добавляется автоматически (Изменить/Удалить).
 */

import PropTypes from 'prop-types';
import { Button } from '../Button/Button';
import styles from './CrudTable.module.css';

export function CrudTable({
  columns,
  items,
  onEdit,
  onDelete,
  emptyIcon,
  emptyTitle = 'Пока ничего нет',
  emptyDescription,
  rowKey = 'id',
  actions,
}) {
  const totalCols = columns.length + (actions === false ? 0 : 1);

  return (
    <div className={styles.tableWrapper}>
      <table className={styles.table}>
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={col.key || col.header}>{col.header}</th>
            ))}
            {actions !== false && <th>Действия</th>}
          </tr>
        </thead>
        <tbody>
          {items.length === 0 ? (
            <tr className={styles.emptyRow}>
              <td colSpan={totalCols}>
                <div className={styles.emptyStateCell}>
                  {emptyIcon && <div className={styles.emptyIcon}>{emptyIcon}</div>}
                  <p className={styles.emptyTitle}>{emptyTitle}</p>
                  {emptyDescription && <p className={styles.emptyDesc}>{emptyDescription}</p>}
                </div>
              </td>
            </tr>
          ) : (
            items.map((item, rowIndex) => (
              <tr key={item[rowKey] ?? rowIndex}>
                {columns.map((col, i) => (
                  <td
                    key={col.key || i}
                    className={i === 0 ? styles.primaryCell : col.className || ''}
                  >
                    {col.render ? col.render(item) : (item[col.field] ?? '—')}
                  </td>
                ))}
                {actions !== false && (
                  <td>
                    <div className={styles.actions}>
                      {onEdit && (
                        <Button variant="ghost" size="sm" onClick={() => onEdit(item)}>
                          Изменить
                        </Button>
                      )}
                      {onDelete && (
                        <Button variant="ghost" size="sm" onClick={() => onDelete(item)}>
                          Удалить
                        </Button>
                      )}
                      {actions && actions(item)}
                    </div>
                  </td>
                )}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}

CrudTable.propTypes = {
  columns: PropTypes.arrayOf(PropTypes.shape({
    key: PropTypes.string,
    header: PropTypes.string.isRequired,
    field: PropTypes.string,
    render: PropTypes.func,
    className: PropTypes.string,
  })).isRequired,
  items: PropTypes.array.isRequired,
  onEdit: PropTypes.func,
  onDelete: PropTypes.func,
  emptyIcon: PropTypes.node,
  emptyTitle: PropTypes.string,
  emptyDescription: PropTypes.string,
  rowKey: PropTypes.string,
  actions: PropTypes.oneOfType([PropTypes.func, PropTypes.bool]),
};

export default CrudTable;
