"""
Transcript API Routes for Intelligence OS
Conversation transcript processing and management endpoints
"""

from flask import Blueprint, request, jsonify, g
from typing import Dict, List, Optional, Any
import logging
import structlog
from datetime import datetime
import asyncio

from ..services.transcript_service import transcript_service, SegmentType, TranscriptStatus
from ..security.auth import auth_manager
from ..security.rate_limiting import rate_limiter
from ..security.validation import input_validator

logger = structlog.get_logger(__name__)

# Create blueprint
transcript_bp = Blueprint('transcript', __name__, url_prefix='/api/transcript')

@transcript_bp.route('/create', methods=['POST'])
@auth_manager.require_user_or_admin()
@rate_limiter.limit("20 per minute")
def create_transcript():
    """Create a new conversation transcript"""
    try:
        data = request.get_json() or {}
        
        # Validate input
        validation_result = input_validator.validate_text(
            data.get('session_id', ''), 'short_text', required=True
        )
        if not validation_result['valid']:
            return jsonify({
                'success': False,
                'error': 'validation_failed',
                'message': f"Session ID validation failed: {', '.join(validation_result['errors'])}"
            }), 400
        
        session_id = validation_result['sanitized']
        meeting_id = data.get('meeting_id')
        title = data.get('title')
        
        # Validate optional fields
        if meeting_id:
            meeting_validation = input_validator.validate_text(meeting_id, 'short_text')
            if meeting_validation['valid']:
                meeting_id = meeting_validation['sanitized']
            else:
                meeting_id = None
        
        if title:
            title_validation = input_validator.validate_text(title, 'title')
            if title_validation['valid']:
                title = title_validation['sanitized']
            else:
                title = None
        
        # Create transcript
        transcript = asyncio.run(transcript_service.create_transcript(
            session_id=session_id,
            meeting_id=meeting_id,
            title=title
        ))
        
        return jsonify({
            'success': True,
            'data': {
                'transcript_id': transcript.id,
                'session_id': transcript.session_id,
                'meeting_id': transcript.meeting_id,
                'title': transcript.title,
                'status': transcript.status.value,
                'start_time': transcript.start_time.isoformat()
            }
        })
        
    except Exception as e:
        logger.error("Transcript creation failed", error=str(e))
        return jsonify({
            'success': False,
            'error': 'creation_failed',
            'message': f'Failed to create transcript: {str(e)}'
        }), 500

@transcript_bp.route('/<transcript_id>/segment', methods=['POST'])
@auth_manager.require_user_or_admin()
@rate_limiter.limit("100 per minute")
def add_segment(transcript_id: str):
    """Add a segment to a transcript"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'missing_data',
                'message': 'Request data is required'
            }), 400
        
        # Validate required fields
        required_fields = ['start_time', 'end_time', 'text']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': 'missing_field',
                    'message': f'Required field missing: {field}'
                }), 400
        
        # Validate and sanitize input
        text_validation = input_validator.validate_text(data['text'], 'long_text', required=True)
        if not text_validation['valid']:
            return jsonify({
                'success': False,
                'error': 'validation_failed',
                'message': f"Text validation failed: {', '.join(text_validation['errors'])}"
            }), 400
        
        start_time = float(data['start_time'])
        end_time = float(data['end_time'])
        text = text_validation['sanitized']
        speaker_id = data.get('speaker_id')
        speaker_name = data.get('speaker_name')
        confidence = float(data.get('confidence', 1.0))
        segment_type = data.get('segment_type', 'speech')
        
        # Validate segment type
        try:
            segment_type_enum = SegmentType(segment_type.lower())
        except ValueError:
            segment_type_enum = SegmentType.SPEECH
        
        # Validate speaker information
        if speaker_id:
            speaker_validation = input_validator.validate_text(speaker_id, 'short_text')
            if speaker_validation['valid']:
                speaker_id = speaker_validation['sanitized']
            else:
                speaker_id = None
        
        if speaker_name:
            name_validation = input_validator.validate_text(speaker_name, 'name')
            if name_validation['valid']:
                speaker_name = name_validation['sanitized']
            else:
                speaker_name = None
        
        # Add segment
        segment = asyncio.run(transcript_service.add_segment(
            transcript_id=transcript_id,
            start_time=start_time,
            end_time=end_time,
            speaker_id=speaker_id,
            speaker_name=speaker_name,
            text=text,
            confidence=confidence,
            segment_type=segment_type_enum
        ))
        
        return jsonify({
            'success': True,
            'data': {
                'segment_id': segment.id,
                'start_time': segment.start_time,
                'end_time': segment.end_time,
                'speaker_id': segment.speaker_id,
                'speaker_name': segment.speaker_name,
                'text': segment.text,
                'confidence': segment.confidence,
                'segment_type': segment.segment_type.value,
                'keywords': segment.keywords,
                'topics': segment.topics,
                'emotions': segment.emotions
            }
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'invalid_transcript',
            'message': str(e)
        }), 404
    except Exception as e:
        logger.error("Segment addition failed", error=str(e))
        return jsonify({
            'success': False,
            'error': 'segment_addition_failed',
            'message': f'Failed to add segment: {str(e)}'
        }), 500

@transcript_bp.route('/<transcript_id>/process', methods=['POST'])
@auth_manager.require_user_or_admin()
@rate_limiter.limit("10 per minute")
def process_transcript(transcript_id: str):
    """Process a transcript to extract insights and metadata"""
    try:
        transcript = asyncio.run(transcript_service.process_transcript(transcript_id))
        
        return jsonify({
            'success': True,
            'data': {
                'transcript_id': transcript.id,
                'status': transcript.status.value,
                'summary': transcript.summary,
                'topics': transcript.topics,
                'keywords': transcript.keywords,
                'sentiment_analysis': transcript.sentiment_analysis,
                'quality_metrics': transcript.quality_metrics,
                'speakers': [
                    {
                        'id': s.id,
                        'name': s.name,
                        'speaking_time': s.speaking_time,
                        'word_count': s.word_count,
                        'speaking_rate': s.speaking_rate,
                        'questions_asked': s.questions_asked,
                        'statements_made': s.statements_made,
                        'sentiment_scores': s.sentiment_scores
                    } for s in transcript.speakers
                ],
                'processing_completed': transcript.end_time.isoformat() if transcript.end_time else None
            }
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'invalid_transcript',
            'message': str(e)
        }), 404
    except Exception as e:
        logger.error("Transcript processing failed", error=str(e))
        return jsonify({
            'success': False,
            'error': 'processing_failed',
            'message': f'Failed to process transcript: {str(e)}'
        }), 500

@transcript_bp.route('/<transcript_id>', methods=['GET'])
@auth_manager.require_user_or_admin()
@rate_limiter.limit("50 per minute")
def get_transcript(transcript_id: str):
    """Get a transcript by ID"""
    try:
        transcript = asyncio.run(transcript_service.get_transcript(transcript_id))
        
        if not transcript:
            return jsonify({
                'success': False,
                'error': 'transcript_not_found',
                'message': f'Transcript not found: {transcript_id}'
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'transcript_id': transcript.id,
                'session_id': transcript.session_id,
                'meeting_id': transcript.meeting_id,
                'title': transcript.title,
                'start_time': transcript.start_time.isoformat(),
                'end_time': transcript.end_time.isoformat() if transcript.end_time else None,
                'duration': transcript.duration,
                'status': transcript.status.value,
                'summary': transcript.summary,
                'topics': transcript.topics,
                'keywords': transcript.keywords,
                'sentiment_analysis': transcript.sentiment_analysis,
                'quality_metrics': transcript.quality_metrics,
                'speakers': [
                    {
                        'id': s.id,
                        'name': s.name,
                        'role': s.role,
                        'speaking_time': s.speaking_time,
                        'word_count': s.word_count,
                        'average_confidence': s.average_confidence,
                        'speaking_rate': s.speaking_rate,
                        'interruptions': s.interruptions,
                        'questions_asked': s.questions_asked,
                        'statements_made': s.statements_made,
                        'sentiment_scores': s.sentiment_scores
                    } for s in transcript.speakers
                ],
                'segments_count': len(transcript.segments),
                'metadata': transcript.metadata
            }
        })
        
    except Exception as e:
        logger.error("Get transcript failed", error=str(e))
        return jsonify({
            'success': False,
            'error': 'retrieval_failed',
            'message': f'Failed to get transcript: {str(e)}'
        }), 500

@transcript_bp.route('/<transcript_id>/segments', methods=['GET'])
@auth_manager.require_user_or_admin()
@rate_limiter.limit("30 per minute")
def get_transcript_segments(transcript_id: str):
    """Get segments for a transcript"""
    try:
        transcript = asyncio.run(transcript_service.get_transcript(transcript_id))
        
        if not transcript:
            return jsonify({
                'success': False,
                'error': 'transcript_not_found',
                'message': f'Transcript not found: {transcript_id}'
            }), 404
        
        # Optional filtering
        speaker_id = request.args.get('speaker_id')
        segment_type = request.args.get('segment_type')
        start_time = request.args.get('start_time', type=float)
        end_time = request.args.get('end_time', type=float)
        
        segments = transcript.segments
        
        # Apply filters
        if speaker_id:
            segments = [s for s in segments if s.speaker_id == speaker_id]
        
        if segment_type:
            try:
                segment_type_enum = SegmentType(segment_type.lower())
                segments = [s for s in segments if s.segment_type == segment_type_enum]
            except ValueError:
                pass
        
        if start_time is not None:
            segments = [s for s in segments if s.start_time >= start_time]
        
        if end_time is not None:
            segments = [s for s in segments if s.end_time <= end_time]
        
        return jsonify({
            'success': True,
            'data': {
                'transcript_id': transcript_id,
                'segments': [
                    {
                        'id': seg.id,
                        'start_time': seg.start_time,
                        'end_time': seg.end_time,
                        'speaker_id': seg.speaker_id,
                        'speaker_name': seg.speaker_name,
                        'text': seg.text,
                        'confidence': seg.confidence,
                        'segment_type': seg.segment_type.value,
                        'language': seg.language,
                        'emotions': seg.emotions,
                        'keywords': seg.keywords,
                        'topics': seg.topics
                    } for seg in segments
                ],
                'total_segments': len(segments),
                'filtered': len(segments) != len(transcript.segments)
            }
        })
        
    except Exception as e:
        logger.error("Get transcript segments failed", error=str(e))
        return jsonify({
            'success': False,
            'error': 'segments_retrieval_failed',
            'message': f'Failed to get transcript segments: {str(e)}'
        }), 500

@transcript_bp.route('/list', methods=['GET'])
@auth_manager.require_user_or_admin()
@rate_limiter.limit("30 per minute")
def list_transcripts():
    """List transcripts with optional filtering"""
    try:
        session_id = request.args.get('session_id')
        meeting_id = request.args.get('meeting_id')
        
        transcripts = asyncio.run(transcript_service.list_transcripts(
            session_id=session_id,
            meeting_id=meeting_id
        ))
        
        return jsonify({
            'success': True,
            'data': {
                'transcripts': [
                    {
                        'transcript_id': t.id,
                        'session_id': t.session_id,
                        'meeting_id': t.meeting_id,
                        'title': t.title,
                        'start_time': t.start_time.isoformat(),
                        'end_time': t.end_time.isoformat() if t.end_time else None,
                        'duration': t.duration,
                        'status': t.status.value,
                        'speakers_count': len(t.speakers),
                        'segments_count': len(t.segments)
                    } for t in transcripts
                ],
                'total_count': len(transcripts)
            }
        })
        
    except Exception as e:
        logger.error("List transcripts failed", error=str(e))
        return jsonify({
            'success': False,
            'error': 'list_failed',
            'message': f'Failed to list transcripts: {str(e)}'
        }), 500

@transcript_bp.route('/search', methods=['GET'])
@auth_manager.require_user_or_admin()
@rate_limiter.limit("20 per minute")
def search_transcripts():
    """Search transcripts by content"""
    try:
        query = request.args.get('q', '').strip()
        limit = request.args.get('limit', 10, type=int)
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'missing_query',
                'message': 'Search query is required'
            }), 400
        
        # Validate query
        query_validation = input_validator.validate_text(query, 'medium_text', required=True)
        if not query_validation['valid']:
            return jsonify({
                'success': False,
                'error': 'invalid_query',
                'message': f"Query validation failed: {', '.join(query_validation['errors'])}"
            }), 400
        
        query = query_validation['sanitized']
        limit = max(1, min(limit, 50))  # Limit between 1 and 50
        
        results = asyncio.run(transcript_service.search_transcripts(query, limit))
        
        return jsonify({
            'success': True,
            'data': {
                'query': query,
                'results': results,
                'total_results': len(results)
            }
        })
        
    except Exception as e:
        logger.error("Transcript search failed", error=str(e))
        return jsonify({
            'success': False,
            'error': 'search_failed',
            'message': f'Failed to search transcripts: {str(e)}'
        }), 500

@transcript_bp.route('/<transcript_id>/export', methods=['GET'])
@auth_manager.require_user_or_admin()
@rate_limiter.limit("10 per minute")
def export_transcript(transcript_id: str):
    """Export transcript in specified format"""
    try:
        format_type = request.args.get('format', 'json').lower()
        
        if format_type not in ['json', 'text']:
            return jsonify({
                'success': False,
                'error': 'invalid_format',
                'message': 'Supported formats: json, text'
            }), 400
        
        export_data = asyncio.run(transcript_service.export_transcript(transcript_id, format_type))
        
        return jsonify({
            'success': True,
            'data': {
                'transcript_id': transcript_id,
                'format': format_type,
                'export_data': export_data,
                'exported_at': datetime.utcnow().isoformat()
            }
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'invalid_transcript',
            'message': str(e)
        }), 404
    except Exception as e:
        logger.error("Transcript export failed", error=str(e))
        return jsonify({
            'success': False,
            'error': 'export_failed',
            'message': f'Failed to export transcript: {str(e)}'
        }), 500

@transcript_bp.route('/<transcript_id>', methods=['DELETE'])
@auth_manager.require_user_or_admin()
@rate_limiter.limit("10 per minute")
def delete_transcript(transcript_id: str):
    """Delete a transcript"""
    try:
        success = asyncio.run(transcript_service.delete_transcript(transcript_id))
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'transcript_not_found',
                'message': f'Transcript not found: {transcript_id}'
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'transcript_id': transcript_id,
                'status': 'deleted',
                'deleted_at': datetime.utcnow().isoformat()
            }
        })
        
    except Exception as e:
        logger.error("Transcript deletion failed", error=str(e))
        return jsonify({
            'success': False,
            'error': 'deletion_failed',
            'message': f'Failed to delete transcript: {str(e)}'
        }), 500

# Health check endpoint
@transcript_bp.route('/health', methods=['GET'])
def health_check():
    """Transcript service health check"""
    try:
        return jsonify({
            'success': True,
            'data': {
                'service': 'transcript',
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'active_transcripts': len(transcript_service.active_transcripts)
            }
        })
        
    except Exception as e:
        logger.error("Transcript health check failed", error=str(e))
        return jsonify({
            'success': False,
            'error': 'health_check_failed',
            'message': f'Transcript health check failed: {str(e)}'
        }), 500