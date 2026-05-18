/**
 * Load experiment image binary via authenticated API and expose a blob URL.
 */

import { useEffect, useState } from 'react';
import { imageService } from '@api/ImageService';

export function useAuthenticatedImageUrl(imageId) {
  const [url, setUrl] = useState(null);
  const [isLoading, setIsLoading] = useState(Boolean(imageId));
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!imageId) {
      setUrl(null);
      setIsLoading(false);
      setError(null);
      return undefined;
    }

    let cancelled = false;
    setIsLoading(true);
    setError(null);

    imageService
      .getAuthenticatedImageUrl(imageId)
      .then((objectUrl) => {
        if (!cancelled) setUrl(objectUrl);
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err);
          setUrl(null);
        }
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [imageId]);

  return { url, isLoading, error };
}

export default useAuthenticatedImageUrl;
