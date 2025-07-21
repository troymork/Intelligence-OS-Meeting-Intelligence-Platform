/**
 * User Feedback Collection and Analysis System
 * Collects user feedback for continuous interface improvement
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import './UserFeedbackSystem.css';

// Feedback collection component
const FeedbackCollector = ({ 
  isVisible, 
  onSubmit, 
  onClose,
  context = {},
  type = 'general' // 'general', 'feature', 'bug', 'suggestion'
}) => {
  const [feedbackData, setFeedbackData] = useState({
    type,
    rating: 0,
    category: '',
    title: '',
    description: '',
    email: '',
    includeScreenshot: false,
    context: context
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [screenshot, setScreenshot] = useState(null);
  const modalRef = useRef(null);

  const categories = {
    general: ['User Interface', 'Performance', 'Accessibility', 'Documentation', 'Other'],
    feature: ['Voice Interface', 'Analytics', 'Human Needs', 'Strategic Alignment', 'Integrations'],
    bug: ['Visual Bug', 'Functionality Issue', 'Performance Problem', 'Data Issue', 'Crash'],
    suggestion: ['New Feature', 'Improvement', 'Integration', 'Workflow', 'Design']
  };

  useEffect(() => {
    if (isVisible && modalRef.current) {
      modalRef.current.focus();
    }
  }, [isVisible]);

  const handleInputChange = (field, value) => {
    setFeedbackData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleRatingChange = (rating) => {
    setFeedbackData(prev => ({
      ...prev,
      rating
    }));
  };

  const captureScreenshot = async () => {
    try {
      if (navigator.mediaDevices && navigator.mediaDevices.getDisplayMedia) {
        const stream = await navigator.mediaDevices.getDisplayMedia({
          video: { mediaSource: 'screen' }
        });
        
        const video = document.createElement('video');
        video.srcObject = stream;
        video.play();
        
        video.addEventListener('loadedmetadata', () => {
          const canvas = document.createElement('canvas');
          canvas.width = video.videoWidth;
          canvas.height = video.videoHeight;
          
          const ctx = canvas.getContext('2d');
          ctx.drawImage(video, 0, 0);
          
          canvas.toBlob(blob => {
            setScreenshot(blob);
            setFeedbackData(prev => ({
              ...prev,
              includeScreenshot: true
            }));
          });
          
          stream.getTracks().forEach(track => track.stop());
        });
      } else {
        // Fallback: use html2canvas if available
        if (window.html2canvas) {
          const canvas = await window.html2canvas(document.body);
          canvas.toBlob(blob => {
            setScreenshot(blob);
            setFeedbackData(prev => ({
              ...prev,
              includeScreenshot: true
            }));
          });
        }
      }
    } catch (error) {
      console.error('Failed to capture screenshot:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const formData = new FormData();
      Object.keys(feedbackData).forEach(key => {
        if (key !== 'context') {
          formData.append(key, feedbackData[key]);
        }
      });
      
      formData.append('context', JSON.stringify(feedbackData.context));
      formData.append('timestamp', new Date().toISOString());
      formData.append('userAgent', navigator.userAgent);
      formData.append('url', window.location.href);
      
      if (screenshot) {
        formData.append('screenshot', screenshot, 'screenshot.png');
      }

      await onSubmit(formData);
      onClose();
    } catch (error) {
      console.error('Failed to submit feedback:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const isValid = feedbackData.title.trim() && feedbackData.description.trim();

  if (!isVisible) return null;

  return (
    <div className="feedback-collector">
      <div className="feedback-overlay" onClick={onClose} />
      <div 
        ref={modalRef}
        className="feedback-modal"
        tabIndex={-1}
        role="dialog"
        aria-labelledby="feedback-title"
        aria-describedby="feedback-description"
      >
        <div className="feedback-modal__header">
          <h2 id="feedback-title">Share Your Feedback</h2>
          <button 
            className="feedback-modal__close"
            onClick={onClose}
            aria-label="Close feedback form"
          >
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} className="feedback-form">
          <div className="feedback-form__body">
            {/* Rating */}
            <div className="feedback-field">
              <label className="feedback-label">
                How would you rate your experience?
              </label>
              <div className="rating-input">
                {[1, 2, 3, 4, 5].map(star => (
                  <button
                    key={star}
                    type="button"
                    className={`rating-star ${feedbackData.rating >= star ? 'active' : ''}`}
                    onClick={() => handleRatingChange(star)}
                    aria-label={`Rate ${star} star${star > 1 ? 's' : ''}`}
                  >
                    ★
                  </button>
                ))}
              </div>
            </div>

            {/* Category */}
            <div className="feedback-field">
              <label htmlFor="feedback-category" className="feedback-label">
                Category
              </label>
              <select
                id="feedback-category"
                className="feedback-select"
                value={feedbackData.category}
                onChange={(e) => handleInputChange('category', e.target.value)}
                required
              >
                <option value="">Select a category</option>
                {categories[feedbackData.type]?.map(category => (
                  <option key={category} value={category}>
                    {category}
                  </option>
                ))}
              </select>
            </div>

            {/* Title */}
            <div className="feedback-field">
              <label htmlFor="feedback-title" className="feedback-label">
                Title *
              </label>
              <input
                id="feedback-title"
                type="text"
                className="feedback-input"
                placeholder="Brief summary of your feedback"
                value={feedbackData.title}
                onChange={(e) => handleInputChange('title', e.target.value)}
                required
              />
            </div>

            {/* Description */}
            <div className="feedback-field">
              <label htmlFor="feedback-description" className="feedback-label">
                Description *
              </label>
              <textarea
                id="feedback-description"
                className="feedback-textarea"
                placeholder="Please provide detailed feedback..."
                rows={5}
                value={feedbackData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                required
              />
            </div>

            {/* Email (optional) */}
            <div className="feedback-field">
              <label htmlFor="feedback-email" className="feedback-label">
                Email (optional)
              </label>
              <input
                id="feedback-email"
                type="email"
                className="feedback-input"
                placeholder="your.email@example.com"
                value={feedbackData.email}
                onChange={(e) => handleInputChange('email', e.target.value)}
              />
              <small className="feedback-help">
                We'll only use this to follow up on your feedback
              </small>
            </div>

            {/* Screenshot option */}
            <div className="feedback-field">
              <div className="feedback-checkbox">
                <input
                  id="include-screenshot"
                  type="checkbox"
                  checked={feedbackData.includeScreenshot}
                  onChange={(e) => handleInputChange('includeScreenshot', e.target.checked)}
                />
                <label htmlFor="include-screenshot">
                  Include screenshot
                </label>
              </div>
              {feedbackData.includeScreenshot && !screenshot && (
                <button
                  type="button"
                  className="screenshot-button"
                  onClick={captureScreenshot}
                >
                  📷 Capture Screenshot
                </button>
              )}
              {screenshot && (
                <div className="screenshot-preview">
                  <span>Screenshot captured ✓</span>
                  <button
                    type="button"
                    onClick={() => {
                      setScreenshot(null);
                      setFeedbackData(prev => ({ ...prev, includeScreenshot: false }));
                    }}
                  >
                    Remove
                  </button>
                </div>
              )}
            </div>
          </div>

          <div className="feedback-form__footer">
            <button
              type="button"
              className="feedback-button feedback-button--secondary"
              onClick={onClose}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="feedback-button feedback-button--primary"
              disabled={!isValid || isSubmitting}
            >
              {isSubmitting ? 'Submitting...' : 'Submit Feedback'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Quick feedback widget
const QuickFeedbackWidget = ({ onFeedbackSubmit }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [quickRating, setQuickRating] = useState(0);
  const [quickComment, setQuickComment] = useState('');

  const handleQuickSubmit = async () => {
    if (quickRating > 0) {
      const feedbackData = {
        type: 'quick',
        rating: quickRating,
        description: quickComment,
        timestamp: new Date().toISOString(),
        context: {
          page: window.location.pathname,
          userAgent: navigator.userAgent
        }
      };

      await onFeedbackSubmit(feedbackData);
      setIsExpanded(false);
      setQuickRating(0);
      setQuickComment('');
    }
  };

  return (
    <div className={`quick-feedback-widget ${isExpanded ? 'expanded' : ''}`}>
      {!isExpanded ? (
        <button
          className="quick-feedback-trigger"
          onClick={() => setIsExpanded(true)}
          aria-label="Quick feedback"
        >
          💬
        </button>
      ) : (
        <div className="quick-feedback-form">
          <div className="quick-feedback-header">
            <span>Quick Feedback</span>
            <button
              className="quick-feedback-close"
              onClick={() => setIsExpanded(false)}
              aria-label="Close quick feedback"
            >
              ×
            </button>
          </div>
          
          <div className="quick-rating">
            {[1, 2, 3, 4, 5].map(star => (
              <button
                key={star}
                className={`quick-rating-star ${quickRating >= star ? 'active' : ''}`}
                onClick={() => setQuickRating(star)}
                aria-label={`Rate ${star} star${star > 1 ? 's' : ''}`}
              >
                ★
              </button>
            ))}
          </div>
          
          <textarea
            className="quick-comment"
            placeholder="Any additional comments? (optional)"
            value={quickComment}
            onChange={(e) => setQuickComment(e.target.value)}
            rows={2}
          />
          
          <button
            className="quick-submit"
            onClick={handleQuickSubmit}
            disabled={quickRating === 0}
          >
            Submit
          </button>
        </div>
      )}
    </div>
  );
};

// Feedback analytics dashboard
const FeedbackAnalytics = ({ feedbackData = [] }) => {
  const [timeRange, setTimeRange] = useState('30d');
  const [selectedCategory, setSelectedCategory] = useState('all');

  const filteredFeedback = feedbackData.filter(feedback => {
    const feedbackDate = new Date(feedback.timestamp);
    const now = new Date();
    const daysAgo = {
      '7d': 7,
      '30d': 30,
      '90d': 90,
      '1y': 365
    }[timeRange];

    const isInTimeRange = (now - feedbackDate) / (1000 * 60 * 60 * 24) <= daysAgo;
    const isInCategory = selectedCategory === 'all' || feedback.category === selectedCategory;

    return isInTimeRange && isInCategory;
  });

  const averageRating = filteredFeedback.length > 0 
    ? filteredFeedback.reduce((sum, f) => sum + (f.rating || 0), 0) / filteredFeedback.length
    : 0;

  const categoryBreakdown = filteredFeedback.reduce((acc, feedback) => {
    const category = feedback.category || 'Uncategorized';
    acc[category] = (acc[category] || 0) + 1;
    return acc;
  }, {});

  const ratingDistribution = filteredFeedback.reduce((acc, feedback) => {
    const rating = feedback.rating || 0;
    acc[rating] = (acc[rating] || 0) + 1;
    return acc;
  }, {});

  return (
    <div className="feedback-analytics">
      <div className="analytics-header">
        <h2>Feedback Analytics</h2>
        <div className="analytics-controls">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="analytics-select"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
            <option value="1y">Last year</option>
          </select>
          
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="analytics-select"
          >
            <option value="all">All Categories</option>
            {Object.keys(categoryBreakdown).map(category => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="analytics-metrics">
        <div className="metric-card">
          <div className="metric-value">{filteredFeedback.length}</div>
          <div className="metric-label">Total Feedback</div>
        </div>
        
        <div className="metric-card">
          <div className="metric-value">{averageRating.toFixed(1)}</div>
          <div className="metric-label">Average Rating</div>
        </div>
        
        <div className="metric-card">
          <div className="metric-value">
            {Object.keys(categoryBreakdown).length}
          </div>
          <div className="metric-label">Categories</div>
        </div>
      </div>

      <div className="analytics-charts">
        <div className="chart-section">
          <h3>Rating Distribution</h3>
          <div className="rating-chart">
            {[1, 2, 3, 4, 5].map(rating => (
              <div key={rating} className="rating-bar">
                <span className="rating-label">{rating}★</span>
                <div className="rating-bar-container">
                  <div 
                    className="rating-bar-fill"
                    style={{ 
                      width: `${(ratingDistribution[rating] || 0) / filteredFeedback.length * 100}%` 
                    }}
                  />
                </div>
                <span className="rating-count">{ratingDistribution[rating] || 0}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="chart-section">
          <h3>Category Breakdown</h3>
          <div className="category-chart">
            {Object.entries(categoryBreakdown).map(([category, count]) => (
              <div key={category} className="category-item">
                <span className="category-name">{category}</span>
                <div className="category-bar-container">
                  <div 
                    className="category-bar-fill"
                    style={{ 
                      width: `${count / filteredFeedback.length * 100}%` 
                    }}
                  />
                </div>
                <span className="category-count">{count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="recent-feedback">
        <h3>Recent Feedback</h3>
        <div className="feedback-list">
          {filteredFeedback.slice(0, 10).map((feedback, index) => (
            <div key={index} className="feedback-item">
              <div className="feedback-item-header">
                <div className="feedback-rating">
                  {'★'.repeat(feedback.rating || 0)}
                </div>
                <div className="feedback-category">{feedback.category}</div>
                <div className="feedback-date">
                  {new Date(feedback.timestamp).toLocaleDateString()}
                </div>
              </div>
              <div className="feedback-title">{feedback.title}</div>
              <div className="feedback-description">{feedback.description}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Main feedback system component
const UserFeedbackSystem = ({ 
  onFeedbackSubmit,
  showQuickWidget = true,
  showAnalytics = false,
  feedbackData = []
}) => {
  const [showFeedbackForm, setShowFeedbackForm] = useState(false);
  const [feedbackType, setFeedbackType] = useState('general');
  const [feedbackContext, setFeedbackContext] = useState({});

  // Listen for feedback requests from other components
  useEffect(() => {
    const handleFeedbackRequest = (event) => {
      const { type = 'general', context = {} } = event.detail || {};
      setFeedbackType(type);
      setFeedbackContext(context);
      setShowFeedbackForm(true);
    };

    window.addEventListener('request-feedback', handleFeedbackRequest);
    return () => window.removeEventListener('request-feedback', handleFeedbackRequest);
  }, []);

  const handleFeedbackSubmit = async (feedbackData) => {
    try {
      await onFeedbackSubmit(feedbackData);
      
      // Show success message
      window.dispatchEvent(new CustomEvent('show-notification', {
        detail: {
          type: 'success',
          message: 'Thank you for your feedback! We appreciate your input.',
          duration: 5000
        }
      }));
    } catch (error) {
      console.error('Failed to submit feedback:', error);
      
      // Show error message
      window.dispatchEvent(new CustomEvent('show-notification', {
        detail: {
          type: 'error',
          message: 'Failed to submit feedback. Please try again.',
          duration: 5000
        }
      }));
    }
  };

  // Expose feedback system globally
  useEffect(() => {
    window.feedbackSystem = {
      showFeedbackForm: (type = 'general', context = {}) => {
        setFeedbackType(type);
        setFeedbackContext(context);
        setShowFeedbackForm(true);
      },
      requestFeedback: (type, context) => {
        window.dispatchEvent(new CustomEvent('request-feedback', {
          detail: { type, context }
        }));
      }
    };
  }, []);

  return (
    <>
      <FeedbackCollector
        isVisible={showFeedbackForm}
        onSubmit={handleFeedbackSubmit}
        onClose={() => setShowFeedbackForm(false)}
        type={feedbackType}
        context={feedbackContext}
      />
      
      {showQuickWidget && (
        <QuickFeedbackWidget onFeedbackSubmit={handleFeedbackSubmit} />
      )}
      
      {showAnalytics && (
        <FeedbackAnalytics feedbackData={feedbackData} />
      )}
    </>
  );
};

export default UserFeedbackSystem;
export { FeedbackCollector, QuickFeedbackWidget, FeedbackAnalytics };