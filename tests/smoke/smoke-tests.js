#!/usr/bin/env node

/**
 * Smoke Tests for Deployment Validation
 * These tests verify basic functionality after deployment
 */

const axios = require('axios');
const { program } = require('commander');

// Configuration
program
  .option('--url <url>', 'Base URL to test', 'http://localhost:3000')
  .option('--timeout <timeout>', 'Request timeout in ms', '10000')
  .option('--retries <retries>', 'Number of retries for failed tests', '3')
  .parse();

const options = program.opts();
const BASE_URL = options.url;
const TIMEOUT = parseInt(options.timeout);
const RETRIES = parseInt(options.retries);

// Test configuration
const axiosConfig = {
  timeout: TIMEOUT,
  validateStatus: () => true, // Don't throw on HTTP errors
};

// Colors for output
const colors = {
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  reset: '\x1b[0m'
};

// Logging functions
const log = (message, color = colors.reset) => {
  console.log(`${color}[${new Date().toISOString()}] ${message}${colors.reset}`);
};

const success = (message) => log(`✅ ${message}`, colors.green);
const error = (message) => log(`❌ ${message}`, colors.red);
const warning = (message) => log(`⚠️  ${message}`, colors.yellow);
const info = (message) => log(`ℹ️  ${message}`, colors.blue);

// Test results tracking
let testResults = {
  passed: 0,
  failed: 0,
  total: 0,
  failures: []
};

// Helper function to run test with retries
async function runTestWithRetries(testName, testFunction, retries = RETRIES) {
  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      await testFunction();
      success(`${testName} (attempt ${attempt}/${retries})`);
      testResults.passed++;
      return;
    } catch (err) {
      if (attempt === retries) {
        error(`${testName} failed after ${retries} attempts: ${err.message}`);
        testResults.failed++;
        testResults.failures.push({ test: testName, error: err.message });
      } else {
        warning(`${testName} failed on attempt ${attempt}/${retries}, retrying...`);
        await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1 second before retry
      }
    }
  }
}

// Test: Frontend Health Check
async function testFrontendHealth() {
  const response = await axios.get(`${BASE_URL}/health`, axiosConfig);
  
  if (response.status !== 200) {
    throw new Error(`Expected status 200, got ${response.status}`);
  }
  
  if (!response.data || typeof response.data !== 'object') {
    throw new Error('Health endpoint should return JSON object');
  }
  
  if (response.data.status !== 'healthy') {
    throw new Error(`Expected status 'healthy', got '${response.data.status}'`);
  }
}

// Test: Backend API Health Check
async function testBackendHealth() {
  const apiUrl = BASE_URL.replace('intelligence-os', 'api.intelligence-os');
  const response = await axios.get(`${apiUrl}/health`, axiosConfig);
  
  if (response.status !== 200) {
    throw new Error(`Expected status 200, got ${response.status}`);
  }
  
  if (!response.data || typeof response.data !== 'object') {
    throw new Error('API health endpoint should return JSON object');
  }
  
  if (response.data.status !== 'healthy') {
    throw new Error(`Expected status 'healthy', got '${response.data.status}'`);
  }
}

// Test: Frontend Page Load
async function testFrontendPageLoad() {
  const response = await axios.get(BASE_URL, axiosConfig);
  
  if (response.status !== 200) {
    throw new Error(`Expected status 200, got ${response.status}`);
  }
  
  if (!response.data || typeof response.data !== 'string') {
    throw new Error('Frontend should return HTML content');
  }
  
  if (!response.data.includes('<html') || !response.data.includes('</html>')) {
    throw new Error('Response does not appear to be valid HTML');
  }
  
  // Check for essential elements
  const requiredElements = ['<title>', '<body>', '<div id="root"'];
  for (const element of requiredElements) {
    if (!response.data.includes(element)) {
      throw new Error(`Missing required HTML element: ${element}`);
    }
  }
}

// Test: API Authentication Endpoint
async function testAPIAuthentication() {
  const apiUrl = BASE_URL.replace('intelligence-os', 'api.intelligence-os');
  const response = await axios.post(`${apiUrl}/auth/login`, {
    email: 'test@example.com',
    password: 'invalid'
  }, axiosConfig);
  
  // Should return 401 for invalid credentials
  if (response.status !== 401) {
    throw new Error(`Expected status 401 for invalid credentials, got ${response.status}`);
  }
  
  if (!response.data || !response.data.error) {
    throw new Error('Authentication endpoint should return error message');
  }
}

// Test: API Rate Limiting
async function testAPIRateLimit() {
  const apiUrl = BASE_URL.replace('intelligence-os', 'api.intelligence-os');
  
  // Make multiple rapid requests to trigger rate limiting
  const requests = Array(10).fill().map(() => 
    axios.get(`${apiUrl}/health`, axiosConfig)
  );
  
  const responses = await Promise.all(requests);
  
  // At least one request should succeed
  const successfulRequests = responses.filter(r => r.status === 200);
  if (successfulRequests.length === 0) {
    throw new Error('No requests succeeded - API may be down');
  }
  
  info(`Rate limiting test: ${successfulRequests.length}/10 requests succeeded`);
}

// Test: Voice Processor Health (if available)
async function testVoiceProcessorHealth() {
  try {
    const voiceUrl = BASE_URL.replace('intelligence-os', 'voice.intelligence-os');
    const response = await axios.get(`${voiceUrl}/health`, axiosConfig);
    
    if (response.status === 200) {
      success('Voice processor is available and healthy');
    } else {
      warning(`Voice processor returned status ${response.status}`);
    }
  } catch (err) {
    warning('Voice processor not available or not accessible');
  }
}

// Test: Static Assets Loading
async function testStaticAssets() {
  const assetPaths = ['/static/css', '/static/js', '/favicon.ico'];
  
  for (const path of assetPaths) {
    try {
      const response = await axios.get(`${BASE_URL}${path}`, axiosConfig);
      if (response.status === 200) {
        info(`Static asset ${path} loaded successfully`);
      } else {
        warning(`Static asset ${path} returned status ${response.status}`);
      }
    } catch (err) {
      warning(`Static asset ${path} failed to load: ${err.message}`);
    }
  }
}

// Test: HTTPS Security Headers
async function testSecurityHeaders() {
  const response = await axios.get(BASE_URL, axiosConfig);
  
  const requiredHeaders = [
    'x-frame-options',
    'x-content-type-options',
    'x-xss-protection',
    'strict-transport-security'
  ];
  
  const missingHeaders = [];
  
  for (const header of requiredHeaders) {
    if (!response.headers[header]) {
      missingHeaders.push(header);
    }
  }
  
  if (missingHeaders.length > 0) {
    warning(`Missing security headers: ${missingHeaders.join(', ')}`);
  } else {
    success('All required security headers present');
  }
}

// Test: API CORS Configuration
async function testCORSConfiguration() {
  const apiUrl = BASE_URL.replace('intelligence-os', 'api.intelligence-os');
  
  try {
    const response = await axios.options(`${apiUrl}/health`, {
      ...axiosConfig,
      headers: {
        'Origin': BASE_URL,
        'Access-Control-Request-Method': 'GET'
      }
    });
    
    if (response.headers['access-control-allow-origin']) {
      success('CORS configuration is present');
    } else {
      warning('CORS headers not found');
    }
  } catch (err) {
    warning(`CORS test failed: ${err.message}`);
  }
}

// Test: Database Connectivity (through API)
async function testDatabaseConnectivity() {
  const apiUrl = BASE_URL.replace('intelligence-os', 'api.intelligence-os');
  
  try {
    const response = await axios.get(`${apiUrl}/status`, axiosConfig);
    
    if (response.status === 200 && response.data.database) {
      if (response.data.database.status === 'connected') {
        success('Database connectivity verified');
      } else {
        throw new Error(`Database status: ${response.data.database.status}`);
      }
    } else {
      warning('Database status endpoint not available');
    }
  } catch (err) {
    warning(`Database connectivity test failed: ${err.message}`);
  }
}

// Main test runner
async function runSmokeTests() {
  info(`Starting smoke tests for ${BASE_URL}`);
  info(`Timeout: ${TIMEOUT}ms, Retries: ${RETRIES}`);
  
  const tests = [
    { name: 'Frontend Health Check', fn: testFrontendHealth },
    { name: 'Backend API Health Check', fn: testBackendHealth },
    { name: 'Frontend Page Load', fn: testFrontendPageLoad },
    { name: 'API Authentication Endpoint', fn: testAPIAuthentication },
    { name: 'API Rate Limiting', fn: testAPIRateLimit },
    { name: 'Security Headers', fn: testSecurityHeaders },
    { name: 'CORS Configuration', fn: testCORSConfiguration },
    { name: 'Database Connectivity', fn: testDatabaseConnectivity }
  ];
  
  // Optional tests (don't fail the suite if they fail)
  const optionalTests = [
    { name: 'Voice Processor Health', fn: testVoiceProcessorHealth },
    { name: 'Static Assets Loading', fn: testStaticAssets }
  ];
  
  testResults.total = tests.length;
  
  // Run required tests
  for (const test of tests) {
    await runTestWithRetries(test.name, test.fn);
  }
  
  // Run optional tests (no retries, don't count towards pass/fail)
  for (const test of optionalTests) {
    try {
      await test.fn();
    } catch (err) {
      warning(`Optional test '${test.name}' failed: ${err.message}`);
    }
  }
  
  // Print results
  console.log('\n' + '='.repeat(50));
  info(`Smoke Test Results:`);
  info(`Total Tests: ${testResults.total}`);
  success(`Passed: ${testResults.passed}`);
  error(`Failed: ${testResults.failed}`);
  
  if (testResults.failures.length > 0) {
    console.log('\nFailure Details:');
    testResults.failures.forEach((failure, index) => {
      error(`${index + 1}. ${failure.test}: ${failure.error}`);
    });
  }
  
  console.log('='.repeat(50));
  
  // Exit with appropriate code
  if (testResults.failed === 0) {
    success('All smoke tests passed! 🎉');
    process.exit(0);
  } else {
    error(`${testResults.failed} smoke tests failed! 💥`);
    process.exit(1);
  }
}

// Run tests if this script is executed directly
if (require.main === module) {
  runSmokeTests().catch(err => {
    error(`Smoke test runner failed: ${err.message}`);
    process.exit(1);
  });
}

module.exports = {
  runSmokeTests,
  testResults
};