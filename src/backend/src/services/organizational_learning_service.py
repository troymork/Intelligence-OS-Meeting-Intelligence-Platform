"""
Organizational Learning Service
Integrates pattern recognition with meeting intelligence for organizational learning
"""

import asyncio
import logging
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import structlog
from .pattern_recognition_engine import (
    PatternRecognitionEngine, 
    DetectedPattern, 
    BestPractice,
    EmotionalFatigueIndicator,
    SystemicIssue
)
from .oracle_output_generator import OracleOutputGenerator

logger = structlog.get_logger(__name__)

@dataclass
class OrganizationalInsight:
    """High-level organizational insight derived from pattern analysis"""
    id: str
    insight_type: str  # pattern, best_practice, systemic_issue, trend
    title: str
    description: str
    supporting_evidence: List[str]
    confidence_score: float
    impact_level: str  # low, medium, high, critical
    actionable_recommendations: List[str]
    stakeholders: List[str]
    timeline_for_action: str
    success_metrics: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class LearningReport:
    """Comprehensive organizational learning report"""
    id: str
    report_period: Dict[str, datetime]
    meetings_analyzed: int
    patterns_detected: List[DetectedPattern]
    best_practices_identified: List[BestPractice]
    emotional_indicators: List[EmotionalFatigueIndicator]
    systemic_issues: List[SystemicIssue]
    organizational_insights: List[OrganizationalInsight]
    learning_trends: Dict[str, Any]
    recommendations_summary: List[str]
    confidence_score: float
    generated_at: datetime = field(default_factory=datetime.utcnow)

class OrganizationalLearningService:
    """Service for organizational learning and pattern-based insights"""
    
    def __init__(self):
        self.pattern_engine = PatternRecognitionEngine()
        self.oracle_generator = OracleOutputGenerator()
        self.learning_history = []  # Store learning reports over time
        self.insight_cache = {}  # Cache organizational insights
        
        # Learning configuration
        self.learning_config = {
            'analysis_window_days': 30,  # Default analysis window
            'min_meetings_for_insights': 5,  # Minimum meetings needed for insights
            'confidence_threshold': 0.6,  # Minimum confidence for insights
            'trend_analysis_periods': 4  # Number of periods for trend analysis
        }
    
    async def analyze_meeting_for_learning(self, meeting_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a meeting for organizational learning patterns"""
        try:
            meeting_id = meeting_data.get('meeting_id', str(uuid.uuid4()))
            
            logger.info("Analyzing meeting for organizational learning", meeting_id=meeting_id)
            
            # Run pattern analysis
            pattern_analysis = await self.pattern_engine.analyze_meeting_patterns(meeting_data)
            
            # Generate learning insights from patterns
            learning_insights = await self._generate_learning_insights(pattern_analysis)
            
            # Update organizational knowledge
            knowledge_updates = await self._update_organizational_knowledge(
                meeting_data, pattern_analysis, learning_insights
            )
            
            # Generate recommendations
            recommendations = await self._generate_learning_recommendations(
                pattern_analysis, learning_insights
            )
            
            result = {
                'meeting_id': meeting_id,
                'pattern_analysis': pattern_analysis,
                'learning_insights': learning_insights,
                'knowledge_updates': knowledge_updates,
                'recommendations': recommendations,
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info("Meeting learning analysis completed", 
                       meeting_id=meeting_id,
                       insights_generated=len(learning_insights),
                       patterns_detected=len(pattern_analysis.get('cross_meeting_patterns', [])))
            
            return result
            
        except Exception as e:
            logger.error("Meeting learning analysis failed", error=str(e))
            raise
    
    async def generate_learning_report(self, 
                                     start_date: Optional[datetime] = None,
                                     end_date: Optional[datetime] = None) -> LearningReport:
        """Generate comprehensive organizational learning report"""
        try:
            # Set default date range if not provided
            if not end_date:
                end_date = datetime.utcnow()
            if not start_date:
                start_date = end_date - timedelta(days=self.learning_config['analysis_window_days'])
            
            logger.info("Generating organizational learning report", 
                       start_date=start_date.isoformat(),
                       end_date=end_date.isoformat())
            
            # Get relevant meetings from the pattern engine
            relevant_meetings = self._get_meetings_in_period(start_date, end_date)
            
            if len(relevant_meetings) < self.learning_config['min_meetings_for_insights']:
                logger.warning("Insufficient meetings for comprehensive learning report",
                             meetings_count=len(relevant_meetings))
            
            # Aggregate pattern analysis results
            all_patterns = []
            all_best_practices = []
            all_emotional_indicators = []
            all_systemic_issues = []
            
            for meeting in relevant_meetings:
                # This would typically come from stored analysis results
                # For now, we'll simulate the aggregation
                patterns = self.pattern_engine.detected_patterns.values()
                all_patterns.extend([p for p in patterns if self._is_pattern_in_period(p, start_date, end_date)])
            
            # Generate high-level organizational insights
            organizational_insights = await self._generate_organizational_insights(
                all_patterns, all_best_practices, all_emotional_indicators, all_systemic_issues
            )
            
            # Analyze learning trends
            learning_trends = await self._analyze_learning_trends(
                all_patterns, start_date, end_date
            )
            
            # Generate summary recommendations
            recommendations_summary = await self._generate_recommendations_summary(
                organizational_insights, learning_trends
            )
            
            # Calculate overall confidence
            confidence_score = self._calculate_report_confidence(
                relevant_meetings, all_patterns, organizational_insights
            )
            
            # Create learning report
            report = LearningReport(
                id=str(uuid.uuid4()),
                report_period={'start': start_date, 'end': end_date},
                meetings_analyzed=len(relevant_meetings),
                patterns_detected=all_patterns,
                best_practices_identified=all_best_practices,
                emotional_indicators=all_emotional_indicators,
                systemic_issues=all_systemic_issues,
                organizational_insights=organizational_insights,
                learning_trends=learning_trends,
                recommendations_summary=recommendations_summary,
                confidence_score=confidence_score
            )
            
            # Store report in learning history
            self.learning_history.append(report)
            
            logger.info("Learning report generated successfully",
                       report_id=report.id,
                       patterns_count=len(all_patterns),
                       insights_count=len(organizational_insights))
            
            return report
            
        except Exception as e:
            logger.error("Learning report generation failed", error=str(e))
            raise
    
    async def _generate_learning_insights(self, pattern_analysis: Dict[str, Any]) -> List[OrganizationalInsight]:
        """Generate high-level learning insights from pattern analysis"""
        try:
            insights = []
            
            # Generate insights from cross-meeting patterns
            cross_patterns = pattern_analysis.get('cross_meeting_patterns', [])
            for pattern in cross_patterns:
                if pattern.confidence_score >= self.learning_config['confidence_threshold']:
                    insight = await self._create_pattern_insight(pattern)
                    insights.append(insight)
            
            # Generate insights from best practices
            best_practices = pattern_analysis.get('best_practices', [])
            for practice in best_practices:
                insight = await self._create_best_practice_insight(practice)
                insights.append(insight)
            
            # Generate insights from emotional indicators
            emotional_indicators = pattern_analysis.get('emotional_indicators', [])
            for indicator in emotional_indicators:
                if indicator.severity.value in ['high', 'critical']:
                    insight = await self._create_emotional_insight(indicator)
                    insights.append(insight)
            
            # Generate insights from systemic issues
            systemic_issues = pattern_analysis.get('systemic_issues', [])
            for issue in systemic_issues:
                insight = await self._create_systemic_insight(issue)
                insights.append(insight)
            
            return insights
            
        except Exception as e:
            logger.error("Learning insights generation failed", error=str(e))
            return []
    
    async def _create_pattern_insight(self, pattern: DetectedPattern) -> OrganizationalInsight:
        """Create organizational insight from a detected pattern"""
        try:
            # Determine impact level based on pattern characteristics
            impact_level = self._determine_pattern_impact_level(pattern)
            
            # Generate actionable recommendations
            recommendations = self._generate_pattern_recommendations(pattern)
            
            # Identify stakeholders
            stakeholders = self._identify_pattern_stakeholders(pattern)
            
            # Determine timeline for action
            timeline = self._determine_action_timeline(pattern)
            
            insight = OrganizationalInsight(
                id=str(uuid.uuid4()),
                insight_type='pattern',
                title=f"Pattern Insight: {pattern.title}",
                description=f"Recurring pattern detected with {pattern.frequency} occurrences. {pattern.description}",
                supporting_evidence=[instance.evidence[0] if instance.evidence else "Pattern instance" for instance in pattern.instances[:3]],
                confidence_score=pattern.confidence_score,
                impact_level=impact_level,
                actionable_recommendations=recommendations,
                stakeholders=stakeholders,
                timeline_for_action=timeline,
                success_metrics=self._define_pattern_success_metrics(pattern)
            )
            
            return insight
            
        except Exception as e:
            logger.error("Pattern insight creation failed", error=str(e))
            return OrganizationalInsight(
                id=str(uuid.uuid4()),
                insight_type='pattern',
                title="Pattern Analysis Error",
                description="Unable to generate insight from pattern",
                supporting_evidence=[],
                confidence_score=0.1,
                impact_level='low',
                actionable_recommendations=["Review pattern analysis"],
                stakeholders=[],
                timeline_for_action='long_term',
                success_metrics=[]
            )
    
    async def _update_organizational_knowledge(self, 
                                             meeting_data: Dict[str, Any],
                                             pattern_analysis: Dict[str, Any],
                                             learning_insights: List[OrganizationalInsight]) -> Dict[str, Any]:
        """Update organizational knowledge base with new learning"""
        try:
            knowledge_updates = {
                'new_patterns_learned': len(pattern_analysis.get('cross_meeting_patterns', [])),
                'best_practices_identified': len(pattern_analysis.get('best_practices', [])),
                'insights_generated': len(learning_insights),
                'knowledge_areas_updated': [],
                'learning_confidence': pattern_analysis.get('confidence_score', 0.5)
            }
            
            # Identify knowledge areas that were updated
            for insight in learning_insights:
                if insight.insight_type == 'pattern':
                    knowledge_updates['knowledge_areas_updated'].append('pattern_recognition')
                elif insight.insight_type == 'best_practice':
                    knowledge_updates['knowledge_areas_updated'].append('best_practices')
                elif insight.insight_type == 'systemic_issue':
                    knowledge_updates['knowledge_areas_updated'].append('systemic_issues')
            
            # Remove duplicates
            knowledge_updates['knowledge_areas_updated'] = list(set(knowledge_updates['knowledge_areas_updated']))
            
            return knowledge_updates
            
        except Exception as e:
            logger.error("Knowledge update failed", error=str(e))
            return {'error': 'Knowledge update failed'}
    
    async def _generate_learning_recommendations(self, 
                                               pattern_analysis: Dict[str, Any],
                                               learning_insights: List[OrganizationalInsight]) -> List[str]:
        """Generate actionable learning recommendations"""
        try:
            recommendations = []
            
            # Aggregate recommendations from insights
            for insight in learning_insights:
                recommendations.extend(insight.actionable_recommendations)
            
            # Add pattern-specific recommendations
            patterns = pattern_analysis.get('cross_meeting_patterns', [])
            for pattern in patterns:
                if hasattr(pattern, 'intervention_recommendations'):
                    recommendations.extend(pattern.intervention_recommendations)
            
            # Add systemic recommendations
            systemic_issues = pattern_analysis.get('systemic_issues', [])
            for issue in systemic_issues:
                if hasattr(issue, 'intervention_strategy'):
                    strategy = issue.intervention_strategy
                    if isinstance(strategy, dict) and 'recommendations' in strategy:
                        recommendations.extend(strategy['recommendations'])
            
            # Remove duplicates and prioritize
            unique_recommendations = list(set(recommendations))
            
            # Prioritize recommendations (this could be more sophisticated)
            prioritized_recommendations = self._prioritize_recommendations(unique_recommendations, learning_insights)
            
            return prioritized_recommendations[:10]  # Top 10 recommendations
            
        except Exception as e:
            logger.error("Learning recommendations generation failed", error=str(e))
            return ["Review organizational learning analysis for actionable insights"]
    
    def _prioritize_recommendations(self, recommendations: List[str], 
                                  insights: List[OrganizationalInsight]) -> List[str]:
        """Prioritize recommendations based on insight impact and confidence"""
        try:
            # Create recommendation scores based on associated insights
            rec_scores = {}
            
            for rec in recommendations:
                score = 0.0
                count = 0
                
                # Find insights that contain this recommendation
                for insight in insights:
                    if rec in insight.actionable_recommendations:
                        impact_weight = {'critical': 1.0, 'high': 0.8, 'medium': 0.6, 'low': 0.4}.get(insight.impact_level, 0.5)
                        score += insight.confidence_score * impact_weight
                        count += 1
                
                if count > 0:
                    rec_scores[rec] = score / count
                else:
                    rec_scores[rec] = 0.5  # Default score
            
            # Sort by score (highest first)
            sorted_recommendations = sorted(rec_scores.items(), key=lambda x: x[1], reverse=True)
            
            return [rec for rec, score in sorted_recommendations]
            
        except Exception as e:
            logger.error("Recommendation prioritization failed", error=str(e))
            return recommendations
    
    def _get_meetings_in_period(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get meetings within the specified time period"""
        try:
            relevant_meetings = []
            
            for meeting in self.pattern_engine.meeting_history:
                meeting_date_str = meeting.get('date')
                if meeting_date_str:
                    try:
                        meeting_date = datetime.fromisoformat(meeting_date_str.replace('Z', '+00:00'))
                        if start_date <= meeting_date <= end_date:
                            relevant_meetings.append(meeting)
                    except ValueError:
                        # Skip meetings with invalid date formats
                        continue
            
            return relevant_meetings
            
        except Exception as e:
            logger.error("Meeting period filtering failed", error=str(e))
            return []
    
    def _calculate_report_confidence(self, meetings: List[Dict[str, Any]], 
                                   patterns: List[DetectedPattern],
                                   insights: List[OrganizationalInsight]) -> float:
        """Calculate overall confidence score for the learning report"""
        try:
            confidence_factors = []
            
            # Data volume factor
            if len(meetings) >= 10:
                confidence_factors.append(0.9)
            elif len(meetings) >= 5:
                confidence_factors.append(0.7)
            else:
                confidence_factors.append(0.5)
            
            # Pattern quality factor
            if patterns:
                pattern_confidences = [p.confidence_score for p in patterns]
                avg_pattern_confidence = sum(pattern_confidences) / len(pattern_confidences)
                confidence_factors.append(avg_pattern_confidence)
            
            # Insight quality factor
            if insights:
                insight_confidences = [i.confidence_score for i in insights]
                avg_insight_confidence = sum(insight_confidences) / len(insight_confidences)
                confidence_factors.append(avg_insight_confidence)
            
            return sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.5
            
        except Exception as e:
            logger.error("Report confidence calculation failed", error=str(e))
            return 0.5

# Global service instance
organizational_learning_service = OrganizationalLearningService()