/**
 * Performance Test Suite
 * Ensures system meets latency and throughput requirements
 */

const axios = require('axios');
const WebSocket = require('ws');
const { performance } = require('perf_hooks');
const fs = require('fs').promises;
const path = require('path');

class PerformanceTestSuite {
  constructor(config = {}) {
    this.config = {
      baseUrl: process.env.TEST_BASE_URL || 'http://localhost:3000',
      apiUrl: process.env.TEST_API_URL || 'http://localhost:8000',
      wsUrl: process.env.TEST_WS_URL || 'ws://localhost:8000/ws',
      
      // Performance thresholds
      maxLatency: 5000,        // 5 seconds max response time
      maxP95Latency: 3000,     // 95th percentile under 3 seconds
      minThroughput: 100,      // 100 requests per second minimum
      maxErrorRate: 0.01,      // 1% error rate maximum
      maxMemoryUsage: 512,     // 512MB max memory usage
      maxCpuUsage: 80,         // 80% max CPU usage
      
      // Test configuration
      warmupRequests: 50,
      testDuration: 60000,     // 60 seconds
      concurrentUsers: 10,
      rampUpTime: 10000,       // 10 seconds ramp up
      
      ...config
    };
    
    this.metrics = {
      requests: [],
      errors: [],
      memory: [],
      cpu: [],
      websockets: []
    };
    
    this.testResults = new Map();
  }

  // Load testing utilities
  async runLoadTest(testName, requestGenerator, options = {}) {
    const {
      duration = this.config.testDuration,
      concurrentUsers = this.config.concurrentUsers,
      rampUpTime = this.config.rampUpTime,
      warmupRequests = this.config.warmupRequests
    } = options;

    console.log(`Starting load test: ${testName}`);
    console.log(`Duration: ${duration}ms, Users: ${concurrentUsers}, Ramp-up: ${rampUpTime}ms`);

    const results = {
      testName,
      startTime: Date.now(),
      endTime: null,
      duration,
      concurrentUsers,
      totalRequests: 0,
      successfulRequests: 0,
      failedRequests: 0,
      latencies: [],
      errors: [],
      throughput: 0,
      averageLatency: 0,
      p50Latency: 0,
      p95Latency: 0,
      p99Latency: 0,
      minLatency: Infinity,
      maxLatency: 0,
      errorRate: 0,
      memoryUsage: [],
      cpuUsage: []
    };

    // Warmup phase
    console.log('Running warmup requests...');
    await this.runWarmup(requestGenerator, warmupRequests);

    // Start monitoring
    const monitoringInterval = this.startMonitoring(results);

    // Ramp up users gradually
    const userPromises = [];
    const userStartInterval = rampUpTime / concurrentUsers;

    for (let i = 0; i < concurrentUsers; i++) {
      setTimeout(() => {
        const userPromise = this.simulateUser(requestGenerator, duration - (i * userStartInterval), results);
        userPromises.push(userPromise);
      }, i * userStartInterval);
    }

    // Wait for all users to complete
    await Promise.all(userPromises);

    // Stop monitoring
    clearInterval(monitoringInterval);

    // Calculate final metrics
    results.endTime = Date.now();
    results.actualDuration = results.endTime - results.startTime;
    results.throughput = results.totalRequests / (results.actualDuration / 1000);
    results.errorRate = results.failedRequests / results.totalRequests;
    
    if (results.latencies.length > 0) {
      results.averageLatency = results.latencies.reduce((sum, l) => sum + l, 0) / results.latencies.length;
      results.p50Latency = this.calculatePercentile(results.latencies, 50);
      results.p95Latency = this.calculatePercentile(results.latencies, 95);
      results.p99Latency = this.calculatePercentile(results.latencies, 99);
      results.minLatency = Math.min(...results.latencies);
      results.maxLatency = Math.max(...results.latencies);
    }

    // Evaluate against thresholds
    results.passed = this.evaluatePerformanceThresholds(results);

    this.testResults.set(testName, results);
    this.logTestResults(results);

    return results;
  }

  async runWarmup(requestGenerator, count) {
    const warmupPromises = [];
    
    for (let i = 0; i < count; i++) {
      warmupPromises.push(
        requestGenerator().catch(() => {}) // Ignore warmup errors
      );
    }
    
    await Promise.all(warmupPromises);
  }

  async simulateUser(requestGenerator, duration, results) {
    const endTime = Date.now() + duration;
    
    while (Date.now() < endTime) {
      const startTime = performance.now();
      
      try {
        await requestGenerator();
        
        const latency = performance.now() - startTime;
        results.latencies.push(latency);
        results.successfulRequests++;
        
      } catch (error) {
        results.errors.push({
          timestamp: Date.now(),
          error: error.message,
          latency: performance.now() - startTime
        });
        results.failedRequests++;
      }
      
      results.totalRequests++;
      
      // Small delay to prevent overwhelming the system
      await this.sleep(Math.random() * 100);
    }
  }

  startMonitoring(results) {
    return setInterval(async () => {
      try {
        // Monitor memory usage
        const memoryUsage = await this.getMemoryUsage();
        if (memoryUsage) {
          results.memoryUsage.push({
            timestamp: Date.now(),
            ...memoryUsage
          });
        }

        // Monitor CPU usage
        const cpuUsage = await this.getCpuUsage();
        if (cpuUsage) {
          results.cpuUsage.push({
            timestamp: Date.now(),
            usage: cpuUsage
          });
        }
      } catch (error) {
        console.error('Monitoring error:', error.message);
      }
    }, 1000);
  }

  // Specific performance tests
  async testApiEndpointPerformance() {
    console.log('Testing API endpoint performance...');
    
    const endpoints = [
      { name: 'Health Check', path: '/health', method: 'GET' },
      { name: 'User Authentication', path: '/api/auth/login', method: 'POST', data: { email: 'test@example.com', password: 'password' } },
      { name: 'Meeting List', path: '/api/meetings', method: 'GET' },
      { name: 'Human Needs Analysis', path: '/api/analysis/human-needs', method: 'POST', data: { transcript: 'Test transcript for analysis' } },
      { name: 'Strategic Alignment', path: '/api/analysis/strategic-alignment', method: 'POST', data: { transcript: 'Strategic discussion content' } }
    ];

    const results = {};

    for (const endpoint of endpoints) {
      const requestGenerator = () => this.makeApiRequest(endpoint);
      
      const testResult = await this.runLoadTest(
        `API: ${endpoint.name}`,
        requestGenerator,
        { duration: 30000, concurrentUsers: 5 }
      );
      
      results[endpoint.name] = testResult;
    }

    return results;
  }

  async testWebSocketPerformance() {
    console.log('Testing WebSocket performance...');
    
    const requestGenerator = async () => {
      const ws = await this.createWebSocketConnection();
      
      return new Promise((resolve, reject) => {
        const timeout = setTimeout(() => {
          ws.close();
          reject(new Error('WebSocket timeout'));
        }, 5000);
        
        ws.on('message', () => {
          clearTimeout(timeout);
          ws.close();
          resolve();
        });
        
        ws.send(JSON.stringify({
          type: 'test_message',
          data: { timestamp: Date.now() }
        }));
      });
    };

    return await this.runLoadTest(
      'WebSocket Communication',
      requestGenerator,
      { duration: 30000, concurrentUsers: 20 }
    );
  }

  async testVoiceProcessingPerformance() {
    console.log('Testing voice processing performance...');
    
    // Generate test audio data
    const testAudioData = Buffer.alloc(1024 * 1024); // 1MB of test data
    
    const requestGenerator = async () => {
      const formData = new FormData();
      formData.append('audio', new Blob([testAudioData]), 'test-audio.wav');
      formData.append('meetingId', 'test-meeting-1');
      
      const response = await axios.post(`${this.config.apiUrl}/api/voice/process`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 30000
      });
      
      return response.data;
    };

    return await this.runLoadTest(
      'Voice Processing',
      requestGenerator,
      { duration: 60000, concurrentUsers: 3 }
    );
  }

  async testDatabasePerformance() {
    console.log('Testing database performance...');
    
    const operations = [
      {
        name: 'Read Operations',
        generator: () => this.get('/api/meetings?limit=50')
      },
      {
        name: 'Write Operations',
        generator: () => this.post('/api/meetings', {
          title: `Performance Test Meeting ${Date.now()}`,
          participants: ['test-user-1'],
          date: new Date().toISOString()
        })
      },
      {
        name: 'Complex Queries',
        generator: () => this.get('/api/analytics/dashboard?timeRange=30d&includePatterns=true')
      }
    ];

    const results = {};

    for (const operation of operations) {
      const testResult = await this.runLoadTest(
        `Database: ${operation.name}`,
        operation.generator,
        { duration: 30000, concurrentUsers: 8 }
      );
      
      results[operation.name] = testResult;
    }

    return results;
  }

  async testFrontendPerformance() {
    console.log('Testing frontend performance...');
    
    // This would typically use a headless browser like Puppeteer
    // For now, we'll test the static asset serving performance
    
    const assets = [
      '/static/js/main.js',
      '/static/css/main.css',
      '/static/media/logo.svg',
      '/',
      '/dashboard',
      '/analytics'
    ];

    const results = {};

    for (const asset of assets) {
      const requestGenerator = () => axios.get(`${this.config.baseUrl}${asset}`);
      
      const testResult = await this.runLoadTest(
        `Frontend: ${asset}`,
        requestGenerator,
        { duration: 20000, concurrentUsers: 15 }
      );
      
      results[asset] = testResult;
    }

    return results;
  }

  // Stress testing
  async runStressTest(testName, requestGenerator, options = {}) {
    console.log(`Starting stress test: ${testName}`);
    
    const {
      maxUsers = 100,
      stepSize = 10,
      stepDuration = 30000,
      breakingPoint = true
    } = options;

    const results = {
      testName,
      steps: [],
      breakingPoint: null,
      maxStableUsers: 0
    };

    for (let users = stepSize; users <= maxUsers; users += stepSize) {
      console.log(`Testing with ${users} concurrent users...`);
      
      const stepResult = await this.runLoadTest(
        `${testName} - ${users} users`,
        requestGenerator,
        {
          duration: stepDuration,
          concurrentUsers: users,
          rampUpTime: 5000
        }
      );

      results.steps.push({
        users,
        ...stepResult
      });

      // Check if we've reached the breaking point
      if (breakingPoint && (
        stepResult.errorRate > this.config.maxErrorRate ||
        stepResult.p95Latency > this.config.maxP95Latency ||
        stepResult.throughput < this.config.minThroughput
      )) {
        results.breakingPoint = users;
        console.log(`Breaking point reached at ${users} users`);
        break;
      }

      if (stepResult.passed) {
        results.maxStableUsers = users;
      }

      // Brief pause between steps
      await this.sleep(5000);
    }

    return results;
  }

  // Spike testing
  async runSpikeTest(testName, requestGenerator, options = {}) {
    console.log(`Starting spike test: ${testName}`);
    
    const {
      baselineUsers = 5,
      spikeUsers = 50,
      spikeDuration = 10000,
      totalDuration = 60000
    } = options;

    const results = {
      testName,
      phases: []
    };

    // Baseline phase
    console.log(`Baseline phase: ${baselineUsers} users`);
    const baselineResult = await this.runLoadTest(
      `${testName} - Baseline`,
      requestGenerator,
      {
        duration: 15000,
        concurrentUsers: baselineUsers,
        rampUpTime: 2000
      }
    );
    results.phases.push({ phase: 'baseline', ...baselineResult });

    // Spike phase
    console.log(`Spike phase: ${spikeUsers} users`);
    const spikeResult = await this.runLoadTest(
      `${testName} - Spike`,
      requestGenerator,
      {
        duration: spikeDuration,
        concurrentUsers: spikeUsers,
        rampUpTime: 1000
      }
    );
    results.phases.push({ phase: 'spike', ...spikeResult });

    // Recovery phase
    console.log(`Recovery phase: ${baselineUsers} users`);
    const recoveryResult = await this.runLoadTest(
      `${testName} - Recovery`,
      requestGenerator,
      {
        duration: 15000,
        concurrentUsers: baselineUsers,
        rampUpTime: 2000
      }
    );
    results.phases.push({ phase: 'recovery', ...recoveryResult });

    // Analyze recovery
    results.recoveryTime = this.calculateRecoveryTime(baselineResult, recoveryResult);
    results.spikeImpact = this.calculateSpikeImpact(baselineResult, spikeResult);

    return results;
  }

  // Utility methods
  async makeApiRequest(endpoint) {
    const config = {
      method: endpoint.method,
      url: `${this.config.apiUrl}${endpoint.path}`,
      timeout: 10000
    };

    if (endpoint.data) {
      config.data = endpoint.data;
    }

    const response = await axios(config);
    return response.data;
  }

  async createWebSocketConnection() {
    return new Promise((resolve, reject) => {
      const ws = new WebSocket(this.config.wsUrl);
      
      ws.on('open', () => resolve(ws));
      ws.on('error', reject);
      
      setTimeout(() => reject(new Error('WebSocket connection timeout')), 5000);
    });
  }

  async get(endpoint) {
    return axios.get(`${this.config.apiUrl}${endpoint}`);
  }

  async post(endpoint, data) {
    return axios.post(`${this.config.apiUrl}${endpoint}`, data);
  }

  async getMemoryUsage() {
    try {
      const response = await axios.get(`${this.config.apiUrl}/admin/metrics/memory`);
      return response.data;
    } catch (error) {
      return process.memoryUsage ? {
        rss: process.memoryUsage().rss,
        heapUsed: process.memoryUsage().heapUsed,
        heapTotal: process.memoryUsage().heapTotal
      } : null;
    }
  }

  async getCpuUsage() {
    try {
      const response = await axios.get(`${this.config.apiUrl}/admin/metrics/cpu`);
      return response.data.usage;
    } catch (error) {
      return null;
    }
  }

  calculatePercentile(values, percentile) {
    const sorted = values.slice().sort((a, b) => a - b);
    const index = Math.ceil((percentile / 100) * sorted.length) - 1;
    return sorted[Math.max(0, index)];
  }

  calculateRecoveryTime(baseline, recovery) {
    const baselineLatency = baseline.averageLatency;
    const recoveryLatency = recovery.averageLatency;
    
    // Recovery is considered successful if latency returns to within 10% of baseline
    const threshold = baselineLatency * 1.1;
    
    return recoveryLatency <= threshold ? 'immediate' : 'delayed';
  }

  calculateSpikeImpact(baseline, spike) {
    const latencyIncrease = (spike.averageLatency - baseline.averageLatency) / baseline.averageLatency;
    const throughputDecrease = (baseline.throughput - spike.throughput) / baseline.throughput;
    const errorRateIncrease = spike.errorRate - baseline.errorRate;
    
    return {
      latencyIncrease: latencyIncrease * 100,
      throughputDecrease: throughputDecrease * 100,
      errorRateIncrease: errorRateIncrease * 100
    };
  }

  evaluatePerformanceThresholds(results) {
    const issues = [];
    
    if (results.averageLatency > this.config.maxLatency) {
      issues.push(`Average latency (${results.averageLatency.toFixed(2)}ms) exceeds threshold (${this.config.maxLatency}ms)`);
    }
    
    if (results.p95Latency > this.config.maxP95Latency) {
      issues.push(`P95 latency (${results.p95Latency.toFixed(2)}ms) exceeds threshold (${this.config.maxP95Latency}ms)`);
    }
    
    if (results.throughput < this.config.minThroughput) {
      issues.push(`Throughput (${results.throughput.toFixed(2)} req/s) below threshold (${this.config.minThroughput} req/s)`);
    }
    
    if (results.errorRate > this.config.maxErrorRate) {
      issues.push(`Error rate (${(results.errorRate * 100).toFixed(2)}%) exceeds threshold (${this.config.maxErrorRate * 100}%)`);
    }
    
    results.issues = issues;
    return issues.length === 0;
  }

  logTestResults(results) {
    console.log(`\n=== ${results.testName} Results ===`);
    console.log(`Duration: ${results.actualDuration}ms`);
    console.log(`Total Requests: ${results.totalRequests}`);
    console.log(`Successful: ${results.successfulRequests}`);
    console.log(`Failed: ${results.failedRequests}`);
    console.log(`Throughput: ${results.throughput.toFixed(2)} req/s`);
    console.log(`Average Latency: ${results.averageLatency.toFixed(2)}ms`);
    console.log(`P95 Latency: ${results.p95Latency.toFixed(2)}ms`);
    console.log(`P99 Latency: ${results.p99Latency.toFixed(2)}ms`);
    console.log(`Error Rate: ${(results.errorRate * 100).toFixed(2)}%`);
    console.log(`Status: ${results.passed ? 'PASS' : 'FAIL'}`);
    
    if (results.issues && results.issues.length > 0) {
      console.log('Issues:');
      results.issues.forEach(issue => console.log(`  - ${issue}`));
    }
    
    console.log('=====================================\n');
  }

  async sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // Comprehensive performance test suite
  async runComprehensivePerformanceTests() {
    console.log('Starting comprehensive performance test suite...');
    
    const allResults = {
      timestamp: new Date().toISOString(),
      config: this.config,
      tests: {}
    };

    try {
      // API endpoint performance
      allResults.tests.apiEndpoints = await this.testApiEndpointPerformance();
      
      // WebSocket performance
      allResults.tests.websockets = await this.testWebSocketPerformance();
      
      // Voice processing performance
      allResults.tests.voiceProcessing = await this.testVoiceProcessingPerformance();
      
      // Database performance
      allResults.tests.database = await this.testDatabasePerformance();
      
      // Frontend performance
      allResults.tests.frontend = await this.testFrontendPerformance();
      
      // Stress tests
      allResults.tests.stressTest = await this.runStressTest(
        'API Stress Test',
        () => this.get('/api/meetings')
      );
      
      // Spike tests
      allResults.tests.spikeTest = await this.runSpikeTest(
        'API Spike Test',
        () => this.get('/api/health')
      );
      
    } catch (error) {
      console.error('Performance test suite error:', error);
      allResults.error = error.message;
    }

    // Generate summary
    allResults.summary = this.generatePerformanceSummary(allResults.tests);
    
    // Save results
    await this.saveResults(allResults);
    
    return allResults;
  }

  generatePerformanceSummary(tests) {
    const summary = {
      overallStatus: 'PASS',
      totalTests: 0,
      passedTests: 0,
      failedTests: 0,
      criticalIssues: [],
      recommendations: []
    };

    const processTestResult = (result) => {
      if (result.passed !== undefined) {
        summary.totalTests++;
        if (result.passed) {
          summary.passedTests++;
        } else {
          summary.failedTests++;
          summary.overallStatus = 'FAIL';
          
          if (result.issues) {
            summary.criticalIssues.push(...result.issues);
          }
        }
      }
    };

    // Process all test results
    for (const [category, categoryResults] of Object.entries(tests)) {
      if (Array.isArray(categoryResults)) {
        categoryResults.forEach(processTestResult);
      } else if (typeof categoryResults === 'object') {
        if (categoryResults.passed !== undefined) {
          processTestResult(categoryResults);
        } else {
          Object.values(categoryResults).forEach(processTestResult);
        }
      }
    }

    // Generate recommendations
    if (summary.criticalIssues.length > 0) {
      summary.recommendations.push('Review and optimize slow endpoints');
      summary.recommendations.push('Consider implementing caching strategies');
      summary.recommendations.push('Monitor resource usage and scale as needed');
    }

    return summary;
  }

  async saveResults(results) {
    const filename = `performance-test-results-${Date.now()}.json`;
    const filepath = path.join(__dirname, 'results', filename);
    
    try {
      await fs.mkdir(path.dirname(filepath), { recursive: true });
      await fs.writeFile(filepath, JSON.stringify(results, null, 2));
      console.log(`Performance test results saved to: ${filepath}`);
    } catch (error) {
      console.error('Failed to save performance test results:', error);
    }
  }
}

module.exports = PerformanceTestSuite;