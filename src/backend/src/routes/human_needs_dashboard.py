"""
Human Needs Visualization and Reporting Dashboard Routes for Intelligence OS
Provides API endpoints for human needs dashboards and analytics
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
import structlog

from ..services.human_needs_engine import human_needs_engine
from ..services.need_imbalance_detector import need_imbalance_detector
from ..services.intervention_engine import intervention_engine
from ..security.auth import require_auth
from ..security.validation import validate_request_data
from ..security.rate_limiting import rate_limit

logger = structlog.get_logger(__name__)

# Create blueprint
human_needs_dashboard_bp = Blueprint('human_needs_dashboard', __name__, url_prefix='/api/human-needs')

@human_needs_dashboard_bp.route('/dashboard/individual/<participant_id>', methods=['GET'])
@require_auth
@rate_limit(requests_per_minute=30)
async def get_individual_dashboard(participant_id: str):
    """Get individual human needs dashboard data"""
    try:
        # Get query parameters
        time_range = request.args.get('time_range', '30d')
        privacy_level = request.args.get('privacy_level', 'private')
        
        # Validate access permissions
        current_user = request.current_user
        if not await _check_dashboard_access(current_user, participant_id, privacy_level):
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403
        
        # Generate dashboard data
        dashboard_data = await _generate_individual_dashboard(participant_id, time_range, privacy_level)
        
        return jsonify({
            'success': True,
            'dashboard': dashboard_data,
            'participant_id': participant_id,
            'time_range': time_range,
            'privacy_level': privacy_level
        }), 200
        
    except Exception as e:
        logger.error("Individual dashboard generation failed", 
                    participant_id=participant_id, error=str(e))
        return jsonify({
            'success': False,
            'error': 'Failed to generate individual dashboard',
            'details': str(e)
        }), 500

@human_needs_dashboard_bp.route('/dashboard/team/<team_id>', methods=['GET'])
@require_auth
@rate_limit(requests_per_minute=20)
async def get_team_dashboard(team_id: str):
    """Get team human needs dashboard data"""
    try:
        # Get query parameters
        time_range = request.args.get('time_range', '30d')
        include_individuals = request.args.get('include_individuals', 'false').lower() == 'true'
        
        # Validate access permissions
        current_user = request.current_user
        if not await _check_team_dashboard_access(current_user, team_id):
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403
        
        # Generate team dashboard data
        dashboard_data = await _generate_team_dashboard(team_id, time_range, include_individuals)
        
        return jsonify({
            'success': True,
            'dashboard': dashboard_data,
            'team_id': team_id,
            'time_range': time_range
        }), 200
        
    except Exception as e:
        logger.error("Team dashboard generation failed", 
                    team_id=team_id, error=str(e))
        return jsonify({
            'success': False,
            'error': 'Failed to generate team dashboard',
            'details': str(e)
        }), 500

@human_needs_dashboard_bp.route('/analytics/trends', methods=['GET'])
@require_auth
@rate_limit(requests_per_minute=15)
async def get_needs_trends():
    """Get human needs trend analysis"""
    try:
        # Get query parameters
        scope = request.args.get('scope', 'team')  # individual, team, organization
        entity_id = request.args.get('entity_id')
        time_range = request.args.get('time_range', '90d')
        needs_filter = request.args.getlist('needs')
        
        # Validate access
        current_user = request.current_user
        if not await _check_analytics_access(current_user, scope, entity_id):
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403
        
        # Generate trend analysis
        trends_data = await _generate_trends_analysis(scope, entity_id, time_range, needs_filter)
        
        return jsonify({
            'success': True,
            'trends': trends_data,
            'scope': scope,
            'time_range': time_range
        }), 200
        
    except Exception as e:
        logger.error("Trends analysis failed", error=str(e))
        return jsonify({
            'success': False,
            'error': 'Failed to generate trends analysis',
            'details': str(e)
        }), 500

@human_needs_dashboard_bp.route('/interventions/progress/<intervention_id>', methods=['GET'])
@require_auth
@rate_limit(requests_per_minute=30)
async def get_intervention_progress(intervention_id: str):
    """Get intervention progress visualization data"""
    try:
        # Validate access
        current_user = request.current_user
        if not await _check_intervention_access(current_user, intervention_id):
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403
        
        # Get progress data
        progress_data = await _generate_intervention_progress_data(intervention_id)
        
        return jsonify({
            'success': True,
            'progress': progress_data,
            'intervention_id': intervention_id
        }), 200
        
    except Exception as e:
        logger.error("Intervention progress retrieval failed", 
                    intervention_id=intervention_id, error=str(e))
        return jsonify({
            'success': False,
            'error': 'Failed to get intervention progress',
            'details': str(e)
        }), 500

@human_needs_dashboard_bp.route('/interventions/effectiveness', methods=['GET'])
@require_auth
@rate_limit(requests_per_minute=10)
async def get_intervention_effectiveness():
    """Get intervention effectiveness analytics"""
    try:
        # Get query parameters
        anonymized = request.args.get('anonymized', 'true').lower() == 'true'
        time_range = request.args.get('time_range', '180d')
        
        # Get effectiveness analytics
        effectiveness_data = await intervention_engine.get_intervention_analytics(anonymized=anonymized)
        
        return jsonify({
            'success': True,
            'effectiveness': effectiveness_data,
            'time_range': time_range,
            'anonymized': anonymized
        }), 200
        
    except Exception as e:
        logger.error("Intervention effectiveness analytics failed", error=str(e))
        return jsonify({
            'success': False,
            'error': 'Failed to get intervention effectiveness',
            'details': str(e)
        }), 500

@human_needs_dashboard_bp.route('/privacy/settings/<participant_id>', methods=['GET', 'PUT'])
@require_auth
@rate_limit(requests_per_minute=20)
async def manage_privacy_settings(participant_id: str):
    """Get or update privacy settings for human needs data"""
    try:
        current_user = request.current_user
        
        # Validate access (only self or authorized managers)
        if not await _check_privacy_settings_access(current_user, participant_id):
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403
        
        if request.method == 'GET':
            # Get current privacy settings
            privacy_settings = await _get_privacy_settings(participant_id)
            
            return jsonify({
                'success': True,
                'privacy_settings': privacy_settings,
                'participant_id': participant_id
            }), 200
        
        elif request.method == 'PUT':
            # Update privacy settings
            data = request.get_json()
            
            updated_settings = await _update_privacy_settings(participant_id, data)
            
            return jsonify({
                'success': True,
                'privacy_settings': updated_settings,
                'message': 'Privacy settings updated successfully'
            }), 200
        
    except Exception as e:
        logger.error("Privacy settings management failed", 
                    participant_id=participant_id, error=str(e))
        return jsonify({
            'success': False,
            'error': 'Failed to manage privacy settings',
            'details': str(e)
        }), 500

@human_needs_dashboard_bp.route('/reports/comprehensive', methods=['POST'])
@require_auth
@rate_limit(requests_per_minute=5)
@validate_request_data({
    'scope': {'type': 'string', 'required': True, 'allowed_values': ['individual', 'team', 'organization']},
    'entity_id': {'type': 'string', 'required': True},
    'time_range': {'type': 'string', 'required': False},
    'include_interventions': {'type': 'boolean', 'required': False},
    'privacy_level': {'type': 'string', 'required': False}
})
async def generate_comprehensive_report():
    """Generate comprehensive human needs report"""
    try:
        data = request.get_json()
        
        # Validate access
        current_user = request.current_user
        if not await _check_report_access(current_user, data['scope'], data['entity_id']):
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403
        
        # Generate comprehensive report
        report_data = await _generate_comprehensive_report(
            scope=data['scope'],
            entity_id=data['entity_id'],
            time_range=data.get('time_range', '90d'),
            include_interventions=data.get('include_interventions', True),
            privacy_level=data.get('privacy_level', 'team')
        )
        
        return jsonify({
            'success': True,
            'report': report_data,
            'generated_at': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error("Comprehensive report generation failed", error=str(e))
        return jsonify({
            'success': False,
            'error': 'Failed to generate comprehensive report',
            'details': str(e)
        }), 500

# Helper functions for dashboard generation

async def _generate_individual_dashboard(participant_id: str, time_range: str, 
                                       privacy_level: str) -> Dict[str, Any]:
    """Generate individual dashboard data"""
    try:
        dashboard = {
            'participant_id': participant_id,
            'current_needs_profile': {},
            'needs_trends': {},
            'active_interventions': [],
            'progress_metrics': {},
            'recommendations': [],
            'privacy_level': privacy_level
        }
        
        # Get current needs assessment (would be from recent analysis)
        # This would integrate with actual stored assessment data
        dashboard['current_needs_profile'] = {
            'certainty': {'score': 0.7, 'level': 'fulfilled', 'trend': 'stable'},
            'variety': {'score': 0.4, 'level': 'lacking', 'trend': 'declining'},
            'significance': {'score': 0.8, 'level': 'fulfilled', 'trend': 'improving'},
            'connection': {'score': 0.6, 'level': 'moderate', 'trend': 'stable'},
            'growth': {'score': 0.5, 'level': 'moderate', 'trend': 'improving'},
            'contribution': {'score': 0.9, 'level': 'overemphasized', 'trend': 'stable'}
        }
        
        # Generate trend data
        dashboard['needs_trends'] = await _generate_individual_trends(participant_id, time_range)
        
        # Get active interventions
        dashboard['active_interventions'] = await _get_active_interventions(participant_id)
        
        # Calculate progress metrics
        dashboard['progress_metrics'] = await _calculate_individual_progress_metrics(participant_id)
        
        # Generate recommendations
        dashboard['recommendations'] = await _generate_individual_recommendations(participant_id)
        
        return dashboard
        
    except Exception as e:
        logger.error("Individual dashboard generation failed", error=str(e))
        return {'error': str(e)}

async def _generate_team_dashboard(team_id: str, time_range: str, 
                                 include_individuals: bool) -> Dict[str, Any]:
    """Generate team dashboard data"""
    try:
        dashboard = {
            'team_id': team_id,
            'team_needs_profile': {},
            'team_dynamics': {},
            'collective_trends': {},
            'team_interventions': [],
            'individual_summaries': [],
            'risk_indicators': [],
            'success_metrics': {}
        }
        
        # Get team needs profile
        dashboard['team_needs_profile'] = {
            'certainty': {'average_score': 0.65, 'distribution': [0.2, 0.3, 0.3, 0.2], 'imbalances': 2},
            'variety': {'average_score': 0.45, 'distribution': [0.4, 0.3, 0.2, 0.1], 'imbalances': 3},
            'significance': {'average_score': 0.75, 'distribution': [0.1, 0.2, 0.4, 0.3], 'imbalances': 1},
            'connection': {'average_score': 0.55, 'distribution': [0.3, 0.2, 0.3, 0.2], 'imbalances': 2},
            'growth': {'average_score': 0.6, 'distribution': [0.2, 0.2, 0.4, 0.2], 'imbalances': 1},
            'contribution': {'average_score': 0.8, 'distribution': [0.1, 0.1, 0.3, 0.5], 'imbalances': 1}
        }
        
        # Get team dynamics
        dashboard['team_dynamics'] = {
            'collaboration_level': 0.7,
            'innovation_capacity': 0.6,
            'stability_level': 0.8,
            'conflict_potential': 0.3,
            'growth_orientation': 0.65,
            'purpose_alignment': 0.85
        }
        
        # Generate collective trends
        dashboard['collective_trends'] = await _generate_team_trends(team_id, time_range)
        
        # Get team interventions
        dashboard['team_interventions'] = await _get_team_interventions(team_id)
        
        # Include individual summaries if requested
        if include_individuals:
            dashboard['individual_summaries'] = await _get_individual_summaries(team_id)
        
        # Identify risk indicators
        dashboard['risk_indicators'] = await _identify_team_risk_indicators(team_id)
        
        return dashboard
        
    except Exception as e:
        logger.error("Team dashboard generation failed", error=str(e))
        return {'error': str(e)}

async def _generate_trends_analysis(scope: str, entity_id: str, time_range: str, 
                                  needs_filter: List[str]) -> Dict[str, Any]:
    """Generate trends analysis data"""
    try:
        trends = {
            'scope': scope,
            'entity_id': entity_id,
            'time_range': time_range,
            'trend_data': {},
            'key_insights': [],
            'predictions': {}
        }
        
        # Generate sample trend data (would be from actual historical data)
        time_points = _generate_time_points(time_range)
        
        needs_to_analyze = needs_filter if needs_filter else ['certainty', 'variety', 'significance', 'connection', 'growth', 'contribution']
        
        for need in needs_to_analyze:
            trends['trend_data'][need] = {
                'time_series': [
                    {'date': point, 'value': 0.5 + (i * 0.05) + ((-1) ** i * 0.1)}
                    for i, point in enumerate(time_points)
                ],
                'trend_direction': 'improving',
                'volatility': 'low',
                'correlation_with_interventions': 0.7
            }
        
        # Generate key insights
        trends['key_insights'] = [
            "Connection needs have shown consistent improvement over the past month",
            "Variety needs remain below optimal levels despite interventions",
            "Strong correlation between growth interventions and overall satisfaction"
        ]
        
        # Generate predictions
        trends['predictions'] = {
            'next_30_days': {
                'expected_improvements': ['connection', 'growth'],
                'areas_of_concern': ['variety'],
                'intervention_recommendations': ['Increase variety-focused activities']
            }
        }
        
        return trends
        
    except Exception as e:
        logger.error("Trends analysis generation failed", error=str(e))
        return {'error': str(e)}

async def _generate_intervention_progress_data(intervention_id: str) -> Dict[str, Any]:
    """Generate intervention progress visualization data"""
    try:
        progress = {
            'intervention_id': intervention_id,
            'status': 'in_progress',
            'completion_percentage': 65,
            'timeline': {},
            'milestones': [],
            'effectiveness_indicators': {},
            'participant_feedback': {},
            'next_steps': []
        }
        
        # Get timeline data
        progress['timeline'] = {
            'start_date': (datetime.utcnow() - timedelta(days=30)).isoformat(),
            'expected_end_date': (datetime.utcnow() + timedelta(days=20)).isoformat(),
            'current_phase': 'Implementation',
            'phases_completed': ['Setup', 'Initial Implementation'],
            'phases_remaining': ['Full Implementation', 'Review']
        }
        
        # Get milestones
        progress['milestones'] = [
            {'name': 'Initial Assessment', 'date': (datetime.utcnow() - timedelta(days=28)).isoformat(), 'status': 'completed'},
            {'name': 'Resource Setup', 'date': (datetime.utcnow() - timedelta(days=25)).isoformat(), 'status': 'completed'},
            {'name': 'First Check-in', 'date': (datetime.utcnow() - timedelta(days=14)).isoformat(), 'status': 'completed'},
            {'name': 'Mid-point Review', 'date': datetime.utcnow().isoformat(), 'status': 'in_progress'},
            {'name': 'Final Assessment', 'date': (datetime.utcnow() + timedelta(days=18)).isoformat(), 'status': 'pending'}
        ]
        
        # Get effectiveness indicators
        progress['effectiveness_indicators'] = {
            'engagement_level': {'current': 0.8, 'target': 0.7, 'trend': 'improving'},
            'skill_development': {'current': 0.6, 'target': 0.8, 'trend': 'improving'},
            'satisfaction': {'current': 0.75, 'target': 0.7, 'trend': 'stable'}
        }
        
        return progress
        
    except Exception as e:
        logger.error("Intervention progress data generation failed", error=str(e))
        return {'error': str(e)}

async def _generate_comprehensive_report(scope: str, entity_id: str, time_range: str,
                                       include_interventions: bool, privacy_level: str) -> Dict[str, Any]:
    """Generate comprehensive human needs report"""
    try:
        report = {
            'scope': scope,
            'entity_id': entity_id,
            'time_range': time_range,
            'privacy_level': privacy_level,
            'executive_summary': {},
            'detailed_analysis': {},
            'intervention_summary': {},
            'recommendations': [],
            'appendices': {}
        }
        
        # Generate executive summary
        report['executive_summary'] = {
            'overall_health_score': 0.72,
            'key_strengths': ['Strong contribution orientation', 'Good significance fulfillment'],
            'primary_concerns': ['Variety needs underserved', 'Connection gaps in some areas'],
            'intervention_effectiveness': 0.68,
            'trend_direction': 'improving'
        }
        
        # Generate detailed analysis
        report['detailed_analysis'] = {
            'needs_breakdown': await _generate_detailed_needs_analysis(scope, entity_id),
            'trend_analysis': await _generate_trends_analysis(scope, entity_id, time_range, []),
            'risk_assessment': await _generate_risk_assessment(scope, entity_id),
            'comparative_analysis': await _generate_comparative_analysis(scope, entity_id)
        }
        
        # Include intervention summary if requested
        if include_interventions:
            report['intervention_summary'] = await _generate_intervention_summary(scope, entity_id)
        
        # Generate recommendations
        report['recommendations'] = await _generate_comprehensive_recommendations(scope, entity_id)
        
        return report
        
    except Exception as e:
        logger.error("Comprehensive report generation failed", error=str(e))
        return {'error': str(e)}

# Access control helper functions

async def _check_dashboard_access(current_user: Dict[str, Any], participant_id: str, 
                                privacy_level: str) -> bool:
    """Check if user has access to individual dashboard"""
    try:
        # Self-access is always allowed
        if current_user.get('id') == participant_id:
            return True
        
        # Manager access based on privacy level
        if privacy_level in ['team', 'manager'] and current_user.get('role') in ['manager', 'admin']:
            return True
        
        # Admin access
        if current_user.get('role') == 'admin':
            return True
        
        return False
        
    except Exception as e:
        logger.error("Dashboard access check failed", error=str(e))
        return False

async def _check_team_dashboard_access(current_user: Dict[str, Any], team_id: str) -> bool:
    """Check if user has access to team dashboard"""
    try:
        # Team member access
        user_teams = current_user.get('teams', [])
        if team_id in user_teams:
            return True
        
        # Manager/Admin access
        if current_user.get('role') in ['manager', 'admin']:
            return True
        
        return False
        
    except Exception as e:
        logger.error("Team dashboard access check failed", error=str(e))
        return False

async def _check_analytics_access(current_user: Dict[str, Any], scope: str, entity_id: str) -> bool:
    """Check if user has access to analytics"""
    try:
        if scope == 'individual':
            return await _check_dashboard_access(current_user, entity_id, 'team')
        elif scope == 'team':
            return await _check_team_dashboard_access(current_user, entity_id)
        elif scope == 'organization':
            return current_user.get('role') in ['admin', 'hr']
        
        return False
        
    except Exception as e:
        logger.error("Analytics access check failed", error=str(e))
        return False

async def _check_intervention_access(current_user: Dict[str, Any], intervention_id: str) -> bool:
    """Check if user has access to intervention data"""
    try:
        # This would check against actual intervention ownership/participation
        return True  # Simplified for now
        
    except Exception as e:
        logger.error("Intervention access check failed", error=str(e))
        return False

async def _check_privacy_settings_access(current_user: Dict[str, Any], participant_id: str) -> bool:
    """Check if user can manage privacy settings"""
    try:
        # Only self or admin can manage privacy settings
        return (current_user.get('id') == participant_id or 
                current_user.get('role') == 'admin')
        
    except Exception as e:
        logger.error("Privacy settings access check failed", error=str(e))
        return False

async def _check_report_access(current_user: Dict[str, Any], scope: str, entity_id: str) -> bool:
    """Check if user can generate reports"""
    try:
        return await _check_analytics_access(current_user, scope, entity_id)
        
    except Exception as e:
        logger.error("Report access check failed", error=str(e))
        return False

# Utility functions

def _generate_time_points(time_range: str) -> List[str]:
    """Generate time points for trend analysis"""
    try:
        if time_range.endswith('d'):
            days = int(time_range[:-1])
            points = []
            for i in range(0, days, max(1, days // 20)):  # Max 20 points
                date = datetime.utcnow() - timedelta(days=days-i)
                points.append(date.isoformat())
            return points
        else:
            # Default to 30 days
            return [(datetime.utcnow() - timedelta(days=30-i)).isoformat() for i in range(0, 30, 2)]
            
    except Exception as e:
        logger.error("Time points generation failed", error=str(e))
        return []

# Placeholder functions for data retrieval (would be implemented with actual data sources)

async def _generate_individual_trends(participant_id: str, time_range: str) -> Dict[str, Any]:
    """Generate individual trend data"""
    return {'placeholder': 'Individual trends data would be generated here'}

async def _get_active_interventions(participant_id: str) -> List[Dict[str, Any]]:
    """Get active interventions for participant"""
    return [{'id': 'int_1', 'name': 'Variety Enhancement Program', 'progress': 0.6}]

async def _calculate_individual_progress_metrics(participant_id: str) -> Dict[str, Any]:
    """Calculate individual progress metrics"""
    return {'overall_improvement': 0.15, 'needs_balanced': 4, 'interventions_completed': 2}

async def _generate_individual_recommendations(participant_id: str) -> List[str]:
    """Generate individual recommendations"""
    return ['Focus on variety-enhancing activities', 'Continue current growth trajectory']

async def _generate_team_trends(team_id: str, time_range: str) -> Dict[str, Any]:
    """Generate team trend data"""
    return {'placeholder': 'Team trends data would be generated here'}

async def _get_team_interventions(team_id: str) -> List[Dict[str, Any]]:
    """Get team interventions"""
    return [{'id': 'team_int_1', 'name': 'Team Connection Building', 'participants': 8}]

async def _get_individual_summaries(team_id: str) -> List[Dict[str, Any]]:
    """Get individual summaries for team members"""
    return [{'participant_id': 'p1', 'overall_score': 0.7, 'primary_need': 'variety'}]

async def _identify_team_risk_indicators(team_id: str) -> List[Dict[str, Any]]:
    """Identify team risk indicators"""
    return [{'type': 'variety_deficit', 'severity': 'moderate', 'affected_members': 3}]

async def _get_privacy_settings(participant_id: str) -> Dict[str, Any]:
    """Get privacy settings for participant"""
    return {
        'dashboard_visibility': 'team',
        'trend_sharing': 'manager',
        'intervention_visibility': 'private',
        'analytics_participation': True
    }

async def _update_privacy_settings(participant_id: str, settings: Dict[str, Any]) -> Dict[str, Any]:
    """Update privacy settings for participant"""
    # Would update actual privacy settings in database
    return settings

async def _generate_detailed_needs_analysis(scope: str, entity_id: str) -> Dict[str, Any]:
    """Generate detailed needs analysis"""
    return {'placeholder': 'Detailed needs analysis would be generated here'}

async def _generate_risk_assessment(scope: str, entity_id: str) -> Dict[str, Any]:
    """Generate risk assessment"""
    return {'overall_risk': 'moderate', 'key_risks': ['variety_deficit', 'connection_gaps']}

async def _generate_comparative_analysis(scope: str, entity_id: str) -> Dict[str, Any]:
    """Generate comparative analysis"""
    return {'benchmark_comparison': 'above_average', 'peer_ranking': 'top_25_percent'}

async def _generate_intervention_summary(scope: str, entity_id: str) -> Dict[str, Any]:
    """Generate intervention summary"""
    return {'total_interventions': 5, 'success_rate': 0.8, 'avg_effectiveness': 0.72}

async def _generate_comprehensive_recommendations(scope: str, entity_id: str) -> List[Dict[str, Any]]:
    """Generate comprehensive recommendations"""
    return [
        {'priority': 'high', 'category': 'variety', 'recommendation': 'Implement job rotation program'},
        {'priority': 'medium', 'category': 'connection', 'recommendation': 'Enhance team building activities'}
    ]

# Error handlers
@human_needs_dashboard_bp.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 'Bad request',
        'details': str(error)
    }), 400

@human_needs_dashboard_bp.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'success': False,
        'error': 'Unauthorized'
    }), 401

@human_needs_dashboard_bp.errorhandler(403)
def forbidden(error):
    return jsonify({
        'success': False,
        'error': 'Forbidden'
    }), 403

@human_needs_dashboard_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Not found'
    }), 404

@human_needs_dashboard_bp.errorhandler(429)
def rate_limit_exceeded(error):
    return jsonify({
        'success': False,
        'error': 'Rate limit exceeded'
    }), 429

@human_needs_dashboard_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500