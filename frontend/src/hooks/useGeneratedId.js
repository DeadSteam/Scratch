import { useId } from 'react';

/**
 * Returns providedId if given, otherwise generates a stable unique ID via
 * React's useId(). Safe for SSR and Concurrent Mode — unlike Math.random().
 */
export const useGeneratedId = (providedId) => {
  const generated = useId();
  return providedId || generated;
};
