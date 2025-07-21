"""
Pattern Analysis API Routes
Provides endpoints for organizational pattern recognition and learning
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import structlog
from ..services.pattern_recognition_engine import PatternRecognitionEngine
from ..services.organizational_learning_service import OrganizationalLearningService
from ..security.auth import require_auth
from ..security.validation import validate_json_input
from ..security.rate_limiting import rate_limit

logger = structlog.get_logger(__name__)

# Create blueprint
pattern_analysis_bp = Blueprint('pattern_analysis', __name__, url_prefix='/api/pattern-analysis')

# Initialize services
pattern_engine = PatternRecognitionEngine()
learning_service = OrganizationalLearningService()

@pattern_analysis_bp.route('/analyze-meeting', methods=['POST'])
@require_auth
@rate_limit(limit=100, window=3600)  # 100 requests per hour
@validate_json_input
def analyze_meeting_patterns():
    """
    Analyze patterns in a single meeting
    
    Expected JSON payload:
    {
        "meeting_data": {
            "meeting_id": "string",
            "date": "ISO datetime string",
            "transcript_analysis": {...},
            "decisions": [...],
            "actions": [...],
            "discussion_dynamics": {...},
            "human_needs_intelligence": {...}
        }
    }
    """
    try:
        data = request.get_json()
        meeting_data = data.get('meeting_data')
        
        if not meeting_data:
            return jsonify({
                'error': 'Missing meeting_data in request',
                'status': 'error'
            }), 400
        
        # Validate required fields
        required_fields = ['meeting_id']
        missing_fields = [field for field in required_fields if field not in meeting_data]
        if missing_fields:
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing_fields)}',
                'status': 'error'
            }), 400
        
        logger.info("Analyzing meeting patterns", meeting_id=meeting_data.get('meeting_id'))
        
        # Perform pattern analysis
        analysis_result = pattern_engine.analyze_meeting_patterns(meeting_data)
        
        # Convert result to JSON-serializable format
        serialized_result = _serialize_pattern_analysis(analysis_result)
        
        logger.info("Meeting pattern analysis completed", 
                   meeting_id=meeting_data.get('meeting_id'),
                   patterns_detected=len(serialized_result.get('cross_meeting_patterns', [])))
        
        return jsonify({
            'status': 'success',
            'data': serialized_result,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error("Meeting pattern analysis failed", error=str(e))
        return jsonify({
            'error': 'Pattern analysis failed',
            'details': str(e),
            'status': 'error'
        }), 500

@pattern_analysis_bp.route('/learning-report', methods=['POST'])
@require_auth
@rate_limit(limit=20, window=3600)  # 20 requests per hour
@validate_json_input
def generate_learning_report():
    """
    Generate organizational learning report
    
    Expected JSON payload:
    {
        "start_date": "ISO datetime string (optional)",
        "end_date": "ISO datetime string (optional)",
        "analysis_window_days": 30 (optional)
    }
    """
    try:
        data = request.get_json() or {}
        
        # Parse date parameters
        start_date = None
        end_date = None
        
        if 'start_date' in data:
            try:
                start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({
                    'error': 'Invalid start_date format. Use ISO datetime format.',
                    'status': 'error'
                }), 400
        
        if 'end_date' in data:
            try:
                end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({
                    'error': 'Invalid end_date format. Use ISO datetime format.',
                    'status': 'error'
                }), 400
        
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            analysis_window_days = data.get('analysis_window_days', 30)
            start_date = end_date - timedelta(days=analysis_window_days)
        
        logger.info("Generating learning report", 
                   start_date=start_date.isoformat(),
                   end_date=end_date.isoformat())
        
        # Generate learning report
        learning_report = learning_service.generate_learning_report(start_date, end_date)
        
        # Convert to JSON-serializable format
        serialized_report = _serialize_learning_report(learning_report)
        
        logger.info("Learning report generated successfully",
                   report_id=learning_report.id,
                   meetings_analyzed=learning_report.meetings_analyzed)
        
        return jsonify({
            'status': 'success',
            'data': serialized_report,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error("Learning report generation failed", error=str(e))
        return jsonify({
            'error': 'Learning report generation failed',
            'details': str(e),
            'status': 'error'
        }), 500

@pattern_analysis_bp.route('/patterns', methods=['GET'])
@require_auth
@rate_limit(limit=200, window=3600)  # 200 requests per hour
def get_detected_patterns():
    """
    Get all detected patterns with optional filtering
    
    Query parameters:
    - pattern_type: Filter by pattern type
    - severity: Filter by severity level
    - limit: Maximum number of patterns to return (default: 50)
    - offset: Number of patterns to skip (default: 0)
    """
    try:
        # Get query parameters
        pattern_type = request.args.get('pattern_type')
        severity = request.args.get('severity')
        limit = min(int(request.args.get('limit', 50)), 100)  # Max 100
        offset = int(request.args.get('offset', 0))
        
        # Get patterns from engine
        all_patterns = list(pattern_engine.detected_patterns.values())
        
        # Apply filters
        filtered_patterns = all_patterns
        
        if pattern_type:
            filtered_patterns = [p for p in filtered_patterns if p.pattern_type.value == pattern_type]
        
        if severity:
            filtered_patterns = [p for p in filtered_patterns if p.severity.value == severity]
        
        # Apply pagination
        paginated_patterns = filtered_patterns[offset:offset + limit]
        
        # Serialize patterns
        serialized_patterns = [_serialize_detected_pattern(p) for p in paginated_patterns]
        
        return jsonify({
            'status': 'success',
            'data': {
                'patterns': serialized_patterns,
                'total_count': len(filtered_patterns),
                'returned_count': len(serialized_patterns),
                'offset': offset,
                'limit': limit
            },
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error("Pattern retrieval failed", error=str(e))
        return jsonify({
            'error': 'Pattern retrieval failed',
            'details': str(e),
            'status': 'error'
        }), 500

@pattern_analysis_bp.route('/best-practices', methods=['GET'])
@require_auth
@rate_limit(limit=200, window=3600)  # 200 requests per hour
def get_best_practices():
    """
    Get identified best practices with optional filtering
    
    Query parameters:
    - category: Filter by category
    - min_effectiveness: Minimum effectiveness score (0-1)
    - limit: Maximum number of practices to return (default: 20)
    - offset: Number of practices to skip (default: 0)
    """
    try:
        # Get query parameters
        category = request.args.get('category')
        min_effectiveness = float(request.args.get('min_effectiveness', 0.0))
        limit = min(int(request.args.get('limit', 20)), 50)  # Max 50
        offset = int(request.args.get('offset', 0))
        
        # Get best practices from engine
        all_practices = list(pattern_engine.best_practices.values())
        
        # Apply filters
        filtered_practices = all_practices
        
        if category:
            filtered_practices = [p for p in filtered_practices if p.category == category]
        
        if min_effectiveness > 0:
            filtered_practices = [p for p in filtered_practices if p.effectiveness_score >= min_effectiveness]
        
        # Apply pagination
        paginated_practices = filtered_practices[offset:offset + limit]
        
        # Serialize practices
        serialized_practices = [_serialize_best_practice(p) for p in paginated_practices]
        
        return jsonify({
            'status': 'success',
            'data': {
                'best_practices': serialized_practices,
                'total_count': len(filtered_practices),
                'returned_count': len(serialized_practices),
                'offset': offset,
                'limit': limit
            },
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error("Best practices retrieval failed", error=str(e))
        return jsonify({
            'error': 'Best practices retrieval failed',
            'details': str(e),
            'status': 'error'
        }), 500

@pattern_analysis_bp.route('/emotional-indicators', methods=['GET'])
@require_auth
@rate_limit(limit=200, window=3600)  # 200 requests per hour
def get_emotional_indicators():
    """
    Get emotional fatigue and misalignment indicators
    
    Query parameters:
    - severity: Filter by severity level
    - indicator_type: Filter by indicator type
    - limit: Maximum number of indicators to return (default: 20)
    - offset: Number of indicators to skip (default: 0)
    """
    try:
        # Get query parameters
        severity = request.args.get('severity')
        indicator_type = request.args.get('indicator_type')
        limit = min(int(request.args.get('limit', 20)), 50)  # Max 50
        offset = int(request.args.get('offset', 0))
        
        # Get indicators from engine
        all_indicators = list(pattern_engine.emotional_indicators.values())
        
        # Apply filters
        filtered_indicators = all_indicators
        
        if severity:
            filtered_indicators = [i for i in filtered_indicators if i.severity.value == severity]
        
        if indicator_type:
            filtered_indicators = [i for i in filtered_indicators if i.indicator_type == indicator_type]
        
        # Apply pagination
        paginated_indicators = filtered_indicators[offset:offset + limit]
        
        # Serialize indicators
        serialized_indicators = [_serialize_emotional_indicator(i) for i in paginated_indicators]
        
        return jsonify({
            'status': 'success',
            'data': {
                'emotional_indicators': serialized_indicators,
                'total_count': len(filtered_indicators),
                'returned_count': len(serialized_indicators),
                'offset': offset,
                'limit': limit
            },
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error("Emotional indicators retrieval failed", error=str(e))
        return jsonify({
            'error': 'Emotional indicators retrieval failed',
            'details': str(e),
            'status': 'error'
        }), 500

@pattern_analysis_bp.route('/systemic-issues', methods=['GET'])
@require_auth
@rate_limit(limit=100, window=3600)  # 100 requests per hour
def get_systemic_issues():
    """
    Get identified systemic issues
    
    Query parameters:
    - urgency_level: Filter by urgency level
    - affected_area: Filter by affected area
    - limit: Maximum number of issues to return (default: 10)
    - offset: Number of issues to skip (default: 0)
    """
    try:
        # Get query parameters
        urgency_level = request.args.get('urgency_level')
        affected_area = request.args.get('affected_area')
        limit = min(int(request.args.get('limit', 10)), 25)  # Max 25
        offset = int(request.args.get('offset', 0))
        
        # Get systemic issues from engine
        all_issues = list(pattern_engine.systemic_issues.values())
        
        # Apply filters
        filtered_issues = all_issues
        
        if urgency_level:
            filtered_issues = [i for i in filtered_issues if i.urgency_level.value == urgency_level]
        
        if affected_area:
            filtered_issues = [i for i in filtered_issues if affected_area in i.affected_areas]
        
        # Apply pagination
        paginated_issues = filtered_issues[offset:offset + limit]
        
        # Serialize issues
        serialized_issues = [_serialize_systemic_issue(i) for i in paginated_issues]
        
        return jsonify({
            'status': 'success',
            'data': {
                'systemic_issues': serialized_issues,
                'total_count': len(filtered_issues),
                'returned_count': len(serialized_issues),
                'offset': offset,
                'limit': limit
            },
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error("Systemic issues retrieval failed", error=str(e))
        return jsonify({
            'error': 'Systemic issues retrieval failed',
            'details': str(e),
            'status': 'error'
        }), 500

# Serialization helper functions
def _serialize_pattern_analysis(analysis_result):
    """Serialize pattern analysis result for JSON response"""
    try:
        serialized = {
            'meeting_id': analysis_result.get('meeting_id'),
            'current_meeting_patterns': analysis_result.get('current_meeting_patterns', []),
            'cross_meeting_patterns': [
                _serialize_detected_pattern(p) for p in analysis_result.get('cross_meeting_patterns', [])
            ],
            'best_practices': [
                _serialize_best_practice(p) for p in analysis_result.get('best_practices', [])
            ],
            'emotional_indicators': [
                _serialize_emotional_indicator(i) for i in analysis_result.get('emotional_indicators', [])
            ],
            'systemic_issues': [
                _serialize_systemic_issue(i) for i in analysis_result.get('systemic_issues', [])
            ],
            'confidence_score': analysis_result.get('confidence_score', 0.0),
            'analysis_timestamp': analysis_result.get('analysis_timestamp')
        }
        return serialized
    except Exception as e:
        logger.error("Pattern analysis serialization failed", error=str(e))
        return {'error': 'Serialization failed'}

def _serialize_detected_pattern(pattern):
    """Serialize DetectedPattern for JSON response"""
    return {
        'id': pattern.id,
        'pattern_type': pattern.pattern_type.value,
        'title': pattern.title,
        'description': pattern.description,
        'frequency': pattern.frequency,
        'severity': pattern.severity.value,
        'trend': pattern.trend.value,
        'first_occurrence': pattern.first_occurrence.isoformat(),
        'last_occurrence': pattern.last_occurrence.isoformat(),
        'affected_participants': list(pattern.affected_participants),
        'root_causes': pattern.root_causes,
        'impact_analysis': pattern.impact_analysis,
        'intervention_recommendations': pattern.intervention_recommendations,
        'confidence_score': pattern.confidence_score,
        'created_at': pattern.created_at.isoformat()
    }

def _serialize_best_practice(practice):
    """Serialize BestPractice for JSON response"""
    return {
        'id': practice.id,
        'title': practice.title,
        'description': practice.description,
        'category': practice.category,
        'success_indicators': practice.success_indicators,
        'implementation_guidance': practice.implementation_guidance,
        'applicable_contexts': practice.applicable_contexts,
        'evidence_meetings': practice.evidence_meetings,
        'effectiveness_score': practice.effectiveness_score,
        'adoption_recommendations': practice.adoption_recommendations,
        'created_at': practice.created_at.isoformat()
    }

def _serialize_emotional_indicator(indicator):
    """Serialize EmotionalFatigueIndicator for JSON response"""
    return {
        'id': indicator.id,
        'indicator_type': indicator.indicator_type,
        'severity': indicator.severity.value,
        'affected_participants': indicator.affected_participants,
        'symptoms': indicator.symptoms,
        'contributing_factors': indicator.contributing_factors,
        'intervention_urgency': indicator.intervention_urgency,
        'recommended_actions': indicator.recommended_actions,
        'monitoring_metrics': indicator.monitoring_metrics,
        'created_at': indicator.created_at.isoformat()
    }

def _serialize_systemic_issue(issue):
    """Serialize SystemicIssue for JSON response"""
    return {
        'id': issue.id,
        'issue_title': issue.issue_title,
        'issue_description': issue.issue_description,
        'root_causes': issue.root_causes,
        'affected_areas': issue.affected_areas,
        'impact_assessment': issue.impact_assessment,
        'urgency_level': issue.urgency_level.value,
        'intervention_strategy': issue.intervention_strategy,
        'success_metrics': issue.success_metrics,
        'timeline_recommendations': issue.timeline_recommendations,
        'stakeholder_involvement': issue.stakeholder_involvement,
        'created_at': issue.created_at.isoformat()
    }

def _serialize_learning_report(report):
    """Serialize LearningReport for JSON response"""
    return {
        'id': report.id,
        'report_period': {
            'start': report.report_period['start'].isoformat(),
            'end': report.report_period['end'].isoformat()
        },
        'meetings_analyzed': report.meetings_analyzed,
        'patterns_detected': [_serialize_detected_pattern(p) for p in report.patterns_detected],
        'best_practices_identified': [_serialize_best_practice(p) for p in report.best_practices_identified],
        'emotional_indicators': [_serialize_emotional_indicator(i) for i in report.emotional_indicators],
        'systemic_issues': [_serialize_systemic_issue(i) for i in report.systemic_issues],
        'organizational_insights': [_serialize_organizational_insight(i) for i in report.organizational_insights],
        'learning_trends': report.learning_trends,
        'recommendations_summary': report.recommendations_summary,
        'confidence_score': report.confidence_score,
        'generated_at': report.generated_at.isoformat()
    }

def _serialize_organizational_insight(insight):
    """Serialize OrganizationalInsight for JSON response"""
    return {
        'id': insight.id,
        'insight_type': insight.insight_type,
        'title': insight.title,
        'description': insight.description,
        'supporting_evidence': insight.supporting_evidence,
        'confidence_score': insight.confidence_score,
        'impact_level': insight.impact_level,
        'actionable_recommendations': insight.actionable_recommendations,
        'stakeholders': insight.stakeholders,
        'timeline_for_action': insight.timeline_for_action,
        'success_metrics': insight.success_metrics,
        'created_at': insight.created_at.isoformat()
    }