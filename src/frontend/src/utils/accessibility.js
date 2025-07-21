/**
 * Accessibility Utilities and WCAG Compliance System
 * Provides comprehensive accessibility features and assistive technology support
 */

// ARIA live region manager for dynamic content announcements
class AriaLiveRegionManager {
  constructor() {
    this.regions = new Map();
    this.init();
  }

  init() {
    // Create live regions if they don't exist
    this.createLiveRegion('polite', 'aria-live-polite');
    this.createLiveRegion('assertive', 'aria-live-assertive');
    this.createLiveRegion('status', 'aria-live-status');
  }

  createLiveRegion(type, id) {
    if (!document.getElementById(id)) {
      const region = document.createElement('div');
      region.id = id;
      region.setAttribute('aria-live', type === 'status' ? 'polite' : type);
      region.setAttribute('aria-atomic', 'true');
      region.className = 'sr-only';
      region.style.cssText = `
        position: absolute !important;
        width: 1px !important;
        height: 1px !important;
        padding: 0 !important;
        margin: -1px !important;
        overflow: hidden !important;
        clip: rect(0, 0, 0, 0) !important;
        white-space: nowrap !important;
        border: 0 !important;
      `;
      document.body.appendChild(region);
      this.regions.set(type, region);
    } else {
      this.regions.set(type, document.getElementById(id));
    }
  }

  announce(message, type = 'polite') {
    const region = this.regions.get(type);
    if (region) {
      // Clear and set message to ensure it's announced
      region.textContent = '';
      setTimeout(() => {
        region.textContent = message;
      }, 100);
    }
  }

  announceStatus(message) {
    this.announce(message, 'status');
  }

  announceAlert(message) {
    this.announce(message, 'assertive');
  }
}

// Keyboard navigation manager
class KeyboardNavigationManager {
  constructor() {
    this.focusableElements = [
      'a[href]',
      'button:not([disabled])',
      'input:not([disabled])',
      'select:not([disabled])',
      'textarea:not([disabled])',
      '[tabindex]:not([tabindex="-1"])',
      '[contenteditable="true"]'
    ].join(', ');
    
    this.trapStack = [];
    this.init();
  }

  init() {
    // Add global keyboard event listeners
    document.addEventListener('keydown', this.handleGlobalKeydown.bind(this));
  }

  handleGlobalKeydown(event) {
    // Handle escape key for modal/dialog closing
    if (event.key === 'Escape' && this.trapStack.length > 0) {
      const currentTrap = this.trapStack[this.trapStack.length - 1];
      if (currentTrap.onEscape) {
        currentTrap.onEscape();
      }
    }

    // Handle tab navigation in focus traps
    if (event.key === 'Tab' && this.trapStack.length > 0) {
      this.handleTrapTabNavigation(event);
    }
  }

  handleTrapTabNavigation(event) {
    const currentTrap = this.trapStack[this.trapStack.length - 1];
    const focusableElements = this.getFocusableElements(currentTrap.container);
    
    if (focusableElements.length === 0) return;

    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    if (event.shiftKey) {
      // Shift + Tab
      if (document.activeElement === firstElement) {
        event.preventDefault();
        lastElement.focus();
      }
    } else {
      // Tab
      if (document.activeElement === lastElement) {
        event.preventDefault();
        firstElement.focus();
      }
    }
  }

  getFocusableElements(container) {
    return Array.from(container.querySelectorAll(this.focusableElements))
      .filter(element => this.isVisible(element) && !element.disabled);
  }

  isVisible(element) {
    const style = window.getComputedStyle(element);
    return style.display !== 'none' && 
           style.visibility !== 'hidden' && 
           style.opacity !== '0';
  }

  trapFocus(container, options = {}) {
    const trap = {
      container,
      previousActiveElement: document.activeElement,
      onEscape: options.onEscape,
      restoreFocus: options.restoreFocus !== false
    };

    this.trapStack.push(trap);

    // Focus first focusable element
    const focusableElements = this.getFocusableElements(container);
    if (focusableElements.length > 0) {
      focusableElements[0].focus();
    }

    return trap;
  }

  releaseFocus(trap) {
    const index = this.trapStack.indexOf(trap);
    if (index > -1) {
      this.trapStack.splice(index, 1);
      
      if (trap.restoreFocus && trap.previousActiveElement) {
        trap.previousActiveElement.focus();
      }
    }
  }

  releaseAllFocus() {
    while (this.trapStack.length > 0) {
      const trap = this.trapStack.pop();
      if (trap.restoreFocus && trap.previousActiveElement) {
        trap.previousActiveElement.focus();
      }
    }
  }
}

// Color contrast checker
class ColorContrastChecker {
  constructor() {
    this.wcagAAThreshold = 4.5;
    this.wcagAAAThreshold = 7;
    this.wcagAALargeThreshold = 3;
    this.wcagAAALargeThreshold = 4.5;
  }

  // Calculate relative luminance
  getRelativeLuminance(rgb) {
    const [r, g, b] = rgb.map(c => {
      c = c / 255;
      return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    });
    
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  }

  // Calculate contrast ratio between two colors
  getContrastRatio(color1, color2) {
    const l1 = this.getRelativeLuminance(color1);
    const l2 = this.getRelativeLuminance(color2);
    
    const lighter = Math.max(l1, l2);
    const darker = Math.min(l1, l2);
    
    return (lighter + 0.05) / (darker + 0.05);
  }

  // Parse color string to RGB array
  parseColor(colorString) {
    const canvas = document.createElement('canvas');
    canvas.width = canvas.height = 1;
    const ctx = canvas.getContext('2d');
    
    ctx.fillStyle = colorString;
    ctx.fillRect(0, 0, 1, 1);
    
    const imageData = ctx.getImageData(0, 0, 1, 1);
    return [imageData.data[0], imageData.data[1], imageData.data[2]];
  }

  // Check if contrast meets WCAG standards
  checkContrast(foreground, background, isLargeText = false) {
    const fgRgb = this.parseColor(foreground);
    const bgRgb = this.parseColor(background);
    const ratio = this.getContrastRatio(fgRgb, bgRgb);

    const aaThreshold = isLargeText ? this.wcagAALargeThreshold : this.wcagAAThreshold;
    const aaaThreshold = isLargeText ? this.wcagAAALargeThreshold : this.wcagAAAThreshold;

    return {
      ratio: Math.round(ratio * 100) / 100,
      passAA: ratio >= aaThreshold,
      passAAA: ratio >= aaaThreshold,
      level: ratio >= aaaThreshold ? 'AAA' : ratio >= aaThreshold ? 'AA' : 'Fail'
    };
  }

  // Audit page for contrast issues
  auditPageContrast() {
    const issues = [];
    const elements = document.querySelectorAll('*');

    elements.forEach(element => {
      const styles = window.getComputedStyle(element);
      const color = styles.color;
      const backgroundColor = styles.backgroundColor;
      
      if (color && backgroundColor && backgroundColor !== 'rgba(0, 0, 0, 0)') {
        const fontSize = parseFloat(styles.fontSize);
        const fontWeight = styles.fontWeight;
        const isLargeText = fontSize >= 18 || (fontSize >= 14 && (fontWeight === 'bold' || parseInt(fontWeight) >= 700));
        
        const result = this.checkContrast(color, backgroundColor, isLargeText);
        
        if (!result.passAA) {
          issues.push({
            element,
            foreground: color,
            background: backgroundColor,
            ratio: result.ratio,
            level: result.level,
            isLargeText,
            recommendation: this.getContrastRecommendation(result, isLargeText)
          });
        }
      }
    });

    return issues;
  }

  getContrastRecommendation(result, isLargeText) {
    const requiredRatio = isLargeText ? this.wcagAALargeThreshold : this.wcagAAThreshold;
    const improvement = requiredRatio - result.ratio;
    
    return {
      currentRatio: result.ratio,
      requiredRatio,
      improvement: Math.round(improvement * 100) / 100,
      suggestion: improvement > 0 ? 
        `Increase contrast by ${Math.round(improvement * 100) / 100} to meet WCAG AA standards` :
        'Contrast meets WCAG AA standards'
    };
  }
}

// Screen reader utilities
class ScreenReaderUtils {
  constructor() {
    this.isScreenReaderActive = this.detectScreenReader();
  }

  detectScreenReader() {
    // Check for common screen reader indicators
    return !!(
      window.navigator.userAgent.match(/NVDA|JAWS|VoiceOver|TalkBack|Orca/i) ||
      window.speechSynthesis ||
      document.querySelector('[aria-hidden="true"]') ||
      window.navigator.userAgent.includes('aXe')
    );
  }

  // Create descriptive text for complex UI elements
  createDescription(element, context = {}) {
    const descriptions = [];
    
    // Element type
    const role = element.getAttribute('role') || element.tagName.toLowerCase();
    descriptions.push(this.getRoleDescription(role));
    
    // Element state
    if (element.disabled) descriptions.push('disabled');
    if (element.checked !== undefined) {
      descriptions.push(element.checked ? 'checked' : 'unchecked');
    }
    if (element.selected) descriptions.push('selected');
    if (element.expanded !== undefined) {
      descriptions.push(element.expanded ? 'expanded' : 'collapsed');
    }
    
    // Position information
    if (context.position) {
      descriptions.push(`${context.position.current} of ${context.position.total}`);
    }
    
    // Additional context
    if (context.group) {
      descriptions.push(`in ${context.group}`);
    }
    
    return descriptions.join(', ');
  }

  getRoleDescription(role) {
    const roleDescriptions = {
      button: 'button',
      link: 'link',
      heading: 'heading',
      list: 'list',
      listitem: 'list item',
      table: 'table',
      row: 'row',
      cell: 'cell',
      dialog: 'dialog',
      menu: 'menu',
      menuitem: 'menu item',
      tab: 'tab',
      tabpanel: 'tab panel',
      checkbox: 'checkbox',
      radio: 'radio button',
      textbox: 'text input',
      combobox: 'combo box',
      slider: 'slider'
    };
    
    return roleDescriptions[role] || role;
  }

  // Announce dynamic content changes
  announceChange(message, priority = 'polite') {
    if (this.isScreenReaderActive) {
      window.ariaLiveManager?.announce(message, priority);
    }
  }

  // Create skip links for navigation
  createSkipLinks(targets) {
    const skipContainer = document.createElement('div');
    skipContainer.className = 'skip-links';
    skipContainer.setAttribute('aria-label', 'Skip navigation links');
    
    targets.forEach(target => {
      const skipLink = document.createElement('a');
      skipLink.href = `#${target.id}`;
      skipLink.textContent = target.label;
      skipLink.className = 'skip-link';
      skipContainer.appendChild(skipLink);
    });
    
    document.body.insertBefore(skipContainer, document.body.firstChild);
    return skipContainer;
  }
}

// High contrast mode manager
class HighContrastManager {
  constructor() {
    this.isHighContrast = this.detectHighContrast();
    this.init();
  }

  detectHighContrast() {
    // Check for Windows high contrast mode
    if (window.matchMedia) {
      return window.matchMedia('(-ms-high-contrast: active)').matches ||
             window.matchMedia('(prefers-contrast: high)').matches;
    }
    return false;
  }

  init() {
    if (window.matchMedia) {
      // Listen for high contrast changes
      const mediaQuery = window.matchMedia('(prefers-contrast: high)');
      mediaQuery.addListener(this.handleContrastChange.bind(this));
      
      // Apply initial state
      this.applyHighContrastStyles(this.isHighContrast);
    }
  }

  handleContrastChange(e) {
    this.isHighContrast = e.matches;
    this.applyHighContrastStyles(this.isHighContrast);
  }

  applyHighContrastStyles(isHighContrast) {
    document.documentElement.classList.toggle('high-contrast', isHighContrast);
    
    if (isHighContrast) {
      // Apply high contrast overrides
      this.addHighContrastCSS();
    } else {
      // Remove high contrast overrides
      this.removeHighContrastCSS();
    }
  }

  addHighContrastCSS() {
    if (!document.getElementById('high-contrast-styles')) {
      const style = document.createElement('style');
      style.id = 'high-contrast-styles';
      style.textContent = `
        .high-contrast {
          --text-primary: #ffffff !important;
          --text-secondary: #ffffff !important;
          --text-muted: #cccccc !important;
          --primary-bg: #000000 !important;
          --secondary-bg: #1a1a1a !important;
          --accent-color: #ffff00 !important;
          --border-color: #ffffff !important;
          --success-color: #00ff00 !important;
          --warning-color: #ffff00 !important;
          --error-color: #ff0000 !important;
        }
        
        .high-contrast * {
          background-image: none !important;
          box-shadow: none !important;
          text-shadow: none !important;
        }
        
        .high-contrast button,
        .high-contrast input,
        .high-contrast select,
        .high-contrast textarea {
          border: 2px solid #ffffff !important;
        }
        
        .high-contrast a {
          color: #ffff00 !important;
          text-decoration: underline !important;
        }
        
        .high-contrast a:visited {
          color: #ff00ff !important;
        }
      `;
      document.head.appendChild(style);
    }
  }

  removeHighContrastCSS() {
    const style = document.getElementById('high-contrast-styles');
    if (style) {
      style.remove();
    }
  }
}

// Motion preferences manager
class MotionPreferencesManager {
  constructor() {
    this.prefersReducedMotion = this.detectReducedMotion();
    this.init();
  }

  detectReducedMotion() {
    if (window.matchMedia) {
      return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    }
    return false;
  }

  init() {
    if (window.matchMedia) {
      const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
      mediaQuery.addListener(this.handleMotionChange.bind(this));
      
      this.applyMotionPreferences(this.prefersReducedMotion);
    }
  }

  handleMotionChange(e) {
    this.prefersReducedMotion = e.matches;
    this.applyMotionPreferences(this.prefersReducedMotion);
  }

  applyMotionPreferences(reduceMotion) {
    document.documentElement.classList.toggle('reduce-motion', reduceMotion);
    
    if (reduceMotion) {
      this.addReducedMotionCSS();
    } else {
      this.removeReducedMotionCSS();
    }
  }

  addReducedMotionCSS() {
    if (!document.getElementById('reduced-motion-styles')) {
      const style = document.createElement('style');
      style.id = 'reduced-motion-styles';
      style.textContent = `
        .reduce-motion *,
        .reduce-motion *::before,
        .reduce-motion *::after {
          animation-duration: 0.01ms !important;
          animation-iteration-count: 1 !important;
          transition-duration: 0.01ms !important;
          scroll-behavior: auto !important;
        }
        
        .reduce-motion .parallax {
          transform: none !important;
        }
      `;
      document.head.appendChild(style);
    }
  }

  removeReducedMotionCSS() {
    const style = document.getElementById('reduced-motion-styles');
    if (style) {
      style.remove();
    }
  }
}

// Initialize accessibility managers
let ariaLiveManager;
let keyboardNavigationManager;
let colorContrastChecker;
let screenReaderUtils;
let highContrastManager;
let motionPreferencesManager;

// Initialize all accessibility features
export function initializeAccessibility() {
  ariaLiveManager = new AriaLiveRegionManager();
  keyboardNavigationManager = new KeyboardNavigationManager();
  colorContrastChecker = new ColorContrastChecker();
  screenReaderUtils = new ScreenReaderUtils();
  highContrastManager = new HighContrastManager();
  motionPreferencesManager = new MotionPreferencesManager();
  
  // Make managers globally available
  window.ariaLiveManager = ariaLiveManager;
  window.keyboardNavigationManager = keyboardNavigationManager;
  window.colorContrastChecker = colorContrastChecker;
  window.screenReaderUtils = screenReaderUtils;
  window.highContrastManager = highContrastManager;
  window.motionPreferencesManager = motionPreferencesManager;
  
  return {
    ariaLiveManager,
    keyboardNavigationManager,
    colorContrastChecker,
    screenReaderUtils,
    highContrastManager,
    motionPreferencesManager
  };
}

// Export individual utilities
export {
  AriaLiveRegionManager,
  KeyboardNavigationManager,
  ColorContrastChecker,
  ScreenReaderUtils,
  HighContrastManager,
  MotionPreferencesManager
};

// Accessibility testing utilities
export const AccessibilityTester = {
  // Run comprehensive accessibility audit
  async runAudit() {
    const results = {
      timestamp: new Date().toISOString(),
      colorContrast: colorContrastChecker?.auditPageContrast() || [],
      missingAltText: this.checkMissingAltText(),
      missingLabels: this.checkMissingLabels(),
      keyboardNavigation: this.checkKeyboardNavigation(),
      headingStructure: this.checkHeadingStructure(),
      landmarks: this.checkLandmarks(),
      focusManagement: this.checkFocusManagement()
    };
    
    return results;
  },
  
  checkMissingAltText() {
    const images = document.querySelectorAll('img');
    const issues = [];
    
    images.forEach(img => {
      if (!img.alt && !img.getAttribute('aria-label') && !img.getAttribute('aria-labelledby')) {
        issues.push({
          element: img,
          issue: 'Missing alt text',
          recommendation: 'Add descriptive alt text or aria-label'
        });
      }
    });
    
    return issues;
  },
  
  checkMissingLabels() {
    const formElements = document.querySelectorAll('input, select, textarea');
    const issues = [];
    
    formElements.forEach(element => {
      const hasLabel = element.labels && element.labels.length > 0;
      const hasAriaLabel = element.getAttribute('aria-label');
      const hasAriaLabelledby = element.getAttribute('aria-labelledby');
      
      if (!hasLabel && !hasAriaLabel && !hasAriaLabelledby) {
        issues.push({
          element,
          issue: 'Missing label',
          recommendation: 'Add label element or aria-label attribute'
        });
      }
    });
    
    return issues;
  },
  
  checkKeyboardNavigation() {
    const focusableElements = document.querySelectorAll(
      'a[href], button, input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const issues = [];
    
    focusableElements.forEach(element => {
      if (element.tabIndex < 0 && element.tabIndex !== -1) {
        issues.push({
          element,
          issue: 'Invalid tabindex',
          recommendation: 'Use tabindex="0" or remove tabindex attribute'
        });
      }
    });
    
    return issues;
  },
  
  checkHeadingStructure() {
    const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
    const issues = [];
    let previousLevel = 0;
    
    headings.forEach(heading => {
      const level = parseInt(heading.tagName.charAt(1));
      
      if (level > previousLevel + 1) {
        issues.push({
          element: heading,
          issue: `Heading level skipped (h${previousLevel} to h${level})`,
          recommendation: 'Use sequential heading levels'
        });
      }
      
      previousLevel = level;
    });
    
    return issues;
  },
  
  checkLandmarks() {
    const landmarks = ['main', 'nav', 'header', 'footer', 'aside', 'section'];
    const issues = [];
    
    landmarks.forEach(landmark => {
      const elements = document.querySelectorAll(landmark);
      if (elements.length === 0 && landmark === 'main') {
        issues.push({
          issue: 'Missing main landmark',
          recommendation: 'Add <main> element or role="main"'
        });
      }
    });
    
    return issues;
  },
  
  checkFocusManagement() {
    const issues = [];
    
    // Check for focus indicators
    const focusableElements = document.querySelectorAll(
      'a[href], button, input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    focusableElements.forEach(element => {
      const styles = window.getComputedStyle(element, ':focus');
      if (styles.outline === 'none' && !styles.boxShadow && !styles.border) {
        issues.push({
          element,
          issue: 'Missing focus indicator',
          recommendation: 'Add visible focus styles'
        });
      }
    });
    
    return issues;
  }
};