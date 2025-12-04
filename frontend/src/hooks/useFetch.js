/**
 * useFetch Hook
 * Hook for fetching data with caching and refetch capabilities
 */

import { useState, useEffect, useCallback, useRef } from 'react';

export function useFetch(fetchFn, dependencies = [], options = {}) {
  const {
    enabled = true,
    initialData = null,
    onSuccess,
    onError,
  } = options;

  const [data, setData] = useState(initialData);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const isMounted = useRef(true);

  const fetch = useCallback(async () => {
    if (!enabled) return;

    setIsLoading(true);
    setError(null);

    try {
      const result = await fetchFn();
      
      if (isMounted.current) {
        setData(result);
        if (onSuccess) {
          onSuccess(result);
        }
      }
      
      return result;
    } catch (err) {
      if (isMounted.current) {
        setError(err.message || 'Ошибка загрузки данных');
        if (onError) {
          onError(err);
        }
      }
      throw err;
    } finally {
      if (isMounted.current) {
        setIsLoading(false);
      }
    }
  }, [fetchFn, enabled, onSuccess, onError]);

  // Initial fetch and refetch on dependency change
  useEffect(() => {
    isMounted.current = true;
    
    if (enabled) {
      fetch();
    }
    
    return () => {
      isMounted.current = false;
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...dependencies, enabled]);

  // Manual refetch function
  const refetch = useCallback(() => {
    return fetch();
  }, [fetch]);

  return {
    data,
    isLoading,
    error,
    refetch,
    setData,
  };
}

export default useFetch;



