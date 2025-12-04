/**
 * ROI Selector Component
 * Canvas-based region of interest selector for images
 */

import { useRef, useState, useEffect, useCallback } from 'react';
import PropTypes from 'prop-types';
import { Button } from '@components/common';
import styles from './ROISelector.module.css';

export function ROISelector({
  imageSrc,
  onSelectionChange,
  initialSelection = null,
}) {
  const containerRef = useRef(null);
  const canvasRef = useRef(null);
  const imageRef = useRef(null);
  
  const [isDrawing, setIsDrawing] = useState(false);
  const [startPoint, setStartPoint] = useState(null);
  const [selection, setSelection] = useState(initialSelection);
  const [imageLoaded, setImageLoaded] = useState(false);
  const [, setImageDimensions] = useState({ width: 0, height: 0 });

  // Get mouse position relative to canvas
  const getMousePosition = useCallback((e) => {
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    
    return {
      x: (e.clientX - rect.left) * scaleX,
      y: (e.clientY - rect.top) * scaleY,
    };
  }, []);

  // Draw selection rectangle
  const drawSelection = useCallback((sel) => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const image = imageRef.current;
    
    // Clear and redraw image
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    if (image && imageLoaded) {
      ctx.drawImage(image, 0, 0, canvas.width, canvas.height);
    }
    
    if (!sel) return;
    
    // Semi-transparent overlay outside selection
    ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
    ctx.fillRect(0, 0, canvas.width, sel.y);
    ctx.fillRect(0, sel.y + sel.height, canvas.width, canvas.height - sel.y - sel.height);
    ctx.fillRect(0, sel.y, sel.x, sel.height);
    ctx.fillRect(sel.x + sel.width, sel.y, canvas.width - sel.x - sel.width, sel.height);
    
    // Selection border
    ctx.strokeStyle = '#00d4ff';
    ctx.lineWidth = 2;
    ctx.setLineDash([6, 4]);
    ctx.strokeRect(sel.x, sel.y, sel.width, sel.height);
    
    // Corner handles
    ctx.setLineDash([]);
    ctx.fillStyle = '#00d4ff';
    const handleSize = 8;
    const corners = [
      { x: sel.x, y: sel.y },
      { x: sel.x + sel.width, y: sel.y },
      { x: sel.x, y: sel.y + sel.height },
      { x: sel.x + sel.width, y: sel.y + sel.height },
    ];
    
    corners.forEach(({ x, y }) => {
      ctx.fillRect(x - handleSize / 2, y - handleSize / 2, handleSize, handleSize);
    });
  }, [imageLoaded]);

  // Load image
  useEffect(() => {
    if (!imageSrc) return;
    
    const image = new Image();
    image.onload = () => {
      imageRef.current = image;
      setImageDimensions({ width: image.width, height: image.height });
      setImageLoaded(true);
    };
    image.src = imageSrc;
  }, [imageSrc]);

  // Setup canvas dimensions
  useEffect(() => {
    if (!imageLoaded || !containerRef.current || !canvasRef.current) return;
    
    const container = containerRef.current;
    const canvas = canvasRef.current;
    const image = imageRef.current;
    
    // Calculate dimensions maintaining aspect ratio
    const containerWidth = container.clientWidth;
    const aspectRatio = image.width / image.height;
    const displayHeight = Math.min(500, containerWidth / aspectRatio);
    const displayWidth = displayHeight * aspectRatio;
    
    canvas.width = image.width;
    canvas.height = image.height;
    canvas.style.width = `${displayWidth}px`;
    canvas.style.height = `${displayHeight}px`;
    
    drawSelection(selection);
  }, [imageLoaded, selection, drawSelection]);

  // Mouse handlers
  const handleMouseDown = (e) => {
    const pos = getMousePosition(e);
    setIsDrawing(true);
    setStartPoint(pos);
  };

  const handleMouseMove = (e) => {
    if (!isDrawing || !startPoint) return;
    
    const pos = getMousePosition(e);
    const newSelection = {
      x: Math.min(startPoint.x, pos.x),
      y: Math.min(startPoint.y, pos.y),
      width: Math.abs(pos.x - startPoint.x),
      height: Math.abs(pos.y - startPoint.y),
    };
    
    setSelection(newSelection);
    drawSelection(newSelection);
  };

  const handleMouseUp = () => {
    if (isDrawing && selection && selection.width > 10 && selection.height > 10) {
      // Convert to image coordinates (already in canvas/image coordinates)
      const coords = [
        Math.round(selection.x),
        Math.round(selection.y),
        Math.round(selection.width),
        Math.round(selection.height),
      ];
      onSelectionChange?.(coords);
    }
    setIsDrawing(false);
  };

  const handleClear = () => {
    setSelection(null);
    setStartPoint(null);
    onSelectionChange?.(null);
    drawSelection(null);
  };

  return (
    <div className={styles.container} ref={containerRef}>
      <div className={styles.canvasWrapper}>
        <canvas
          ref={canvasRef}
          className={styles.canvas}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
        />
        
        {!imageLoaded && (
          <div className={styles.placeholder}>
            Загрузка изображения...
          </div>
        )}
      </div>
      
      {/* Selection info */}
      <div className={styles.info}>
        {selection ? (
          <div className={styles.coords}>
            <span className={styles.coordLabel}>Выбранная область:</span>
            <span className={styles.coordValue}>X: {Math.round(selection.x)}</span>
            <span className={styles.coordValue}>Y: {Math.round(selection.y)}</span>
            <span className={styles.coordValue}>Ширина: {Math.round(selection.width)}</span>
            <span className={styles.coordValue}>Высота: {Math.round(selection.height)}</span>
            <Button variant="ghost" size="sm" onClick={handleClear}>
              Очистить выбор
            </Button>
          </div>
        ) : (
          <p className={styles.hint}>
            Нажмите и перетащите на изображении, чтобы выбрать область интереса
          </p>
        )}
      </div>
    </div>
  );
}

ROISelector.propTypes = {
  imageSrc: PropTypes.string.isRequired,
  onSelectionChange: PropTypes.func,
  initialSelection: PropTypes.shape({
    x: PropTypes.number,
    y: PropTypes.number,
    width: PropTypes.number,
    height: PropTypes.number,
  }),
};

export default ROISelector;

