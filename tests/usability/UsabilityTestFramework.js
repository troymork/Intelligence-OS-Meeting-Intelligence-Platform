/**
 * Comprehensive Usability Testing Framework
 * Tests user experience, accessibility, and interface optimization
 */

const puppeteer = require('puppeteer');
const axeCore = require('axe-core');

class UsabilityTestFramework {
    constructor(baseUrl = 'http://localhost:3000') {
        this.baseUrl = baseUrl;
        this.browser = null;
        this.page = null;
        this.testResults = [];
        this.userScenarios = [];
    }

    // Initialize browser for testing
    async initialize() {
        this.browser = await puppeteer.launch({
            headless: false, // Set to true for CI/CD
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
        this.page = await this.browser.newPage();
        
        // Set viewport for consistent testing
        await this.page.setViewport({ width: 1920, height: 1080 });
        
        // Enable accessibility features
        await this.page.evaluateOnNewDocument(() => {
            // Inject axe-core for accessibility testing
            const script = document.createElement('script');
            script.src = 'https://unpkg.com/axe-core@4.7.0/axe.min.js';
            document.head.appendChild(script);
        });
    }

    // Clean up resources
    async cleanup() {
        if (this.page) await this.page.close();
        if (this.browser) await this.browser.close();
    }

    // Define user scenarios for testing
    defineUserScenarios() {
        this.userScenarios = [
            {
                name: 'New User Onboarding',
                description: 'First-time user discovers and learns the platform',
                steps: [
                    { action: 'navigate', target: '/' },
                    { action: 'wait', target: 2000 },
                    { action: 'click', target: '[data-testid="get-started-button"]' },
                    { action: 'fill', target: '[data-testid="email-input"]', value: 'newuser@example.com' },
                    { action: 'fill', target: '[data-testid="password-input"]', value: 'securepassword123' },
                    { action: 'click', target: '[data-testid="signup-button"]' },
                    { action: 'wait', target: 3000 },
                    { action: 'verify', target: '[data-testid="welcome-message"]' }
                ],
                expectedOutcome: 'User successfully completes registration and sees welcome message',
                maxDuration: 30000
            },
            {
                name: 'Voice Interface Interaction',
                description: 'User interacts with voice-first interface',
                steps: [
                    { action: 'navigate', target: '/dashboard' },
                    { action: 'click', target: '[data-testid="voice-activation-orb"]' },
                    { action: 'wait', target: 1000 },
                    { action: 'verify', target: '[data-testid="voice-listening-indicator"]' },
                    { action: 'simulate-speech', target: 'Start new meeting analysis' },
                    { action: 'wait', target: 3000 },
                    { action: 'verify', target: '[data-testid="analysis-started-confirmation"]' }
                ],
                expectedOutcome: 'Voice command is recognized and analysis begins',
                maxDuration: 15000
            },
            {
                name: 'Meeting Analysis Workflow',
                description: 'User uploads and analyzes a meeting transcript',
                steps: [
                    { action: 'navigate', target: '/meetings' },
                    { action: 'click', target: '[data-testid="upload-transcript-button"]' },
                    { action: 'upload', target: '[data-testid="file-input"]', file: 'test-transcript.txt' },
                    { action: 'click', target: '[data-testid="analyze-button"]' },
                    { action: 'wait', target: 5000 },
                    { action: 'verify', target: '[data-testid="analysis-results"]' },
                    { action: 'click', target: '[data-testid="view-insights-button"]' },
                    { action: 'verify', target: '[data-testid="insights-dashboard"]' }
                ],
                expectedOutcome: 'Meeting is analyzed and insights are displayed',
                maxDuration: 45000
            },
            {
                name: 'Dashboard Navigation',
                description: 'User navigates through different dashboard sections',
                steps: [
                    { action: 'navigate', target: '/dashboard' },
                    { action: 'click', target: '[data-testid="human-needs-tab"]' },
                    { action: 'wait', target: 2000 },
                    { action: 'verify', target: '[data-testid="human-needs-visualization"]' },
                    { action: 'click', target: '[data-testid="strategic-alignment-tab"]' },
                    { action: 'wait', target: 2000 },
                    { action: 'verify', target: '[data-testid="strategic-dashboard"]' },
                    { action: 'click', target: '[data-testid="pattern-analysis-tab"]' },
                    { action: 'wait', target: 2000 },
                    { action: 'verify', target: '[data-testid="pattern-visualization"]' }
                ],
                expectedOutcome: 'User can navigate between dashboard sections smoothly',
                maxDuration: 20000
            },
            {
                name: 'Accessibility Features Usage',
                description: 'User with accessibility needs uses the platform',
                steps: [
                    { action: 'navigate', target: '/' },
                    { action: 'keyboard-navigate', target: 'Tab', count: 5 },
                    { action: 'verify', target: '[data-testid="skip-to-content"]' },
                    { action: 'press-key', target: 'Enter' },
                    { action: 'verify', target: '[data-testid="main-content"]' },
                    { action: 'toggle-high-contrast', target: true },
                    { action: 'verify', target: '.high-contrast-mode' },
                    { action: 'increase-font-size', target: 2 },
                    { action: 'verify-font-size', target: '18px' }
                ],
                expectedOutcome: 'Accessibility features work correctly',
                maxDuration: 25000
            }
        ];
    }

    // Execute a user scenario
    async executeScenario(scenario) {
        const startTime = Date.now();
        const result = {
            scenario: scenario.name,
            status: 'PASS',
            duration: 0,
            steps: [],
            errors: [],
            metrics: {}
        };

        try {
            for (const step of scenario.steps) {
                const stepStartTime = Date.now();
                await this.executeStep(step);
                const stepDuration = Date.now() - stepStartTime;
                
                result.steps.push({
                    action: step.action,
                    target: step.target,
                    duration: stepDuration,
                    status: 'SUCCESS'
                });
            }

            result.duration = Date.now() - startTime;
            
            // Check if scenario exceeded max duration
            if (result.duration > scenario.maxDuration) {
                result.status = 'FAIL';
                result.errors.push(`Scenario exceeded maximum duration: ${result.duration}ms > ${scenario.maxDuration}ms`);
            }

            // Collect performance metrics
            result.metrics = await this.collectPerformanceMetrics();

        } catch (error) {
            result.status = 'FAIL';
            result.duration = Date.now() - startTime;
            result.errors.push(error.message);
        }

        return result;
    }

    // Execute individual test step
    async executeStep(step) {
        switch (step.action) {
            case 'navigate':
                await this.page.goto(`${this.baseUrl}${step.target}`, { waitUntil: 'networkidle0' });
                break;
                
            case 'wait':
                await this.page.waitForTimeout(step.target);
                break;
                
            case 'click':
                await this.page.waitForSelector(step.target, { timeout: 10000 });
                await this.page.click(step.target);
                break;
                
            case 'fill':
                await this.page.waitForSelector(step.target, { timeout: 10000 });
                await this.page.fill(step.target, step.value);
                break;
                
            case 'verify':
                await this.page.waitForSelector(step.target, { timeout: 10000 });
                break;
                
            case 'upload':
                const fileInput = await this.page.$(step.target);
                await fileInput.uploadFile(step.file);
                break;
                
            case 'keyboard-navigate':
                for (let i = 0; i < (step.count || 1); i++) {
                    await this.page.keyboard.press(step.target);
                    await this.page.waitForTimeout(100);
                }
                break;
                
            case 'press-key':
                await this.page.keyboard.press(step.target);
                break;
                
            case 'simulate-speech':
                // Simulate speech input (would integrate with actual speech API in real implementation)
                await this.page.evaluate((text) => {
                    window.dispatchEvent(new CustomEvent('speech-input', { detail: { text } }));
                }, step.target);
                break;
                
            case 'toggle-high-contrast':
                await this.page.evaluate((enable) => {
                    document.body.classList.toggle('high-contrast-mode', enable);
                }, step.target);
                break;
                
            case 'increase-font-size':
                await this.page.evaluate((steps) => {
                    const currentSize = parseInt(getComputedStyle(document.body).fontSize);
                    document.body.style.fontSize = `${currentSize + (steps * 2)}px`;
                }, step.target);
                break;
                
            case 'verify-font-size':
                const fontSize = await this.page.evaluate(() => getComputedStyle(document.body).fontSize);
                if (fontSize !== step.target) {
                    throw new Error(`Font size mismatch: expected ${step.target}, got ${fontSize}`);
                }
                break;
                
            default:
                throw new Error(`Unknown action: ${step.action}`);
        }
    }

    // Collect performance metrics
    async collectPerformanceMetrics() {
        const metrics = await this.page.evaluate(() => {
            const navigation = performance.getEntriesByType('navigation')[0];
            const paint = performance.getEntriesByType('paint');
            
            return {
                loadTime: navigation.loadEventEnd - navigation.loadEventStart,
                domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
                firstPaint: paint.find(p => p.name === 'first-paint')?.startTime || 0,
                firstContentfulPaint: paint.find(p => p.name === 'first-contentful-paint')?.startTime || 0,
                totalPageSize: navigation.transferSize,
                resourceCount: performance.getEntriesByType('resource').length
            };
        });

        return metrics;
    }

    // Run accessibility tests
    async runAccessibilityTests() {
        const results = [];
        const testPages = ['/', '/dashboard', '/meetings', '/settings'];

        for (const pagePath of testPages) {
            await this.page.goto(`${this.baseUrl}${pagePath}`, { waitUntil: 'networkidle0' });
            
            // Wait for axe-core to load
            await this.page.waitForTimeout(1000);
            
            const axeResults = await this.page.evaluate(async () => {
                if (typeof axe !== 'undefined') {
                    return await axe.run();
                }
                return { violations: [], passes: [] };
            });

            results.push({
                page: pagePath,
                violations: axeResults.violations,
                passes: axeResults.passes,
                violationCount: axeResults.violations.length,
                passCount: axeResults.passes.length
            });
        }

        return results;
    }

    // Test responsive design
    async testResponsiveDesign() {
        const viewports = [
            { name: 'Mobile', width: 375, height: 667 },
            { name: 'Tablet', width: 768, height: 1024 },
            { name: 'Desktop', width: 1920, height: 1080 },
            { name: 'Large Desktop', width: 2560, height: 1440 }
        ];

        const results = [];

        for (const viewport of viewports) {
            await this.page.setViewport(viewport);
            await this.page.goto(`${this.baseUrl}/dashboard`, { waitUntil: 'networkidle0' });

            const layoutMetrics = await this.page.evaluate(() => {
                const body = document.body;
                const hasHorizontalScroll = body.scrollWidth > body.clientWidth;
                const hasVerticalScroll = body.scrollHeight > body.clientHeight;
                
                return {
                    hasHorizontalScroll,
                    hasVerticalScroll,
                    bodyWidth: body.scrollWidth,
                    bodyHeight: body.scrollHeight,
                    viewportWidth: window.innerWidth,
                    viewportHeight: window.innerHeight
                };
            });

            // Check if critical elements are visible
            const criticalElements = await this.page.evaluate(() => {
                const elements = [
                    '[data-testid="main-navigation"]',
                    '[data-testid="voice-activation-orb"]',
                    '[data-testid="dashboard-content"]'
                ];

                return elements.map(selector => {
                    const element = document.querySelector(selector);
                    if (!element) return { selector, visible: false, reason: 'Element not found' };
                    
                    const rect = element.getBoundingClientRect();
                    const visible = rect.width > 0 && rect.height > 0 && 
                                   rect.top >= 0 && rect.left >= 0 &&
                                   rect.bottom <= window.innerHeight && 
                                   rect.right <= window.innerWidth;
                    
                    return { selector, visible, rect };
                });
            });

            results.push({
                viewport: viewport.name,
                dimensions: viewport,
                layoutMetrics,
                criticalElements,
                issues: this.identifyResponsiveIssues(layoutMetrics, criticalElements)
            });
        }

        return results;
    }

    // Identify responsive design issues
    identifyResponsiveIssues(layoutMetrics, criticalElements) {
        const issues = [];

        if (layoutMetrics.hasHorizontalScroll) {
            issues.push('Horizontal scrollbar present - content may be too wide');
        }

        const invisibleElements = criticalElements.filter(el => !el.visible);
        if (invisibleElements.length > 0) {
            issues.push(`Critical elements not visible: ${invisibleElements.map(el => el.selector).join(', ')}`);
        }

        return issues;
    }

    // Run A/B testing scenarios
    async runABTests() {
        const abTests = [
            {
                name: 'Voice Orb Position',
                variants: [
                    { name: 'Bottom Right', css: '.voice-orb { position: fixed; bottom: 20px; right: 20px; }' },
                    { name: 'Top Center', css: '.voice-orb { position: fixed; top: 20px; left: 50%; transform: translateX(-50%); }' }
                ],
                metric: 'click-through-rate'
            },
            {
                name: 'Dashboard Layout',
                variants: [
                    { name: 'Grid Layout', css: '.dashboard-content { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }' },
                    { name: 'Flex Layout', css: '.dashboard-content { display: flex; flex-wrap: wrap; }' }
                ],
                metric: 'time-to-interaction'
            }
        ];

        const results = [];

        for (const test of abTests) {
            const variantResults = [];

            for (const variant of test.variants) {
                await this.page.goto(`${this.baseUrl}/dashboard`, { waitUntil: 'networkidle0' });
                
                // Apply variant CSS
                await this.page.addStyleTag({ content: variant.css });
                
                // Measure interaction metrics
                const metrics = await this.measureInteractionMetrics(test.metric);
                
                variantResults.push({
                    variant: variant.name,
                    metrics: metrics
                });
            }

            results.push({
                testName: test.name,
                variants: variantResults,
                winner: this.determineABTestWinner(variantResults, test.metric)
            });
        }

        return results;
    }

    // Measure interaction metrics for A/B testing
    async measureInteractionMetrics(metricType) {
        switch (metricType) {
            case 'click-through-rate':
                // Simulate user interactions and measure clicks
                return await this.page.evaluate(() => {
                    let clickCount = 0;
                    const elements = document.querySelectorAll('[data-testid]');
                    
                    elements.forEach(el => {
                        el.addEventListener('click', () => clickCount++);
                    });
                    
                    // Simulate some clicks
                    setTimeout(() => {
                        elements[0]?.click();
                        elements[1]?.click();
                    }, 100);
                    
                    return new Promise(resolve => {
                        setTimeout(() => resolve({ clickCount }), 1000);
                    });
                });
                
            case 'time-to-interaction':
                return await this.page.evaluate(() => {
                    const startTime = performance.now();
                    
                    return new Promise(resolve => {
                        const observer = new PerformanceObserver((list) => {
                            const entries = list.getEntries();
                            const interactionTime = entries[0]?.startTime || performance.now();
                            resolve({ timeToInteraction: interactionTime - startTime });
                        });
                        
                        observer.observe({ entryTypes: ['first-input'] });
                        
                        // Fallback timeout
                        setTimeout(() => {
                            resolve({ timeToInteraction: performance.now() - startTime });
                        }, 5000);
                    });
                });
                
            default:
                return {};
        }
    }

    // Determine A/B test winner
    determineABTestWinner(variantResults, metric) {
        if (variantResults.length < 2) return null;
        
        let bestVariant = variantResults[0];
        
        for (const variant of variantResults) {
            if (metric === 'click-through-rate' && variant.metrics.clickCount > bestVariant.metrics.clickCount) {
                bestVariant = variant;
            } else if (metric === 'time-to-interaction' && variant.metrics.timeToInteraction < bestVariant.metrics.timeToInteraction) {
                bestVariant = variant;
            }
        }
        
        return bestVariant.variant;
    }

    // Run all usability tests
    async runAllTests() {
        console.log('Starting comprehensive usability testing...');
        
        await this.initialize();
        this.defineUserScenarios();
        
        const results = {
            userScenarios: [],
            accessibility: [],
            responsiveDesign: [],
            abTests: [],
            summary: {}
        };

        try {
            // Run user scenarios
            console.log('Running user scenarios...');
            for (const scenario of this.userScenarios) {
                const result = await this.executeScenario(scenario);
                results.userScenarios.push(result);
            }

            // Run accessibility tests
            console.log('Running accessibility tests...');
            results.accessibility = await this.runAccessibilityTests();

            // Run responsive design tests
            console.log('Running responsive design tests...');
            results.responsiveDesign = await this.testResponsiveDesign();

            // Run A/B tests
            console.log('Running A/B tests...');
            results.abTests = await this.runABTests();

            // Generate summary
            results.summary = this.generateTestSummary(results);

        } finally {
            await this.cleanup();
        }

        return results;
    }

    // Generate test summary
    generateTestSummary(results) {
        const scenariosPassed = results.userScenarios.filter(s => s.status === 'PASS').length;
        const totalScenarios = results.userScenarios.length;
        
        const totalViolations = results.accessibility.reduce((sum, page) => sum + page.violationCount, 0);
        const totalAccessibilityTests = results.accessibility.reduce((sum, page) => sum + page.passCount + page.violationCount, 0);
        
        const responsiveIssues = results.responsiveDesign.reduce((sum, viewport) => sum + viewport.issues.length, 0);
        
        return {
            userScenarios: {
                total: totalScenarios,
                passed: scenariosPassed,
                failed: totalScenarios - scenariosPassed,
                successRate: totalScenarios > 0 ? (scenariosPassed / totalScenarios) * 100 : 0
            },
            accessibility: {
                totalTests: totalAccessibilityTests,
                violations: totalViolations,
                complianceRate: totalAccessibilityTests > 0 ? ((totalAccessibilityTests - totalViolations) / totalAccessibilityTests) * 100 : 0
            },
            responsiveDesign: {
                viewportsTested: results.responsiveDesign.length,
                issuesFound: responsiveIssues,
                responsiveScore: results.responsiveDesign.length > 0 ? ((results.responsiveDesign.length - responsiveIssues) / results.responsiveDesign.length) * 100 : 0
            },
            overallUsabilityScore: this.calculateOverallUsabilityScore(results)
        };
    }

    // Calculate overall usability score
    calculateOverallUsabilityScore(results) {
        const scenarioScore = results.summary?.userScenarios?.successRate || 0;
        const accessibilityScore = results.summary?.accessibility?.complianceRate || 0;
        const responsiveScore = results.summary?.responsiveDesign?.responsiveScore || 0;
        
        return (scenarioScore + accessibilityScore + responsiveScore) / 3;
    }
}

module.exports = UsabilityTestFramework;