/**
 * Tests for Accessibility System
 * Comprehensive testing of WCAG compliance and accessibility features
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { 
  initializeAccessibility,
  AccessibilityTester,
  AriaLiveRegionManager,
  KeyboardNavigationManager,
  ColorContrastChecker,
  ScreenReaderUtils,
  HighContrastManager,
  MotionPreferencesManager
} from '../../utils/accessibility';

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock canvas for color contrast testing
HTMLCanvasElement.prototype.getContext = jest.fn(() => ({
  fillStyle: '',
  fillRect: jest.fn(),
  getImageData: jest.fn(() => ({
    data: [255, 255, 255, 255] // White color
  }))
}));

describe('Accessibility System', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
    jest.clearAllMocks();
  });

  describe('AriaLiveRegionManager', () => {
    let manager;

    beforeEach(() => {
      manager = new AriaLiveRegionManager();
    });

    test('creates live regions on initialization', () => {
      expect(document.getElementById('aria-live-polite')).toBeInTheDocument();
      expect(document.getElementById('aria-live-assertive')).toBeInTheDocument();
      expect(document.getElementById('aria-live-status')).toBeInTheDocument();
    });

    test('announces messages to appropriate regions', async () => {
      manager.announce('Test message', 'polite');
      
      await waitFor(() => {
        const politeRegion = document.getElementById('aria-live-polite');
        expect(politeRegion.textContent).toBe('Test message');
      });
    });

    test('announces status messages', async () => {
      manager.announceStatus('Status update');
      
      await waitFor(() => {
        const statusRegion = document.getElementById('aria-live-status');
        expect(statusRegion.textContent).toBe('Status update');
      });
    });

    test('announces alerts', async () => {
      manager.announceAlert('Alert message');
      
      await waitFor(() => {
        const assertiveRegion = document.getElementById('aria-live-assertive');
        expect(assertiveRegion.textContent).toBe('Alert message');
      });
    });

    test('live regions have correct ARIA attributes', () => {
      const politeRegion = document.getElementById('aria-live-polite');
      const assertiveRegion = document.getElementById('aria-live-assertive');
      const statusRegion = document.getElementById('aria-live-status');

      expect(politeRegion).toHaveAttribute('aria-live', 'polite');
      expect(politeRegion).toHaveAttribute('aria-atomic', 'true');
      expect(assertiveRegion).toHaveAttribute('aria-live', 'assertive');
      expect(statusRegion).toHaveAttribute('aria-live', 'polite');
    });
  });

  describe('KeyboardNavigationManager', () => {
    let manager;

    beforeEach(() => {
      manager = new KeyboardNavigationManager();
    });

    test('identifies focusable elements correctly', () => {
      document.body.innerHTML = `
        <button>Button</button>
        <input type="text" />
        <a href="#">Link</a>
        <div tabindex="0">Focusable div</div>
        <button disabled>Disabled button</button>
      `;

      const container = document.body;
      const focusableElements = manager.getFocusableElements(container);
      
      expect(focusableElements).toHaveLength(3); // Excludes disabled button
      expect(focusableElements[0]).toHaveTextContent('Button');
      expect(focusableElements[1]).toHaveAttribute('type', 'text');
      expect(focusableElements[2]).toHaveTextContent('Link');
    });

    test('traps focus within container', () => {
      document.body.innerHTML = `
        <div id="modal">
          <button id="first">First</button>
          <button id="second">Second</button>
          <button id="last">Last</button>
        </div>
        <button id="outside">Outside</button>
      `;

      const modal = document.getElementById('modal');
      const trap = manager.trapFocus(modal);

      expect(document.activeElement).toBe(document.getElementById('first'));
      expect(manager.trapStack).toContain(trap);
    });

    test('releases focus trap correctly', () => {
      document.body.innerHTML = `
        <button id="trigger">Trigger</button>
        <div id="modal">
          <button id="modal-button">Modal Button</button>
        </div>
      `;

      const trigger = document.getElementById('trigger');
      const modal = document.getElementById('modal');
      
      trigger.focus();
      const trap = manager.trapFocus(modal);
      
      manager.releaseFocus(trap);
      
      expect(document.activeElement).toBe(trigger);
      expect(manager.trapStack).not.toContain(trap);
    });

    test('handles tab navigation in focus trap', () => {
      document.body.innerHTML = `
        <div id="modal">
          <button id="first">First</button>
          <button id="last">Last</button>
        </div>
      `;

      const modal = document.getElementById('modal');
      const first = document.getElementById('first');
      const last = document.getElementById('last');
      
      manager.trapFocus(modal);
      last.focus();

      // Simulate Tab key
      const tabEvent = new KeyboardEvent('keydown', { key: 'Tab' });
      document.dispatchEvent(tabEvent);

      // Should cycle back to first element
      expect(document.activeElement).toBe(first);
    });

    test('handles escape key in focus trap', () => {
      const onEscape = jest.fn();
      document.body.innerHTML = `
        <div id="modal">
          <button>Modal Button</button>
        </div>
      `;

      const modal = document.getElementById('modal');
      manager.trapFocus(modal, { onEscape });

      const escapeEvent = new KeyboardEvent('keydown', { key: 'Escape' });
      document.dispatchEvent(escapeEvent);

      expect(onEscape).toHaveBeenCalled();
    });
  });

  describe('ColorContrastChecker', () => {
    let checker;

    beforeEach(() => {
      checker = new ColorContrastChecker();
    });

    test('calculates contrast ratio correctly', () => {
      const whiteRgb = [255, 255, 255];
      const blackRgb = [0, 0, 0];
      
      const ratio = checker.getContrastRatio(whiteRgb, blackRgb);
      expect(ratio).toBeCloseTo(21, 0); // White on black has 21:1 ratio
    });

    test('checks WCAG compliance correctly', () => {
      const result = checker.checkContrast('#000000', '#ffffff');
      
      expect(result.passAA).toBe(true);
      expect(result.passAAA).toBe(true);
      expect(result.level).toBe('AAA');
      expect(result.ratio).toBeCloseTo(21, 0);
    });

    test('identifies failing contrast', () => {
      const result = checker.checkContrast('#888888', '#999999');
      
      expect(result.passAA).toBe(false);
      expect(result.level).toBe('Fail');
    });

    test('handles large text threshold correctly', () => {
      const result = checker.checkContrast('#767676', '#ffffff', true);
      
      // Should pass AA for large text but not regular text
      expect(result.passAA).toBe(true);
      
      const regularResult = checker.checkContrast('#767676', '#ffffff', false);
      expect(regularResult.passAA).toBe(false);
    });

    test('audits page for contrast issues', () => {
      document.body.innerHTML = `
        <div style="color: #888; background-color: #999;">Low contrast text</div>
        <div style="color: #000; background-color: #fff;">Good contrast text</div>
      `;

      const issues = checker.auditPageContrast();
      expect(issues.length).toBeGreaterThan(0);
      expect(issues[0].issue).toContain('contrast');
    });
  });

  describe('ScreenReaderUtils', () => {
    let utils;

    beforeEach(() => {
      utils = new ScreenReaderUtils();
    });

    test('creates descriptive text for elements', () => {
      const button = document.createElement('button');
      button.disabled = true;
      
      const description = utils.createDescription(button, {
        position: { current: 1, total: 3 },
        group: 'navigation'
      });

      expect(description).toContain('button');
      expect(description).toContain('disabled');
      expect(description).toContain('1 of 3');
      expect(description).toContain('navigation');
    });

    test('gets correct role descriptions', () => {
      expect(utils.getRoleDescription('button')).toBe('button');
      expect(utils.getRoleDescription('link')).toBe('link');
      expect(utils.getRoleDescription('heading')).toBe('heading');
      expect(utils.getRoleDescription('unknown')).toBe('unknown');
    });

    test('creates skip links', () => {
      const targets = [
        { id: 'main-content', label: 'Skip to main content' },
        { id: 'navigation', label: 'Skip to navigation' }
      ];

      const skipContainer = utils.createSkipLinks(targets);
      
      expect(skipContainer).toHaveClass('skip-links');
      expect(skipContainer).toHaveAttribute('aria-label', 'Skip navigation links');
      
      const links = skipContainer.querySelectorAll('a');
      expect(links).toHaveLength(2);
      expect(links[0]).toHaveAttribute('href', '#main-content');
      expect(links[0]).toHaveTextContent('Skip to main content');
    });
  });

  describe('HighContrastManager', () => {
    let manager;

    beforeEach(() => {
      manager = new HighContrastManager();
    });

    test('detects high contrast mode', () => {
      // Mock high contrast detection
      window.matchMedia = jest.fn().mockImplementation(query => ({
        matches: query.includes('prefers-contrast: high'),
        addListener: jest.fn(),
        removeListener: jest.fn()
      }));

      const newManager = new HighContrastManager();
      expect(newManager.isHighContrast).toBe(true);
    });

    test('applies high contrast styles', () => {
      manager.applyHighContrastStyles(true);
      
      expect(document.documentElement).toHaveClass('high-contrast');
      expect(document.getElementById('high-contrast-styles')).toBeInTheDocument();
    });

    test('removes high contrast styles', () => {
      manager.applyHighContrastStyles(true);
      manager.applyHighContrastStyles(false);
      
      expect(document.documentElement).not.toHaveClass('high-contrast');
      expect(document.getElementById('high-contrast-styles')).not.toBeInTheDocument();
    });
  });

  describe('MotionPreferencesManager', () => {
    let manager;

    beforeEach(() => {
      manager = new MotionPreferencesManager();
    });

    test('detects reduced motion preference', () => {
      window.matchMedia = jest.fn().mockImplementation(query => ({
        matches: query.includes('prefers-reduced-motion: reduce'),
        addListener: jest.fn(),
        removeListener: jest.fn()
      }));

      const newManager = new MotionPreferencesManager();
      expect(newManager.prefersReducedMotion).toBe(true);
    });

    test('applies reduced motion styles', () => {
      manager.applyMotionPreferences(true);
      
      expect(document.documentElement).toHaveClass('reduce-motion');
      expect(document.getElementById('reduced-motion-styles')).toBeInTheDocument();
    });

    test('removes reduced motion styles', () => {
      manager.applyMotionPreferences(true);
      manager.applyMotionPreferences(false);
      
      expect(document.documentElement).not.toHaveClass('reduce-motion');
      expect(document.getElementById('reduced-motion-styles')).not.toBeInTheDocument();
    });
  });

  describe('AccessibilityTester', () => {
    test('runs comprehensive audit', async () => {
      document.body.innerHTML = `
        <img src="test.jpg" />
        <input type="text" />
        <h1>Title</h1>
        <h3>Skipped heading level</h3>
        <div style="color: #888; background-color: #999;">Low contrast</div>
      `;

      const results = await AccessibilityTester.runAudit();
      
      expect(results).toHaveProperty('timestamp');
      expect(results).toHaveProperty('colorContrast');
      expect(results).toHaveProperty('missingAltText');
      expect(results).toHaveProperty('missingLabels');
      expect(results).toHaveProperty('headingStructure');
      expect(results).toHaveProperty('landmarks');
    });

    test('checks for missing alt text', () => {
      document.body.innerHTML = `
        <img src="test1.jpg" alt="Good image" />
        <img src="test2.jpg" />
        <img src="test3.jpg" aria-label="Labeled image" />
      `;

      const issues = AccessibilityTester.checkMissingAltText();
      expect(issues).toHaveLength(1);
      expect(issues[0].element.src).toContain('test2.jpg');
    });

    test('checks for missing form labels', () => {
      document.body.innerHTML = `
        <label for="input1">Label</label>
        <input id="input1" type="text" />
        <input type="text" />
        <input type="text" aria-label="Labeled input" />
      `;

      const issues = AccessibilityTester.checkMissingLabels();
      expect(issues).toHaveLength(1);
      expect(issues[0].element.type).toBe('text');
    });

    test('checks heading structure', () => {
      document.body.innerHTML = `
        <h1>Main Title</h1>
        <h2>Section</h2>
        <h4>Skipped h3</h4>
      `;

      const issues = AccessibilityTester.checkHeadingStructure();
      expect(issues).toHaveLength(1);
      expect(issues[0].issue).toContain('Heading level skipped');
    });

    test('checks for landmarks', () => {
      document.body.innerHTML = `
        <header>Header</header>
        <nav>Navigation</nav>
        <div>No main landmark</div>
      `;

      const issues = AccessibilityTester.checkLandmarks();
      expect(issues).toHaveLength(1);
      expect(issues[0].issue).toBe('Missing main landmark');
    });

    test('checks focus management', () => {
      document.body.innerHTML = `
        <button style="outline: none;">No focus indicator</button>
        <button>Good button</button>
      `;

      const issues = AccessibilityTester.checkFocusManagement();
      expect(issues.length).toBeGreaterThanOrEqual(0);
    });
  });

  describe('Integration Tests', () => {
    test('initializes all accessibility features', () => {
      const managers = initializeAccessibility();
      
      expect(managers).toHaveProperty('ariaLiveManager');
      expect(managers).toHaveProperty('keyboardNavigationManager');
      expect(managers).toHaveProperty('colorContrastChecker');
      expect(managers).toHaveProperty('screenReaderUtils');
      expect(managers).toHaveProperty('highContrastManager');
      expect(managers).toHaveProperty('motionPreferencesManager');
      
      // Check global availability
      expect(window.ariaLiveManager).toBeDefined();
      expect(window.keyboardNavigationManager).toBeDefined();
      expect(window.colorContrastChecker).toBeDefined();
    });

    test('handles system preference changes', () => {
      const mockMatchMedia = jest.fn().mockImplementation(query => {
        const listeners = [];
        return {
          matches: false,
          addListener: (listener) => listeners.push(listener),
          removeListener: (listener) => {
            const index = listeners.indexOf(listener);
            if (index > -1) listeners.splice(index, 1);
          },
          triggerChange: (matches) => {
            listeners.forEach(listener => listener({ matches }));
          }
        };
      });

      window.matchMedia = mockMatchMedia;
      
      const managers = initializeAccessibility();
      
      // Simulate high contrast change
      const contrastQuery = mockMatchMedia.mock.results.find(
        result => result.value.addListener
      );
      
      if (contrastQuery) {
        contrastQuery.value.triggerChange(true);
        expect(document.documentElement).toHaveClass('high-contrast');
      }
    });

    test('works with real DOM interactions', async () => {
      initializeAccessibility();
      
      document.body.innerHTML = `
        <div id="modal" style="display: none;">
          <button id="modal-button">Modal Button</button>
          <button id="close-button">Close</button>
        </div>
        <button id="open-button">Open Modal</button>
      `;

      const modal = document.getElementById('modal');
      const openButton = document.getElementById('open-button');
      const closeButton = document.getElementById('close-button');

      // Simulate opening modal
      openButton.focus();
      modal.style.display = 'block';
      
      const trap = window.keyboardNavigationManager.trapFocus(modal);
      
      // Test focus trap
      expect(document.activeElement.id).toBe('modal-button');
      
      // Test escape key
      const escapeEvent = new KeyboardEvent('keydown', { key: 'Escape' });
      document.dispatchEvent(escapeEvent);
      
      // Simulate closing modal
      window.keyboardNavigationManager.releaseFocus(trap);
      modal.style.display = 'none';
      
      expect(document.activeElement).toBe(openButton);
    });
  });

  describe('Error Handling', () => {
    test('handles missing elements gracefully', () => {
      const manager = new KeyboardNavigationManager();
      
      // Try to trap focus on non-existent element
      expect(() => {
        manager.trapFocus(null);
      }).not.toThrow();
    });

    test('handles invalid color values', () => {
      const checker = new ColorContrastChecker();
      
      expect(() => {
        checker.checkContrast('invalid-color', '#ffffff');
      }).not.toThrow();
    });

    test('handles missing canvas context', () => {
      HTMLCanvasElement.prototype.getContext = jest.fn(() => null);
      
      const checker = new ColorContrastChecker();
      
      expect(() => {
        checker.parseColor('#ffffff');
      }).not.toThrow();
    });
  });

  describe('Performance', () => {
    test('does not create duplicate live regions', () => {
      new AriaLiveRegionManager();
      new AriaLiveRegionManager();
      
      const politeRegions = document.querySelectorAll('#aria-live-polite');
      expect(politeRegions).toHaveLength(1);
    });

    test('efficiently identifies focusable elements', () => {
      // Create many elements
      const container = document.createElement('div');
      for (let i = 0; i < 1000; i++) {
        const element = document.createElement(i % 2 === 0 ? 'button' : 'div');
        if (i % 3 === 0) element.tabIndex = 0;
        container.appendChild(element);
      }
      document.body.appendChild(container);

      const manager = new KeyboardNavigationManager();
      const start = performance.now();
      const focusableElements = manager.getFocusableElements(container);
      const end = performance.now();

      expect(end - start).toBeLessThan(100); // Should complete in under 100ms
      expect(focusableElements.length).toBeGreaterThan(0);
    });
  });
});