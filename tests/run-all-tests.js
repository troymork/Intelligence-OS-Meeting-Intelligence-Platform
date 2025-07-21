#!/usr/bin/env node

/**
 * Main Test Execution Script
 * Runs the comprehensive test suite using the TestRunner
 */

const TestRunner = require('./TestRunner');
const path = require('path');

async function main() {
  console.log('🚀 Intelligence OS - Comprehensive Test Suite');
  console.log('============================================\n');
  
  // Parse command line arguments
  const args = process.argv.slice(2);
  const config = parseArguments(args);
  
  // Create and configure test runner
  const testRunner = new TestRunner(config);
  
  try {
    // Run all tests
    const results = await testRunner.runAllTests();
    
    // Exit with appropriate code
    process.exit(results.summary.overallStatus === 'PASSED' ? 0 : 1);
    
  } catch (error) {
    console.error('❌ Test suite execution failed:', error);
    process.exit(1);
  }
}

function parseArguments(args) {
  const config = {
    runUnitTests: true,
    runIntegrationTests: true,
    runAIModelTests: true,
    runPerformanceTests: true,
    runE2ETests: true,
    generateReports: true
  };
  
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    
    switch (arg) {
      case '--unit-only':
        config.runIntegrationTests = false;
        config.runAIModelTests = false;
        config.runPerformanceTests = false;
        config.runE2ETests = false;
        break;
        
      case '--integration-only':
        config.runUnitTests = false;
        config.runAIModelTests = false;
        config.runPerformanceTests = false;
        config.runE2ETests = false;
        break;
        
      case '--ai-only':
        config.runUnitTests = false;
        config.runIntegrationTests = false;
        config.runPerformanceTests = false;
        config.runE2ETests = false;
        break;
        
      case '--performance-only':
        config.runUnitTests = false;
        config.runIntegrationTests = false;
        config.runAIModelTests = false;
        config.runE2ETests = false;
        break;
        
      case '--e2e-only':
        config.runUnitTests = false;
        config.runIntegrationTests = false;
        config.runAIModelTests = false;
        config.runPerformanceTests = false;
        break;
        
      case '--skip-unit':
        config.runUnitTests = false;
        break;
        
      case '--skip-integration':
        config.runIntegrationTests = false;
        break;
        
      case '--skip-ai':
        config.runAIModelTests = false;
        break;
        
      case '--skip-performance':
        config.runPerformanceTests = false;
        break;
        
      case '--skip-e2e':
        config.runE2ETests = false;
        break;
        
      case '--no-reports':
        config.generateReports = false;
        break;
        
      case '--base-url':
        config.baseUrl = args[++i];
        break;
        
      case '--api-url':
        config.apiUrl = args[++i];
        break;
        
      case '--coverage-threshold':
        config.coverageThreshold = parseInt(args[++i]);
        break;
        
      case '--output-dir':
        config.outputDir = path.resolve(args[++i]);
        break;
        
      case '--help':
      case '-h':
        printHelp();
        process.exit(0);
        break;
        
      default:
        if (arg.startsWith('--')) {
          console.warn(`Unknown option: ${arg}`);
        }
        break;
    }
  }
  
  return config;
}

function printHelp() {
  console.log(`
Intelligence OS Test Suite

Usage: node tests/run-all-tests.js [options]

Options:
  --unit-only              Run only unit tests
  --integration-only       Run only integration tests
  --ai-only               Run only AI model tests
  --performance-only      Run only performance tests
  --e2e-only              Run only end-to-end tests
  
  --skip-unit             Skip unit tests
  --skip-integration      Skip integration tests
  --skip-ai               Skip AI model tests
  --skip-performance      Skip performance tests
  --skip-e2e              Skip end-to-end tests
  
  --no-reports            Skip report generation
  --base-url <url>        Frontend base URL (default: http://localhost:3000)
  --api-url <url>         Backend API URL (default: http://localhost:8000)
  --coverage-threshold <n> Coverage threshold percentage (default: 90)
  --output-dir <path>     Output directory for reports (default: ./test-results)
  
  --help, -h              Show this help message

Examples:
  node tests/run-all-tests.js                    # Run all tests
  node tests/run-all-tests.js --unit-only        # Run only unit tests
  node tests/run-all-tests.js --skip-performance # Skip performance tests
  node tests/run-all-tests.js --coverage-threshold 85 # Set coverage to 85%
`);
}

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  console.error('❌ Uncaught Exception:', error);
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('❌ Unhandled Rejection at:', promise, 'reason:', reason);
  process.exit(1);
});

// Run the main function
if (require.main === module) {
  main();
}

module.exports = { main, parseArguments };