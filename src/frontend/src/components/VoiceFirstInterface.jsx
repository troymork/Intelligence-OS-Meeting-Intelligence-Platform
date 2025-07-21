/**
 * Voice-First Interface Component
 * Main interface component that combines voice activation with neumorphic design
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import VoiceActivationOrb from './VoiceActivationOrb';
import ExpandableCard, { ExpandableCardGroup, AnalysisCard, ActionCard } from './ExpandableCard';
import './VoiceFirstInterface.css';

const VoiceFirstInterface = ({
  onVoiceCommand,
  onAnalysisRequest,
  analysisResults = [],
  actionItems = [],
  isProcessing = false,
  theme = 'light',
  className = ''
}) => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [confidence, setConfidence] = useState(0);
  const [currentView, setCurrentView] = useState('dashboard');
  const [notifications, setNotifications] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearchFocused, setIsSearchFocused] = useState(false);
  
  const interfaceRef = useRef(null);
  const searchInputRef = useRef(null);
  
  // Voice command handlers
  const handleVoiceStart = useCallback(() => {
    setIsListening(true);
    setTranscript('');
    setConfidence(0);
  }, []);
  
  const handleVoiceEnd = useCallback(() => {
    setIsListening(false);
  }, []);
  
  const handleTranscript = useCallback((text, isFinal) => {
    setTranscript(text);
    
    if (isFinal && text.trim()) {
      // Process voice command
      onVoiceCommand?.(text);
      
      // Parse common voice commands
      parseVoiceCommand(text);
    }
  }, [onVoiceCommand]);
  
  const handleVoiceError = useCallback((error) => {
    console.error('Voice recognition error:', error);
    addNotification({
      type: 'error',
      message: 'Voice recognition error. Please try again.',
      duration: 5000
    });
  }, []);
  
  // Voice command parsing
  const parseVoiceCommand = useCallback((command) => {
    const lowerCommand = command.toLowerCase().trim();
    
    // Navigation commands
    if (lowerCommand.includes('show dashboard') || lowerCommand.includes('go to dashboard')) {
      setCurrentView('dashboard');
      addNotification({ type: 'info', message: 'Switched to dashboard view' });
    } else if (lowerCommand.includes('show analysis') || lowerCommand.includes('analyze')) {
      setCurrentView('analysis');
      if (lowerCommand.includes('meeting') || lowerCommand.includes('transcript')) {
        onAnalysisRequest?.('meeting_analysis');
      }
      addNotification({ type: 'info', message: 'Switched to analysis view' });
    } else if (lowerCommand.includes('show actions') || lowerCommand.includes('action items')) {
      setCurrentView('actions');
      addNotification({ type: 'info', message: 'Switched to actions view' });
    }
    
    // Search commands
    else if (lowerCommand.startsWith('search for ') || lowerCommand.startsWith('find ')) {
      const searchTerm = lowerCommand.replace(/^(search for |find )/, '');
      setSearchQuery(searchTerm);
      searchInputRef.current?.focus();
      addNotification({ type: 'info', message: `Searching for: ${searchTerm}` });
    }
    
    // Theme commands
    else if (lowerCommand.includes('dark mode') || lowerCommand.includes('dark theme')) {
      document.documentElement.setAttribute('data-theme', 'dark');
      addNotification({ type: 'info', message: 'Switched to dark mode' });
    } else if (lowerCommand.includes('light mode') || lowerCommand.includes('light theme')) {
      document.documentElement.setAttribute('data-theme', 'light');
      addNotification({ type: 'info', message: 'Switched to light mode' });
    }
    
    // Help command
    else if (lowerCommand.includes('help') || lowerCommand.includes('what can you do')) {
      showHelpDialog();
    }
    
    // Default: treat as search or analysis request
    else {
      setSearchQuery(command);
      onAnalysisRequest?.(command);
    }
  }, [onAnalysisRequest]);
  
  // Notification system
  const addNotification = useCallback((notification) => {
    const id = Date.now() + Math.random();
    const newNotification = {
      id,
      type: 'info',
      duration: 3000,
      ...notification
    };
    
    setNotifications(prev => [...prev, newNotification]);
    
    // Auto-remove notification
    if (newNotification.duration > 0) {
      setTimeout(() => {
        setNotifications(prev => prev.filter(n => n.id !== id));
      }, newNotification.duration);
    }
  }, []);
  
  const removeNotification = useCallback((id) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  }, []);
  
  // Help dialog
  const showHelpDialog = useCallback(() => {
    addNotification({
      type: 'info',
      message: 'Voice commands: "show dashboard", "analyze meeting", "search for [term]", "dark mode", "help"',
      duration: 8000
    });
  }, [addNotification]);
  
  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (event) => {
      // Global shortcuts
      if (event.ctrlKey || event.metaKey) {
        switch (event.key) {
          case 'k':
            event.preventDefault();
            searchInputRef.current?.focus();
            break;
          case '1':
            event.preventDefault();
            setCurrentView('dashboard');
            break;
          case '2':
            event.preventDefault();
            setCurrentView('analysis');
            break;
          case '3':
            event.preventDefault();
            setCurrentView('actions');
            break;
        }
      }
      
      // Escape key
      if (event.key === 'Escape') {
        setIsSearchFocused(false);
        searchInputRef.current?.blur();
      }
    };
    
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);
  
  // Filter content based on search
  const filteredAnalysisResults = analysisResults.filter(result =>
    !searchQuery || 
    result.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    result.summary.toLowerCase().includes(searchQuery.toLowerCase())
  );
  
  const filteredActionItems = actionItems.filter(action =>
    !searchQuery ||
    action.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    action.description.toLowerCase().includes(searchQuery.toLowerCase())
  );
  
  return (
    <div 
      ref={interfaceRef}
      className={`voice-first-interface ${className}`}
      data-theme={theme}
    >
      {/* Header */}
      <header className="voice-interface__header">
        <div className="voice-interface__header-content">
          {/* Logo/Title */}
          <div className="voice-interface__brand">
            <h1>Intelligence OS</h1>
            <span className="voice-interface__subtitle">Voice-First Analytics</span>
          </div>
          
          {/* Search Bar */}
          <div className="voice-interface__search">
            <div className={`neu-input-group ${isSearchFocused ? 'neu-input-group--focused' : ''}`}>
              <div className="neu-input-group__icon">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
                </svg>
              </div>
              <input
                ref={searchInputRef}
                type="text"
                className="neu-input"
                placeholder="Search or ask a question... (Ctrl+K)"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onFocus={() => setIsSearchFocused(true)}
                onBlur={() => setIsSearchFocused(false)}
              />
            </div>
          </div>
          
          {/* Navigation */}
          <nav className="voice-interface__nav">
            <button
              className={`neu-button ${currentView === 'dashboard' ? 'neu-button--primary' : ''}`}
              onClick={() => setCurrentView('dashboard')}
            >
              Dashboard
            </button>
            <button
              className={`neu-button ${currentView === 'analysis' ? 'neu-button--primary' : ''}`}
              onClick={() => setCurrentView('analysis')}
            >
              Analysis
            </button>
            <button
              className={`neu-button ${currentView === 'actions' ? 'neu-button--primary' : ''}`}
              onClick={() => setCurrentView('actions')}
            >
              Actions
            </button>
          </nav>
          
          {/* Theme Toggle */}
          <div className="voice-interface__theme-toggle">
            <div className="neu-toggle">
              <input
                type="checkbox"
                className="neu-toggle__input"
                id="theme-toggle"
                checked={theme === 'dark'}
                onChange={(e) => {
                  const newTheme = e.target.checked ? 'dark' : 'light';
                  document.documentElement.setAttribute('data-theme', newTheme);
                }}
              />
              <label htmlFor="theme-toggle" className="neu-toggle__slider"></label>
            </div>
          </div>
        </div>
      </header>
      
      {/* Voice Activation Section */}
      <section className="voice-interface__voice-section">
        <VoiceActivationOrb
          size="large"
          isListening={isListening}
          isProcessing={isProcessing}
          confidence={confidence}
          onVoiceStart={handleVoiceStart}
          onVoiceEnd={handleVoiceEnd}
          onTranscript={handleTranscript}
          onError={handleVoiceError}
        />
        
        {/* Live Transcript */}
        {transcript && (
          <div className="voice-interface__transcript">
            <div className="neu-card voice-interface__transcript-card">
              <p className="voice-interface__transcript-text">
                "{transcript}"
              </p>
              {confidence > 0 && (
                <div className="voice-interface__confidence">
                  Confidence: {Math.round(confidence * 100)}%
                </div>
              )}
            </div>
          </div>
        )}
      </section>
      
      {/* Main Content */}
      <main className="voice-interface__main">
        {/* Dashboard View */}
        {currentView === 'dashboard' && (
          <div className="voice-interface__dashboard">
            <ExpandableCardGroup
              title="Dashboard Overview"
              subtitle="Recent activity and key insights"
              layout="grid"
              columns="auto"
            >
              {/* Quick Stats */}
              <ExpandableCard
                title="Recent Activity"
                subtitle="Last 24 hours"
                summary={`${analysisResults.length} analyses, ${actionItems.length} actions`}
                icon={
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z"/>
                  </svg>
                }
                size="medium"
              >
                <div className="dashboard-stats">
                  <div className="dashboard-stat">
                    <span className="dashboard-stat__value">{analysisResults.length}</span>
                    <span className="dashboard-stat__label">Analyses</span>
                  </div>
                  <div className="dashboard-stat">
                    <span className="dashboard-stat__value">{actionItems.length}</span>
                    <span className="dashboard-stat__label">Actions</span>
                  </div>
                  <div className="dashboard-stat">
                    <span className="dashboard-stat__value">
                      {actionItems.filter(a => a.status === 'completed').length}
                    </span>
                    <span className="dashboard-stat__label">Completed</span>
                  </div>
                </div>
              </ExpandableCard>
              
              {/* Recent Analysis Preview */}
              {analysisResults.slice(0, 2).map((analysis, index) => (
                <AnalysisCard
                  key={index}
                  analysis={analysis}
                  size="medium"
                  defaultExpanded={false}
                />
              ))}
              
              {/* Recent Actions Preview */}
              {actionItems.slice(0, 2).map((action, index) => (
                <ActionCard
                  key={index}
                  action={action}
                  size="medium"
                  defaultExpanded={false}
                />
              ))}
            </ExpandableCardGroup>
          </div>
        )}
        
        {/* Analysis View */}
        {currentView === 'analysis' && (
          <div className="voice-interface__analysis">
            <ExpandableCardGroup
              title="Analysis Results"
              subtitle={`${filteredAnalysisResults.length} results found`}
              layout="grid"
              columns="auto"
            >
              {filteredAnalysisResults.map((analysis, index) => (
                <AnalysisCard
                  key={index}
                  analysis={analysis}
                  size="large"
                  defaultExpanded={index === 0}
                />
              ))}
              
              {filteredAnalysisResults.length === 0 && (
                <div className="voice-interface__empty-state">
                  <div className="neu-card">
                    <div className="empty-state">
                      <svg viewBox="0 0 24 24" fill="currentColor">
                        <path d="M9 11H7v6h2v-6zm4 0h-2v6h2v-6zm4 0h-2v6h2v-6zm2.5-9H19V1h-2v1H7V1H5v1H4.5C3.67 2 3 2.67 3 3.5v15C3 19.33 3.67 20 4.5 20h15c.83 0 1.5-.67 1.5-1.5v-15C21 2.67 20.33 2 19.5 2z"/>
                      </svg>
                      <h3>No Analysis Results</h3>
                      <p>Use voice commands or upload a transcript to get started</p>
                    </div>
                  </div>
                </div>
              )}
            </ExpandableCardGroup>
          </div>
        )}
        
        {/* Actions View */}
        {currentView === 'actions' && (
          <div className="voice-interface__actions">
            <ExpandableCardGroup
              title="Action Items"
              subtitle={`${filteredActionItems.length} actions found`}
              layout="list"
            >
              {filteredActionItems.map((action, index) => (
                <ActionCard
                  key={index}
                  action={action}
                  size="medium"
                  defaultExpanded={false}
                />
              ))}
              
              {filteredActionItems.length === 0 && (
                <div className="voice-interface__empty-state">
                  <div className="neu-card">
                    <div className="empty-state">
                      <svg viewBox="0 0 24 24" fill="currentColor">
                        <path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 2 2h8c1.1 0 2-.9 2-2V8l-6-6zm4 18H6V4h7v5h5v11z"/>
                      </svg>
                      <h3>No Action Items</h3>
                      <p>Action items will appear here after analysis</p>
                    </div>
                  </div>
                </div>
              )}
            </ExpandableCardGroup>
          </div>
        )}
      </main>
      
      {/* Notifications */}
      <div className="voice-interface__notifications">
        {notifications.map((notification) => (
          <div
            key={notification.id}
            className={`voice-interface__notification voice-interface__notification--${notification.type}`}
            onClick={() => removeNotification(notification.id)}
          >
            <div className="voice-interface__notification-content">
              <span>{notification.message}</span>
              <button className="voice-interface__notification-close">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                </svg>
              </button>
            </div>
          </div>
        ))}
      </div>
      
      {/* Loading Overlay */}
      {isProcessing && (
        <div className="voice-interface__loading-overlay">
          <div className="voice-interface__loading-content">
            <div className="voice-interface__loading-spinner" />
            <p>Processing your request...</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default VoiceFirstInterface;