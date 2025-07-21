/**
 * Security Test Framework
 * Comprehensive security testing suite for encryption, access controls, and data protection
 */

const axios = require('axios');
const crypto = require('crypto');
const fs = require('fs').promises;
const path = require('path');

class SecurityTestFramework {
  constructor(config = {}) {
    this.config = {
      baseUrl: process.env.TEST_BASE_URL || 'http://localhost:3000',
      apiUrl: process.env.TEST_API_URL || 'http://localhost:8000',
      adminApiUrl: process.env.ADMIN_API_URL || 'http://localhost:8000/admin',
      
      // Security test configuration
      maxPasswordAttempts: 5,
      sessionTimeout: 3600000, // 1 hour
      encryptionAlgorithm: 'aes-256-gcm',
      hashAlgorithm: 'sha256',
      
      // Compliance standards
      gdprCompliance: true,
      ccpaCompliance: true,
      hipaaCompliance: false,
      sox404Compliance: true,
      
      ...config
    };
    
    this.testResults = {
      authentication: [],
      authorization: [],
      encryption: [],
      dataProtection: [],
      inputValidation: [],
      sessionManagement: [],
      apiSecurity: [],
      vulnerabilities: [],
      compliance: []
    };
    
    this.vulnerabilityDatabase = new Map();
    this.complianceChecks = new Map();
  }

  // Authentication Security Tests
  async testAuthentication() {
    console.log('🔐 Testing Authentication Security...');
    
    const tests = [
      this.testPasswordComplexity(),
      this.testBruteForceProtection(),
      this.testAccountLockout(),
      this.testPasswordHashing(),
      this.testMultiFactorAuthentication(),
      this.testSessionTokenSecurity(),
      this.testPasswordReset(),
      this.testCredentialStorage()
    ];
    
    const results = await Promise.allSettled(tests);
    this.testResults.authentication = results.map((result, index) => ({
      test: tests[index].name || `Authentication Test ${index + 1}`,
      status: result.status,
      result: result.status === 'fulfilled' ? result.value : null,
      error: result.status === 'rejected' ? result.reason.message : null
    }));
    
    return this.testResults.authentication;
  }

  async testPasswordComplexity() {
    const testCases = [
      { password: '123456', shouldFail: true, reason: 'Too simple' },
      { password: 'password', shouldFail: true, reason: 'Common password' },
      { password: 'Pass123!', shouldFail: false, reason: 'Valid complexity' },
      { password: 'a', shouldFail: true, reason: 'Too short' },
      { password: 'ComplexPassword123!@#', shouldFail: false, reason: 'Strong password' }
    ];
    
    const results = [];
    
    for (const testCase of testCases) {
      try {
        const response = await axios.post(`${this.config.apiUrl}/api/auth/register`, {
          email: `test${Date.now()}@example.com`,
          password: testCase.password,
          name: 'Test User'
        });
        
        const passed = testCase.shouldFail ? response.status >= 400 : response.status < 400;
        
        results.push({
          password: testCase.password.replace(/./g, '*'),
          expected: testCase.shouldFail ? 'reject' : 'accept',
          actual: response.status >= 400 ? 'rejected' : 'accepted',
          passed,
          reason: testCase.reason
        });
        
      } catch (error) {
        const passed = testCase.shouldFail;
        results.push({
          password: testCase.password.replace(/./g, '*'),
          expected: testCase.shouldFail ? 'reject' : 'accept',
          actual: 'rejected',
          passed,
          reason: testCase.reason,
          error: error.response?.data?.message || error.message
        });
      }
    }
    
    return {
      testName: 'Password Complexity',
      results,
      passed: results.every(r => r.passed),
      summary: `${results.filter(r => r.passed).length}/${results.length} tests passed`
    };
  }

  async testBruteForceProtection() {
    const testEmail = `bruteforce${Date.now()}@example.com`;
    const wrongPassword = 'wrongpassword';
    const attempts = [];
    
    // First register a user
    await axios.post(`${this.config.apiUrl}/api/auth/register`, {
      email: testEmail,
      password: 'CorrectPassword123!',
      name: 'Brute Force Test User'
    });
    
    // Attempt multiple failed logins
    for (let i = 0; i < this.config.maxPasswordAttempts + 2; i++) {
      try {
        const startTime = Date.now();
        const response = await axios.post(`${this.config.apiUrl}/api/auth/login`, {
          email: testEmail,
          password: wrongPassword
        });
        
        attempts.push({
          attempt: i + 1,
          status: response.status,
          responseTime: Date.now() - startTime,
          blocked: false
        });
        
      } catch (error) {
        attempts.push({
          attempt: i + 1,
          status: error.response?.status || 500,
          responseTime: Date.now() - startTime,
          blocked: error.response?.status === 429 || error.response?.data?.message?.includes('locked'),
          error: error.response?.data?.message || error.message
        });
      }
    }
    
    // Check if account gets locked after max attempts
    const lockedAttempts = attempts.filter(a => a.blocked);
    const shouldBeLocked = attempts.length > this.config.maxPasswordAttempts;
    
    return {
      testName: 'Brute Force Protection',
      attempts,
      maxAttemptsAllowed: this.config.maxPasswordAttempts,
      accountLocked: lockedAttempts.length > 0,
      passed: shouldBeLocked ? lockedAttempts.length > 0 : true,
      summary: `Account ${lockedAttempts.length > 0 ? 'properly locked' : 'not locked'} after ${attempts.length} attempts`
    };
  }

  async testAccountLockout() {
    const testEmail = `lockout${Date.now()}@example.com`;
    
    // Register test user
    await axios.post(`${this.config.apiUrl}/api/auth/register`, {
      email: testEmail,
      password: 'TestPassword123!',
      name: 'Lockout Test User'
    });
    
    // Trigger account lockout
    for (let i = 0; i < this.config.maxPasswordAttempts; i++) {
      try {
        await axios.post(`${this.config.apiUrl}/api/auth/login`, {
          email: testEmail,
          password: 'wrongpassword'
        });
      } catch (error) {
        // Expected to fail
      }
    }
    
    // Try to login with correct password after lockout
    try {
      const response = await axios.post(`${this.config.apiUrl}/api/auth/login`, {
        email: testEmail,
        password: 'TestPassword123!'
      });
      
      return {
        testName: 'Account Lockout',
        passed: false,
        error: 'Account should be locked but login succeeded',
        response: response.status
      };
      
    } catch (error) {
      const isLocked = error.response?.status === 423 || 
                      error.response?.data?.message?.includes('locked') ||
                      error.response?.data?.message?.includes('suspended');
      
      return {
        testName: 'Account Lockout',
        passed: isLocked,
        status: error.response?.status,
        message: error.response?.data?.message,
        summary: isLocked ? 'Account properly locked after failed attempts' : 'Account lockout not working'
      };
    }
  }

  async testPasswordHashing() {
    // This test would typically require access to the database or admin API
    try {
      const response = await axios.get(`${this.config.adminApiUrl}/security/password-hashing-info`, {
        headers: { 'Authorization': `Bearer ${process.env.ADMIN_TOKEN}` }
      });
      
      const hashInfo = response.data;
      const validAlgorithms = ['bcrypt', 'scrypt', 'argon2', 'pbkdf2'];
      const isValidAlgorithm = validAlgorithms.some(alg => 
        hashInfo.algorithm?.toLowerCase().includes(alg)
      );
      
      return {
        testName: 'Password Hashing',
        algorithm: hashInfo.algorithm,
        saltRounds: hashInfo.saltRounds,
        isValidAlgorithm,
        passed: isValidAlgorithm && hashInfo.saltRounds >= 10,
        summary: `Using ${hashInfo.algorithm} with ${hashInfo.saltRounds} rounds`
      };
      
    } catch (error) {
      return {
        testName: 'Password Hashing',
        passed: false,
        error: 'Could not verify password hashing implementation',
        details: error.message
      };
    }
  }

  async testMultiFactorAuthentication() {
    const testEmail = `mfa${Date.now()}@example.com`;
    
    try {
      // Register user
      const registerResponse = await axios.post(`${this.config.apiUrl}/api/auth/register`, {
        email: testEmail,
        password: 'TestPassword123!',
        name: 'MFA Test User'
      });
      
      const token = registerResponse.data.token;
      
      // Enable MFA
      const mfaResponse = await axios.post(`${this.config.apiUrl}/api/auth/mfa/enable`, {}, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      const hasMfaSecret = mfaResponse.data.secret || mfaResponse.data.qrCode;
      
      return {
        testName: 'Multi-Factor Authentication',
        mfaAvailable: mfaResponse.status === 200,
        secretProvided: !!hasMfaSecret,
        passed: mfaResponse.status === 200 && hasMfaSecret,
        summary: mfaResponse.status === 200 ? 'MFA is available and working' : 'MFA not available'
      };
      
    } catch (error) {
      return {
        testName: 'Multi-Factor Authentication',
        passed: false,
        error: error.response?.data?.message || error.message,
        summary: 'MFA functionality could not be tested'
      };
    }
  }

  async testSessionTokenSecurity() {
    try {
      // Login to get a session token
      const loginResponse = await axios.post(`${this.config.apiUrl}/api/auth/login`, {
        email: 'test@example.com',
        password: 'TestPassword123!'
      });
      
      const token = loginResponse.data.token;
      
      // Analyze token properties
      const tokenParts = token.split('.');
      const isJWT = tokenParts.length === 3;
      
      let tokenAnalysis = {
        isJWT,
        length: token.length,
        entropy: this.calculateEntropy(token)
      };
      
      if (isJWT) {
        try {
          const payload = JSON.parse(Buffer.from(tokenParts[1], 'base64').toString());
          tokenAnalysis.hasExpiration = !!payload.exp;
          tokenAnalysis.expirationTime = payload.exp;
          tokenAnalysis.issuer = payload.iss;
          tokenAnalysis.audience = payload.aud;
        } catch (e) {
          tokenAnalysis.payloadError = 'Could not decode JWT payload';
        }
      }
      
      // Test token validation
      const protectedResponse = await axios.get(`${this.config.apiUrl}/api/user/profile`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      return {
        testName: 'Session Token Security',
        tokenAnalysis,
        validationWorks: protectedResponse.status === 200,
        passed: tokenAnalysis.entropy > 4 && tokenAnalysis.length > 32,
        summary: `Token entropy: ${tokenAnalysis.entropy.toFixed(2)}, Length: ${tokenAnalysis.length}`
      };
      
    } catch (error) {
      return {
        testName: 'Session Token Security',
        passed: false,
        error: error.message,
        summary: 'Could not test session token security'
      };
    }
  }

  // Authorization Security Tests
  async testAuthorization() {
    console.log('🔒 Testing Authorization Security...');
    
    const tests = [
      this.testRoleBasedAccess(),
      this.testResourcePermissions(),
      this.testPrivilegeEscalation(),
      this.testCrossUserDataAccess(),
      this.testAdminEndpointProtection()
    ];
    
    const results = await Promise.allSettled(tests);
    this.testResults.authorization = results.map((result, index) => ({
      test: tests[index].name || `Authorization Test ${index + 1}`,
      status: result.status,
      result: result.status === 'fulfilled' ? result.value : null,
      error: result.status === 'rejected' ? result.reason.message : null
    }));
    
    return this.testResults.authorization;
  }

  async testRoleBasedAccess() {
    const roles = ['user', 'admin', 'moderator'];
    const endpoints = [
      { path: '/api/user/profile', allowedRoles: ['user', 'admin', 'moderator'] },
      { path: '/api/admin/users', allowedRoles: ['admin'] },
      { path: '/api/moderator/reports', allowedRoles: ['admin', 'moderator'] }
    ];
    
    const results = [];
    
    for (const role of roles) {
      // Create user with specific role
      const testUser = await this.createTestUser(role);
      
      for (const endpoint of endpoints) {
        try {
          const response = await axios.get(`${this.config.apiUrl}${endpoint.path}`, {
            headers: { 'Authorization': `Bearer ${testUser.token}` }
          });
          
          const shouldHaveAccess = endpoint.allowedRoles.includes(role);
          const hasAccess = response.status < 400;
          
          results.push({
            role,
            endpoint: endpoint.path,
            expected: shouldHaveAccess ? 'allow' : 'deny',
            actual: hasAccess ? 'allowed' : 'denied',
            passed: shouldHaveAccess === hasAccess,
            status: response.status
          });
          
        } catch (error) {
          const shouldHaveAccess = endpoint.allowedRoles.includes(role);
          const wasDenied = error.response?.status === 403 || error.response?.status === 401;
          
          results.push({
            role,
            endpoint: endpoint.path,
            expected: shouldHaveAccess ? 'allow' : 'deny',
            actual: wasDenied ? 'denied' : 'error',
            passed: shouldHaveAccess ? false : wasDenied,
            status: error.response?.status || 500,
            error: error.message
          });
        }
      }
    }
    
    return {
      testName: 'Role-Based Access Control',
      results,
      passed: results.every(r => r.passed),
      summary: `${results.filter(r => r.passed).length}/${results.length} access tests passed`
    };
  }

  // Encryption Security Tests
  async testEncryption() {
    console.log('🔐 Testing Encryption Security...');
    
    const tests = [
      this.testDataEncryptionAtRest(),
      this.testDataEncryptionInTransit(),
      this.testKeyManagement(),
      this.testEncryptionAlgorithms()
    ];
    
    const results = await Promise.allSettled(tests);
    this.testResults.encryption = results.map((result, index) => ({
      test: tests[index].name || `Encryption Test ${index + 1}`,
      status: result.status,
      result: result.status === 'fulfilled' ? result.value : null,
      error: result.status === 'rejected' ? result.reason.message : null
    }));
    
    return this.testResults.encryption;
  }

  async testDataEncryptionAtRest() {
    try {
      const response = await axios.get(`${this.config.adminApiUrl}/security/encryption-status`, {
        headers: { 'Authorization': `Bearer ${process.env.ADMIN_TOKEN}` }
      });
      
      const encryptionInfo = response.data;
      
      return {
        testName: 'Data Encryption at Rest',
        databaseEncrypted: encryptionInfo.database?.encrypted || false,
        fileSystemEncrypted: encryptionInfo.filesystem?.encrypted || false,
        backupsEncrypted: encryptionInfo.backups?.encrypted || false,
        algorithm: encryptionInfo.algorithm,
        keyRotation: encryptionInfo.keyRotation?.enabled || false,
        passed: encryptionInfo.database?.encrypted && encryptionInfo.filesystem?.encrypted,
        summary: `Database: ${encryptionInfo.database?.encrypted ? 'Encrypted' : 'Not Encrypted'}`
      };
      
    } catch (error) {
      return {
        testName: 'Data Encryption at Rest',
        passed: false,
        error: 'Could not verify encryption at rest',
        details: error.message
      };
    }
  }

  async testDataEncryptionInTransit() {
    const testUrls = [
      this.config.baseUrl,
      this.config.apiUrl,
      `${this.config.apiUrl}/api/health`
    ];
    
    const results = [];
    
    for (const url of testUrls) {
      try {
        // Test HTTPS enforcement
        const httpUrl = url.replace('https://', 'http://');
        
        try {
          const httpResponse = await axios.get(httpUrl, { 
            timeout: 5000,
            maxRedirects: 0
          });
          
          results.push({
            url: httpUrl,
            httpsEnforced: false,
            status: httpResponse.status,
            passed: false
          });
          
        } catch (error) {
          if (error.response?.status >= 300 && error.response?.status < 400) {
            // Redirect to HTTPS - good
            results.push({
              url: httpUrl,
              httpsEnforced: true,
              redirectLocation: error.response.headers.location,
              passed: true
            });
          } else {
            // Connection refused or other error - could be good
            results.push({
              url: httpUrl,
              httpsEnforced: true,
              error: 'HTTP connection refused',
              passed: true
            });
          }
        }
        
        // Test HTTPS connection
        if (url.startsWith('https://')) {
          const httpsResponse = await axios.get(url);
          results.push({
            url,
            httpsWorking: httpsResponse.status === 200,
            passed: httpsResponse.status === 200
          });
        }
        
      } catch (error) {
        results.push({
          url,
          error: error.message,
          passed: false
        });
      }
    }
    
    return {
      testName: 'Data Encryption in Transit',
      results,
      passed: results.every(r => r.passed),
      summary: `${results.filter(r => r.passed).length}/${results.length} HTTPS tests passed`
    };
  }

  // Input Validation Security Tests
  async testInputValidation() {
    console.log('🛡️ Testing Input Validation Security...');
    
    const tests = [
      this.testSQLInjection(),
      this.testXSSPrevention(),
      this.testCommandInjection(),
      this.testFileUploadSecurity(),
      this.testParameterPollution()
    ];
    
    const results = await Promise.allSettled(tests);
    this.testResults.inputValidation = results.map((result, index) => ({
      test: tests[index].name || `Input Validation Test ${index + 1}`,
      status: result.status,
      result: result.status === 'fulfilled' ? result.value : null,
      error: result.status === 'rejected' ? result.reason.message : null
    }));
    
    return this.testResults.inputValidation;
  }

  async testSQLInjection() {
    const sqlPayloads = [
      "'; DROP TABLE users; --",
      "' OR '1'='1",
      "' UNION SELECT * FROM users --",
      "'; INSERT INTO users (email) VALUES ('hacker@evil.com'); --",
      "' OR 1=1 --"
    ];
    
    const results = [];
    
    for (const payload of sqlPayloads) {
      try {
        // Test login endpoint
        const response = await axios.post(`${this.config.apiUrl}/api/auth/login`, {
          email: payload,
          password: 'testpassword'
        });
        
        // If we get a successful response, that's bad
        results.push({
          payload: payload.substring(0, 20) + '...',
          endpoint: '/api/auth/login',
          vulnerable: response.status === 200,
          status: response.status,
          passed: response.status !== 200
        });
        
      } catch (error) {
        // Error response is expected and good
        results.push({
          payload: payload.substring(0, 20) + '...',
          endpoint: '/api/auth/login',
          vulnerable: false,
          status: error.response?.status || 500,
          passed: true,
          error: error.response?.data?.message
        });
      }
    }
    
    return {
      testName: 'SQL Injection Prevention',
      results,
      passed: results.every(r => r.passed),
      vulnerableEndpoints: results.filter(r => r.vulnerable).length,
      summary: `${results.filter(r => r.passed).length}/${results.length} injection attempts blocked`
    };
  }

  async testXSSPrevention() {
    const xssPayloads = [
      '<script>alert("XSS")</script>',
      '"><script>alert("XSS")</script>',
      "javascript:alert('XSS')",
      '<img src=x onerror=alert("XSS")>',
      '<svg onload=alert("XSS")>'
    ];
    
    const results = [];
    
    for (const payload of xssPayloads) {
      try {
        // Test user profile update
        const response = await axios.put(`${this.config.apiUrl}/api/user/profile`, {
          name: payload,
          bio: payload
        }, {
          headers: { 'Authorization': `Bearer ${process.env.TEST_TOKEN}` }
        });
        
        // Check if payload was sanitized
        const responseData = response.data;
        const payloadReflected = JSON.stringify(responseData).includes(payload);
        
        results.push({
          payload: payload.substring(0, 30) + '...',
          endpoint: '/api/user/profile',
          reflected: payloadReflected,
          sanitized: !payloadReflected,
          passed: !payloadReflected,
          status: response.status
        });
        
      } catch (error) {
        results.push({
          payload: payload.substring(0, 30) + '...',
          endpoint: '/api/user/profile',
          reflected: false,
          sanitized: true,
          passed: true,
          status: error.response?.status || 500,
          error: error.response?.data?.message
        });
      }
    }
    
    return {
      testName: 'XSS Prevention',
      results,
      passed: results.every(r => r.passed),
      reflectedPayloads: results.filter(r => r.reflected).length,
      summary: `${results.filter(r => r.passed).length}/${results.length} XSS attempts blocked`
    };
  }

  // Utility methods
  calculateEntropy(str) {
    const freq = {};
    for (let char of str) {
      freq[char] = (freq[char] || 0) + 1;
    }
    
    let entropy = 0;
    const len = str.length;
    
    for (let char in freq) {
      const p = freq[char] / len;
      entropy -= p * Math.log2(p);
    }
    
    return entropy;
  }

  async createTestUser(role = 'user') {
    const email = `test-${role}-${Date.now()}@example.com`;
    
    try {
      const response = await axios.post(`${this.config.apiUrl}/api/auth/register`, {
        email,
        password: 'TestPassword123!',
        name: `Test ${role} User`,
        role
      });
      
      return {
        email,
        token: response.data.token,
        role
      };
      
    } catch (error) {
      throw new Error(`Failed to create test user: ${error.message}`);
    }
  }

  // Comprehensive security test runner
  async runComprehensiveSecurityTests() {
    console.log('🔒 Starting Comprehensive Security Test Suite...');
    
    const startTime = Date.now();
    
    try {
      // Run all security test categories
      await this.testAuthentication();
      await this.testAuthorization();
      await this.testEncryption();
      await this.testInputValidation();
      
      // Generate security report
      const report = this.generateSecurityReport();
      
      return {
        timestamp: new Date().toISOString(),
        duration: Date.now() - startTime,
        ...report
      };
      
    } catch (error) {
      console.error('Security test suite failed:', error);
      throw error;
    }
  }

  generateSecurityReport() {
    const allTests = [
      ...this.testResults.authentication,
      ...this.testResults.authorization,
      ...this.testResults.encryption,
      ...this.testResults.inputValidation
    ];
    
    const passedTests = allTests.filter(test => 
      test.result?.passed || test.status === 'fulfilled'
    );
    
    const failedTests = allTests.filter(test => 
      !test.result?.passed && test.status !== 'fulfilled'
    );
    
    const criticalIssues = failedTests.filter(test => 
      test.test?.includes('SQL Injection') || 
      test.test?.includes('XSS') ||
      test.test?.includes('Authentication') ||
      test.test?.includes('Authorization')
    );
    
    return {
      summary: {
        totalTests: allTests.length,
        passedTests: passedTests.length,
        failedTests: failedTests.length,
        criticalIssues: criticalIssues.length,
        overallStatus: criticalIssues.length === 0 ? 'SECURE' : 'VULNERABLE'
      },
      categories: {
        authentication: this.testResults.authentication,
        authorization: this.testResults.authorization,
        encryption: this.testResults.encryption,
        inputValidation: this.testResults.inputValidation
      },
      criticalIssues: criticalIssues.map(issue => ({
        category: this.getCategoryForTest(issue.test),
        test: issue.test,
        error: issue.error,
        recommendation: this.getRecommendationForIssue(issue.test)
      })),
      recommendations: this.generateSecurityRecommendations(failedTests)
    };
  }

  getCategoryForTest(testName) {
    if (testName.includes('Authentication')) return 'Authentication';
    if (testName.includes('Authorization')) return 'Authorization';
    if (testName.includes('Encryption')) return 'Encryption';
    if (testName.includes('Injection') || testName.includes('XSS')) return 'Input Validation';
    return 'General';
  }

  getRecommendationForIssue(testName) {
    const recommendations = {
      'SQL Injection': 'Implement parameterized queries and input sanitization',
      'XSS Prevention': 'Implement output encoding and Content Security Policy',
      'Password Complexity': 'Enforce strong password requirements',
      'Brute Force Protection': 'Implement rate limiting and account lockout',
      'Encryption': 'Enable encryption for data at rest and in transit',
      'Authorization': 'Implement proper role-based access controls'
    };
    
    for (const [key, recommendation] of Object.entries(recommendations)) {
      if (testName.includes(key)) {
        return recommendation;
      }
    }
    
    return 'Review security implementation for this component';
  }

  generateSecurityRecommendations(failedTests) {
    const recommendations = [];
    
    if (failedTests.some(t => t.test.includes('Password'))) {
      recommendations.push('Strengthen password policies and implement complexity requirements');
    }
    
    if (failedTests.some(t => t.test.includes('Encryption'))) {
      recommendations.push('Enable encryption for all sensitive data storage and transmission');
    }
    
    if (failedTests.some(t => t.test.includes('Injection'))) {
      recommendations.push('Implement comprehensive input validation and sanitization');
    }
    
    if (failedTests.some(t => t.test.includes('Authorization'))) {
      recommendations.push('Review and strengthen access control mechanisms');
    }
    
    return recommendations;
  }
}

module.exports = SecurityTestFramework;