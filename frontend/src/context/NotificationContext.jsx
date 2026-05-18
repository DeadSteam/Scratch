import { createContext, useContext, useState, useCallback, useRef } from 'react';
import { TOAST_DURATION } from '@utils/constants';

const NotificationContext = createContext(null);

export function NotificationProvider({ children }) {
  const [notifications, setNotifications] = useState([]);
  const idRef = useRef(0);
  const timersRef = useRef({});

  const removeNotification = useCallback((id) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
    clearTimeout(timersRef.current[id]);
    delete timersRef.current[id];
  }, []);

  const addNotification = useCallback((notification) => {
    const id = ++idRef.current;
    const entry = {
      type: 'info',
      duration: TOAST_DURATION.MEDIUM,
      ...notification,
      id,
    };

    setNotifications((prev) => [...prev, entry]);

    if (entry.duration > 0) {
      timersRef.current[id] = setTimeout(() => removeNotification(id), entry.duration);
    }

    return id;
  }, [removeNotification]);

  const clearNotifications = useCallback(() => {
    Object.values(timersRef.current).forEach(clearTimeout);
    timersRef.current = {};
    setNotifications([]);
  }, []);

  const success = useCallback((message, opts) =>
    addNotification({ type: 'success', message, ...opts }), [addNotification]);

  const error = useCallback((message, opts) =>
    addNotification({ type: 'error', message, duration: TOAST_DURATION.LONG, ...opts }), [addNotification]);

  const warning = useCallback((message, opts) =>
    addNotification({ type: 'warning', message, ...opts }), [addNotification]);

  const info = useCallback((message, opts) =>
    addNotification({ type: 'info', message, ...opts }), [addNotification]);

  return (
    <NotificationContext.Provider value={{
      notifications,
      addNotification,
      removeNotification,
      clearNotifications,
      success,
      error,
      warning,
      info,
    }}>
      {children}
    </NotificationContext.Provider>
  );
}

export function useNotification() {
  const context = useContext(NotificationContext);
  if (!context) throw new Error('useNotification must be used within a NotificationProvider');
  return context;
}

export default NotificationContext;
