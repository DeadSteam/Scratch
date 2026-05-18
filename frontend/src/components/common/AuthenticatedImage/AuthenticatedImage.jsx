/**
 * Image that loads via authenticated API (blob URL), not raw /images/{id}/data.
 */

import PropTypes from 'prop-types';
import { useAuthenticatedImageUrl } from '@hooks/useAuthenticatedImageUrl';
import { Spinner } from '../Spinner/Spinner';
import styles from './AuthenticatedImage.module.css';

export function AuthenticatedImage({
  imageId,
  alt = '',
  className = '',
  onClick,
  ...imgProps
}) {
  const { url, isLoading, error } = useAuthenticatedImageUrl(imageId);

  if (!imageId) return null;

  if (isLoading) {
    return (
      <span className={`${styles.placeholder} ${className}`} aria-hidden>
        <Spinner size="sm" />
      </span>
    );
  }

  if (error || !url) {
    return (
      <span
        className={`${styles.error} ${className}`}
        role="img"
        aria-label={alt || 'Изображение недоступно'}
      />
    );
  }

  return (
    <img
      src={url}
      alt={alt}
      className={className}
      onClick={onClick}
      {...imgProps}
    />
  );
}

AuthenticatedImage.propTypes = {
  imageId: PropTypes.string,
  alt: PropTypes.string,
  className: PropTypes.string,
  onClick: PropTypes.func,
};

export default AuthenticatedImage;
