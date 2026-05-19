import { useEffect } from 'react';

/**
 * Вызывает handler, если клик произошёл вне ref-элемента.
 * Активен только когда active=true (по умолчанию — всегда), чтобы не плодить
 * лишних подписок.
 */
export function useClickOutside(ref, handler, active = true) {
  useEffect(() => {
    if (!active) return undefined;
    const listener = (event) => {
      const node = ref.current;
      if (!node || node.contains(event.target)) return;
      handler(event);
    };
    document.addEventListener('mousedown', listener);
    document.addEventListener('touchstart', listener);
    return () => {
      document.removeEventListener('mousedown', listener);
      document.removeEventListener('touchstart', listener);
    };
  }, [ref, handler, active]);
}

export default useClickOutside;
