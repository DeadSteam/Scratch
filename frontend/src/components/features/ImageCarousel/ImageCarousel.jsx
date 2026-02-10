/**
 * Image Carousel Component
 * Display experiment images with navigation and delete functionality
 */

import { useState, useMemo, useRef, useEffect } from 'react';
import PropTypes from 'prop-types';
import { API_BASE_URL } from '@utils/constants';
import styles from './ImageCarousel.module.css';

const MAX_VISIBLE_THUMBNAILS = 6;

export function ImageCarousel({ images = [], onImageClick, onImageDelete, onAddImage }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [deleteConfirm, setDeleteConfirm] = useState(null);
  const thumbnailsRef = useRef(null);

  // Sort images by passes
  const sortedImages = useMemo(() => {
    return [...images].sort((a, b) => a.passes - b.passes);
  }, [images]);

  const currentImage = sortedImages[currentIndex];

  const handlePrev = () => {
    const newIndex = currentIndex > 0 ? currentIndex - 1 : sortedImages.length - 1;
    setCurrentIndex(newIndex);
    scrollToThumbnail(newIndex);
  };

  const handleNext = () => {
    const newIndex = currentIndex < sortedImages.length - 1 ? currentIndex + 1 : 0;
    setCurrentIndex(newIndex);
    scrollToThumbnail(newIndex);
  };

  const handleThumbnailClick = (index) => {
    setCurrentIndex(index);
    scrollToThumbnail(index);
  };

  // Scroll thumbnails to show the active one
  const scrollToThumbnail = (index) => {
    if (!thumbnailsRef.current) return;
    
    const thumbnailWidth = 72 + 8; // width + gap
    const scrollPosition = index * thumbnailWidth - (MAX_VISIBLE_THUMBNAILS / 2) * thumbnailWidth;
    
    thumbnailsRef.current.scrollTo({
      left: Math.max(0, scrollPosition),
      behavior: 'smooth',
    });
  };

  const handleThumbnailsPrev = () => {
    if (!thumbnailsRef.current) return;
    const scrollAmount = (72 + 8) * 3; // 3 thumbnails at a time
    thumbnailsRef.current.scrollBy({
      left: -scrollAmount,
      behavior: 'smooth',
    });
  };

  const handleThumbnailsNext = () => {
    if (!thumbnailsRef.current) return;
    const scrollAmount = (72 + 8) * 3; // 3 thumbnails at a time
    thumbnailsRef.current.scrollBy({
      left: scrollAmount,
      behavior: 'smooth',
    });
  };

  const [canScrollPrev, setCanScrollPrev] = useState(false);
  const [canScrollNext, setCanScrollNext] = useState(false);

  // Update scroll state
  const updateScrollState = () => {
    if (!thumbnailsRef.current) return;
    const { scrollLeft, scrollWidth, clientWidth } = thumbnailsRef.current;
    setCanScrollPrev(scrollLeft > 0);
    setCanScrollNext(scrollLeft < scrollWidth - clientWidth - 1);
  };

  // Update scroll state on mount and when images change
  useEffect(() => {
    updateScrollState();
    const thumbnails = thumbnailsRef.current;
    if (thumbnails) {
      thumbnails.addEventListener('scroll', updateScrollState);
      return () => thumbnails.removeEventListener('scroll', updateScrollState);
    }
  }, [sortedImages]);

  const handleKeyDown = (e) => {
    if (e.key === 'ArrowLeft') handlePrev();
    if (e.key === 'ArrowRight') handleNext();
    if (e.key === 'Delete' && currentImage && onImageDelete) {
      setDeleteConfirm(currentImage.id);
    }
  };

  const handleDeleteClick = (e, imageId) => {
    e.stopPropagation();
    setDeleteConfirm(imageId);
  };

  const handleConfirmDelete = async () => {
    if (deleteConfirm && onImageDelete) {
      await onImageDelete(deleteConfirm);
      // Adjust current index if needed
      if (currentIndex >= sortedImages.length - 1 && currentIndex > 0) {
        setCurrentIndex(currentIndex - 1);
      }
    }
    setDeleteConfirm(null);
  };

  const handleCancelDelete = () => {
    setDeleteConfirm(null);
  };

  if (sortedImages.length === 0) {
    return (
      <div className={styles.empty}>
        <svg width="48" height="48" viewBox="0 0 48 48" fill="none" stroke="currentColor" strokeWidth="1.5">
          <rect x="6" y="10" width="36" height="28" rx="4" />
          <circle cx="18" cy="22" r="4" />
          <path d="M42 30l-8-8-12 12-6-6-10 10" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
        <p>Нет изображений</p>
      </div>
    );
  }

  // Create image URL from API endpoint
  const getImageUrl = (imageId) => {
    if (!imageId) return '';
    return `${API_BASE_URL}/images/${imageId}/data`;
  };

  return (
    <div 
      className={styles.container}
      tabIndex={0}
      onKeyDown={handleKeyDown}
    >
      {/* Delete confirmation overlay */}
      {deleteConfirm && (
        <div className={styles.deleteOverlay}>
          <div className={styles.deleteModal}>
            <div className={styles.deleteIcon}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
                <line x1="10" y1="11" x2="10" y2="17"/>
                <line x1="14" y1="11" x2="14" y2="17"/>
              </svg>
            </div>
            <h4>Удалить изображение?</h4>
            <p>Это действие нельзя отменить</p>
            <div className={styles.deleteActions}>
              <button 
                className={styles.cancelButton}
                onClick={handleCancelDelete}
              >
                Отмена
              </button>
              <button 
                className={styles.confirmButton}
                onClick={handleConfirmDelete}
              >
                Удалить
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main image */}
      <div className={styles.mainImage}>
        <img
          src={getImageUrl(currentImage?.id)}
          alt={`Проходов: ${currentImage?.passes || 0}`}
          onClick={() => onImageClick?.(currentImage)}
        />
        
        {/* Delete button on main image */}
        {onImageDelete && (
          <button
            className={styles.deleteMainButton}
            onClick={(e) => handleDeleteClick(e, currentImage?.id)}
            aria-label="Удалить изображение"
            title="Удалить изображение"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
            </svg>
          </button>
        )}
        
        {/* Navigation arrows */}
        {sortedImages.length > 1 && (
          <>
            <button 
              className={`${styles.navButton} ${styles.prevButton}`}
              onClick={handlePrev}
              aria-label="Предыдущее"
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                <path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z" />
              </svg>
            </button>
            <button 
              className={`${styles.navButton} ${styles.nextButton}`}
              onClick={handleNext}
              aria-label="Следующее"
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                <path d="M8.59 16.59L10 18l6-6-6-6-1.41 1.41L13.17 12z" />
              </svg>
            </button>
          </>
        )}

        {/* Image info overlay */}
        <div className={styles.imageInfo}>
          <span className={styles.passesLabel}>
            {currentImage?.passes === 0 ? 'Эталон' : `${currentImage?.passes} проходов`}
          </span>
          <span className={styles.counter}>
            {currentIndex + 1} / {sortedImages.length}
          </span>
        </div>
      </div>

      {/* Thumbnails */}
      {sortedImages.length > 1 && (
        <div className={styles.thumbnailsContainer}>
          {sortedImages.length > MAX_VISIBLE_THUMBNAILS && (
            <button
              className={`${styles.thumbnailsNavButton} ${styles.thumbnailsPrev}`}
              onClick={handleThumbnailsPrev}
              aria-label="Предыдущие миниатюры"
              disabled={!canScrollPrev}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z" />
              </svg>
            </button>
          )}
          <div 
            ref={thumbnailsRef}
            className={styles.thumbnails}
          >
            {sortedImages.map((image, index) => (
              <div 
                key={image.id}
                className={`${styles.thumbnailWrapper} ${index === currentIndex ? styles.active : ''}`}
              >
                <button
                  className={styles.thumbnail}
                  onClick={() => handleThumbnailClick(index)}
                  aria-label={`Изображение ${index + 1}`}
                >
                  <img
                    src={getImageUrl(image.id)}
                    alt={`Проходов: ${image.passes}`}
                  />
                  <span className={styles.thumbnailLabel}>
                    {image.passes === 0 ? 'Эт.' : image.passes}
                  </span>
                </button>
                {onImageDelete && (
                  <button
                    className={styles.thumbnailDelete}
                    onClick={(e) => handleDeleteClick(e, image.id)}
                    aria-label="Удалить"
                    title="Удалить"
                  >
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                    </svg>
                  </button>
                )}
              </div>
            ))}
            {onAddImage && (
              <button
                className={styles.addThumbnail}
                onClick={onAddImage}
                aria-label="Добавить фото"
                title="Добавить фото"
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
                </svg>
              </button>
            )}
          </div>
          {sortedImages.length > MAX_VISIBLE_THUMBNAILS && (
            <button
              className={`${styles.thumbnailsNavButton} ${styles.thumbnailsNext}`}
              onClick={handleThumbnailsNext}
              aria-label="Следующие миниатюры"
              disabled={!canScrollNext}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <path d="M8.59 16.59L10 18l6-6-6-6-1.41 1.41L13.17 12z" />
              </svg>
            </button>
          )}
        </div>
      )}
    </div>
  );
}

ImageCarousel.propTypes = {
  images: PropTypes.arrayOf(PropTypes.shape({
    id: PropTypes.string.isRequired,
    passes: PropTypes.number.isRequired,
  })),
  onImageClick: PropTypes.func,
  onImageDelete: PropTypes.func,
  onAddImage: PropTypes.func,
};

export default ImageCarousel;
