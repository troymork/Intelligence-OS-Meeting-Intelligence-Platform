/**
 * User Personalization System
 * Adapts interface behavior to individual preferences and expertise levels
 */

// User preferences manager
class UserPreferencesManager {
  constructor() {
    this.storageKey = 'intelligence-os-user-preferences';
    this.defaultPreferences = {
      // Accessibility preferences
      accessibility: {
        highContrast: false,
        reducedMotion: false,
        largeText: false,
        screenReaderOptimized: false,
        keyboardNavigation: true,
        focusIndicators: true,
        announcements: true
      },
      
      // Interface preferences
      interface: {
        theme: 'auto', // 'light', 'dark', 'auto'
        density: 'comfortable', // 'compact', 'comfortable', 'spacious'
        language: 'en',
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        dateFormat: 'MM/dd/yyyy',
        timeFormat: '12h', // '12h', '24h'
        numberFormat: 'en-US'
      },
      
      // Dashboard preferences
      dashboard: {
        defaultView: 'overview',
        cardLayout: 'grid', // 'grid', 'list'
        autoRefresh: true,
        refreshInterval: 30000, // 30 seconds
        showNotifications: true,
        compactMode: false,
        favoriteWidgets: [],
        hiddenWidgets: []
      },
      
      // Voice interface preferences
      voice: {
        enabled: true,
        wakeWord: 'Oracle',
        voiceSpeed: 1.0,
        voicePitch: 1.0,
        autoListen: false,
        confirmActions: true,
        voiceFeedback: true,
        preferredVoice: null
      },
      
      // Analytics preferences
      analytics: {
        defaultTimeRange: '30d',
        preferredChartTypes: {
          needs: 'radar',
          strategic: 'bar',
          patterns: 'line'
        },
        showAdvancedMetrics: false,
        autoExpandCards: true,
        showTooltips: true,
        animateCharts: true
      },
      
      // Expertise level
      expertise: {
        level: 'intermediate', // 'beginner', 'intermediate', 'advanced', 'expert'
        showHelpTips: true,
        showAdvancedFeatures: false,
        skipOnboarding: false,
        customWorkflows: []
      },
      
      // Privacy preferences
      privacy: {
        shareUsageData: false,
        personalizedRecommendations: true,
        saveSearchHistory: true,
        autoSavePreferences: true,
        dataRetention: '1y' // '30d', '90d', '1y', 'indefinite'
      }
    };
    
    this.preferences = this.loadPreferences();
    this.observers = new Set();
    this.init();
  }

  init() {
    // Apply initial preferences
    this.applyPreferences();
    
    // Listen for system preference changes
    this.setupSystemListeners();
    
    // Auto-save preferences periodically
    if (this.preferences.privacy.autoSavePreferences) {
      setInterval(() => this.savePreferences(), 30000);
    }
  }

  loadPreferences() {
    try {
      const stored = localStorage.getItem(this.storageKey);
      if (stored) {
        const parsed = JSON.parse(stored);
        return this.mergePreferences(this.defaultPreferences, parsed);
      }
    } catch (error) {
      console.warn('Failed to load user preferences:', error);
    }
    
    return { ...this.defaultPreferences };
  }

  mergePreferences(defaults, stored) {
    const merged = { ...defaults };
    
    Object.keys(stored).forEach(category => {
      if (merged[category] && typeof merged[category] === 'object') {
        merged[category] = { ...merged[category], ...stored[category] };
      } else {
        merged[category] = stored[category];
      }
    });
    
    return merged;
  }

  savePreferences() {
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(this.preferences));
      this.notifyObservers('preferences-saved', this.preferences);
    } catch (error) {
      console.error('Failed to save user preferences:', error);
    }
  }

  getPreference(path) {
    const keys = path.split('.');
    let value = this.preferences;
    
    for (const key of keys) {
      if (value && typeof value === 'object' && key in value) {
        value = value[key];
      } else {
        return undefined;
      }
    }
    
    return value;
  }

  setPreference(path, value) {
    const keys = path.split('.');
    const lastKey = keys.pop();
    let target = this.preferences;
    
    for (const key of keys) {
      if (!target[key] || typeof target[key] !== 'object') {
        target[key] = {};
      }
      target = target[key];
    }
    
    const oldValue = target[lastKey];
    target[lastKey] = value;
    
    this.applyPreference(path, value, oldValue);
    this.notifyObservers('preference-changed', { path, value, oldValue });
    
    if (this.preferences.privacy.autoSavePreferences) {
      this.savePreferences();
    }
  }

  applyPreferences() {
    // Apply all preferences
    Object.keys(this.preferences).forEach(category => {
      Object.keys(this.preferences[category]).forEach(key => {
        const path = `${category}.${key}`;
        const value = this.preferences[category][key];
        this.applyPreference(path, value);
      });
    });
  }

  applyPreference(path, value, oldValue) {
    switch (path) {
      case 'interface.theme':
        this.applyTheme(value);
        break;
      case 'interface.density':
        this.applyDensity(value);
        break;
      case 'interface.language':
        this.applyLanguage(value);
        break;
      case 'accessibility.highContrast':
        this.applyHighContrast(value);
        break;
      case 'accessibility.reducedMotion':
        this.applyReducedMotion(value);
        break;
      case 'accessibility.largeText':
        this.applyLargeText(value);
        break;
      case 'dashboard.compactMode':
        this.applyCompactMode(value);
        break;
      case 'voice.enabled':
        this.applyVoiceEnabled(value);
        break;
      case 'expertise.level':
        this.applyExpertiseLevel(value);
        break;
    }
  }

  applyTheme(theme) {
    const root = document.documentElement;
    
    if (theme === 'auto') {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      root.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
    } else {
      root.setAttribute('data-theme', theme);
    }
  }

  applyDensity(density) {
    document.documentElement.setAttribute('data-density', density);
  }

  applyLanguage(language) {
    document.documentElement.setAttribute('lang', language);
    // Trigger language change event for i18n systems
    window.dispatchEvent(new CustomEvent('language-changed', { detail: language }));
  }

  applyHighContrast(enabled) {
    document.documentElement.classList.toggle('high-contrast-user', enabled);
  }

  applyReducedMotion(enabled) {
    document.documentElement.classList.toggle('reduce-motion-user', enabled);
  }

  applyLargeText(enabled) {
    document.documentElement.classList.toggle('large-text', enabled);
  }

  applyCompactMode(enabled) {
    document.documentElement.classList.toggle('compact-mode', enabled);
  }

  applyVoiceEnabled(enabled) {
    window.dispatchEvent(new CustomEvent('voice-preference-changed', { 
      detail: { enabled } 
    }));
  }

  applyExpertiseLevel(level) {
    document.documentElement.setAttribute('data-expertise', level);
    window.dispatchEvent(new CustomEvent('expertise-level-changed', { 
      detail: { level } 
    }));
  }

  setupSystemListeners() {
    // Theme preference changes
    if (window.matchMedia) {
      const themeQuery = window.matchMedia('(prefers-color-scheme: dark)');
      themeQuery.addListener(() => {
        if (this.preferences.interface.theme === 'auto') {
          this.applyTheme('auto');
        }
      });
    }
  }

  // Observer pattern for preference changes
  addObserver(callback) {
    this.observers.add(callback);
  }

  removeObserver(callback) {
    this.observers.delete(callback);
  }

  notifyObservers(event, data) {
    this.observers.forEach(callback => {
      try {
        callback(event, data);
      } catch (error) {
        console.error('Error in preference observer:', error);
      }
    });
  }

  // Export/import preferences
  exportPreferences() {
    return JSON.stringify(this.preferences, null, 2);
  }

  importPreferences(preferencesJson) {
    try {
      const imported = JSON.parse(preferencesJson);
      this.preferences = this.mergePreferences(this.defaultPreferences, imported);
      this.applyPreferences();
      this.savePreferences();
      return true;
    } catch (error) {
      console.error('Failed to import preferences:', error);
      return false;
    }
  }

  resetPreferences() {
    this.preferences = { ...this.defaultPreferences };
    this.applyPreferences();
    this.savePreferences();
  }
}

// Adaptive UI manager
class AdaptiveUIManager {
  constructor(preferencesManager) {
    this.preferencesManager = preferencesManager;
    this.usagePatterns = new Map();
    this.adaptations = new Set();
    this.init();
  }

  init() {
    this.trackUsagePatterns();
    this.setupAdaptiveFeatures();
  }

  trackUsagePatterns() {
    // Track feature usage
    document.addEventListener('click', (event) => {
      const feature = this.identifyFeature(event.target);
      if (feature) {
        this.recordUsage(feature);
      }
    });

    // Track time spent in different sections
    this.setupSectionTracking();
  }

  identifyFeature(element) {
    // Identify features based on data attributes or classes
    const featureAttr = element.getAttribute('data-feature');
    if (featureAttr) return featureAttr;

    const classList = element.classList;
    if (classList.contains('voice-activation')) return 'voice';
    if (classList.contains('analytics-chart')) return 'analytics';
    if (classList.contains('needs-visualization')) return 'human-needs';
    if (classList.contains('strategic-dashboard')) return 'strategic';

    return null;
  }

  recordUsage(feature) {
    const now = Date.now();
    if (!this.usagePatterns.has(feature)) {
      this.usagePatterns.set(feature, {
        count: 0,
        lastUsed: now,
        frequency: 0,
        timeSpent: 0
      });
    }

    const pattern = this.usagePatterns.get(feature);
    pattern.count++;
    pattern.lastUsed = now;
    pattern.frequency = this.calculateFrequency(pattern);
  }

  calculateFrequency(pattern) {
    const daysSinceFirst = (Date.now() - pattern.firstUsed) / (1000 * 60 * 60 * 24);
    return daysSinceFirst > 0 ? pattern.count / daysSinceFirst : 0;
  }

  setupSectionTracking() {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const section = entry.target.getAttribute('data-section');
          if (section) {
            this.startSectionTimer(section);
          }
        } else {
          const section = entry.target.getAttribute('data-section');
          if (section) {
            this.endSectionTimer(section);
          }
        }
      });
    }, { threshold: 0.5 });

    document.querySelectorAll('[data-section]').forEach(section => {
      observer.observe(section);
    });
  }

  startSectionTimer(section) {
    this.sectionStartTime = Date.now();
    this.currentSection = section;
  }

  endSectionTimer(section) {
    if (this.currentSection === section && this.sectionStartTime) {
      const timeSpent = Date.now() - this.sectionStartTime;
      this.recordSectionTime(section, timeSpent);
    }
  }

  recordSectionTime(section, timeSpent) {
    if (!this.usagePatterns.has(section)) {
      this.usagePatterns.set(section, {
        count: 0,
        timeSpent: 0,
        averageTime: 0
      });
    }

    const pattern = this.usagePatterns.get(section);
    pattern.timeSpent += timeSpent;
    pattern.count++;
    pattern.averageTime = pattern.timeSpent / pattern.count;
  }

  setupAdaptiveFeatures() {
    // Adaptive menu ordering
    this.adaptMenuOrder();
    
    // Adaptive widget visibility
    this.adaptWidgetVisibility();
    
    // Adaptive shortcuts
    this.adaptShortcuts();
  }

  adaptMenuOrder() {
    const menuItems = document.querySelectorAll('[data-menu-item]');
    const sortedItems = Array.from(menuItems).sort((a, b) => {
      const featureA = a.getAttribute('data-menu-item');
      const featureB = b.getAttribute('data-menu-item');
      
      const usageA = this.usagePatterns.get(featureA)?.frequency || 0;
      const usageB = this.usagePatterns.get(featureB)?.frequency || 0;
      
      return usageB - usageA; // Sort by frequency descending
    });

    // Reorder menu items
    const menu = menuItems[0]?.parentElement;
    if (menu) {
      sortedItems.forEach(item => menu.appendChild(item));
    }
  }

  adaptWidgetVisibility() {
    const widgets = document.querySelectorAll('[data-widget]');
    const expertiseLevel = this.preferencesManager.getPreference('expertise.level');
    
    widgets.forEach(widget => {
      const widgetLevel = widget.getAttribute('data-expertise-level');
      const widgetFeature = widget.getAttribute('data-widget');
      const usage = this.usagePatterns.get(widgetFeature);
      
      // Hide advanced widgets for beginners unless frequently used
      if (expertiseLevel === 'beginner' && widgetLevel === 'advanced') {
        const isFrequentlyUsed = usage && usage.frequency > 0.1;
        widget.style.display = isFrequentlyUsed ? '' : 'none';
      }
      
      // Show frequently used widgets prominently
      if (usage && usage.frequency > 0.5) {
        widget.classList.add('frequently-used');
      }
    });
  }

  adaptShortcuts() {
    const topFeatures = Array.from(this.usagePatterns.entries())
      .sort(([,a], [,b]) => b.frequency - a.frequency)
      .slice(0, 5)
      .map(([feature]) => feature);

    // Create adaptive shortcuts
    this.createShortcutBar(topFeatures);
  }

  createShortcutBar(features) {
    let shortcutBar = document.getElementById('adaptive-shortcuts');
    if (!shortcutBar) {
      shortcutBar = document.createElement('div');
      shortcutBar.id = 'adaptive-shortcuts';
      shortcutBar.className = 'adaptive-shortcuts';
      document.body.appendChild(shortcutBar);
    }

    shortcutBar.innerHTML = '';
    features.forEach(feature => {
      const shortcut = document.createElement('button');
      shortcut.className = 'adaptive-shortcut';
      shortcut.textContent = this.getFeatureLabel(feature);
      shortcut.onclick = () => this.activateFeature(feature);
      shortcutBar.appendChild(shortcut);
    });
  }

  getFeatureLabel(feature) {
    const labels = {
      voice: '🎤 Voice',
      analytics: '📊 Analytics',
      'human-needs': '❤️ Needs',
      strategic: '🎯 Strategy',
      patterns: '🔍 Patterns'
    };
    return labels[feature] || feature;
  }

  activateFeature(feature) {
    window.dispatchEvent(new CustomEvent('activate-feature', { 
      detail: { feature } 
    }));
  }

  // Get personalized recommendations
  getRecommendations() {
    const recommendations = [];
    const expertiseLevel = this.preferencesManager.getPreference('expertise.level');
    
    // Recommend features based on usage patterns
    const unusedFeatures = this.getUnusedFeatures();
    if (unusedFeatures.length > 0) {
      recommendations.push({
        type: 'feature-discovery',
        title: 'Discover New Features',
        description: `Try these features that might help: ${unusedFeatures.slice(0, 3).join(', ')}`,
        action: 'show-feature-tour'
      });
    }

    // Recommend expertise level adjustment
    const avgUsage = this.getAverageUsageComplexity();
    if (expertiseLevel === 'beginner' && avgUsage > 0.7) {
      recommendations.push({
        type: 'expertise-upgrade',
        title: 'Ready for More?',
        description: 'You seem comfortable with advanced features. Consider upgrading to intermediate level.',
        action: 'upgrade-expertise'
      });
    }

    // Recommend efficiency improvements
    const inefficiencies = this.detectInefficiencies();
    if (inefficiencies.length > 0) {
      recommendations.push({
        type: 'efficiency',
        title: 'Work Smarter',
        description: inefficiencies[0].suggestion,
        action: inefficiencies[0].action
      });
    }

    return recommendations;
  }

  getUnusedFeatures() {
    const allFeatures = ['voice', 'analytics', 'human-needs', 'strategic', 'patterns'];
    return allFeatures.filter(feature => !this.usagePatterns.has(feature));
  }

  getAverageUsageComplexity() {
    const complexFeatures = ['strategic', 'patterns', 'advanced-analytics'];
    const usedComplex = complexFeatures.filter(feature => 
      this.usagePatterns.has(feature) && this.usagePatterns.get(feature).frequency > 0.1
    );
    return usedComplex.length / complexFeatures.length;
  }

  detectInefficiencies() {
    const inefficiencies = [];
    
    // Check for repetitive actions
    const repetitiveActions = Array.from(this.usagePatterns.entries())
      .filter(([, pattern]) => pattern.frequency > 2)
      .map(([feature]) => feature);

    if (repetitiveActions.length > 0) {
      inefficiencies.push({
        type: 'repetitive-action',
        suggestion: 'Consider creating shortcuts for frequently used features',
        action: 'create-shortcuts'
      });
    }

    return inefficiencies;
  }
}

// Context-aware help system
class ContextAwareHelpSystem {
  constructor(preferencesManager) {
    this.preferencesManager = preferencesManager;
    this.helpContent = new Map();
    this.currentContext = null;
    this.init();
  }

  init() {
    this.loadHelpContent();
    this.setupContextDetection();
    this.createHelpInterface();
  }

  loadHelpContent() {
    // Define contextual help content
    this.helpContent.set('voice-interface', {
      title: 'Voice Interface',
      content: 'Use voice commands to interact with the system. Say "Oracle" to activate.',
      tips: [
        'Speak clearly and at normal pace',
        'Use natural language commands',
        'Wait for the activation sound before speaking'
      ],
      shortcuts: [
        { key: 'Space', action: 'Push to talk' },
        { key: 'Esc', action: 'Cancel voice input' }
      ]
    });

    this.helpContent.set('analytics-dashboard', {
      title: 'Analytics Dashboard',
      content: 'View comprehensive analytics and insights about your meetings and team dynamics.',
      tips: [
        'Click on charts to drill down into details',
        'Use time range selector to view historical data',
        'Hover over data points for more information'
      ],
      shortcuts: [
        { key: 'R', action: 'Refresh data' },
        { key: 'F', action: 'Toggle fullscreen' }
      ]
    });

    this.helpContent.set('human-needs', {
      title: 'Human Needs Analysis',
      content: 'Understand individual and team needs fulfillment patterns.',
      tips: [
        'Switch between team and individual views',
        'Look for imbalances highlighted in red',
        'Use trends view to see changes over time'
      ],
      shortcuts: [
        { key: '1', action: 'Team view' },
        { key: '2', action: 'Individual view' },
        { key: '3', action: 'Trends view' }
      ]
    });
  }

  setupContextDetection() {
    // Detect context based on current page/section
    const observer = new MutationObserver(() => {
      this.detectCurrentContext();
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['class', 'data-context']
    });

    // Initial context detection
    this.detectCurrentContext();
  }

  detectCurrentContext() {
    const activeElement = document.activeElement;
    const visibleSections = document.querySelectorAll('[data-context]:not([style*="display: none"])');
    
    let newContext = null;

    // Check for explicit context markers
    if (activeElement && activeElement.getAttribute('data-context')) {
      newContext = activeElement.getAttribute('data-context');
    } else if (visibleSections.length > 0) {
      // Use the most prominent visible section
      newContext = visibleSections[0].getAttribute('data-context');
    }

    if (newContext !== this.currentContext) {
      this.currentContext = newContext;
      this.updateContextualHelp();
    }
  }

  updateContextualHelp() {
    const helpButton = document.getElementById('contextual-help-button');
    if (helpButton && this.currentContext) {
      const helpData = this.helpContent.get(this.currentContext);
      if (helpData) {
        helpButton.style.display = 'block';
        helpButton.title = `Help: ${helpData.title}`;
      } else {
        helpButton.style.display = 'none';
      }
    }
  }

  createHelpInterface() {
    // Create floating help button
    const helpButton = document.createElement('button');
    helpButton.id = 'contextual-help-button';
    helpButton.className = 'contextual-help-button';
    helpButton.innerHTML = '?';
    helpButton.title = 'Get help';
    helpButton.onclick = () => this.showContextualHelp();
    
    // Position button
    helpButton.style.cssText = `
      position: fixed;
      bottom: 20px;
      right: 20px;
      width: 50px;
      height: 50px;
      border-radius: 50%;
      background: var(--accent-color);
      color: white;
      border: none;
      font-size: 20px;
      font-weight: bold;
      cursor: pointer;
      box-shadow: var(--shadow-neu-raised);
      z-index: 1000;
      display: none;
    `;

    document.body.appendChild(helpButton);
  }

  showContextualHelp() {
    if (!this.currentContext) return;

    const helpData = this.helpContent.get(this.currentContext);
    if (!helpData) return;

    this.createHelpModal(helpData);
  }

  createHelpModal(helpData) {
    // Remove existing modal
    const existingModal = document.getElementById('help-modal');
    if (existingModal) {
      existingModal.remove();
    }

    // Create modal
    const modal = document.createElement('div');
    modal.id = 'help-modal';
    modal.className = 'help-modal';
    modal.innerHTML = `
      <div class="help-modal-content">
        <div class="help-modal-header">
          <h2>${helpData.title}</h2>
          <button class="help-modal-close" onclick="this.closest('.help-modal').remove()">×</button>
        </div>
        <div class="help-modal-body">
          <p>${helpData.content}</p>
          
          ${helpData.tips ? `
            <div class="help-section">
              <h3>Tips</h3>
              <ul>
                ${helpData.tips.map(tip => `<li>${tip}</li>`).join('')}
              </ul>
            </div>
          ` : ''}
          
          ${helpData.shortcuts ? `
            <div class="help-section">
              <h3>Keyboard Shortcuts</h3>
              <div class="shortcuts-list">
                ${helpData.shortcuts.map(shortcut => `
                  <div class="shortcut-item">
                    <kbd>${shortcut.key}</kbd>
                    <span>${shortcut.action}</span>
                  </div>
                `).join('')}
              </div>
            </div>
          ` : ''}
        </div>
      </div>
    `;

    // Style modal
    modal.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.5);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 10000;
    `;

    document.body.appendChild(modal);

    // Close on outside click
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.remove();
      }
    });

    // Close on escape key
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        modal.remove();
        document.removeEventListener('keydown', handleEscape);
      }
    };
    document.addEventListener('keydown', handleEscape);
  }

  addHelpContent(context, content) {
    this.helpContent.set(context, content);
  }

  getHelpForContext(context) {
    return this.helpContent.get(context);
  }
}

// Initialize personalization system
let userPreferencesManager;
let adaptiveUIManager;
let contextAwareHelpSystem;

export function initializePersonalization() {
  userPreferencesManager = new UserPreferencesManager();
  adaptiveUIManager = new AdaptiveUIManager(userPreferencesManager);
  contextAwareHelpSystem = new ContextAwareHelpSystem(userPreferencesManager);

  // Make managers globally available
  window.userPreferencesManager = userPreferencesManager;
  window.adaptiveUIManager = adaptiveUIManager;
  window.contextAwareHelpSystem = contextAwareHelpSystem;

  return {
    userPreferencesManager,
    adaptiveUIManager,
    contextAwareHelpSystem
  };
}

export {
  UserPreferencesManager,
  AdaptiveUIManager,
  ContextAwareHelpSystem
};