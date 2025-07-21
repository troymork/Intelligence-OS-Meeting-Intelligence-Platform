"""
NLU API Routes for Intelligence OS
Natural Language Understanding endpoints
"""

from flask import Blueprint, request, jsonify, g
from typing import Dict, List, Optional, Any
import logging
import structlog
from datetime import datetime

from ..services.nlu_service import nlu_service
from ..services.conversation_service import conversation_service
from ..services.intent_service import intent_service
from ..security.auth import auth_manager
from ..security.rate_limiting import rate_limiter

logger = structlog.get_logger(__name__)

# Create blueprint
nlu_bp = Blueprint('nlu', __name__, url_prefix='/api/nlu')

@nlu_bp.route('/process', methods=['POST'])
@auth_manager.require_user_or_admin()
@rate_limiter.limit("30 per minute")
def process_text():
    """Process text for NLU analysis"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'error': 'missing_text',
                'message': 'Text is required for NLU processing'
            }), 400
        
        text = data['text']
        session_id = data.get('session_id')
        user_id = g.current_user_id
        meeting_context = data.get('meeting_context', {})
        
        # Process text with NLU service
        result = asyncio.run(nlu_service.process_text(
            text=text,
            session_id=session_id,
            user_id=user_id,
            meeting_context=meeting_context
        ))
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error("NLU processing failed", error=str(e))
        return jsonify({
            'success': False,
            'error': 'processing_failed',
            'message': f'NLU processing failed: {str(e)}'
        }), 500

@nlu_bp.route('/conversation/start', methods=['POST'])
@auth_manager.require_user_or_admin()
@rate_limiter.limit("10 per minute")
def start_conversation():
    """Start a new conversation session"""
    try:
        data = request.get_json() or {}
        
        session_id = data.get('session_id', f"session_{int(datetime.utcnow().timestamp())}")
        meeting_id = data.get('meeting_id')
        participants = data.get('participants', [])
        
        # Start conversation session
        session = asyncio.run(conversation_service.start_conversation(
            session_id=session_id,
            meeting_id=meeting_id,
            participants=participants
        ))
        
        return jsonify({
            'success': True,
            'data': {
                'session_id': session.session_id,
                'meeting_id': session.meeting_id,
                'participants': session.participants,
                'state': session.state.value,
                'start_time': session.start_time.isoformat()
            }
        })
        
    except Exception as e:
        logger.error("Conversation start failed", error=str(e))
        return jsonify({
            'success': False,
            'error': 'conversation_start_failed',
            'message': f'Failed to start conversation: {str(e)}'
        }), 500

@nlu_bp.route('/conversation/turn', methods=['POST'])
@auth_manager.require_user_or_admin()
@rate_limiter.limit("60 per minute")
def process_conversation_turn():
    """Process a conversation turn"""
    try:
        data = request.get_json()
        
        if not data or 'session_id' not in data or 'text' not in data:
            return jsonify({
                'success': False,
                'error': 'missing_required_fields',
                'message': 'session_id and text are required'
            }), 400
        
        session_id = data['session_id']
        text = data['text']
        speaker = data.get('speaker')
        intent = data.get('intent')
        entities = data.get('entities', {})
        
        # Process conversation turn
        result = asyncio.run(conversation_service.process_conversation_turn(
            session_id=session_id,
            text=text,
            speaker=speaker,
            intent=intent,
            entities=entities
        ))
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error("Conversation turn processing failed", error=str(e))
        return jsonify({
            'success': False,
            'error': 'turn_processing_failed',
            'message': f'Failed to process conversation turn: {str(e)}'
        }), 500

@nlu_bp.route('/conversation/<session_id>/end', methods=['POST'])
@auth_manager.require_user_or_admin()
@rate_limiter.limit("10 per minute")
def end_conversation(session_id: str):
    """End a conversation session"""
    try:
        # End conversation session
        result = asyncio.run(conversation_service.end_conversation(session_id))
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error("Conversation end failed", error=str(e))
        return jsonify({
            'success': False,
            'error': 'conversation_end_failed',
            'message': f'Failed to end conversation: {str(e)}'
        }), 500

@nlu_bp.route('/conversation/<session_id>/state', methods=['GET'])
@auth_manager.require_user_or_admin()
@rate_limiter.limit("30 per minute")
def get_conversation_state(session_id: str):
    """Get conversation state"""
    try:
        state = asyncio.run(conversation_service.get_conversation_state(session_id))
        
        if not state:
            return jsonify({
                'success': False,
                'error': 'session_not_found',
                'message': f'No active session found: {session_id}'
            }), 404
        
        return jsonify({
            'success': True,
            'data': state
        })
        
    except Exception as e:
        logger.error("Get conversation state failed", error=str(e))
        return jsonify({
            'success': False,
            'error': 'state_retrieval_failed',
            'message': f'Failed to get conversation state: {str(e)}'
        }), 500

@nlu_bp.route('/conversation/<session_id>/history', methods=['GET'])
@auth_manager.require_user_or_admin()
@rate_limiter.limit("20 per minute")
def get_conversation_history(session_id: str):
    """Get conversation history"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        history = asyncio.run(conversation_service.get_conversation_history(session_id, limit))
        
        return jsonify({
            'success': True,
            'data': {
                'session_id': session_id,
                'history': history,
                'count': len(history)
            }
        })
        
    except Exception as e:
        logger.error("Get conversation history failed", error=str(e))
        return jsonify({
            'success': False,
            'error': 'history_retrieval_failed',
            'message': f'Failed to get conversation history: {str(e)}'
        }), 500

@nlu_bp.route('/intent/process', methods=['POST'])
@auth_manager.require_user_or_admin()
@rate_limiter.limit("20 per minute")
def process_intent():
    """Process a specific intent"""
    try:
        data = request.get_json()
        
        if not data or 'intent_name' not in data:
            return jsonify({
                'success': False,
                'error': 'missing_intent_name',
                'message': 'intent_name is required'
            }), 400
        
        intent_name = data['intent_name']
        entities = data.get('entities', {})
        context = data.get('context', {})
        session_id = data.get('session_id')
        
        # Process intent
        result = asyncio.run(intent_service.process_intent(
            intent_name=intent_name,
            entities=entities,
            context=context,
            session_id=session_id
        ))
        
        return jsonify({
            'success': True,
            'data': {
                'intent_name': result.intent_name,
                'status': result.status.value,
                'actions_taken': result.actions_taken,
                'data_created': result.data_created,
                'next_steps': result.next_steps,
                'confidence': result.confidence,
                'processing_time': result.processing_time,
                'metadata': result.metadata
            }
        })
        
    except Exception as e:
        logger.error("Intent processing failed", error=str(e))
        return jsonify({
            'success': False,
            'error': 'intent_processing_failed',
            'message': f'Failed to process intent: {str(e)}'
        }), 500

@nlu_bp.route('/intent/active', methods=['GET'])
@auth_manager.require_user_or_admin()
@rate_limiter.limit("30 per minute")
def get_active_intents():
    """Get active intents"""
    try:
        active_intents = asyncio.run(intent_service.get_active_intents())
        
        return jsonify({
            'success': True,
            'data': {
                'active_intents': active_intents,
                'count': len(active_intents)
            }
        })
        
    except Exception as e:
        logger.error("Get active intents failed", error=str(e))
        return jsonify({
            'success': False,
            'error': 'active_intents_retrieval_failed',
            'message': f'Failed to get active intents: {str(e)}'
        }), 500

@nlu_bp.route('/intent/history', methods=['GET'])
@auth_manager.require_user_or_admin()
@rate_limiter.limit("20 per minute")
def get_intent_history():
    """Get intent processing history"""
    try:
        limit = request.args.get('limit', 50, type=int)
        
        history = asyncio.run(intent_service.get_intent_history(limit))
        
        return jsonify({
            'success': True,
            'data': {
                'history': history,
                'count': len(history)
            }
        })
        
    except Exception as e:
        logger.error("Get intent history failed", error=str(e))
        return jsonify({
            'success': False,
            'error': 'intent_history_retrieval_failed',
            'message': f'Failed to get intent history: {str(e)}'
        }), 500

@nlu_bp.route('/intent/<intent_id>/cancel', methods=['POST'])
@auth_manager.require_user_or_admin()
@rate_limiter.limit("10 per minute")
def cancel_intent(intent_id: str):
    """Cancel an active intent"""
    try:
        success = asyncio.run(intent_service.cancel_intent(intent_id))
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'intent_not_found',
                'message': f'No active intent found: {intent_id}'
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'intent_id': intent_id,
                'status': 'cancelled'
            }
        })
        
    except Exception as e:
        logger.error("Cancel intent failed", error=str(e))
        return jsonify({
            'success': False,
            'error': 'intent_cancellation_failed',
            'message': f'Failed to cancel intent: {str(e)}'
        }), 500

@nlu_bp.route('/context/<session_id>', methods=['GET'])
@auth_manager.require_user_or_admin()
@rate_limiter.limit("30 per minute")
def get_nlu_context(session_id: str):
    """Get NLU context for a session"""
    try:
        context = asyncio.run(nlu_service.get_conversation_context(session_id))
        
        if not context:
            return jsonify({
                'success': False,
                'error': 'context_not_found',
                'message': f'No NLU context found for session: {session_id}'
            }), 404
        
        return jsonify({
            'success': True,
            'data': context
        })
        
    except Exception as e:
        logger.error("Get NLU context failed", error=str(e))
        return jsonify({
            'success': False,
            'error': 'context_retrieval_failed',
            'message': f'Failed to get NLU context: {str(e)}'
        }), 500

@nlu_bp.route('/context/<session_id>', methods=['DELETE'])
@auth_manager.require_user_or_admin()
@rate_limiter.limit("10 per minute")
def clear_nlu_context(session_id: str):
    """Clear NLU context for a session"""
    try:
        asyncio.run(nlu_service.clear_conversation_context(session_id))
        
        return jsonify({
            'success': True,
            'data': {
                'session_id': session_id,
                'status': 'context_cleared'
            }
        })
        
    except Exception as e:
        logger.error("Clear NLU context failed", error=str(e))
        return jsonify({
            'success': False,
            'error': 'context_clear_failed',
            'message': f'Failed to clear NLU context: {str(e)}'
        }), 500

# Health check endpoint
@nlu_bp.route('/health', methods=['GET'])
def health_check():
    """NLU service health check"""
    try:
        return jsonify({
            'success': True,
            'data': {
                'service': 'nlu',
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'components': {
                    'nlu_service': 'ready',
                    'conversation_service': 'ready',
                    'intent_service': 'ready'
                }
            }
        })
        
    except Exception as e:
        logger.error("NLU health check failed", error=str(e))
        return jsonify({
            'success': False,
            'error': 'health_check_failed',
            'message': f'NLU health check failed: {str(e)}'
        }), 500

# Import asyncio at the top level to avoid issues
import asyncio