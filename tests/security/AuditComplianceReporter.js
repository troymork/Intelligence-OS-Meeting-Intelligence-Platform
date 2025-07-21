/**
 * Audit and Compliance Reporting System
 * Generates comprehensive documentation and evidence collection
 */

const fs = require('fs').promises;
const path = require('path');
const crypto = require('crypto');

class AuditComplianceReporter {
    constructor() {
        this.reportData = {
            metadata: {
                generatedAt: new Date().toISOString(),
                version: '1.0.0',
                reportId: crypto.randomUUID()
            },
            securityTests: [],
            complianceTests: [],
            vulnerabilityAssessments: [],
            recommendations: [],
            evidence: []
        };
    }

    // Add security test results
    addSecurityTestResults(testResults) {
        this.reportData.securityTests.push({
            timestamp: new Date().toISOString(),
            results: testResults,
            summary: this.generateSecuritySummary(testResults)
        });
    }

    // Add compliance test results
    addComplianceTestResults(complianceResults) {
        this.reportData.complianceTests.push({
            timestamp: new Date().toISOString(),
            results: complianceResults,
            summary: this.generateComplianceSummary(complianceResults)
        });
    }

    // Add vulnerability assessment results
    addVulnerabilityResults(vulnResults) {
        this.reportData.vulnerabilityAssessments.push({
            timestamp: new Date().toISOString(),
            results: vulnResults,
            summary: this.generateVulnerabilitySummary(vulnResults)
        });
    }

    // Generate security test summary
    generateSecuritySummary(testResults) {
        const total = testResults.length;
        const passed = testResults.filter(t => t.status === 'PASS').length;
        const failed = total - passed;
        
        return {
            totalTests: total,
            passed: passed,
            failed: failed,
            successRate: total > 0 ? (passed / total) * 100 : 0,
            criticalIssues: testResults.filter(t => t.severity === 'CRITICAL' && t.status === 'FAIL').length,
            highIssues: testResults.filter(t => t.severity === 'HIGH' && t.status === 'FAIL').length
        };
    }

    // Generate compliance summary
    generateComplianceSummary(complianceResults) {
        return {
            gdprCompliance: this.calculateComplianceScore(complianceResults.gdpr || []),
            ccpaCompliance: this.calculateComplianceScore(complianceResults.ccpa || []),
            overallCompliance: complianceResults.summary?.compliancePercentage || 0,
            criticalGaps: complianceResults.results?.filter(r => r.status === 'FAIL' && r.severity === 'CRITICAL').length || 0
        };
    }

    // Generate vulnerability summary
    generateVulnerabilitySummary(vulnResults) {
        const vulnerabilities = vulnResults.vulnerabilities || [];
        
        return {
            totalVulnerabilities: vulnerabilities.length,
            critical: vulnerabilities.filter(v => v.severity === 'CRITICAL').length,
            high: vulnerabilities.filter(v => v.severity === 'HIGH').length,
            medium: vulnerabilities.filter(v => v.severity === 'MEDIUM').length,
            low: vulnerabilities.filter(v => v.severity === 'LOW').length,
            riskScore: vulnResults.riskScore || 0
        };
    }

    // Calculate compliance score
    calculateComplianceScore(tests) {
        if (!tests || tests.length === 0) return 0;
        const passed = tests.filter(t => t.status === 'PASS').length;
        return (passed / tests.length) * 100;
    }

    // Add evidence file
    async addEvidence(evidenceType, filePath, description) {
        try {
            const fileContent = await fs.readFile(filePath, 'utf8');
            const hash = crypto.createHash('sha256').update(fileContent).digest('hex');
            
            this.reportData.evidence.push({
                type: evidenceType,
                description: description,
                filePath: filePath,
                hash: hash,
                timestamp: new Date().toISOString(),
                size: fileContent.length
            });
        } catch (error) {
            console.warn(`Failed to add evidence from ${filePath}:`, error.message);
        }
    }

    // Add recommendation
    addRecommendation(category, priority, title, description, remediation) {
        this.reportData.recommendations.push({
            id: crypto.randomUUID(),
            category: category,
            priority: priority,
            title: title,
            description: description,
            remediation: remediation,
            timestamp: new Date().toISOString()
        });
    }

    // Generate executive summary
    generateExecutiveSummary() {
        const securitySummary = this.reportData.securityTests.length > 0 
            ? this.reportData.securityTests[this.reportData.securityTests.length - 1].summary
            : { totalTests: 0, passed: 0, failed: 0, successRate: 0 };

        const complianceSummary = this.reportData.complianceTests.length > 0
            ? this.reportData.complianceTests[this.reportData.complianceTests.length - 1].summary
            : { overallCompliance: 0, criticalGaps: 0 };

        const vulnSummary = this.reportData.vulnerabilityAssessments.length > 0
            ? this.reportData.vulnerabilityAssessments[this.reportData.vulnerabilityAssessments.length - 1].summary
            : { totalVulnerabilities: 0, critical: 0, high: 0, riskScore: 0 };

        return {
            overallSecurityPosture: this.calculateOverallSecurityPosture(securitySummary, complianceSummary, vulnSummary),
            keyFindings: this.generateKeyFindings(securitySummary, complianceSummary, vulnSummary),
            criticalActions: this.generateCriticalActions(),
            complianceStatus: this.generateComplianceStatus(complianceSummary),
            riskAssessment: this.generateRiskAssessment(vulnSummary)
        };
    }

    // Calculate overall security posture
    calculateOverallSecurityPosture(security, compliance, vulnerability) {
        const securityScore = security.successRate || 0;
        const complianceScore = compliance.overallCompliance || 0;
        const vulnerabilityScore = Math.max(0, 100 - (vulnerability.riskScore || 0));
        
        const overallScore = (securityScore + complianceScore + vulnerabilityScore) / 3;
        
        if (overallScore >= 90) return { level: 'EXCELLENT', score: overallScore };
        if (overallScore >= 80) return { level: 'GOOD', score: overallScore };
        if (overallScore >= 70) return { level: 'ACCEPTABLE', score: overallScore };
        if (overallScore >= 60) return { level: 'NEEDS_IMPROVEMENT', score: overallScore };
        return { level: 'CRITICAL', score: overallScore };
    }

    // Generate key findings
    generateKeyFindings(security, compliance, vulnerability) {
        const findings = [];
        
        if (security.failed > 0) {
            findings.push(`${security.failed} security tests failed out of ${security.totalTests} total tests`);
        }
        
        if (compliance.criticalGaps > 0) {
            findings.push(`${compliance.criticalGaps} critical compliance gaps identified`);
        }
        
        if (vulnerability.critical > 0) {
            findings.push(`${vulnerability.critical} critical vulnerabilities discovered`);
        }
        
        if (vulnerability.high > 0) {
            findings.push(`${vulnerability.high} high-severity vulnerabilities found`);
        }

        return findings;
    }

    // Generate critical actions
    generateCriticalActions() {
        return this.reportData.recommendations
            .filter(r => r.priority === 'CRITICAL')
            .map(r => ({
                title: r.title,
                description: r.description,
                remediation: r.remediation
            }));
    }

    // Generate compliance status
    generateComplianceStatus(compliance) {
        return {
            gdpr: {
                status: compliance.gdprCompliance >= 95 ? 'COMPLIANT' : 'NON_COMPLIANT',
                score: compliance.gdprCompliance
            },
            ccpa: {
                status: compliance.ccpaCompliance >= 95 ? 'COMPLIANT' : 'NON_COMPLIANT',
                score: compliance.ccpaCompliance
            },
            overall: {
                status: compliance.overallCompliance >= 95 ? 'COMPLIANT' : 'NON_COMPLIANT',
                score: compliance.overallCompliance
            }
        };
    }

    // Generate risk assessment
    generateRiskAssessment(vulnerability) {
        let riskLevel = 'LOW';
        
        if (vulnerability.critical > 0) {
            riskLevel = 'CRITICAL';
        } else if (vulnerability.high > 5) {
            riskLevel = 'HIGH';
        } else if (vulnerability.high > 0 || vulnerability.medium > 10) {
            riskLevel = 'MEDIUM';
        }

        return {
            level: riskLevel,
            score: vulnerability.riskScore,
            factors: [
                `${vulnerability.critical} critical vulnerabilities`,
                `${vulnerability.high} high-severity vulnerabilities`,
                `${vulnerability.medium} medium-severity vulnerabilities`
            ]
        };
    }

    // Generate detailed HTML report
    async generateHTMLReport(outputPath) {
        const executiveSummary = this.generateExecutiveSummary();
        
        const htmlContent = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Security and Compliance Audit Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 40px; border-bottom: 2px solid #007bff; padding-bottom: 20px; }
        .summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 40px; }
        .summary-card { background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #007bff; }
        .status-excellent { border-left-color: #28a745; }
        .status-good { border-left-color: #17a2b8; }
        .status-warning { border-left-color: #ffc107; }
        .status-critical { border-left-color: #dc3545; }
        .section { margin-bottom: 40px; }
        .section h2 { color: #333; border-bottom: 1px solid #ddd; padding-bottom: 10px; }
        .test-result { margin: 10px 0; padding: 10px; border-radius: 4px; }
        .test-pass { background-color: #d4edda; border-left: 4px solid #28a745; }
        .test-fail { background-color: #f8d7da; border-left: 4px solid #dc3545; }
        .recommendation { background: #fff3cd; padding: 15px; margin: 10px 0; border-radius: 4px; border-left: 4px solid #ffc107; }
        .evidence-item { background: #e9ecef; padding: 10px; margin: 5px 0; border-radius: 4px; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f8f9fa; font-weight: bold; }
        .metric { font-size: 2em; font-weight: bold; color: #007bff; }
        .timestamp { color: #6c757d; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Security and Compliance Audit Report</h1>
            <p class="timestamp">Generated: ${this.reportData.metadata.generatedAt}</p>
            <p>Report ID: ${this.reportData.metadata.reportId}</p>
        </div>

        <div class="section">
            <h2>Executive Summary</h2>
            <div class="summary-grid">
                <div class="summary-card status-${executiveSummary.overallSecurityPosture.level.toLowerCase()}">
                    <h3>Overall Security Posture</h3>
                    <div class="metric">${Math.round(executiveSummary.overallSecurityPosture.score)}%</div>
                    <p>${executiveSummary.overallSecurityPosture.level.replace('_', ' ')}</p>
                </div>
                <div class="summary-card">
                    <h3>Compliance Status</h3>
                    <div class="metric">${Math.round(executiveSummary.complianceStatus.overall.score)}%</div>
                    <p>${executiveSummary.complianceStatus.overall.status}</p>
                </div>
                <div class="summary-card status-${executiveSummary.riskAssessment.level.toLowerCase()}">
                    <h3>Risk Level</h3>
                    <div class="metric">${executiveSummary.riskAssessment.level}</div>
                    <p>Score: ${executiveSummary.riskAssessment.score}</p>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>Key Findings</h2>
            <ul>
                ${executiveSummary.keyFindings.map(finding => `<li>${finding}</li>`).join('')}
            </ul>
        </div>

        <div class="section">
            <h2>Critical Actions Required</h2>
            ${executiveSummary.criticalActions.map(action => `
                <div class="recommendation">
                    <h4>${action.title}</h4>
                    <p><strong>Description:</strong> ${action.description}</p>
                    <p><strong>Remediation:</strong> ${action.remediation}</p>
                </div>
            `).join('')}
        </div>

        <div class="section">
            <h2>Security Test Results</h2>
            ${this.reportData.securityTests.map(test => `
                <h3>Test Run - ${test.timestamp}</h3>
                <p><strong>Summary:</strong> ${test.summary.passed}/${test.summary.totalTests} tests passed (${Math.round(test.summary.successRate)}%)</p>
                ${test.results.map(result => `
                    <div class="test-result test-${result.status.toLowerCase()}">
                        <strong>${result.test}</strong> - ${result.status}
                        <br><small>${result.message}</small>
                    </div>
                `).join('')}
            `).join('')}
        </div>

        <div class="section">
            <h2>Compliance Assessment</h2>
            <table>
                <tr>
                    <th>Regulation</th>
                    <th>Compliance Score</th>
                    <th>Status</th>
                </tr>
                <tr>
                    <td>GDPR</td>
                    <td>${Math.round(executiveSummary.complianceStatus.gdpr.score)}%</td>
                    <td>${executiveSummary.complianceStatus.gdpr.status}</td>
                </tr>
                <tr>
                    <td>CCPA</td>
                    <td>${Math.round(executiveSummary.complianceStatus.ccpa.score)}%</td>
                    <td>${executiveSummary.complianceStatus.ccpa.status}</td>
                </tr>
            </table>
        </div>

        <div class="section">
            <h2>Recommendations</h2>
            ${this.reportData.recommendations.map(rec => `
                <div class="recommendation">
                    <h4>${rec.title} (${rec.priority})</h4>
                    <p><strong>Category:</strong> ${rec.category}</p>
                    <p><strong>Description:</strong> ${rec.description}</p>
                    <p><strong>Remediation:</strong> ${rec.remediation}</p>
                </div>
            `).join('')}
        </div>

        <div class="section">
            <h2>Evidence Collection</h2>
            ${this.reportData.evidence.map(evidence => `
                <div class="evidence-item">
                    <strong>${evidence.type}:</strong> ${evidence.description}
                    <br><small>File: ${evidence.filePath} | Hash: ${evidence.hash.substring(0, 16)}... | Size: ${evidence.size} bytes</small>
                </div>
            `).join('')}
        </div>
    </div>
</body>
</html>`;

        await fs.writeFile(outputPath, htmlContent, 'utf8');
        return outputPath;
    }

    // Generate JSON report
    async generateJSONReport(outputPath) {
        const reportWithSummary = {
            ...this.reportData,
            executiveSummary: this.generateExecutiveSummary()
        };

        await fs.writeFile(outputPath, JSON.stringify(reportWithSummary, null, 2), 'utf8');
        return outputPath;
    }

    // Generate CSV report for spreadsheet analysis
    async generateCSVReport(outputPath) {
        const csvData = [];
        
        // Add header
        csvData.push(['Test Type', 'Test Name', 'Status', 'Severity', 'Message', 'Timestamp']);
        
        // Add security test results
        this.reportData.securityTests.forEach(testRun => {
            testRun.results.forEach(result => {
                csvData.push([
                    'Security',
                    result.test,
                    result.status,
                    result.severity || 'N/A',
                    result.message,
                    result.timestamp
                ]);
            });
        });

        // Add compliance test results
        this.reportData.complianceTests.forEach(testRun => {
            testRun.results.results?.forEach(result => {
                csvData.push([
                    'Compliance',
                    result.test,
                    result.status,
                    'N/A',
                    result.message,
                    result.timestamp
                ]);
            });
        });

        const csvContent = csvData.map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');
        await fs.writeFile(outputPath, csvContent, 'utf8');
        return outputPath;
    }

    // Generate all report formats
    async generateAllReports(baseOutputPath) {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const baseName = `security-audit-report-${timestamp}`;
        
        const reports = {
            html: await this.generateHTMLReport(`${baseOutputPath}/${baseName}.html`),
            json: await this.generateJSONReport(`${baseOutputPath}/${baseName}.json`),
            csv: await this.generateCSVReport(`${baseOutputPath}/${baseName}.csv`)
        };

        return reports;
    }
}

module.exports = AuditComplianceReporter;