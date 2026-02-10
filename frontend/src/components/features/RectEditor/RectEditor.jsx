/**
 * RectEditor - Interactive rectangle selection on image
 * Used for selecting analysis region with visual feedback
 */

import { useState, useRef, useEffect, useCallback } from 'react';
import PropTypes from 'prop-types';
import styles from './RectEditor.module.css';

export function RectEditor({ imageUrl, rect, onRectChange }) {
  const containerRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);
  const [dragMode, setDragMode] = useState(null); // 'move' | 'resize'
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [localRect, setLocalRect] = useState(rect || { x: 50, y: 50, width: 200, height: 150 });
  const [imageSize, setImageSize] = useState({ width: 0, height: 0 });

  // Update local rect when prop changes
  useEffect(() => {
    if (rect) {
      setLocalRect(rect);
    }
  }, [rect]);

  const handleImageLoad = (e) => {
    setImageSize({ width: e.target.naturalWidth, height: e.target.naturalHeight });
  };

  const getMousePos = useCallback((e) => {
    if (!containerRef.current) return { x: 0, y: 0 };
    const bounds = containerRef.current.getBoundingClientRect();
    return {
      x: e.clientX - bounds.left,
      y: e.clientY - bounds.top,
    };
  }, []);

  const handleMouseDown = (e, mode) => {
    e.preventDefault();
    e.stopPropagation();
    const pos = getMousePos(e);
    setIsDragging(true);
    setDragMode(mode);
    setDragStart(pos);
  };

  const handleMouseMove = useCallback((e) => {
    if (!isDragging || !containerRef.current) return;

    const pos = getMousePos(e);
    const dx = pos.x - dragStart.x;
    const dy = pos.y - dragStart.y;

    setLocalRect((prev) => {
      if (dragMode === 'move') {
        return {
          ...prev,
          x: Math.max(0, prev.x + dx),
          y: Math.max(0, prev.y + dy),
        };
      } else if (dragMode === 'resize') {
        return {
          ...prev,
          width: Math.max(20, prev.width + dx),
          height: Math.max(20, prev.height + dy),
        };
      }
      return prev;
    });

    setDragStart(pos);
  }, [isDragging, dragMode, dragStart, getMousePos]);

  const handleMouseUp = useCallback(() => {
    if (isDragging && onRectChange) {
      onRectChange(localRect);
    }
    setIsDragging(false);
    setDragMode(null);
  }, [isDragging, localRect, onRectChange]);

  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isDragging, handleMouseMove, handleMouseUp]);

  return (
    <div className={styles.container}>
      <div className={styles.imageWrapper} ref={containerRef}>
        <img
          src={imageUrl}
          alt="Analysis region"
          className={styles.image}
          onLoad={handleImageLoad}
          draggable={false}
        />
        {/* Rect overlay */}
        <div
          className={styles.rectOverlay}
          style={{
            left: `${localRect.x}px`,
            top: `${localRect.y}px`,
            width: `${localRect.width}px`,
            height: `${localRect.height}px`,
          }}
          onMouseDown={(e) => handleMouseDown(e, 'move')}
        >
          {/* Resize handle */}
          <div
            className={styles.resizeHandle}
            onMouseDown={(e) => handleMouseDown(e, 'resize')}
          />
        </div>
      </div>
      <div className={styles.coordsDisplay}>
        X: {Math.round(localRect.x)}, Y: {Math.round(localRect.y)}, 
        Ширина: {Math.round(localRect.width)}, Высота: {Math.round(localRect.height)}
      </div>
    </div>
  );
}

RectEditor.propTypes = {
  imageUrl: PropTypes.string.isRequired,
  rect: PropTypes.shape({
    x: PropTypes.number,
    y: PropTypes.number,
    width: PropTypes.number,
    height: PropTypes.number,
  }),
  onRectChange: PropTypes.func,
};

export default RectEditor;
