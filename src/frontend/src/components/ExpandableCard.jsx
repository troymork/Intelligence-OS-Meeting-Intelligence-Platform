/**
 * Expandable Card Component
 * Neumorphic expandable cards for progressive disclosure of complex analytical outputs
 */

import React, { useState, useRef, useEffect, useCallback } from 'react';
import './ExpandableCard.css';

const ExpandableCard = ({
  title,
  subtitle,
  summary,
  children,
  icon,
  badge,
  priority = 'normal',
  expandable = true,
  defaultExpanded = false,
  onExpand,
  onCollapse,
  className = '',
  headerActions,
  footer,
  loading = false,
  error = null,
  size = 'medium',
  variant = 'default'
}) => {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);
  const [isAnimating, setIsAnimating] = useState(false);
  const [contentHeight, setContentHeight] = useState(0);
  const contentRef = useRef(null);
  const headerRef = useRef(null);
  
  // Measure content height for smooth animations
  const measureContentHeight = useCallback(() => {
    if (contentRef.current) {
      const height = contentRef.current.scrollHeight;
      setContentHeight(height);
    }
  }, []);
  
  useEffect(() => {
    measureContentHeight();
    
    // Re-measure on window resize
    const handleResize = () => measureContentHeight();
    window.addEventListener('resize', handleResize);
    
    return () => window.removeEventListener('resize', handleResize);
  }, [children, measureContentHeight]);
  
  // Handle expand/collapse
  const handleToggle = useCallback(() => {
    if (!expandable || loading) return;
    
    setIsAnimating(true);
    const newExpanded = !isExpanded;
    setIsExpanded(newExpanded);
    
    // Call callbacks
    if (newExpanded) {
      onExpand?.();
    } else {
      onCollapse?.();
    }
    
    // Reset animation state
    setTimeout(() => setIsAnimating(false), 300);
  }, [expandable, loading, isExpanded, onExpand, onCollapse]);
  
  // Handle keyboard navigation
  const handleKeyDown = useCallback((event) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      handleToggle();
    }
  }, [handleToggle]);
  
  // Generate CSS classes
  const cardClasses = [
    'expandable-card',
    `expandable-card--${size}`,
    `expandable-card--${variant}`,
    `expandable-card--${priority}`,
    isExpanded ? 'expandable-card--expanded' : 'expandable-card--collapsed',
    isAnimating ? 'expandable-card--animating' : '',
    loading ? 'expandable-card--loading' : '',
    error ? 'expandable-card--error' : '',
    !expandable ? 'expandable-card--static' : '',
    className
  ].filter(Boolean).join(' ');
  
  return (
    <div className={cardClasses}>
      {/* Card Header */}
      <div
        ref={headerRef}
        className="expandable-card__header"
        onClick={expandable ? handleToggle : undefined}
        onKeyDown={expandable ? handleKeyDown : undefined}
        tabIndex={expandable ? 0 : -1}
        role={expandable ? 'button' : undefined}
        aria-expanded={expandable ? isExpanded : undefined}
        aria-controls={expandable ? 'card-content' : undefined}
      >
        {/* Header Content */}
        <div className="expandable-card__header-content">
          {/* Icon */}
          {icon && (
            <div className="expandable-card__icon">
              {typeof icon === 'string' ? (
                <img src={icon} alt="" />
              ) : (
                icon
              )}
            </div>
          )}
          
          {/* Title and Subtitle */}
          <div className="expandable-card__title-section">
            <div className="expandable-card__title-row">
              <h3 className="expandable-card__title">{title}</h3>
              
              {/* Badge */}
              {badge && (
                <span className={`expandable-card__badge expandable-card__badge--${badge.type || 'default'}`}>
                  {badge.text}
                </span>
              )}
            </div>
            
            {subtitle && (
              <p className="expandable-card__subtitle">{subtitle}</p>
            )}
          </div>
          
          {/* Header Actions */}
          {headerActions && (
            <div className="expandable-card__header-actions">
              {headerActions}
            </div>
          )}
          
          {/* Expand/Collapse Button */}
          {expandable && (
            <button
              className="expandable-card__toggle"
              aria-label={isExpanded ? 'Collapse card' : 'Expand card'}
              tabIndex={-1} // Header handles keyboard interaction
            >
              <svg
                className="expandable-card__toggle-icon"
                viewBox="0 0 24 24"
                fill="currentColor"
              >
                <path d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6 1.41-1.41z" />
              </svg>
            </button>
          )}
        </div>
        
        {/* Summary (visible when collapsed) */}
        {summary && !isExpanded && (
          <div className="expandable-card__summary">
            {typeof summary === 'string' ? (
              <p>{summary}</p>
            ) : (
              summary
            )}
          </div>
        )}
        
        {/* Loading Indicator */}
        {loading && (
          <div className="expandable-card__loading">
            <div className="expandable-card__loading-spinner" />
            <span>Loading...</span>
          </div>
        )}
        
        {/* Error Message */}
        {error && (
          <div className="expandable-card__error">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
            <span>{error}</span>
          </div>
        )}
      </div>
      
      {/* Card Content */}
      <div
        className="expandable-card__content-wrapper"
        style={{
          maxHeight: isExpanded ? `${contentHeight}px` : '0px'
        }}
      >
        <div
          ref={contentRef}
          className="expandable-card__content"
          id="card-content"
          aria-hidden={!isExpanded}
        >
          {children}
        </div>
      </div>
      
      {/* Card Footer */}
      {footer && isExpanded && (
        <div className="expandable-card__footer">
          {footer}
        </div>
      )}
    </div>
  );
};

// Card Group Component for organizing multiple cards
export const ExpandableCardGroup = ({
  children,
  title,
  subtitle,
  layout = 'grid',
  columns = 'auto',
  gap = 'medium',
  className = ''
}) => {
  const groupClasses = [
    'expandable-card-group',
    `expandable-card-group--${layout}`,
    `expandable-card-group--gap-${gap}`,
    className
  ].filter(Boolean).join(' ');
  
  const gridColumns = {
    1: '1fr',
    2: 'repeat(2, 1fr)',
    3: 'repeat(3, 1fr)',
    4: 'repeat(4, 1fr)',
    auto: 'repeat(auto-fit, minmax(300px, 1fr))'
  };
  
  return (
    <div className={groupClasses}>
      {(title || subtitle) && (
        <div className="expandable-card-group__header">
          {title && <h2 className="expandable-card-group__title">{title}</h2>}
          {subtitle && <p className="expandable-card-group__subtitle">{subtitle}</p>}
        </div>
      )}
      
      <div
        className="expandable-card-group__content"
        style={{
          gridTemplateColumns: layout === 'grid' ? gridColumns[columns] : undefined
        }}
      >
        {children}
      </div>
    </div>
  );
};

// Specialized card variants
export const AnalysisCard = ({ analysis, ...props }) => (
  <ExpandableCard
    title={analysis.title}
    subtitle={analysis.type}
    summary={analysis.summary}
    badge={{
      text: `${Math.round(analysis.confidence * 100)}%`,
      type: analysis.confidence > 0.8 ? 'success' : analysis.confidence > 0.6 ? 'warning' : 'error'
    }}
    priority={analysis.priority}
    {...props}
  >
    <div className="analysis-card__content">
      {analysis.insights && (
        <div className="analysis-card__insights">
          <h4>Key Insights</h4>
          <ul>
            {analysis.insights.map((insight, index) => (
              <li key={index}>{insight}</li>
            ))}
          </ul>
        </div>
      )}
      
      {analysis.recommendations && (
        <div className="analysis-card__recommendations">
          <h4>Recommendations</h4>
          <ul>
            {analysis.recommendations.map((rec, index) => (
              <li key={index}>{rec}</li>
            ))}
          </ul>
        </div>
      )}
      
      {analysis.metrics && (
        <div className="analysis-card__metrics">
          <h4>Metrics</h4>
          <div className="analysis-card__metrics-grid">
            {Object.entries(analysis.metrics).map(([key, value]) => (
              <div key={key} className="analysis-card__metric">
                <span className="analysis-card__metric-label">{key}</span>
                <span className="analysis-card__metric-value">{value}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  </ExpandableCard>
);

export const ActionCard = ({ action, ...props }) => (
  <ExpandableCard
    title={action.title}
    subtitle={`Due: ${action.dueDate}`}
    summary={action.description}
    badge={{
      text: action.status,
      type: action.status === 'completed' ? 'success' : 
            action.status === 'in_progress' ? 'info' : 
            action.status === 'overdue' ? 'error' : 'default'
    }}
    priority={action.priority}
    {...props}
  >
    <div className="action-card__content">
      <div className="action-card__details">
        <p><strong>Assignee:</strong> {action.assignee}</p>
        <p><strong>Estimated Hours:</strong> {action.estimatedHours}</p>
        {action.dependencies && (
          <p><strong>Dependencies:</strong> {action.dependencies.join(', ')}</p>
        )}
      </div>
      
      {action.progress !== undefined && (
        <div className="action-card__progress">
          <label>Progress: {Math.round(action.progress * 100)}%</label>
          <div className="neu-progress">
            <div 
              className="neu-progress__bar"
              style={{ width: `${action.progress * 100}%` }}
            />
          </div>
        </div>
      )}
    </div>
  </ExpandableCard>
);

export default ExpandableCard;