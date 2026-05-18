/**
 * Image Carousel Component
 * Display experiment images with navigation and delete functionality
 */

import { useState, useMemo, useRef, useEffect } from 'react';
import PropTypes from 'prop-types';
import {
  Images,
  Trash,
  CaretLeft,
  CaretRight,
  X,
  Plus,
} from '@phosphor-icons/react';
import { ph } from '@components/icons/phosphor';
import { Modal } from '@components/common/Modal/Modal';
import { Button } from '@components/common/Button/Button';
import { imageService } from '@api';
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
        <Images {...ph(48)} aria-hidden />
        <p>Нет изображений</p>
      </div>
    );
  }

  const getImageUrl = (imageId) => imageId ? imageService.getImageDataUrl(imageId) : '';

  return (
    <div 
      className={styles.container}
      tabIndex={0}
      onKeyDown={handleKeyDown}
    >
      {/* Delete confirmation modal */}
      <Modal
        isOpen={!!deleteConfirm}
        onClose={handleCancelDelete}
        title="Удалить изображение?"
        size="sm"
      >
        <div className={styles.deleteModalContent}>
          <div className={styles.deleteIcon}>
            <Trash {...ph(48)} aria-hidden />
          </div>
          <p className={styles.deleteMessage}>Это действие нельзя отменить</p>
          <div className={styles.deleteActions}>
            <Button variant="secondary" onClick={handleCancelDelete}>
              Отмена
            </Button>
            <Button variant="danger" onClick={handleConfirmDelete}>
              Удалить
            </Button>
          </div>
        </div>
      </Modal>

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
            <Trash {...ph(20)} aria-hidden />
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
              <CaretLeft {...ph(24)} weight="fill" aria-hidden />
            </button>
            <button 
              className={`${styles.navButton} ${styles.nextButton}`}
              onClick={handleNext}
              aria-label="Следующее"
            >
              <CaretRight {...ph(24)} weight="fill" aria-hidden />
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
              <CaretLeft {...ph(20)} weight="fill" aria-hidden />
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
                    <X {...ph(12)} weight="bold" aria-hidden />
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
                <Plus {...ph(20)} weight="bold" aria-hidden />
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
              <CaretRight {...ph(20)} weight="fill" aria-hidden />
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
