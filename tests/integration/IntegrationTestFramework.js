/**
 * Integration Test Framework
 * Comprehensive testing for end-to-end workflows and system interactions
 */

const axios = require('axios');
const WebSocket = require('ws');
const { spawn } = require('child_process');
const fs = require('fs').promises;
const path = require('path');

class IntegrationTestFramework {
  constructor(config = {}) {
    this.config = {
      baseUrl: process.env.TEST_BASE_URL || 'http://localhost:3000',
      apiUrl: process.env.TEST_API_URL || 'http://localhost:8000',
      wsUrl: process.env.TEST_WS_URL || 'ws://localhost:8000/ws',
      timeout: 30000,
      retries: 3,
      ...config
    };
    
    this.services = new Map();
    this.testData = new Map();
    this.cleanup = [];
  }

  // Service management
  async startService(name, command, args = [], options = {}) {
    console.log(`Starting service: ${name}`);
    
    const service = spawn(command, args, {
      stdio: 'pipe',
      env: { ...process.env, ...options.env },
      cwd: options.cwd || process.cwd()
    });

    service.stdout.on('data', (data) => {
      if (options.verbose) {
        console.log(`[${name}] ${data.toString()}`);
      }
    });

    service.stderr.on('data', (data) => {
      console.error(`[${name}] ${data.toString()}`);
    });

    this.services.set(name, service);
    this.cleanup.push(() => this.stopService(name));

    // Wait for service to be ready
    if (options.healthCheck) {
      await this.waitForHealthCheck(options.healthCheck, options.timeout || 30000);
    }

    return service;
  }

  async stopService(name) {
    const service = this.services.get(name);
    if (service) {
      service.kill('SIGTERM');
      this.services.delete(name);
      console.log(`Stopped service: ${name}`);
    }
  }

  async waitForHealthCheck(url, timeout = 30000) {
    const start = Date.now();
    
    while (Date.now() - start < timeout) {
      try {
        const response = await axios.get(url, { timeout: 5000 });
        if (response.status === 200) {
          return true;
        }
      } catch (error) {
        // Service not ready yet
      }
      
      await this.sleep(1000);
    }
    
    throw new Error(`Health check failed for ${url} after ${timeout}ms`);
  }

  // HTTP testing utilities
  async makeRequest(method, endpoint, data = null, headers = {}) {
    const url = `${this.config.apiUrl}${endpoint}`;
    const config = {
      method,
      url,
      headers: {
        'Content-Type': 'application/json',
        ...headers
      },
      timeout: this.config.timeout
    };

    if (data) {
      config.data = data;
    }

    try {
      const response = await axios(config);
      return {
        status: response.status,
        data: response.data,
        headers: response.headers
      };
    } catch (error) {
      if (error.response) {
        return {
          status: error.response.status,
          data: error.response.data,
          headers: error.response.headers,
          error: error.message
        };
      }
      throw error;
    }
  }

  async get(endpoint, headers = {}) {
    return this.makeRequest('GET', endpoint, null, headers);
  }

  async post(endpoint, data, headers = {}) {
    return this.makeRequest('POST', endpoint, data, headers);
  }

  async put(endpoint, data, headers = {}) {
    return this.makeRequest('PUT', endpoint, data, headers);
  }

  async delete(endpoint, headers = {}) {
    return this.makeRequest('DELETE', endpoint, null, headers);
  }

  // WebSocket testing utilities
  async createWebSocketConnection(endpoint = '') {
    return new Promise((resolve, reject) => {
      const ws = new WebSocket(`${this.config.wsUrl}${endpoint}`);
      
      ws.on('open', () => {
        resolve(ws);
      });
      
      ws.on('error', (error) => {
        reject(error);
      });
      
      setTimeout(() => {
        reject(new Error('WebSocket connection timeout'));
      }, this.config.timeout);
    });
  }

  async sendWebSocketMessage(ws, message) {
    return new Promise((resolve, reject) => {
      ws.send(JSON.stringify(message));
      
      const timeout = setTimeout(() => {
        reject(new Error('WebSocket message timeout'));
      }, this.config.timeout);
      
      ws.once('message', (data) => {
        clearTimeout(timeout);
        try {
          const response = JSON.parse(data);
          resolve(response);
        } catch (error) {
          resolve(data.toString());
        }
      });
    });
  }

  // Database testing utilities
  async setupTestDatabase() {
    // Create test database
    await this.post('/admin/database/create-test', {
      name: 'test_intelligence_os'
    });
    
    // Run migrations
    await this.post('/admin/database/migrate', {
      database: 'test_intelligence_os'
    });
    
    // Seed test data
    await this.seedTestData();
  }

  async cleanupTestDatabase() {
    await this.post('/admin/database/drop-test', {
      name: 'test_intelligence_os'
    });
  }

  async seedTestData() {
    const testData = {
      users: [
        {
          id: 'test-user-1',
          name: 'Test User 1',
          email: 'test1@example.com',
          role: 'user'
        },
        {
          id: 'test-user-2',
          name: 'Test User 2',
          email: 'test2@example.com',
          role: 'admin'
        }
      ],
      meetings: [
        {
          id: 'test-meeting-1',
          title: 'Test Meeting 1',
          participants: ['test-user-1', 'test-user-2'],
          date: new Date().toISOString(),
          transcript: 'This is a test meeting transcript for integration testing.'
        }
      ],
      analyses: [
        {
          id: 'test-analysis-1',
          meetingId: 'test-meeting-1',
          type: 'human_needs',
          results: {
            subsistence: 75,
            protection: 80,
            affection: 65,
            understanding: 90
          }
        }
      ]
    };

    for (const [collection, items] of Object.entries(testData)) {
      for (const item of items) {
        await this.post(`/api/${collection}`, item);
      }
    }

    this.testData.set('seeded', testData);
  }

  // File system utilities
  async createTestFile(filename, content) {
    const filepath = path.join(__dirname, 'temp', filename);
    await fs.mkdir(path.dirname(filepath), { recursive: true });
    await fs.writeFile(filepath, content);
    this.cleanup.push(() => fs.unlink(filepath).catch(() => {}));
    return filepath;
  }

  async readTestFile(filename) {
    const filepath = path.join(__dirname, 'temp', filename);
    return fs.readFile(filepath, 'utf8');
  }

  // Workflow testing utilities
  async testVoiceToAnalysisWorkflow() {
    console.log('Testing voice-to-analysis workflow...');
    
    // 1. Upload audio file
    const audioFile = await this.createTestFile('test-audio.wav', 'mock audio data');
    const uploadResponse = await this.post('/api/voice/upload', {
      file: audioFile,
      meetingId: 'test-meeting-1'
    });
    
    expect(uploadResponse.status).toBe(200);
    expect(uploadResponse.data.transcriptId).toBeDefined();
    
    // 2. Wait for transcription
    const transcriptId = uploadResponse.data.transcriptId;
    let transcript = null;
    
    for (let i = 0; i < 30; i++) {
      const transcriptResponse = await this.get(`/api/transcripts/${transcriptId}`);
      if (transcriptResponse.data.status === 'completed') {
        transcript = transcriptResponse.data;
        break;
      }
      await this.sleep(1000);
    }
    
    expect(transcript).toBeTruthy();
    expect(transcript.text).toBeDefined();
    
    // 3. Trigger analysis
    const analysisResponse = await this.post('/api/analysis/start', {
      transcriptId,
      analysisTypes: ['human_needs', 'strategic_alignment']
    });
    
    expect(analysisResponse.status).toBe(200);
    expect(analysisResponse.data.analysisId).toBeDefined();
    
    // 4. Wait for analysis completion
    const analysisId = analysisResponse.data.analysisId;
    let analysis = null;
    
    for (let i = 0; i < 60; i++) {
      const analysisStatusResponse = await this.get(`/api/analysis/${analysisId}`);
      if (analysisStatusResponse.data.status === 'completed') {
        analysis = analysisStatusResponse.data;
        break;
      }
      await this.sleep(2000);
    }
    
    expect(analysis).toBeTruthy();
    expect(analysis.results).toBeDefined();
    expect(analysis.results.human_needs).toBeDefined();
    expect(analysis.results.strategic_alignment).toBeDefined();
    
    return analysis;
  }

  async testRealTimeCollaborationWorkflow() {
    console.log('Testing real-time collaboration workflow...');
    
    // 1. Create WebSocket connections for multiple users
    const user1Ws = await this.createWebSocketConnection('/collaboration');
    const user2Ws = await this.createWebSocketConnection('/collaboration');
    
    // 2. Join collaboration session
    await this.sendWebSocketMessage(user1Ws, {
      type: 'join_session',
      sessionId: 'test-session-1',
      userId: 'test-user-1'
    });
    
    await this.sendWebSocketMessage(user2Ws, {
      type: 'join_session',
      sessionId: 'test-session-1',
      userId: 'test-user-2'
    });
    
    // 3. Test real-time updates
    const updatePromise = new Promise((resolve) => {
      user2Ws.once('message', (data) => {
        const message = JSON.parse(data);
        resolve(message);
      });
    });
    
    await this.sendWebSocketMessage(user1Ws, {
      type: 'update_analysis',
      sessionId: 'test-session-1',
      data: {
        type: 'human_needs',
        updates: { subsistence: 85 }
      }
    });
    
    const receivedUpdate = await updatePromise;
    expect(receivedUpdate.type).toBe('analysis_updated');
    expect(receivedUpdate.data.updates.subsistence).toBe(85);
    
    // 4. Clean up connections
    user1Ws.close();
    user2Ws.close();
  }

  async testDataPipelineWorkflow() {
    console.log('Testing data pipeline workflow...');
    
    // 1. Create test meeting data
    const meetingData = {
      title: 'Pipeline Test Meeting',
      participants: ['test-user-1'],
      transcript: 'This meeting discusses strategic initiatives and team collaboration.',
      metadata: {
        duration: 3600,
        language: 'en'
      }
    };
    
    const meetingResponse = await this.post('/api/meetings', meetingData);
    expect(meetingResponse.status).toBe(201);
    
    const meetingId = meetingResponse.data.id;
    
    // 2. Trigger full analysis pipeline
    const pipelineResponse = await this.post('/api/pipeline/process', {
      meetingId,
      stages: [
        'transcript_processing',
        'pattern_recognition',
        'human_needs_analysis',
        'strategic_alignment',
        'knowledge_graph_update'
      ]
    });
    
    expect(pipelineResponse.status).toBe(200);
    const pipelineId = pipelineResponse.data.pipelineId;
    
    // 3. Monitor pipeline progress
    let pipelineStatus = null;
    
    for (let i = 0; i < 120; i++) {
      const statusResponse = await this.get(`/api/pipeline/${pipelineId}/status`);
      pipelineStatus = statusResponse.data;
      
      if (pipelineStatus.status === 'completed' || pipelineStatus.status === 'failed') {
        break;
      }
      
      await this.sleep(2000);
    }
    
    expect(pipelineStatus.status).toBe('completed');
    expect(pipelineStatus.stages).toBeDefined();
    
    // 4. Verify results
    const resultsResponse = await this.get(`/api/meetings/${meetingId}/analysis`);
    expect(resultsResponse.status).toBe(200);
    
    const results = resultsResponse.data;
    expect(results.human_needs).toBeDefined();
    expect(results.strategic_alignment).toBeDefined();
    expect(results.patterns).toBeDefined();
    
    return results;
  }

  // Performance testing utilities
  async testPerformance(testName, testFunction, options = {}) {
    const {
      iterations = 10,
      concurrency = 1,
      timeout = 60000
    } = options;
    
    console.log(`Running performance test: ${testName}`);
    
    const results = {
      testName,
      iterations,
      concurrency,
      startTime: Date.now(),
      endTime: null,
      totalDuration: null,
      averageDuration: null,
      minDuration: Infinity,
      maxDuration: 0,
      successCount: 0,
      errorCount: 0,
      errors: []
    };
    
    const runTest = async () => {
      const start = Date.now();
      try {
        await testFunction();
        const duration = Date.now() - start;
        
        results.successCount++;
        results.minDuration = Math.min(results.minDuration, duration);
        results.maxDuration = Math.max(results.maxDuration, duration);
        
        return duration;
      } catch (error) {
        results.errorCount++;
        results.errors.push(error.message);
        return Date.now() - start;
      }
    };
    
    // Run tests with specified concurrency
    const batches = [];
    for (let i = 0; i < iterations; i += concurrency) {
      const batch = [];
      for (let j = 0; j < concurrency && i + j < iterations; j++) {
        batch.push(runTest());
      }
      batches.push(Promise.all(batch));
    }
    
    const allDurations = [];
    for (const batch of batches) {
      const durations = await batch;
      allDurations.push(...durations);
    }
    
    results.endTime = Date.now();
    results.totalDuration = results.endTime - results.startTime;
    results.averageDuration = allDurations.reduce((sum, d) => sum + d, 0) / allDurations.length;
    
    console.log(`Performance test completed: ${testName}`);
    console.log(`  Total duration: ${results.totalDuration}ms`);
    console.log(`  Average duration: ${results.averageDuration.toFixed(2)}ms`);
    console.log(`  Min duration: ${results.minDuration}ms`);
    console.log(`  Max duration: ${results.maxDuration}ms`);
    console.log(`  Success rate: ${(results.successCount / iterations * 100).toFixed(2)}%`);
    
    return results;
  }

  // Utility methods
  async sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  async retry(fn, retries = this.config.retries) {
    for (let i = 0; i < retries; i++) {
      try {
        return await fn();
      } catch (error) {
        if (i === retries - 1) throw error;
        await this.sleep(1000 * (i + 1));
      }
    }
  }

  // Cleanup
  async cleanup() {
    console.log('Running integration test cleanup...');
    
    // Run all cleanup functions
    for (const cleanupFn of this.cleanup.reverse()) {
      try {
        await cleanupFn();
      } catch (error) {
        console.error('Cleanup error:', error.message);
      }
    }
    
    // Stop all services
    for (const [name] of this.services) {
      await this.stopService(name);
    }
    
    // Clean up test database
    try {
      await this.cleanupTestDatabase();
    } catch (error) {
      console.error('Database cleanup error:', error.message);
    }
    
    console.log('Integration test cleanup completed');
  }
}

module.exports = IntegrationTestFramework;