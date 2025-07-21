/**
 * Test Data Generator
 * Generates realistic test data for various testing scenarios
 */

class TestDataGenerator {
  constructor() {
    this.faker = this.createFaker();
  }

  // Create a simple faker implementation
  createFaker() {
    const names = ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank', 'Grace', 'Henry'];
    const companies = ['TechCorp', 'InnovateLtd', 'FutureSoft', 'DataDyne', 'CloudFirst'];
    const topics = ['strategy', 'planning', 'review', 'brainstorming', 'decision-making'];
    
    return {
      name: () => names[Math.floor(Math.random() * names.length)],
      company: () => companies[Math.floor(Math.random() * companies.length)],
      email: (name) => `${name.toLowerCase()}@example.com`,
      topic: () => topics[Math.floor(Math.random() * topics.length)],
      sentence: () => 'This is a sample sentence for testing purposes.',
      paragraph: () => 'This is a sample paragraph with multiple sentences. It contains realistic content for testing. The content is designed to be meaningful yet generic.',
      number: (min = 0, max = 100) => Math.floor(Math.random() * (max - min + 1)) + min,
      date: () => new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000),
      boolean: () => Math.random() > 0.5
    };
  }

  // Generate user data
  generateUser(overrides = {}) {
    const name = this.faker.name();
    return {
      id: `user-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      name,
      email: this.faker.email(name),
      role: 'user',
      createdAt: this.faker.date().toISOString(),
      preferences: this.generateUserPreferences(),
      ...overrides
    };
  }

  generateUserPreferences() {
    return {
      theme: 'auto',
      language: 'en',
      notifications: true,
      voiceEnabled: true,
      expertiseLevel: 'intermediate'
    };
  }

  // Generate meeting data
  generateMeeting(overrides = {}) {
    const participants = Array.from({ length: this.faker.number(2, 8) }, () => this.generateUser());
    
    return {
      id: `meeting-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      title: `${this.faker.topic()} Meeting`,
      description: this.faker.paragraph(),
      participants: participants.map(p => p.id),
      startTime: this.faker.date().toISOString(),
      duration: this.faker.number(30, 120) * 60000, // 30-120 minutes in ms
      status: 'completed',
      transcript: this.generateTranscript(),
      ...overrides
    };
  }

  generateTranscript() {
    const speakers = ['Speaker A', 'Speaker B', 'Speaker C'];
    const segments = [];
    
    for (let i = 0; i < this.faker.number(10, 30); i++) {
      segments.push({
        speaker: speakers[Math.floor(Math.random() * speakers.length)],
        timestamp: i * 30000, // 30 seconds apart
        text: this.faker.paragraph(),
        confidence: 0.8 + Math.random() * 0.2
      });
    }
    
    return {
      segments,
      fullText: segments.map(s => s.text).join(' '),
      duration: segments.length * 30000,
      language: 'en'
    };
  }

  // Generate analysis results
  generateHumanNeedsAnalysis(overrides = {}) {
    const needs = [
      'subsistence', 'protection', 'affection', 'understanding',
      'participation', 'leisure', 'creation', 'identity', 'freedom'
    ];
    
    const results = {};
    needs.forEach(need => {
      results[need] = {
        score: this.faker.number(20, 95),
        confidence: 0.7 + Math.random() * 0.3,
        evidence: [this.faker.sentence(), this.faker.sentence()],
        trend: Math.random() > 0.5 ? 'increasing' : 'stable'
      };
    });
    
    return {
      id: `analysis-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      type: 'human_needs',
      results,
      timestamp: new Date().toISOString(),
      ...overrides
    };
  }

  generateStrategicAlignmentAnalysis(overrides = {}) {
    const sdgs = [
      'sdg_1', 'sdg_3', 'sdg_4', 'sdg_5', 'sdg_8', 'sdg_9', 'sdg_10', 'sdg_11', 'sdg_13', 'sdg_16'
    ];
    
    const sdgAlignment = {};
    sdgs.forEach(sdg => {
      sdgAlignment[sdg] = {
        score: Math.random(),
        confidence: 0.6 + Math.random() * 0.4,
        evidence: [this.faker.sentence()]
      };
    });
    
    return {
      id: `analysis-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      type: 'strategic_alignment',
      results: {
        sdg_alignment: sdgAlignment,
        doughnut_economy: {
          environmental_ceiling: {
            score: Math.random(),
            confidence: 0.7 + Math.random() * 0.3
          },
          social_foundation: {
            score: Math.random(),
            confidence: 0.7 + Math.random() * 0.3
          }
        }
      },
      timestamp: new Date().toISOString(),
      ...overrides
    };
  }

  generatePatternAnalysis(overrides = {}) {
    const patternTypes = [
      'communication_style', 'decision_making', 'collaboration',
      'time_management', 'conflict_resolution', 'innovation'
    ];
    
    const patterns = patternTypes.map(type => ({
      type,
      frequency: Math.random(),
      strength: Math.random(),
      confidence: 0.6 + Math.random() * 0.4,
      trend: Math.random() > 0.5 ? 'increasing' : 'stable',
      impact: Math.random() > 0.7 ? 'high' : Math.random() > 0.4 ? 'medium' : 'low',
      description: `Pattern related to ${type.replace('_', ' ')}`,
      evidence: [this.faker.sentence(), this.faker.sentence()]
    }));
    
    return {
      id: `analysis-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      type: 'pattern_recognition',
      results: { patterns },
      timestamp: new Date().toISOString(),
      ...overrides
    };
  }

  // Generate performance test data
  generatePerformanceTestData(size = 'medium') {
    const sizes = {
      small: { users: 10, meetings: 50, analyses: 100 },
      medium: { users: 100, meetings: 500, analyses: 1000 },
      large: { users: 1000, meetings: 5000, analyses: 10000 }
    };
    
    const config = sizes[size] || sizes.medium;
    
    return {
      users: Array.from({ length: config.users }, () => this.generateUser()),
      meetings: Array.from({ length: config.meetings }, () => this.generateMeeting()),
      analyses: Array.from({ length: config.analyses }, () => {
        const type = Math.random();
        if (type < 0.33) return this.generateHumanNeedsAnalysis();
        if (type < 0.66) return this.generateStrategicAlignmentAnalysis();
        return this.generatePatternAnalysis();
      })
    };
  }

  // Generate load test scenarios
  generateLoadTestScenarios() {
    return [
      {
        name: 'Normal Load',
        users: 10,
        duration: 60000,
        rampUp: 10000,
        requests: [
          { endpoint: '/api/meetings', weight: 0.4 },
          { endpoint: '/api/analysis/human-needs', weight: 0.3 },
          { endpoint: '/api/analysis/strategic-alignment', weight: 0.2 },
          { endpoint: '/api/dashboard', weight: 0.1 }
        ]
      },
      {
        name: 'Peak Load',
        users: 50,
        duration: 120000,
        rampUp: 20000,
        requests: [
          { endpoint: '/api/meetings', weight: 0.5 },
          { endpoint: '/api/analysis/human-needs', weight: 0.25 },
          { endpoint: '/api/analysis/strategic-alignment', weight: 0.15 },
          { endpoint: '/api/dashboard', weight: 0.1 }
        ]
      },
      {
        name: 'Stress Test',
        users: 100,
        duration: 300000,
        rampUp: 30000,
        requests: [
          { endpoint: '/api/meetings', weight: 0.6 },
          { endpoint: '/api/analysis/human-needs', weight: 0.2 },
          { endpoint: '/api/analysis/strategic-alignment', weight: 0.1 },
          { endpoint: '/api/dashboard', weight: 0.1 }
        ]
      }
    ];
  }

  // Generate AI model test cases
  generateAITestCases(type, count = 10) {
    const cases = [];
    
    for (let i = 0; i < count; i++) {
      switch (type) {
        case 'human_needs':
          cases.push(this.generateHumanNeedsTestCase());
          break;
        case 'strategic_alignment':
          cases.push(this.generateStrategicAlignmentTestCase());
          break;
        case 'pattern_recognition':
          cases.push(this.generatePatternRecognitionTestCase());
          break;
        default:
          throw new Error(`Unknown test case type: ${type}`);
      }
    }
    
    return cases;
  }

  generateHumanNeedsTestCase() {
    const scenarios = [
      {
        transcript: "I'm feeling overwhelmed with the workload and need more support from the team.",
        expected: { subsistence: 40, protection: 35, affection: 60 }
      },
      {
        transcript: "Great collaboration today! Everyone contributed and we made excellent progress.",
        expected: { participation: 85, affection: 80, creation: 75 }
      },
      {
        transcript: "I need more autonomy in my role to make decisions and drive initiatives.",
        expected: { identity: 70, freedom: 80, creation: 65 }
      }
    ];
    
    const scenario = scenarios[Math.floor(Math.random() * scenarios.length)];
    
    return {
      id: `hn-test-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      input: {
        transcript: scenario.transcript,
        context: { meetingType: 'team-check-in', duration: 1800 }
      },
      expected: scenario.expected,
      tags: ['human-needs', 'sentiment']
    };
  }

  generateStrategicAlignmentTestCase() {
    const scenarios = [
      {
        transcript: "We need to focus on sustainable practices and environmental responsibility.",
        expected: { sdg_13: 0.9, sdg_12: 0.8 }
      },
      {
        transcript: "Our diversity and inclusion initiatives are making a real difference.",
        expected: { sdg_5: 0.85, sdg_10: 0.8 }
      },
      {
        transcript: "Innovation and technology development are key to our future success.",
        expected: { sdg_9: 0.9, sdg_8: 0.7 }
      }
    ];
    
    const scenario = scenarios[Math.floor(Math.random() * scenarios.length)];
    
    return {
      id: `sa-test-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      input: {
        transcript: scenario.transcript,
        context: { meetingType: 'strategy-session', participants: 5 }
      },
      expected: { sdg_alignment: scenario.expected },
      tags: ['strategic-alignment', 'sdg']
    };
  }

  generatePatternRecognitionTestCase() {
    return {
      id: `pr-test-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      input: {
        transcripts: [
          "We always run out of time in these meetings.",
          "Another meeting where we didn't finish the agenda.",
          "Time management is becoming a real issue."
        ],
        context: { timespan: '30d', meetingCount: 12 }
      },
      expected: {
        patterns: [{
          type: 'time_management',
          frequency: 0.75,
          confidence: 0.9
        }]
      },
      tags: ['pattern-recognition', 'time-management']
    };
  }

  // Utility methods
  generateBatch(generator, count) {
    return Array.from({ length: count }, () => generator());
  }

  saveToFile(data, filename) {
    const fs = require('fs');
    const path = require('path');
    
    const filepath = path.join(__dirname, '../test-data', filename);
    fs.writeFileSync(filepath, JSON.stringify(data, null, 2));
    
    return filepath;
  }

  loadFromFile(filename) {
    const fs = require('fs');
    const path = require('path');
    
    const filepath = path.join(__dirname, '../test-data', filename);
    return JSON.parse(fs.readFileSync(filepath, 'utf8'));
  }
}

module.exports = TestDataGenerator;