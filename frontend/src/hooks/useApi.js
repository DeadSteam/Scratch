/**
 * useApi Hook
 * Generic hook for API calls with loading and error states
 */

import { useState, useCallback } from 'react';
import { useNotification } from '@context/NotificationContext';

export function useApi() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const { error: showError } = useNotification();

  const execute = useCallback(async (apiCall, options = {}) => {
    const {
      onSuccess,
      onError,
      showErrorNotification = true,
      successMessage,
    } = options;

    setIsLoading(true);
    setError(null);

    try {
      const result = await apiCall();
      
      if (onSuccess) {
        onSuccess(result);
      }
      
      if (successMessage) {
        // Can add success notification here if needed
      }
      
      return result;
    } catch (err) {
      const errorMessage = err.message || 'Произошла ошибка';
      setError(errorMessage);
      
      if (showErrorNotification) {
        showError(errorMessage);
      }
      
      if (onError) {
        onError(err);
      }
      
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [showError]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    isLoading,
    error,
    execute,
    clearError,
  };
}

export default useApi;



