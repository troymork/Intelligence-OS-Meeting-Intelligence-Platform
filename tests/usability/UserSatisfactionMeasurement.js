/**
 * User Satisfaction Measurement and Continuous Improvement System
 * Collects and analyzes user feedback for UX optimization
 */

class UserSatisfactionMeasurement {
    constructor() {
        this.feedbackData = [];
        this.satisfactionMetrics = {};
        this.improvementActions = [];
    }

    // Collect user feedback through various channels
    async collectFeedback(feedbackType, data) {
        const feedback = {
            id: this.generateFeedbackId(),
            type: feedbackType,
            timestamp: new Date().toISOString(),
            data: data,
            processed: false
        };

        this.feedbackData.push(feedback);
        return feedback.id;
    }

    // System Usability Scale (SUS) questionnaire
    async conductSUSEvaluation(responses) {
        const susQuestions = [
            "I think that I would like to use this system frequently",
            "I found the system unnecessarily complex",
            "I thought the system was easy to use",
            "I think that I would need the support of a technical person to be able to use this system",
            "I found the various functions in this system were well integrated",
            "I thought there was too much inconsistency in this system",
            "I would imagine that most people would learn to use this system very quickly",
            "I found the system very cumbersome to use",
            "I felt very confident using the system",
            "I needed to learn a lot of things before I could get going with this system"
        ];

        // Calculate SUS score (0-100 scale)
        let totalScore = 0;
        
        responses.forEach((response, index) => {
            if (index % 2 === 0) { // Odd-numbered questions (positive)
                totalScore += response - 1;
            } else { // Even-numbered questions (negative)
                totalScore += 5 - response;
            }
        });

        const susScore = (totalScore / 40) * 100;
        
        await this.collectFeedback('SUS_EVALUATION', {
            responses: responses,
            score: susScore,
            interpretation: this.interpretSUSScore(susScore)
        });

        return {
            score: susScore,
            interpretation: this.interpretSUSScore(susScore),
            recommendations: this.generateSUSRecommendations(susScore, responses)
        };
    }

    // Interpret SUS score
    interpretSUSScore(score) {
        if (score >= 80) return 'Excellent';
        if (score >= 70) return 'Good';
        if (score >= 50) return 'OK';
        if (score >= 25) return 'Poor';
        return 'Awful';
    }

    // Generate recommendations based on SUS responses
    generateSUSRecommendations(score, responses) {
        const recommendations = [];

        // Check specific problem areas
        if (responses[1] > 3) { // System complexity
            recommendations.push({
                area: 'Complexity',
                issue: 'Users find the system unnecessarily complex',
                recommendation: 'Simplify user interface and reduce cognitive load',
                priority: 'HIGH'
            });
        }

        if (responses[3] > 3) { // Need for technical support
            recommendations.push({
                area: 'Self-sufficiency',
                issue: 'Users need technical support to use the system',
                recommendation: 'Improve onboarding and help documentation',
                priority: 'HIGH'
            });
        }

        if (responses[5] > 3) { // Inconsistency
            recommendations.push({
                area: 'Consistency',
                issue: 'Users perceive inconsistency in the system',
                recommendation: 'Standardize UI patterns and interactions',
                priority: 'MEDIUM'
            });
        }

        if (responses[7] > 3) { // Cumbersome to use
            recommendations.push({
                area: 'Efficiency',
                issue: 'Users find the system cumbersome',
                recommendation: 'Streamline workflows and reduce steps',
                priority: 'HIGH'
            });
        }

        return recommendations;
    }

    // Net Promoter Score (NPS) calculation
    async calculateNPS(scores) {
        const promoters = scores.filter(score => score >= 9).length;
        const detractors = scores.filter(score => score <= 6).length;
        const total = scores.length;

        const nps = total > 0 ? ((promoters - detractors) / total) * 100 : 0;

        await this.collectFeedback('NPS_SURVEY', {
            scores: scores,
            promoters: promoters,
            detractors: detractors,
            passives: total - promoters - detractors,
            nps: nps
        });

        return {
            score: nps,
            interpretation: this.interpretNPS(nps),
            breakdown: {
                promoters: (promoters / total) * 100,
                passives: ((total - promoters - detractors) / total) * 100,
                detractors: (detractors / total) * 100
            }
        };
    }

    // Interpret NPS score
    interpretNPS(score) {
        if (score >= 70) return 'Excellent';
        if (score >= 50) return 'Great';
        if (score >= 30) return 'Good';
        if (score >= 0) return 'Needs Improvement';
        return 'Critical';
    }

    // Customer Effort Score (CES) evaluation
    async evaluateCustomerEffort(taskEffortScores) {
        const averageEffort = taskEffortScores.reduce((sum, score) => sum + score, 0) / taskEffortScores.length;
        
        await this.collectFeedback('CES_EVALUATION', {
            scores: taskEffortScores,
            averageEffort: averageEffort,
            interpretation: this.interpretCES(averageEffort)
        });

        return {
            averageScore: averageEffort,
            interpretation: this.interpretCES(averageEffort),
            recommendations: this.generateCESRecommendations(averageEffort, taskEffortScores)
        };
    }

    // Interpret Customer Effort Score
    interpretCES(score) {
        if (score <= 2) return 'Very Easy';
        if (score <= 3) return 'Easy';
        if (score <= 4) return 'Neutral';
        if (score <= 5) return 'Difficult';
        return 'Very Difficult';
    }

    // Generate CES recommendations
    generateCESRecommendations(averageScore, scores) {
        const recommendations = [];

        if (averageScore > 4) {
            recommendations.push({
                area: 'Task Complexity',
                issue: 'Users find tasks difficult to complete',
                recommendation: 'Simplify task flows and provide better guidance',
                priority: 'HIGH'
            });
        }

        const highEffortTasks = scores.filter(score => score > 4).length;
        if (highEffortTasks > scores.length * 0.3) {
            recommendations.push({
                area: 'User Experience',
                issue: 'Multiple tasks require high effort',
                recommendation: 'Conduct task analysis and redesign problematic workflows',
                priority: 'MEDIUM'
            });
        }

        return recommendations;
    }

    // Collect qualitative feedback
    async collectQualitativeFeedback(feedback) {
        const processedFeedback = {
            sentiment: await this.analyzeSentiment(feedback.text),
            themes: await this.extractThemes(feedback.text),
            actionableItems: await this.identifyActionableItems(feedback.text),
            urgency: this.assessUrgency(feedback.text)
        };

        await this.collectFeedback('QUALITATIVE_FEEDBACK', {
            original: feedback,
            processed: processedFeedback
        });

        return processedFeedback;
    }

    // Analyze sentiment of feedback text
    async analyzeSentiment(text) {
        // Simple sentiment analysis (in production, use a proper NLP service)
        const positiveWords = ['good', 'great', 'excellent', 'love', 'amazing', 'helpful', 'easy', 'intuitive'];
        const negativeWords = ['bad', 'terrible', 'awful', 'hate', 'difficult', 'confusing', 'slow', 'broken'];

        const words = text.toLowerCase().split(/\s+/);
        let positiveCount = 0;
        let negativeCount = 0;

        words.forEach(word => {
            if (positiveWords.includes(word)) positiveCount++;
            if (negativeWords.includes(word)) negativeCount++;
        });

        if (positiveCount > negativeCount) return 'POSITIVE';
        if (negativeCount > positiveCount) return 'NEGATIVE';
        return 'NEUTRAL';
    }

    // Extract themes from feedback
    async extractThemes(text) {
        const themes = [];
        const themeKeywords = {
            'Navigation': ['navigate', 'menu', 'find', 'search', 'lost'],
            'Performance': ['slow', 'fast', 'loading', 'wait', 'delay'],
            'Usability': ['easy', 'difficult', 'intuitive', 'confusing', 'user-friendly'],
            'Features': ['feature', 'function', 'tool', 'capability', 'option'],
            'Design': ['design', 'layout', 'appearance', 'visual', 'color'],
            'Accessibility': ['accessible', 'screen reader', 'keyboard', 'contrast', 'font']
        };

        const lowerText = text.toLowerCase();
        
        Object.entries(themeKeywords).forEach(([theme, keywords]) => {
            if (keywords.some(keyword => lowerText.includes(keyword))) {
                themes.push(theme);
            }
        });

        return themes;
    }

    // Identify actionable items from feedback
    async identifyActionableItems(text) {
        const actionableItems = [];
        const actionPatterns = [
            /should (.*)/gi,
            /need to (.*)/gi,
            /would like (.*)/gi,
            /suggest (.*)/gi,
            /recommend (.*)/gi
        ];

        actionPatterns.forEach(pattern => {
            const matches = text.match(pattern);
            if (matches) {
                actionableItems.push(...matches);
            }
        });

        return actionableItems;
    }

    // Assess urgency of feedback
    assessUrgency(text) {
        const urgentKeywords = ['urgent', 'critical', 'broken', 'error', 'bug', 'crash', 'immediately'];
        const lowerText = text.toLowerCase();
        
        if (urgentKeywords.some(keyword => lowerText.includes(keyword))) {
            return 'HIGH';
        }
        
        return 'MEDIUM';
    }

    // Generate satisfaction metrics dashboard
    generateSatisfactionMetrics() {
        const recentFeedback = this.feedbackData.filter(
            feedback => new Date(feedback.timestamp) > new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
        );

        const susFeedback = recentFeedback.filter(f => f.type === 'SUS_EVALUATION');
        const npsFeedback = recentFeedback.filter(f => f.type === 'NPS_SURVEY');
        const cesFeedback = recentFeedback.filter(f => f.type === 'CES_EVALUATION');
        const qualitativeFeedback = recentFeedback.filter(f => f.type === 'QUALITATIVE_FEEDBACK');

        return {
            period: 'Last 30 days',
            totalFeedback: recentFeedback.length,
            metrics: {
                sus: {
                    averageScore: this.calculateAverageSUS(susFeedback),
                    responseCount: susFeedback.length,
                    trend: this.calculateTrend(susFeedback, 'SUS_EVALUATION')
                },
                nps: {
                    currentScore: this.calculateCurrentNPS(npsFeedback),
                    responseCount: npsFeedback.length,
                    trend: this.calculateTrend(npsFeedback, 'NPS_SURVEY')
                },
                ces: {
                    averageScore: this.calculateAverageCES(cesFeedback),
                    responseCount: cesFeedback.length,
                    trend: this.calculateTrend(cesFeedback, 'CES_EVALUATION')
                },
                sentiment: this.analyzeFeedbackSentiment(qualitativeFeedback)
            },
            topIssues: this.identifyTopIssues(recentFeedback),
            improvementOpportunities: this.identifyImprovementOpportunities(recentFeedback)
        };
    }

    // Calculate average SUS score
    calculateAverageSUS(susFeedback) {
        if (susFeedback.length === 0) return 0;
        const totalScore = susFeedback.reduce((sum, feedback) => sum + feedback.data.score, 0);
        return totalScore / susFeedback.length;
    }

    // Calculate current NPS
    calculateCurrentNPS(npsFeedback) {
        if (npsFeedback.length === 0) return 0;
        return npsFeedback[npsFeedback.length - 1]?.data.nps || 0;
    }

    // Calculate average CES
    calculateAverageCES(cesFeedback) {
        if (cesFeedback.length === 0) return 0;
        const totalScore = cesFeedback.reduce((sum, feedback) => sum + feedback.data.averageEffort, 0);
        return totalScore / cesFeedback.length;
    }

    // Calculate trend for metrics
    calculateTrend(feedbackArray, type) {
        if (feedbackArray.length < 2) return 'STABLE';
        
        const recent = feedbackArray.slice(-5);
        const older = feedbackArray.slice(-10, -5);
        
        if (recent.length === 0 || older.length === 0) return 'STABLE';
        
        let recentAvg, olderAvg;
        
        switch (type) {
            case 'SUS_EVALUATION':
                recentAvg = recent.reduce((sum, f) => sum + f.data.score, 0) / recent.length;
                olderAvg = older.reduce((sum, f) => sum + f.data.score, 0) / older.length;
                break;
            case 'NPS_SURVEY':
                recentAvg = recent.reduce((sum, f) => sum + f.data.nps, 0) / recent.length;
                olderAvg = older.reduce((sum, f) => sum + f.data.nps, 0) / older.length;
                break;
            case 'CES_EVALUATION':
                recentAvg = recent.reduce((sum, f) => sum + f.data.averageEffort, 0) / recent.length;
                olderAvg = older.reduce((sum, f) => sum + f.data.averageEffort, 0) / older.length;
                break;
            default:
                return 'STABLE';
        }
        
        const difference = recentAvg - olderAvg;
        const threshold = type === 'CES_EVALUATION' ? -0.2 : 5; // CES improvement means lower scores
        
        if (type === 'CES_EVALUATION') {
            if (difference < -threshold) return 'IMPROVING';
            if (difference > threshold) return 'DECLINING';
        } else {
            if (difference > threshold) return 'IMPROVING';
            if (difference < -threshold) return 'DECLINING';
        }
        
        return 'STABLE';
    }

    // Analyze overall feedback sentiment
    analyzeFeedbackSentiment(qualitativeFeedback) {
        if (qualitativeFeedback.length === 0) {
            return { positive: 0, neutral: 0, negative: 0 };
        }

        const sentiments = qualitativeFeedback.map(f => f.data.processed.sentiment);
        const positive = sentiments.filter(s => s === 'POSITIVE').length;
        const negative = sentiments.filter(s => s === 'NEGATIVE').length;
        const neutral = sentiments.length - positive - negative;

        return {
            positive: (positive / sentiments.length) * 100,
            neutral: (neutral / sentiments.length) * 100,
            negative: (negative / sentiments.length) * 100
        };
    }

    // Identify top issues from feedback
    identifyTopIssues(feedbackArray) {
        const issues = {};
        
        feedbackArray.forEach(feedback => {
            if (feedback.type === 'QUALITATIVE_FEEDBACK') {
                feedback.data.processed.themes.forEach(theme => {
                    if (feedback.data.processed.sentiment === 'NEGATIVE') {
                        issues[theme] = (issues[theme] || 0) + 1;
                    }
                });
            }
        });

        return Object.entries(issues)
            .sort(([,a], [,b]) => b - a)
            .slice(0, 5)
            .map(([issue, count]) => ({ issue, count }));
    }

    // Identify improvement opportunities
    identifyImprovementOpportunities(feedbackArray) {
        const opportunities = [];
        
        // Analyze SUS feedback for specific improvements
        const susIssues = feedbackArray
            .filter(f => f.type === 'SUS_EVALUATION')
            .flatMap(f => f.data.recommendations || []);
        
        // Group similar recommendations
        const groupedRecommendations = {};
        susIssues.forEach(rec => {
            const key = rec.area;
            if (!groupedRecommendations[key]) {
                groupedRecommendations[key] = {
                    area: rec.area,
                    count: 0,
                    recommendations: [],
                    priority: rec.priority
                };
            }
            groupedRecommendations[key].count++;
            groupedRecommendations[key].recommendations.push(rec.recommendation);
        });

        return Object.values(groupedRecommendations)
            .sort((a, b) => b.count - a.count)
            .slice(0, 5);
    }

    // Generate feedback ID
    generateFeedbackId() {
        return `feedback_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    // Export satisfaction data for analysis
    exportSatisfactionData(format = 'json') {
        const data = {
            metadata: {
                exportDate: new Date().toISOString(),
                totalFeedback: this.feedbackData.length,
                format: format
            },
            metrics: this.generateSatisfactionMetrics(),
            rawFeedback: this.feedbackData
        };

        switch (format) {
            case 'csv':
                return this.convertToCSV(data);
            case 'json':
            default:
                return JSON.stringify(data, null, 2);
        }
    }

    // Convert data to CSV format
    convertToCSV(data) {
        const headers = ['ID', 'Type', 'Timestamp', 'Score', 'Sentiment', 'Themes', 'Urgency'];
        const rows = [headers.join(',')];

        data.rawFeedback.forEach(feedback => {
            const row = [
                feedback.id,
                feedback.type,
                feedback.timestamp,
                feedback.data.score || feedback.data.nps || feedback.data.averageEffort || '',
                feedback.data.processed?.sentiment || '',
                feedback.data.processed?.themes?.join(';') || '',
                feedback.data.processed?.urgency || ''
            ];
            rows.push(row.map(cell => `"${cell}"`).join(','));
        });

        return rows.join('\n');
    }
}

module.exports = UserSatisfactionMeasurement;