/**
 * Compliance Test Framework
 * Privacy compliance testing for regulatory adherence and user data protection
 */

const axios = require('axios');
const fs = require('fs').promises;
const path = require('path');

class ComplianceTestFramework {
  constructor(config = {}) {
    this.config = {
      baseUrl: process.env.TEST_BASE_URL || 'http://localhost:3000',
      apiUrl: process.env.TEST_API_URL || 'http://localhost:8000',
      adminApiUrl: process.env.ADMIN_API_URL || 'http://localhost:8000/admin',
      
      // Compliance standards to test
      standards: {
        gdpr: true,
        ccpa: true,
        hipaa: false,
        sox404: true,
        pci: false,
        iso27001: true
      },
      
      // Data retention policies
      dataRetentionPeriods: {
        userProfiles: 2555, // 7 years in days
        meetingData: 1095,  // 3 years in days
        analyticsData: 365, // 1 year in days
        auditLogs: 2555     // 7 years in days
      },
      
      ...config
    };
    
    this.complianceResults = {
      gdpr: [],
      ccpa: [],
      dataRetention: [],
      auditTrail: [],
      privacyControls: [],
      dataMinimization: [],
      consentManagement: []
    };
    
    this.complianceChecklist = new Map();
    this.initializeComplianceChecklist();
  }

  initializeComplianceChecklist() {
    // GDPR Compliance Checklist
    this.complianceChecklist.set('gdpr', [
      { id: 'gdpr-1', requirement: 'Right to Access', description: 'Users can access their personal data' },
      { id: 'gdpr-2', requirement: 'Right to Rectification', description: 'Users can correct their personal data' },
      { id: 'gdpr-3', requirement: 'Right to Erasure', description: 'Users can delete their personal data' },
      { id: 'gdpr-4', requirement: 'Right to Portability', description: 'Users can export their personal data' },
      { id: 'gdpr-5', requirement: 'Right to Restrict Processing', description: 'Users can limit data processing' },
      { id: 'gdpr-6', requirement: 'Consent Management', description: 'Clear consent mechanisms for data processing' },
      { id: 'gdpr-7', requirement: 'Data Protection by Design', description: 'Privacy built into system design' },
      { id: 'gdpr-8', requirement: 'Data Breach Notification', description: 'Breach notification within 72 hours' },
      { id: 'gdpr-9', requirement: 'Privacy Policy', description: 'Clear and accessible privacy policy' },
      { id: 'gdpr-10', requirement: 'Data Processing Records', description: 'Records of processing activities' }
    ]);
    
    // CCPA Compliance Checklist
    this.complianceChecklist.set('ccpa', [
      { id: 'ccpa-1', requirement: 'Right to Know', description: 'Consumers can know what data is collected' },
      { id: 'ccpa-2', requirement: 'Right to Delete', description: 'Consumers can delete their personal information' },
      { id: 'ccpa-3', requirement: 'Right to Opt-Out', description: 'Consumers can opt-out of data sale' },
      { id: 'ccpa-4', requirement: 'Non-Discrimination', description: 'No discrimination for exercising rights' },
      { id: 'ccpa-5', requirement: 'Privacy Notice', description: 'Clear notice of data collection practices' },
      { id: 'ccpa-6', requirement: 'Verifiable Consumer Requests', description: 'Process for verifying consumer identity' }
    ]);
    
    // SOX 404 Compliance Checklist
    this.complianceChecklist.set('sox404', [
      { id: 'sox-1', requirement: 'Internal Controls', description: 'Adequate internal controls over financial reporting' },
      { id: 'sox-2', requirement: 'Management Assessment', description: 'Management assessment of internal controls' },
      { id: 'sox-3', requirement: 'Auditor Attestation', description: 'External auditor attestation of controls' },
      { id: 'sox-4', requirement: 'Documentation', description: 'Comprehensive documentation of controls' },
      { id: 'sox-5', requirement: 'Testing', description: 'Regular testing of control effectiveness' }
    ]);
  }

  // GDPR Compliance Tests
  async testGDPRCompliance() {
    console.log('🇪🇺 Testing GDPR Compliance...');
    
    if (!this.config.standards.gdpr) {
      return { skipped: true, reason: 'GDPR testing disabled' };
    }
    
    const tests = [
      this.testRightToAccess(),
      this.testRightToRectification(),
      this.testRightToErasure(),
      this.testRightToPortability(),
      this.testConsentManagement(),
      this.testDataProtectionByDesign(),
      this.testPrivacyPolicy(),
      this.testDataProcessingRecords()
    ];
    
    const results = await Promise.allSettled(tests);
    this.complianceResults.gdpr = results.map((result, index) => ({
      test: tests[index].name || `GDPR Test ${index + 1}`,
      status: result.status,
      result: result.status === 'fulfilled' ? result.value : null,
      error: result.status === 'rejected' ? result.reason.message : null
    }));
    
    return this.complianceResults.gdpr;
  }

  async testRightToAccess() {
    const testUser = await this.createTestUser();
    
    try {
      // Test data access endpoint
      const response = await axios.get(`${this.config.apiUrl}/api/privacy/data-export`, {
        headers: { 'Authorization': `Bearer ${testUser.token}` }
      });
      
      const userData = response.data;
      const hasPersonalData = userData.profile || userData.meetings || userData.preferences;
      const isStructured = typeof userData === 'object' && userData !== null;
      
      return {
        testName: 'Right to Access (GDPR Article 15)',
        endpointExists: response.status === 200,
        dataProvided: hasPersonalData,
        structuredFormat: isStructured,
        dataCategories: Object.keys(userData),
        passed: response.status === 200 && hasPersonalData && isStructured,
        summary: `User can ${response.status === 200 ? 'access' : 'not access'} their personal data`
      };
      
    } catch (error) {
      return {
        testName: 'Right to Access (GDPR Article 15)',
        passed: false,
        error: error.response?.data?.message || error.message,
        status: error.response?.status,
        summary: 'Data access endpoint not available or not working'
      };
    }
  }

  async testRightToRectification() {
    const testUser = await this.createTestUser();
    
    try {
      // Test data update endpoint
      const updateData = {
        name: 'Updated Test User',
        email: `updated-${Date.now()}@example.com`,
        preferences: { theme: 'dark' }
      };
      
      const response = await axios.put(`${this.config.apiUrl}/api/user/profile`, updateData, {
        headers: { 'Authorization': `Bearer ${testUser.token}` }
      });
      
      // Verify the update was applied
      const verifyResponse = await axios.get(`${this.config.apiUrl}/api/user/profile`, {
        headers: { 'Authorization': `Bearer ${testUser.token}` }
      });
      
      const updatedCorrectly = verifyResponse.data.name === updateData.name;
      
      return {
        testName: 'Right to Rectification (GDPR Article 16)',
        updateEndpointExists: response.status === 200,
        dataUpdated: updatedCorrectly,
        passed: response.status === 200 && updatedCorrectly,
        summary: `User can ${updatedCorrectly ? 'update' : 'not update'} their personal data`
      };
      
    } catch (error) {
      return {
        testName: 'Right to Rectification (GDPR Article 16)',
        passed: false,
        error: error.response?.data?.message || error.message,
        summary: 'Data rectification not available'
      };
    }
  }

  async testRightToErasure() {
    const testUser = await this.createTestUser();
    
    try {
      // Test account deletion endpoint
      const response = await axios.delete(`${this.config.apiUrl}/api/user/account`, {
        headers: { 'Authorization': `Bearer ${testUser.token}` }
      });
      
      // Verify the account was deleted
      try {
        await axios.get(`${this.config.apiUrl}/api/user/profile`, {
          headers: { 'Authorization': `Bearer ${testUser.token}` }
        });
        
        // If we get here, deletion didn't work
        return {
          testName: 'Right to Erasure (GDPR Article 17)',
          deletionEndpointExists: response.status === 200,
          accountDeleted: false,
          passed: false,
          summary: 'Account deletion endpoint exists but data not actually deleted'
        };
        
      } catch (verifyError) {
        // Error accessing profile after deletion is expected
        const accountDeleted = verifyError.response?.status === 401 || verifyError.response?.status === 404;
        
        return {
          testName: 'Right to Erasure (GDPR Article 17)',
          deletionEndpointExists: response.status === 200,
          accountDeleted,
          passed: response.status === 200 && accountDeleted,
          summary: `Account ${accountDeleted ? 'successfully deleted' : 'deletion failed'}`
        };
      }
      
    } catch (error) {
      return {
        testName: 'Right to Erasure (GDPR Article 17)',
        passed: false,
        error: error.response?.data?.message || error.message,
        summary: 'Account deletion not available'
      };
    }
  }

  async testRightToPortability() {
    const testUser = await this.createTestUser();
    
    try {
      // Test data export endpoint
      const response = await axios.get(`${this.config.apiUrl}/api/privacy/data-export?format=json`, {
        headers: { 'Authorization': `Bearer ${testUser.token}` }
      });
      
      const exportData = response.data;
      const isPortableFormat = response.headers['content-type']?.includes('application/json') ||
                              response.headers['content-type']?.includes('text/csv');
      
      // Test different export formats
      const formats = ['json', 'csv', 'xml'];
      const supportedFormats = [];
      
      for (const format of formats) {
        try {
          const formatResponse = await axios.get(`${this.config.apiUrl}/api/privacy/data-export?format=${format}`, {
            headers: { 'Authorization': `Bearer ${testUser.token}` }
          });
          
          if (formatResponse.status === 200) {
            supportedFormats.push(format);
          }
        } catch (e) {
          // Format not supported
        }
      }
      
      return {
        testName: 'Right to Data Portability (GDPR Article 20)',
        exportEndpointExists: response.status === 200,
        portableFormat: isPortableFormat,
        supportedFormats,
        machineReadable: supportedFormats.includes('json') || supportedFormats.includes('xml'),
        passed: response.status === 200 && isPortableFormat && supportedFormats.length > 0,
        summary: `Data export available in ${supportedFormats.length} format(s): ${supportedFormats.join(', ')}`
      };
      
    } catch (error) {
      return {
        testName: 'Right to Data Portability (GDPR Article 20)',
        passed: false,
        error: error.response?.data?.message || error.message,
        summary: 'Data portability not available'
      };
    }
  }

  async testConsentManagement() {
    try {
      // Test consent management endpoints
      const consentResponse = await axios.get(`${this.config.apiUrl}/api/privacy/consent-status`);
      const consentData = consentResponse.data;
      
      // Test consent update
      const updateResponse = await axios.post(`${this.config.apiUrl}/api/privacy/consent`, {
        analytics: false,
        marketing: false,
        functional: true
      });
      
      const hasConsentCategories = consentData.categories && Array.isArray(consentData.categories);
      const canUpdateConsent = updateResponse.status === 200;
      
      return {
        testName: 'Consent Management (GDPR Article 7)',
        consentEndpointExists: consentResponse.status === 200,
        categorizedConsent: hasConsentCategories,
        consentCategories: consentData.categories || [],
        canUpdateConsent,
        granularControl: hasConsentCategories && consentData.categories.length > 1,
        passed: consentResponse.status === 200 && hasConsentCategories && canUpdateConsent,
        summary: `Consent management ${hasConsentCategories ? 'available' : 'not available'} with ${consentData.categories?.length || 0} categories`
      };
      
    } catch (error) {
      return {
        testName: 'Consent Management (GDPR Article 7)',
        passed: false,
        error: error.response?.data?.message || error.message,
        summary: 'Consent management not implemented'
      };
    }
  }

  // CCPA Compliance Tests
  async testCCPACompliance() {
    console.log('🇺🇸 Testing CCPA Compliance...');
    
    if (!this.config.standards.ccpa) {
      return { skipped: true, reason: 'CCPA testing disabled' };
    }
    
    const tests = [
      this.testRightToKnow(),
      this.testRightToDelete(),
      this.testRightToOptOut(),
      this.testNonDiscrimination(),
      this.testPrivacyNotice()
    ];
    
    const results = await Promise.allSettled(tests);
    this.complianceResults.ccpa = results.map((result, index) => ({
      test: tests[index].name || `CCPA Test ${index + 1}`,
      status: result.status,
      result: result.status === 'fulfilled' ? result.value : null,
      error: result.status === 'rejected' ? result.reason.message : null
    }));
    
    return this.complianceResults.ccpa;
  }

  async testRightToKnow() {
    try {
      // Test data categories disclosure
      const response = await axios.get(`${this.config.apiUrl}/api/privacy/data-categories`);
      const dataCategories = response.data;
      
      const requiredCategories = [
        'personal_identifiers',
        'commercial_information',
        'internet_activity',
        'professional_information'
      ];
      
      const hasRequiredCategories = requiredCategories.every(category => 
        dataCategories.categories?.some(cat => cat.id === category)
      );
      
      return {
        testName: 'Right to Know (CCPA)',
        endpointExists: response.status === 200,
        categoriesProvided: !!dataCategories.categories,
        requiredCategoriesPresent: hasRequiredCategories,
        categories: dataCategories.categories || [],
        passed: response.status === 200 && hasRequiredCategories,
        summary: `Data categories ${hasRequiredCategories ? 'properly disclosed' : 'not properly disclosed'}`
      };
      
    } catch (error) {
      return {
        testName: 'Right to Know (CCPA)',
        passed: false,
        error: error.response?.data?.message || error.message,
        summary: 'Data categories disclosure not available'
      };
    }
  }

  async testRightToOptOut() {
    try {
      // Test opt-out mechanism
      const response = await axios.post(`${this.config.apiUrl}/api/privacy/opt-out`, {
        dataSale: true,
        marketing: true,
        analytics: false
      });
      
      // Verify opt-out status
      const statusResponse = await axios.get(`${this.config.apiUrl}/api/privacy/opt-out-status`);
      const optOutStatus = statusResponse.data;
      
      return {
        testName: 'Right to Opt-Out (CCPA)',
        optOutEndpointExists: response.status === 200,
        statusEndpointExists: statusResponse.status === 200,
        granularOptOut: optOutStatus.categories && Object.keys(optOutStatus.categories).length > 1,
        passed: response.status === 200 && statusResponse.status === 200,
        summary: `Opt-out mechanism ${response.status === 200 ? 'available' : 'not available'}`
      };
      
    } catch (error) {
      return {
        testName: 'Right to Opt-Out (CCPA)',
        passed: false,
        error: error.response?.data?.message || error.message,
        summary: 'Opt-out mechanism not implemented'
      };
    }
  }

  // Data Retention Compliance Tests
  async testDataRetentionCompliance() {
    console.log('📅 Testing Data Retention Compliance...');
    
    try {
      const response = await axios.get(`${this.config.adminApiUrl}/compliance/data-retention-policy`, {
        headers: { 'Authorization': `Bearer ${process.env.ADMIN_TOKEN}` }
      });
      
      const retentionPolicy = response.data;
      const results = [];
      
      for (const [dataType, expectedDays] of Object.entries(this.config.dataRetentionPeriods)) {
        const policyDays = retentionPolicy[dataType]?.retentionDays;
        const hasPolicy = policyDays !== undefined;
        const meetsRequirement = policyDays <= expectedDays;
        
        results.push({
          dataType,
          expectedDays,
          actualDays: policyDays,
          hasPolicy,
          meetsRequirement,
          passed: hasPolicy && meetsRequirement
        });
      }
      
      this.complianceResults.dataRetention = results;
      
      return {
        testName: 'Data Retention Compliance',
        results,
        passed: results.every(r => r.passed),
        summary: `${results.filter(r => r.passed).length}/${results.length} data types have compliant retention policies`
      };
      
    } catch (error) {
      return {
        testName: 'Data Retention Compliance',
        passed: false,
        error: error.response?.data?.message || error.message,
        summary: 'Data retention policies not accessible'
      };
    }
  }

  // Audit Trail Compliance Tests
  async testAuditTrailCompliance() {
    console.log('📋 Testing Audit Trail Compliance...');
    
    try {
      const response = await axios.get(`${this.config.adminApiUrl}/compliance/audit-logs`, {
        headers: { 'Authorization': `Bearer ${process.env.ADMIN_TOKEN}` },
        params: { limit: 100 }
      });
      
      const auditLogs = response.data.logs || [];
      
      // Check audit log completeness
      const requiredFields = ['timestamp', 'userId', 'action', 'resource', 'ipAddress'];
      const completeEntries = auditLogs.filter(log => 
        requiredFields.every(field => log[field] !== undefined)
      );
      
      // Check for different types of audited actions
      const actionTypes = [...new Set(auditLogs.map(log => log.action))];
      const expectedActions = ['login', 'logout', 'data_access', 'data_update', 'data_delete'];
      const auditedActions = expectedActions.filter(action => actionTypes.includes(action));
      
      return {
        testName: 'Audit Trail Compliance',
        auditLogsExist: auditLogs.length > 0,
        totalEntries: auditLogs.length,
        completeEntries: completeEntries.length,
        completenessRate: auditLogs.length > 0 ? completeEntries.length / auditLogs.length : 0,
        actionTypes,
        auditedActions,
        actionCoverage: auditedActions.length / expectedActions.length,
        passed: completeEntries.length > 0 && auditedActions.length >= 3,
        summary: `${completeEntries.length} complete audit entries, ${auditedActions.length}/${expectedActions.length} action types covered`
      };
      
    } catch (error) {
      return {
        testName: 'Audit Trail Compliance',
        passed: false,
        error: error.response?.data?.message || error.message,
        summary: 'Audit trail not accessible or not implemented'
      };
    }
  }

  // Privacy Controls Tests
  async testPrivacyControls() {
    console.log('🔒 Testing Privacy Controls...');
    
    const tests = [
      this.testDataMinimization(),
      this.testPurposeLimitation(),
      this.testStorageLimitation(),
      this.testAccuracyControls()
    ];
    
    const results = await Promise.allSettled(tests);
    this.complianceResults.privacyControls = results.map((result, index) => ({
      test: tests[index].name || `Privacy Control Test ${index + 1}`,
      status: result.status,
      result: result.status === 'fulfilled' ? result.value : null,
      error: result.status === 'rejected' ? result.reason.message : null
    }));
    
    return this.complianceResults.privacyControls;
  }

  async testDataMinimization() {
    try {
      // Test registration form to check for excessive data collection
      const response = await axios.get(`${this.config.apiUrl}/api/auth/registration-fields`);
      const fields = response.data.fields || [];
      
      // Essential fields for user registration
      const essentialFields = ['email', 'password', 'name'];
      const optionalFields = fields.filter(field => !essentialFields.includes(field.name));
      const excessiveFields = optionalFields.filter(field => !field.optional);
      
      return {
        testName: 'Data Minimization',
        totalFields: fields.length,
        essentialFields: essentialFields.length,
        optionalFields: optionalFields.length,
        excessiveFields: excessiveFields.length,
        minimizationCompliant: excessiveFields.length === 0,
        passed: excessiveFields.length === 0,
        summary: `${excessiveFields.length} excessive mandatory fields found`
      };
      
    } catch (error) {
      return {
        testName: 'Data Minimization',
        passed: false,
        error: error.response?.data?.message || error.message,
        summary: 'Could not assess data minimization practices'
      };
    }
  }

  // Utility methods
  async createTestUser() {
    const email = `compliance-test-${Date.now()}@example.com`;
    
    try {
      const response = await axios.post(`${this.config.apiUrl}/api/auth/register`, {
        email,
        password: 'TestPassword123!',
        name: 'Compliance Test User'
      });
      
      return {
        email,
        token: response.data.token,
        id: response.data.user?.id
      };
      
    } catch (error) {
      throw new Error(`Failed to create test user: ${error.message}`);
    }
  }

  // Comprehensive compliance test runner
  async runComprehensiveComplianceTests() {
    console.log('📋 Starting Comprehensive Compliance Test Suite...');
    
    const startTime = Date.now();
    
    try {
      const results = {};
      
      // Run compliance tests based on configuration
      if (this.config.standards.gdpr) {
        results.gdpr = await this.testGDPRCompliance();
      }
      
      if (this.config.standards.ccpa) {
        results.ccpa = await this.testCCPACompliance();
      }
      
      results.dataRetention = await this.testDataRetentionCompliance();
      results.auditTrail = await this.testAuditTrailCompliance();
      results.privacyControls = await this.testPrivacyControls();
      
      // Generate compliance report
      const report = this.generateComplianceReport(results);
      
      return {
        timestamp: new Date().toISOString(),
        duration: Date.now() - startTime,
        standards: this.config.standards,
        ...report
      };
      
    } catch (error) {
      console.error('Compliance test suite failed:', error);
      throw error;
    }
  }

  generateComplianceReport(results) {
    const allTests = [];
    const complianceScores = {};
    
    // Collect all test results
    for (const [standard, tests] of Object.entries(results)) {
      if (Array.isArray(tests)) {
        allTests.push(...tests);
        
        const passedTests = tests.filter(test => 
          test.result?.passed || test.status === 'fulfilled'
        ).length;
        
        complianceScores[standard] = {
          total: tests.length,
          passed: passedTests,
          score: tests.length > 0 ? (passedTests / tests.length) * 100 : 0
        };
      }
    }
    
    const overallScore = Object.values(complianceScores).reduce((sum, score) => sum + score.score, 0) / Object.keys(complianceScores).length;
    
    return {
      summary: {
        overallScore: Math.round(overallScore),
        totalTests: allTests.length,
        passedTests: allTests.filter(test => test.result?.passed).length,
        complianceStatus: overallScore >= 80 ? 'COMPLIANT' : overallScore >= 60 ? 'PARTIALLY_COMPLIANT' : 'NON_COMPLIANT'
      },
      standardsScores: complianceScores,
      detailedResults: results,
      recommendations: this.generateComplianceRecommendations(results)
    };
  }

  generateComplianceRecommendations(results) {
    const recommendations = [];
    
    // Analyze failed tests and generate recommendations
    for (const [standard, tests] of Object.entries(results)) {
      if (Array.isArray(tests)) {
        const failedTests = tests.filter(test => !test.result?.passed);
        
        if (failedTests.length > 0) {
          recommendations.push({
            standard: standard.toUpperCase(),
            priority: 'HIGH',
            issue: `${failedTests.length} compliance tests failed`,
            recommendation: `Review and implement missing ${standard.toUpperCase()} requirements`,
            failedTests: failedTests.map(test => test.test)
          });
        }
      }
    }
    
    return recommendations;
  }
}

module.exports = ComplianceTestFramework;