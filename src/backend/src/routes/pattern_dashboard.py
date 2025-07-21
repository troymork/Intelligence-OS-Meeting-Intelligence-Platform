"""
Pattern Dashboard API Routes
Provides endpoints for pattern visualization and intervention management dashboard
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import structlog
from ..services.pattern_visualization_service import PatternVisualizationService
from ..services.intervention_management_service import InterventionManagementService
from ..services.predictive_analytics_service import PredictiveAnalyticsService
from ..services.pattern_recognition_engine import PatternRecognitionEngine
from ..security.auth import require_auth
from ..security.validation import validate_json_input
from ..security.rate_limiting import rate_limit

logger = structlog.get_logger(__name__)

# Create blueprint
pattern_dashboard_bp = Blueprint('pattern_dashboard', __name__, url_prefix='/api/pattern-dashboard')

# Initialize services
visualization_service = PatternVisualizationService()
intervention_service = InterventionManagementService()
predictive_service = PredictiveAnalyticsService()
pattern_engine = PatternRecognitionEngine()

@pattern_dashboard_bp.route('/overview', methods=['GET'])
@require_auth
@rate_limit(limit=100, window=3600)  # 100 requests per hour
def get_dashboard_overview():
    """
    Get comprehensive dashboard overview with key metrics and visualizations
    """
    try:
        logger.info("Generating dashboard overview")
        
        # Get pattern summary
        pattern_summary = _get_pattern_summary()
        
        # Get intervention summary
        intervention_summary = _get_intervention_summary()
        
        # Get predictive insights
        predictive_insights = predictive_service.get_predictive_dashboard_data()
        
        # Get recent trends
        recent_trends = _get_recent_trends()
        
        # Get alerts and notifications
        alerts = _get_dashboard_alerts()
        
        overview = {
            'pattern_summary': pattern_summary,
            'intervention_summary': intervention_summary,
            'predictive_insights': predictive_insights,
            'recent_trends': recent_trends,
            'alerts': alerts,
            'last_updated': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'status': 'success',
            'data': overview,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error("Dashboard overview generation failed", error=str(e))
        return jsonify({
            'error': 'Dashboard overview generation failed',
            'details': str(e),
            'status': 'error'
        }), 500

@pattern_dashboard_bp.route('/visualizations/pattern-timeline', methods=['POST'])
@require_auth
@rate_limit(limit=50, window=3600)  # 50 requests per hour
@validate_json_input
def create_pattern_timeline():
    """
    Create pattern frequency timeline visualization
    
    Expected JSON payload:
    {
        "pattern_data": [...],
        "time_range": {
            "start": "ISO datetime",
            "end": "ISO datetime"
        }
    }
    """
    try:
        data = request.get_json()
        pattern_data = data.get('pattern_data', [])
        time_range_data = data.get('time_range', {})
        
        if not pattern_data:
            return jsonify({
                'error': 'pattern_data is required',
                'status': 'error'
            }), 400
        
        # Parse time range
        start_date = datetime.fromisoformat(time_range_data.get('start', (datetime.utcnow() - timedelta(days=30)).isoformat()))
        end_date = datetime.fromisoformat(time_range_data.get('end', datetime.utcnow().isoformat()))
        
        # Create visualization
        chart_data = visualization_service.create_pattern_timeline_visualization(
            pattern_data, (start_date, end_date)
        )
        
        # Serialize chart data
        serialized_data = {
            'labels': chart_data.labels,
            'datasets': chart_data.datasets,
            'metadata': chart_data.metadata,
            'last_updated': chart_data.last_updated.isoformat(),
            'data_quality_score': chart_data.data_quality_score
        }
        
        return jsonify({
            'status': 'success',
            'data': serialized_data,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error("Pattern timeline visualization creation failed", error=str(e))
        return jsonify({
            'error': 'Timeline visualization creation failed',
            'details': str(e),
            'status': 'error'
        }), 500

@pattern_dashboard_bp.route('/visualizations/concept-network', methods=['POST'])
@require_auth
@rate_limit(limit=30, window=3600)  # 30 requests per hour
@validate_json_input
def create_concept_network():
    """
    Create concept relationship network visualization
    
    Expected JSON payload:
    {
        "concepts": [...],
        "relationships": [...]
    }
    """
    try:
        data = request.get_json()
        concepts = data.get('concepts', [])
        relationships = data.get('relationships', [])
        
        if not concepts:
            return jsonify({
                'error': 'concepts data is required',
                'status': 'error'
            }), 400
        
        # Create network visualization
        network_data = visualization_service.create_concept_network_visualization(
            concepts, relationships
        )
        
        # Serialize network data
        serialized_data = {
            'nodes': network_data.nodes,
            'edges': network_data.edges,
            'layout_config': network_data.layout_config,
            'interaction_config': network_data.interaction_config,
            'styling_config': network_data.styling_config
        }
        
        return jsonify({
            'status': 'success',
            'data': serialized_data,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error("Concept network visualization creation failed", error=str(e))
        return jsonify({
            'error': 'Network visualization creation failed',
            'details': str(e),
            'status': 'error'
        }), 500

@pattern_dashboard_bp.route('/interventions/recommendations', methods=['POST'])
@require_auth
@rate_limit(limit=20, window=3600)  # 20 requests per hour
@validate_json_input
def get_intervention_recommendations():
    """
    Get intervention recommendations based on detected patterns
    
    Expected JSON payload:
    {
        "detected_patterns": [...]
    }
    """
    try:
        data = request.get_json()
        detected_patterns = data.get('detected_patterns', [])
        
        if not detected_patterns:
            return jsonify({
                'error': 'detected_patterns is required',
                'status': 'error'
            }), 400
        
        # Generate recommendations
        recommendations = intervention_service.generate_intervention_recommendations(detected_patterns)
        
        # Serialize recommendations
        serialized_recommendations = []
        for rec in recommendations:
            serialized_recommendations.append({
                'id': rec.id,
                'target_pattern_id': rec.target_pattern_id,
                'recommended_intervention_type': rec.recommended_intervention_type.value,
                'rationale': rec.rationale,
                'expected_effectiveness': rec.expected_effectiveness,
                'implementation_complexity': rec.implementation_complexity,
                'resource_estimate': rec.resource_estimate,
                'timeline_estimate': rec.timeline_estimate,
                'success_probability': rec.success_probability,
                'alternative_approaches': rec.alternative_approaches,
                'similar_case_studies': rec.similar_case_studies,
                'confidence_score': rec.confidence_score
            })
        
        return jsonify({
            'status': 'success',
            'data': {
                'recommendations': serialized_recommendations,
                'total_count': len(serialized_recommendations)
            },
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error("Intervention recommendations generation failed", error=str(e))
        return jsonify({
            'error': 'Intervention recommendations generation failed',
            'details': str(e),
            'status': 'error'
        }), 500

@pattern_dashboard_bp.route('/interventions/<intervention_id>/effectiveness', methods=['GET'])
@require_auth
@rate_limit(limit=100, window=3600)  # 100 requests per hour
def track_intervention_effectiveness(intervention_id):
    """
    Track effectiveness of a specific intervention
    """
    try:
        # Track intervention effectiveness
        effectiveness_data = intervention_service.track_intervention_effectiveness(intervention_id)
        
        return jsonify({
            'status': 'success',
            'data': effectiveness_data,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error("Intervention effectiveness tracking failed", error=str(e))
        return jsonify({
            'error': 'Intervention effectiveness tracking failed',
            'details': str(e),
            'status': 'error'
        }), 500

@pattern_dashboard_bp.route('/predictions/pattern-forecast', methods=['POST'])
@require_auth
@rate_limit(limit=10, window=3600)  # 10 requests per hour (expensive operation)
@validate_json_input
def generate_pattern_forecast():
    """
    Generate forecast for pattern frequency
    
    Expected JSON payload:
    {
        "pattern_id": "string",
        "forecast_horizon": "short_term|medium_term|long_term|strategic"
    }
    """
    try:
        data = request.get_json()
        pattern_id = data.get('pattern_id')
        forecast_horizon_str = data.get('forecast_horizon', 'medium_term')
        
        if not pattern_id:
            return jsonify({
                'error': 'pattern_id is required',
                'status': 'error'
            }), 400
        
        # Validate forecast horizon
        from ..services.predictive_analytics_service import ForecastHorizon
        try:
            forecast_horizon = ForecastHorizon(forecast_horizon_str)
        except ValueError:
            return jsonify({
                'error': f'Invalid forecast_horizon. Must be one of: {[h.value for h in ForecastHorizon]}',
                'status': 'error'
            }), 400
        
        # Generate forecast
        forecast_result = predictive_service.generate_pattern_frequency_forecast(
            pattern_id, forecast_horizon
        )
        
        # Serialize forecast result
        serialized_result = predictive_service._serialize_forecast_result(forecast_result)
        
        return jsonify({
            'status': 'success',
            'data': serialized_result,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error("Pattern forecast generation failed", error=str(e))
        return jsonify({
            'error': 'Pattern forecast generation failed',
            'details': str(e),
            'status': 'error'
        }), 500

@pattern_dashboard_bp.route('/analytics/anomalies', methods=['POST'])
@require_auth
@rate_limit(limit=50, window=3600)  # 50 requests per hour
@validate_json_input
def detect_anomalies():
    """
    Detect anomalies in organizational patterns
    
    Expected JSON payload:
    {
        "variable_name": "string",
        "detection_window_days": 30
    }
    """
    try:
        data = request.get_json()
        variable_name = data.get('variable_name')
        detection_window_days = data.get('detection_window_days', 30)
        
        if not variable_name:
            return jsonify({
                'error': 'variable_name is required',
                'status': 'error'
            }), 400
        
        # Detect anomalies
        anomalies = predictive_service.detect_anomalies(variable_name, detection_window_days)
        
        # Serialize anomalies
        serialized_anomalies = []
        for anomaly in anomalies:
            serialized_anomalies.append({
                'id': anomaly.id,
                'timestamp': anomaly.timestamp.isoformat(),
                'variable_name': anomaly.variable_name,
                'observed_value': anomaly.observed_value,
                'expected_value': anomaly.expected_value,
                'anomaly_score': anomaly.anomaly_score,
                'anomaly_type': anomaly.anomaly_type,
                'severity': anomaly.severity,
                'potential_causes': anomaly.potential_causes,
                'impact_assessment': anomaly.impact_assessment,
                'recommended_actions': anomaly.recommended_actions
            })
        
        return jsonify({
            'status': 'success',
            'data': {
                'anomalies': serialized_anomalies,
                'total_count': len(serialized_anomalies),
                'detection_window_days': detection_window_days
            },
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error("Anomaly detection failed", error=str(e))
        return jsonify({
            'error': 'Anomaly detection failed',
            'details': str(e),
            'status': 'error'
        }), 500

@pattern_dashboard_bp.route('/dashboards', methods=['POST'])
@require_auth
@rate_limit(limit=20, window=3600)  # 20 requests per hour
@validate_json_input
def create_dashboard():
    """
    Create a new dashboard from template
    
    Expected JSON payload:
    {
        "template": "executive_overview|learning_analytics|intervention_management|predictive_insights",
        "custom_config": {...} (optional)
    }
    """
    try:
        data = request.get_json()
        template = data.get('template')
        custom_config = data.get('custom_config')
        user_id = request.user_id  # Assuming user_id is available from auth
        
        if not template:
            return jsonify({
                'error': 'template is required',
                'status': 'error'
            }), 400
        
        # Create dashboard
        dashboard = visualization_service.create_dashboard(template, user_id, custom_config)
        
        # Serialize dashboard
        serialized_dashboard = {
            'id': dashboard.id,
            'name': dashboard.name,
            'description': dashboard.description,
            'category': dashboard.category.value,
            'widgets': [_serialize_widget(w) for w in dashboard.widgets],
            'layout_config': dashboard.layout_config,
            'auto_refresh_enabled': dashboard.auto_refresh_enabled,
            'refresh_interval': dashboard.refresh_interval,
            'created_by': dashboard.created_by,
            'created_at': dashboard.created_at.isoformat(),
            'last_modified': dashboard.last_modified.isoformat()
        }
        
        return jsonify({
            'status': 'success',
            'data': serialized_dashboard,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error("Dashboard creation failed", error=str(e))
        return jsonify({
            'error': 'Dashboard creation failed',
            'details': str(e),
            'status': 'error'
        }), 500

@pattern_dashboard_bp.route('/dashboards/<dashboard_id>', methods=['GET'])
@require_auth
@rate_limit(limit=200, window=3600)  # 200 requests per hour
def get_dashboard(dashboard_id):
    """
    Get dashboard configuration and data
    """
    try:
        dashboard = visualization_service.dashboards.get(dashboard_id)
        
        if not dashboard:
            return jsonify({
                'error': 'Dashboard not found',
                'status': 'error'
            }), 404
        
        # Check access permissions
        user_id = getattr(request, 'user_id', None)
        if user_id not in dashboard.access_permissions:
            return jsonify({
                'error': 'Access denied',
                'status': 'error'
            }), 403
        
        # Serialize dashboard with current data
        serialized_dashboard = {
            'id': dashboard.id,
            'name': dashboard.name,
            'description': dashboard.description,
            'category': dashboard.category.value,
            'widgets': [_serialize_widget_with_data(w) for w in dashboard.widgets],
            'layout_config': dashboard.layout_config,
            'auto_refresh_enabled': dashboard.auto_refresh_enabled,
            'refresh_interval': dashboard.refresh_interval,
            'created_by': dashboard.created_by,
            'created_at': dashboard.created_at.isoformat(),
            'last_modified': dashboard.last_modified.isoformat()
        }
        
        return jsonify({
            'status': 'success',
            'data': serialized_dashboard,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error("Dashboard retrieval failed", error=str(e))
        return jsonify({
            'error': 'Dashboard retrieval failed',
            'details': str(e),
            'status': 'error'
        }), 500

# Helper functions
def _get_pattern_summary():
    """Get summary of detected patterns"""
    try:
        patterns = list(pattern_engine.detected_patterns.values())
        
        # Calculate summary statistics
        total_patterns = len(patterns)
        high_severity_patterns = len([p for p in patterns if p.severity.value in ['high', 'critical']])
        recent_patterns = len([p for p in patterns if p.last_occurrence > datetime.utcnow() - timedelta(days=7)])
        
        # Pattern type distribution
        pattern_types = {}
        for pattern in patterns:
            pattern_type = pattern.pattern_type.value
            pattern_types[pattern_type] = pattern_types.get(pattern_type, 0) + 1
        
        return {
            'total_patterns': total_patterns,
            'high_severity_patterns': high_severity_patterns,
            'recent_patterns': recent_patterns,
            'pattern_type_distribution': pattern_types,
            'average_confidence': sum(p.confidence_score for p in patterns) / len(patterns) if patterns else 0
        }
        
    except Exception as e:
        logger.error("Pattern summary generation failed", error=str(e))
        return {'error': 'Pattern summary generation failed'}

def _get_intervention_summary():
    """Get summary of interventions"""
    try:
        interventions = list(intervention_service.intervention_executions.values())
        recommendations = list(intervention_service.intervention_recommendations.values())
        
        # Calculate summary statistics
        total_interventions = len(interventions)
        active_interventions = len([i for i in interventions if i.status.value in ['in_progress', 'monitoring']])
        completed_interventions = len([i for i in interventions if i.status.value == 'completed'])
        pending_recommendations = len(recommendations)
        
        return {
            'total_interventions': total_interventions,
            'active_interventions': active_interventions,
            'completed_interventions': completed_interventions,
            'pending_recommendations': pending_recommendations,
            'success_rate': completed_interventions / total_interventions if total_interventions > 0 else 0
        }
        
    except Exception as e:
        logger.error("Intervention summary generation failed", error=str(e))
        return {'error': 'Intervention summary generation failed'}

def _get_recent_trends():
    """Get recent trend information"""
    try:
        trends = list(predictive_service.trend_analyses.values())
        recent_trends = [t for t in trends if hasattr(t, 'created_at')]  # Filter recent trends
        
        trend_summary = {
            'improving_trends': len([t for t in recent_trends if t.trend_direction == 'increasing']),
            'declining_trends': len([t for t in recent_trends if t.trend_direction == 'decreasing']),
            'stable_trends': len([t for t in recent_trends if t.trend_direction == 'stable']),
            'total_trends_analyzed': len(recent_trends)
        }
        
        return trend_summary
        
    except Exception as e:
        logger.error("Recent trends generation failed", error=str(e))
        return {'error': 'Recent trends generation failed'}

def _get_dashboard_alerts():
    """Get dashboard alerts and notifications"""
    try:
        alerts = []
        
        # Check for critical patterns
        patterns = list(pattern_engine.detected_patterns.values())
        critical_patterns = [p for p in patterns if p.severity.value == 'critical']
        
        for pattern in critical_patterns[:5]:  # Top 5 critical patterns
            alerts.append({
                'type': 'critical_pattern',
                'title': f'Critical Pattern Detected: {pattern.title}',
                'description': pattern.description[:100] + '...' if len(pattern.description) > 100 else pattern.description,
                'severity': 'critical',
                'timestamp': pattern.last_occurrence.isoformat()
            })
        
        # Check for recent anomalies
        anomalies = list(predictive_service.anomaly_detections.values())
        recent_anomalies = [a for a in anomalies if a.timestamp > datetime.utcnow() - timedelta(days=1)]
        
        for anomaly in recent_anomalies[:3]:  # Top 3 recent anomalies
            alerts.append({
                'type': 'anomaly_detected',
                'title': f'Anomaly Detected in {anomaly.variable_name}',
                'description': f'{anomaly.anomaly_type} anomaly with score {anomaly.anomaly_score:.2f}',
                'severity': anomaly.severity,
                'timestamp': anomaly.timestamp.isoformat()
            })
        
        return alerts[:10]  # Return top 10 alerts
        
    except Exception as e:
        logger.error("Dashboard alerts generation failed", error=str(e))
        return []

def _serialize_widget(widget):
    """Serialize dashboard widget"""
    return {
        'id': widget.id,
        'title': widget.title,
        'description': widget.description,
        'widget_type': widget.widget_type,
        'position': widget.position,
        'is_active': widget.is_active,
        'last_updated': widget.last_updated.isoformat(),
        'update_frequency': widget.update_frequency
    }

def _serialize_widget_with_data(widget):
    """Serialize dashboard widget with current data"""
    serialized = _serialize_widget(widget)
    
    # Add current data if available
    if hasattr(widget, 'data') and widget.data:
        if hasattr(widget.data, 'labels'):  # ChartData
            serialized['data'] = {
                'labels': widget.data.labels,
                'datasets': widget.data.datasets,
                'metadata': widget.data.metadata
            }
        elif hasattr(widget.data, 'nodes'):  # NetworkGraphData
            serialized['data'] = {
                'nodes': widget.data.nodes[:50],  # Limit nodes for performance
                'edges': widget.data.edges[:100],  # Limit edges for performance
                'layout_config': widget.data.layout_config
            }
    
    return serialized