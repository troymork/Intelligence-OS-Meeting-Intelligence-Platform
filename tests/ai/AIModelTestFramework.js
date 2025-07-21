/**
 * AI Model Testing Framework
 * Validates analysis accuracy and consistency across diverse scenarios
 */

const fs = require('fs').promises;
const path = require('path');
const axios = require('axios');

class AIModelTestFramework {
  constructor(config = {}) {
    this.config = {
      apiUrl: process.env.TEST_API_URL || 'http://localhost:8000',
      testDataPath: path.join(__dirname, 'test-data'),
      accuracyThreshold: 0.85,
      consistencyThreshold: 0.90,
      performanceThreshold: 5000, // 5 seconds
      ...config
    };
    
    this.testResults = new Map();
    this.benchmarkData = new Map();
  }

  // Test data management
  async loadTestDatasets() {
    console.log('Loading AI test datasets...');
    
    const datasets = {
      humanNeeds: await this.loadDataset('human-needs-test-cases.json'),
      strategicAlignment: await this.loadDataset('strategic-alignment-test-cases.json'),
      patternRecognition: await this.loadDataset('pattern-recognition-test-cases.json'),
      narrativeGeneration: await this.loadDataset('narrative-generation-test-cases.json'),
      sentimentAnalysis: await this.loadDataset('sentiment-analysis-test-cases.json')
    };
    
    return datasets;
  }

  async loadDataset(filename) {
    try {
      const filepath = path.join(this.config.testDataPath, filename);
      const content = await fs.readFile(filepath, 'utf8');
      return JSON.parse(content);
    } catch (error) {
      console.warn(`Could not load dataset ${filename}:`, error.message);
      return this.generateSyntheticDataset(filename);
    }
  }

  generateSyntheticDataset(filename) {
    const type = filename.split('-')[0];
    
    switch (type) {
      case 'human':
        return this.generateHumanNeedsTestCases();
      case 'strategic':
        return this.generateStrategicAlignmentTestCases();
      case 'pattern':
        return this.generatePatternRecognitionTestCases();
      case 'narrative':
        return this.generateNarrativeTestCases();
      case 'sentiment':
        return this.generateSentimentTestCases();
      default:
        return [];
    }
  }

  generateHumanNeedsTestCases() {
    return [
      {
        id: 'hn-001',
        input: {
          transcript: "I'm feeling overwhelmed with work and haven't had time for myself lately. The team dynamics are stressful.",
          context: { meetingType: 'team-check-in', duration: 1800 }
        },
        expected: {
          subsistence: { score: 40, confidence: 0.8 },
          protection: { score: 35, confidence: 0.9 },
          affection: { score: 45, confidence: 0.7 },
          understanding: { score: 60, confidence: 0.8 },
          participation: { score: 70, confidence: 0.9 },
          leisure: { score: 20, confidence: 0.9 },
          creation: { score: 50, confidence: 0.6 },
          identity: { score: 40, confidence: 0.7 },
          freedom: { score: 30, confidence: 0.8 }
        },
        tags: ['stress', 'work-life-balance', 'team-dynamics']
      },
      {
        id: 'hn-002',
        input: {
          transcript: "The project is going well, everyone is collaborating effectively, and we're making great progress toward our goals.",
          context: { meetingType: 'project-update', duration: 2400 }
        },
        expected: {
          subsistence: { score: 75, confidence: 0.7 },
          protection: { score: 80, confidence: 0.8 },
          affection: { score: 85, confidence: 0.9 },
          understanding: { score: 80, confidence: 0.8 },
          participation: { score: 90, confidence: 0.9 },
          leisure: { score: 70, confidence: 0.6 },
          creation: { score: 85, confidence: 0.9 },
          identity: { score: 80, confidence: 0.8 },
          freedom: { score: 75, confidence: 0.7 }
        },
        tags: ['collaboration', 'progress', 'positive']
      }
    ];
  }

  generateStrategicAlignmentTestCases() {
    return [
      {
        id: 'sa-001',
        input: {
          transcript: "We need to focus on sustainable practices and reducing our environmental impact while maintaining profitability.",
          context: { meetingType: 'strategy-session', participants: 5 }
        },
        expected: {
          sdg_alignment: {
            sdg_13: { score: 0.9, confidence: 0.9 }, // Climate Action
            sdg_12: { score: 0.8, confidence: 0.8 }, // Responsible Consumption
            sdg_8: { score: 0.7, confidence: 0.7 }   // Decent Work
          },
          doughnut_economy: {
            environmental_ceiling: { score: 0.85, confidence: 0.9 },
            social_foundation: { score: 0.6, confidence: 0.7 }
          }
        },
        tags: ['sustainability', 'environment', 'strategy']
      }
    ];
  }

  generatePatternRecognitionTestCases() {
    return [
      {
        id: 'pr-001',
        input: {
          transcripts: [
            "We always seem to run out of time in these meetings.",
            "Another meeting where we didn't finish the agenda.",
            "Time management is becoming a real issue for our team."
          ],
          context: { timespan: '30d', meetingCount: 12 }
        },
        expected: {
          patterns: [
            {
              type: 'time_management',
              frequency: 0.75,
              confidence: 0.9,
              impact: 'high',
              trend: 'increasing'
            }
          ]
        },
        tags: ['time-management', 'recurring-issue']
      }
    ];
  }

  generateNarrativeTestCases() {
    return [
      {
        id: 'ng-001',
        input: {
          analysisResults: {
            humanNeeds: { subsistence: 60, protection: 70, affection: 80 },
            patterns: [{ type: 'collaboration', strength: 0.8 }],
            strategicAlignment: { sdg_alignment: 0.7 }
          },
          context: { meetingType: 'team-retrospective', duration: 3600 }
        },
        expected: {
          narrative: {
            length: { min: 200, max: 500 },
            tone: 'constructive',
            keyPoints: ['collaboration', 'needs-fulfillment', 'strategic-alignment'],
            actionItems: { min: 2, max: 5 }
          }
        },
        tags: ['narrative-generation', 'retrospective']
      }
    ];
  }

  generateSentimentTestCases() {
    return [
      {
        id: 'st-001',
        input: {
          text: "I'm really excited about this new project and the opportunities it brings for our team!"
        },
        expected: {
          sentiment: {
            polarity: 0.8,
            confidence: 0.9,
            emotions: ['excitement', 'optimism']
          }
        },
        tags: ['positive-sentiment', 'excitement']
      },
      {
        id: 'st-002',
        input: {
          text: "I'm concerned about the timeline and whether we can deliver quality work under these constraints."
        },
        expected: {
          sentiment: {
            polarity: -0.4,
            confidence: 0.8,
            emotions: ['concern', 'anxiety']
          }
        },
        tags: ['negative-sentiment', 'concern']
      }
    ];
  }

  // Model testing methods
  async testHumanNeedsModel(testCases) {
    console.log('Testing Human Needs Analysis Model...');
    
    const results = {
      testName: 'Human Needs Analysis',
      totalCases: testCases.length,
      passedCases: 0,
      failedCases: 0,
      averageAccuracy: 0,
      averageLatency: 0,
      details: []
    };

    for (const testCase of testCases) {
      const startTime = Date.now();
      
      try {
        const response = await axios.post(`${this.config.apiUrl}/api/analysis/human-needs`, {
          transcript: testCase.input.transcript,
          context: testCase.input.context
        });

        const latency = Date.now() - startTime;
        const actual = response.data.results;
        const accuracy = this.calculateHumanNeedsAccuracy(testCase.expected, actual);
        
        const testResult = {
          id: testCase.id,
          passed: accuracy >= this.config.accuracyThreshold,
          accuracy,
          latency,
          expected: testCase.expected,
          actual,
          tags: testCase.tags
        };

        results.details.push(testResult);
        
        if (testResult.passed) {
          results.passedCases++;
        } else {
          results.failedCases++;
        }
        
        results.averageLatency += latency;
        results.averageAccuracy += accuracy;

      } catch (error) {
        results.failedCases++;
        results.details.push({
          id: testCase.id,
          passed: false,
          error: error.message,
          tags: testCase.tags
        });
      }
    }

    results.averageAccuracy /= testCases.length;
    results.averageLatency /= testCases.length;
    results.successRate = results.passedCases / results.totalCases;

    this.testResults.set('humanNeeds', results);
    return results;
  }

  async testStrategicAlignmentModel(testCases) {
    console.log('Testing Strategic Alignment Model...');
    
    const results = {
      testName: 'Strategic Alignment',
      totalCases: testCases.length,
      passedCases: 0,
      failedCases: 0,
      averageAccuracy: 0,
      averageLatency: 0,
      details: []
    };

    for (const testCase of testCases) {
      const startTime = Date.now();
      
      try {
        const response = await axios.post(`${this.config.apiUrl}/api/analysis/strategic-alignment`, {
          transcript: testCase.input.transcript,
          context: testCase.input.context
        });

        const latency = Date.now() - startTime;
        const actual = response.data.results;
        const accuracy = this.calculateStrategicAlignmentAccuracy(testCase.expected, actual);
        
        const testResult = {
          id: testCase.id,
          passed: accuracy >= this.config.accuracyThreshold,
          accuracy,
          latency,
          expected: testCase.expected,
          actual,
          tags: testCase.tags
        };

        results.details.push(testResult);
        
        if (testResult.passed) {
          results.passedCases++;
        } else {
          results.failedCases++;
        }
        
        results.averageLatency += latency;
        results.averageAccuracy += accuracy;

      } catch (error) {
        results.failedCases++;
        results.details.push({
          id: testCase.id,
          passed: false,
          error: error.message,
          tags: testCase.tags
        });
      }
    }

    results.averageAccuracy /= testCases.length;
    results.averageLatency /= testCases.length;
    results.successRate = results.passedCases / results.totalCases;

    this.testResults.set('strategicAlignment', results);
    return results;
  }

  async testPatternRecognitionModel(testCases) {
    console.log('Testing Pattern Recognition Model...');
    
    const results = {
      testName: 'Pattern Recognition',
      totalCases: testCases.length,
      passedCases: 0,
      failedCases: 0,
      averageAccuracy: 0,
      averageLatency: 0,
      details: []
    };

    for (const testCase of testCases) {
      const startTime = Date.now();
      
      try {
        const response = await axios.post(`${this.config.apiUrl}/api/analysis/patterns`, {
          transcripts: testCase.input.transcripts,
          context: testCase.input.context
        });

        const latency = Date.now() - startTime;
        const actual = response.data.results;
        const accuracy = this.calculatePatternRecognitionAccuracy(testCase.expected, actual);
        
        const testResult = {
          id: testCase.id,
          passed: accuracy >= this.config.accuracyThreshold,
          accuracy,
          latency,
          expected: testCase.expected,
          actual,
          tags: testCase.tags
        };

        results.details.push(testResult);
        
        if (testResult.passed) {
          results.passedCases++;
        } else {
          results.failedCases++;
        }
        
        results.averageLatency += latency;
        results.averageAccuracy += accuracy;

      } catch (error) {
        results.failedCases++;
        results.details.push({
          id: testCase.id,
          passed: false,
          error: error.message,
          tags: testCase.tags
        });
      }
    }

    results.averageAccuracy /= testCases.length;
    results.averageLatency /= testCases.length;
    results.successRate = results.passedCases / results.totalCases;

    this.testResults.set('patternRecognition', results);
    return results;
  }

  // Accuracy calculation methods
  calculateHumanNeedsAccuracy(expected, actual) {
    const needs = Object.keys(expected);
    let totalAccuracy = 0;

    for (const need of needs) {
      const expectedScore = expected[need].score;
      const actualScore = actual[need]?.score || 0;
      const scoreDiff = Math.abs(expectedScore - actualScore) / 100;
      const scoreAccuracy = Math.max(0, 1 - scoreDiff);
      
      const expectedConfidence = expected[need].confidence;
      const actualConfidence = actual[need]?.confidence || 0;
      const confidenceDiff = Math.abs(expectedConfidence - actualConfidence);
      const confidenceAccuracy = Math.max(0, 1 - confidenceDiff);
      
      // Weight score accuracy more heavily than confidence
      const needAccuracy = (scoreAccuracy * 0.8) + (confidenceAccuracy * 0.2);
      totalAccuracy += needAccuracy;
    }

    return totalAccuracy / needs.length;
  }

  calculateStrategicAlignmentAccuracy(expected, actual) {
    let totalAccuracy = 0;
    let componentCount = 0;

    // SDG alignment accuracy
    if (expected.sdg_alignment && actual.sdg_alignment) {
      const sdgs = Object.keys(expected.sdg_alignment);
      let sdgAccuracy = 0;
      
      for (const sdg of sdgs) {
        const expectedScore = expected.sdg_alignment[sdg].score;
        const actualScore = actual.sdg_alignment[sdg]?.score || 0;
        const scoreDiff = Math.abs(expectedScore - actualScore);
        sdgAccuracy += Math.max(0, 1 - scoreDiff);
      }
      
      totalAccuracy += sdgAccuracy / sdgs.length;
      componentCount++;
    }

    // Doughnut economy accuracy
    if (expected.doughnut_economy && actual.doughnut_economy) {
      const components = Object.keys(expected.doughnut_economy);
      let doughnutAccuracy = 0;
      
      for (const component of components) {
        const expectedScore = expected.doughnut_economy[component].score;
        const actualScore = actual.doughnut_economy[component]?.score || 0;
        const scoreDiff = Math.abs(expectedScore - actualScore);
        doughnutAccuracy += Math.max(0, 1 - scoreDiff);
      }
      
      totalAccuracy += doughnutAccuracy / components.length;
      componentCount++;
    }

    return componentCount > 0 ? totalAccuracy / componentCount : 0;
  }

  calculatePatternRecognitionAccuracy(expected, actual) {
    const expectedPatterns = expected.patterns || [];
    const actualPatterns = actual.patterns || [];
    
    if (expectedPatterns.length === 0) return actualPatterns.length === 0 ? 1 : 0;
    
    let totalAccuracy = 0;
    
    for (const expectedPattern of expectedPatterns) {
      const matchingPattern = actualPatterns.find(p => p.type === expectedPattern.type);
      
      if (matchingPattern) {
        const frequencyDiff = Math.abs(expectedPattern.frequency - matchingPattern.frequency);
        const confidenceDiff = Math.abs(expectedPattern.confidence - matchingPattern.confidence);
        
        const patternAccuracy = Math.max(0, 1 - (frequencyDiff + confidenceDiff) / 2);
        totalAccuracy += patternAccuracy;
      }
    }
    
    return totalAccuracy / expectedPatterns.length;
  }

  // Consistency testing
  async testModelConsistency(modelName, testCase, iterations = 10) {
    console.log(`Testing ${modelName} consistency with ${iterations} iterations...`);
    
    const results = [];
    
    for (let i = 0; i < iterations; i++) {
      try {
        const response = await axios.post(`${this.config.apiUrl}/api/analysis/${modelName}`, testCase.input);
        results.push(response.data.results);
      } catch (error) {
        console.error(`Consistency test iteration ${i + 1} failed:`, error.message);
      }
    }
    
    if (results.length < 2) {
      return { consistency: 0, error: 'Insufficient results for consistency testing' };
    }
    
    // Calculate consistency based on variance in results
    const consistency = this.calculateResultConsistency(results);
    
    return {
      consistency,
      iterations: results.length,
      passed: consistency >= this.config.consistencyThreshold
    };
  }

  calculateResultConsistency(results) {
    // Implementation depends on result structure
    // For human needs, calculate variance across all needs
    if (results[0].subsistence !== undefined) {
      return this.calculateHumanNeedsConsistency(results);
    }
    
    // For other models, implement specific consistency calculations
    return 0.5; // Placeholder
  }

  calculateHumanNeedsConsistency(results) {
    const needs = ['subsistence', 'protection', 'affection', 'understanding', 
                   'participation', 'leisure', 'creation', 'identity', 'freedom'];
    
    let totalConsistency = 0;
    
    for (const need of needs) {
      const scores = results.map(r => r[need]?.score || 0);
      const mean = scores.reduce((sum, score) => sum + score, 0) / scores.length;
      const variance = scores.reduce((sum, score) => sum + Math.pow(score - mean, 2), 0) / scores.length;
      const standardDeviation = Math.sqrt(variance);
      
      // Consistency is inversely related to standard deviation
      // Normalize to 0-1 scale where 1 is perfectly consistent
      const needConsistency = Math.max(0, 1 - (standardDeviation / 50)); // 50 is max expected std dev
      totalConsistency += needConsistency;
    }
    
    return totalConsistency / needs.length;
  }

  // Performance testing
  async testModelPerformance(modelName, testCases, options = {}) {
    const {
      concurrentRequests = 5,
      iterations = 100
    } = options;
    
    console.log(`Testing ${modelName} performance with ${iterations} iterations and ${concurrentRequests} concurrent requests...`);
    
    const results = {
      modelName,
      iterations,
      concurrentRequests,
      latencies: [],
      errors: [],
      startTime: Date.now(),
      endTime: null
    };
    
    const testPromises = [];
    
    for (let i = 0; i < iterations; i++) {
      const testCase = testCases[i % testCases.length];
      
      const testPromise = (async () => {
        const startTime = Date.now();
        try {
          await axios.post(`${this.config.apiUrl}/api/analysis/${modelName}`, testCase.input);
          const latency = Date.now() - startTime;
          results.latencies.push(latency);
        } catch (error) {
          results.errors.push(error.message);
        }
      })();
      
      testPromises.push(testPromise);
      
      // Control concurrency
      if (testPromises.length >= concurrentRequests) {
        await Promise.all(testPromises);
        testPromises.length = 0;
      }
    }
    
    // Wait for remaining promises
    if (testPromises.length > 0) {
      await Promise.all(testPromises);
    }
    
    results.endTime = Date.now();
    results.totalDuration = results.endTime - results.startTime;
    results.averageLatency = results.latencies.reduce((sum, l) => sum + l, 0) / results.latencies.length;
    results.minLatency = Math.min(...results.latencies);
    results.maxLatency = Math.max(...results.latencies);
    results.p95Latency = this.calculatePercentile(results.latencies, 95);
    results.p99Latency = this.calculatePercentile(results.latencies, 99);
    results.throughput = results.latencies.length / (results.totalDuration / 1000);
    results.errorRate = results.errors.length / iterations;
    
    return results;
  }

  calculatePercentile(values, percentile) {
    const sorted = values.slice().sort((a, b) => a - b);
    const index = Math.ceil((percentile / 100) * sorted.length) - 1;
    return sorted[index];
  }

  // Comprehensive test suite
  async runComprehensiveTests() {
    console.log('Running comprehensive AI model tests...');
    
    const datasets = await this.loadTestDatasets();
    const allResults = {};
    
    // Test each model
    if (datasets.humanNeeds.length > 0) {
      allResults.humanNeeds = await this.testHumanNeedsModel(datasets.humanNeeds);
      allResults.humanNeedsConsistency = await this.testModelConsistency('human-needs', datasets.humanNeeds[0]);
      allResults.humanNeedsPerformance = await this.testModelPerformance('human-needs', datasets.humanNeeds);
    }
    
    if (datasets.strategicAlignment.length > 0) {
      allResults.strategicAlignment = await this.testStrategicAlignmentModel(datasets.strategicAlignment);
      allResults.strategicConsistency = await this.testModelConsistency('strategic-alignment', datasets.strategicAlignment[0]);
      allResults.strategicPerformance = await this.testModelPerformance('strategic-alignment', datasets.strategicAlignment);
    }
    
    if (datasets.patternRecognition.length > 0) {
      allResults.patternRecognition = await this.testPatternRecognitionModel(datasets.patternRecognition);
      allResults.patternConsistency = await this.testModelConsistency('patterns', datasets.patternRecognition[0]);
      allResults.patternPerformance = await this.testModelPerformance('patterns', datasets.patternRecognition);
    }
    
    // Generate summary report
    const summary = this.generateTestSummary(allResults);
    
    return {
      summary,
      detailed: allResults,
      timestamp: new Date().toISOString()
    };
  }

  generateTestSummary(results) {
    const summary = {
      overallStatus: 'PASS',
      totalTests: 0,
      passedTests: 0,
      failedTests: 0,
      averageAccuracy: 0,
      averageLatency: 0,
      issues: []
    };
    
    const accuracyTests = [];
    const latencyTests = [];
    
    for (const [testName, result] of Object.entries(results)) {
      if (result.totalCases) {
        summary.totalTests += result.totalCases;
        summary.passedTests += result.passedCases;
        summary.failedTests += result.failedCases;
        accuracyTests.push(result.averageAccuracy);
        latencyTests.push(result.averageLatency);
        
        if (result.averageAccuracy < this.config.accuracyThreshold) {
          summary.issues.push(`${testName} accuracy below threshold: ${result.averageAccuracy.toFixed(3)}`);
          summary.overallStatus = 'FAIL';
        }
        
        if (result.averageLatency > this.config.performanceThreshold) {
          summary.issues.push(`${testName} latency above threshold: ${result.averageLatency}ms`);
          summary.overallStatus = 'FAIL';
        }
      }
      
      if (result.consistency !== undefined && result.consistency < this.config.consistencyThreshold) {
        summary.issues.push(`${testName} consistency below threshold: ${result.consistency.toFixed(3)}`);
        summary.overallStatus = 'FAIL';
      }
    }
    
    summary.averageAccuracy = accuracyTests.reduce((sum, acc) => sum + acc, 0) / accuracyTests.length;
    summary.averageLatency = latencyTests.reduce((sum, lat) => sum + lat, 0) / latencyTests.length;
    
    return summary;
  }
}

module.exports = AIModelTestFramework;