"""
AI Conductor Routes for Intelligence OS
Provides API endpoints for AI orchestration and analysis
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
import structlog

from ..services.ai_conductor import ai_conductor
from ..security.auth import require_auth
from ..security.validation import validate_request_data
from ..security.rate_limiting import rate_limit

logger = structlog.get_logger(__name__)

# Create blueprint
ai_conductor_bp = Blueprint('ai_conductor', __name__, url_prefix='/api/ai-conductor')

@ai_conductor_bp.route('/analyze', methods=['POST'])
@require_auth
@rate_limit(requests_per_minute=10)
@validate_request_data({
    'transcript': {'type': 'string', 'required': True, 'min_length': 10},
    'meeting_title': {'type': 'string', 'required': False},
    'participants': {'type': 'list', 'required': False},
    'meeting_id': {'type': 'string', 'required': False},
    'transcript_id': {'type': 'string', 'required': False},
    'organization_context': {'type': 'dict', 'required': False},
    'organization_history': {'type': 'dict', 'required': False},
    'team_context': {'type': 'dict', 'required': False},
    'available_resources': {'type': 'dict', 'required': False}
})
async def start_analysis():
    """Start a comprehensive AI analysis session"""
    try:
        data = request.get_json()
        
        # Prepare input data for analysis
        input_data = {
            'transcript': data['transcript'],
            'meeting_title': data.get('meeting_title', 'Untitled Meeting'),
            'participants': data.get('participants', []),
            'organization_context': data.get('organization_context', {}),
            'organization_history': data.get('organization_history', {}),
            'team_context': data.get('team_context', {}),
            'available_resources': data.get('available_resources', {})
        }
        
        # Start analysis session
        session = await ai_conductor.start_analysis_session(
            meeting_id=data.get('meeting_id'),
            transcript_id=data.get('transcript_id'),
            input_data=input_data
        )
        
        logger.info("Analysis session started via API",
                   session_id=session.id,
                   meeting_id=data.get('meeting_id'),
                   transcript_length=len(data['transcript']))
        
        return jsonify({
            'success': True,
            'session_id': session.id,
            'status': session.status.value,
            'tasks_created': len(session.tasks),
            'estimated_completion_time': '5-10 minutes',
            'message': 'Analysis session started successfully'
        }), 202
        
    except Exception as e:
        logger.error("Failed to start analysis session", error=str(e))
        return jsonify({
            'success': False,
            'error': 'Failed to start analysis session',
            'details': str(e)
        }), 500

@ai_conductor_bp.route('/session/<session_id>/status', methods=['GET'])
@require_auth
@rate_limit(requests_per_minute=30)
async def get_session_status(session_id: str):
    """Get the status of an analysis session"""
    try:
        status = await ai_conductor.get_session_status(session_id)
        
        if not status:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
        
        return jsonify({
            'success': True,
            'session': status
        }), 200
        
    except Exception as e:
        logger.error("Failed to get session status", session_id=session_id, error=str(e))
        return jsonify({
            'success': False,
            'error': 'Failed to get session status',
            'details': str(e)
        }), 500

@ai_conductor_bp.route('/session/<session_id>/results', methods=['GET'])
@require_auth
@rate_limit(requests_per_minute=20)
async def get_session_results(session_id: str):
    """Get the results of a completed analysis session"""
    try:
        results = await ai_conductor.get_session_results(session_id)
        
        if not results:
            return jsonify({
                'success': False,
                'error': 'Session not found or not completed'
            }), 404
        
        return jsonify({
            'success': True,
            'results': results
        }), 200
        
    except Exception as e:
        logger.error("Failed to get session results", session_id=session_id, error=str(e))
        return jsonify({
            'success': False,
            'error': 'Failed to get session results',
            'details': str(e)
        }), 500

@ai_conductor_bp.route('/status', methods=['GET'])
@require_auth
@rate_limit(requests_per_minute=60)
async def get_conductor_status():
    """Get overall AI Conductor status and metrics"""
    try:
        status = await ai_conductor.get_conductor_status()
        
        return jsonify({
            'success': True,
            'conductor': status
        }), 200
        
    except Exception as e:
        logger.error("Failed to get conductor status", error=str(e))
        return jsonify({
            'success': False,
            'error': 'Failed to get conductor status',
            'details': str(e)
        }), 500

@ai_conductor_bp.route('/performers', methods=['GET'])
@require_auth
@rate_limit(requests_per_minute=30)
async def get_performers_info():
    """Get information about AI performers"""
    try:
        performers_info = {}
        
        # Get status from each AI performer
        for performer_id, ai_performer in ai_conductor.ai_performers.items():
            performers_info[performer_id] = await ai_performer.get_status()
        
        return jsonify({
            'success': True,
            'performers': performers_info
        }), 200
        
    except Exception as e:
        logger.error("Failed to get performers info", error=str(e))
        return jsonify({
            'success': False,
            'error': 'Failed to get performers info',
            'details': str(e)
        }), 500

@ai_conductor_bp.route('/sessions', methods=['GET'])
@require_auth
@rate_limit(requests_per_minute=30)
async def list_active_sessions():
    """List all active analysis sessions"""
    try:
        sessions = []
        
        for session_id, session in ai_conductor.active_sessions.items():
            sessions.append({
                'session_id': session.id,
                'status': session.status.value,
                'meeting_id': session.meeting_id,
                'transcript_id': session.transcript_id,
                'start_time': session.start_time.isoformat(),
                'tasks_total': len(session.tasks),
                'tasks_completed': sum(1 for t in session.tasks if t.status.value == 'completed'),
                'overall_confidence': session.overall_confidence
            })
        
        return jsonify({
            'success': True,
            'active_sessions': sessions,
            'total_sessions': len(sessions)
        }), 200
        
    except Exception as e:
        logger.error("Failed to list active sessions", error=str(e))
        return jsonify({
            'success': False,
            'error': 'Failed to list active sessions',
            'details': str(e)
        }), 500

@ai_conductor_bp.route('/metrics', methods=['GET'])
@require_auth
@rate_limit(requests_per_minute=30)
async def get_performance_metrics():
    """Get AI Conductor performance metrics"""
    try:
        metrics = ai_conductor.performance_metrics.copy()
        
        # Add real-time metrics
        metrics['active_sessions'] = len(ai_conductor.active_sessions)
        metrics['queued_tasks'] = len(ai_conductor.task_queue)
        metrics['completed_sessions_count'] = len(ai_conductor.completed_sessions)
        
        # Calculate additional metrics
        if metrics['total_sessions'] > 0:
            metrics['success_rate'] = metrics['successful_sessions'] / metrics['total_sessions']
            metrics['failure_rate'] = metrics['failed_sessions'] / metrics['total_sessions']
        else:
            metrics['success_rate'] = 0.0
            metrics['failure_rate'] = 0.0
        
        return jsonify({
            'success': True,
            'metrics': metrics,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error("Failed to get performance metrics", error=str(e))
        return jsonify({
            'success': False,
            'error': 'Failed to get performance metrics',
            'details': str(e)
        }), 500

@ai_conductor_bp.route('/session/<session_id>/cancel', methods=['POST'])
@require_auth
@rate_limit(requests_per_minute=10)
async def cancel_session(session_id: str):
    """Cancel an active analysis session"""
    try:
        if session_id not in ai_conductor.active_sessions:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
        
        session = ai_conductor.active_sessions[session_id]
        
        # Cancel all pending tasks
        for task in session.tasks:
            if task.status.value in ['pending', 'assigned', 'processing']:
                task.status = ai_conductor.ProcessingStatus.CANCELLED
                task.end_time = datetime.utcnow()
                task.error_message = 'Session cancelled by user'
        
        # Update session status
        session.status = ai_conductor.ProcessingStatus.CANCELLED
        session.end_time = datetime.utcnow()
        
        logger.info("Analysis session cancelled", session_id=session_id)
        
        return jsonify({
            'success': True,
            'message': 'Session cancelled successfully',
            'session_id': session_id
        }), 200
        
    except Exception as e:
        logger.error("Failed to cancel session", session_id=session_id, error=str(e))
        return jsonify({
            'success': False,
            'error': 'Failed to cancel session',
            'details': str(e)
        }), 500

@ai_conductor_bp.route('/health', methods=['GET'])
@rate_limit(requests_per_minute=120)
async def health_check():
    """Health check endpoint for AI Conductor"""
    try:
        # Check if AI Conductor is initialized
        if not hasattr(ai_conductor, 'performers') or not ai_conductor.performers:
            return jsonify({
                'success': False,
                'status': 'unhealthy',
                'error': 'AI Conductor not properly initialized'
            }), 503
        
        # Check performer status
        unhealthy_performers = []
        for performer_id, performer in ai_conductor.performers.items():
            if performer.status != 'ready':
                unhealthy_performers.append(performer_id)
        
        status = 'healthy' if not unhealthy_performers else 'degraded'
        
        return jsonify({
            'success': True,
            'status': status,
            'performers_count': len(ai_conductor.performers),
            'active_sessions': len(ai_conductor.active_sessions),
            'queued_tasks': len(ai_conductor.task_queue),
            'unhealthy_performers': unhealthy_performers,
            'timestamp': datetime.utcnow().isoformat()
        }), 200 if status == 'healthy' else 206
        
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e)
        }), 503

# Error handlers
@ai_conductor_bp.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 'Bad request',
        'details': str(error)
    }), 400

@ai_conductor_bp.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'success': False,
        'error': 'Unauthorized'
    }), 401

@ai_conductor_bp.errorhandler(403)
def forbidden(error):
    return jsonify({
        'success': False,
        'error': 'Forbidden'
    }), 403

@ai_conductor_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Not found'
    }), 404

@ai_conductor_bp.errorhandler(429)
def rate_limit_exceeded(error):
    return jsonify({
        'success': False,
        'error': 'Rate limit exceeded'
    }), 429

@ai_conductor_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500