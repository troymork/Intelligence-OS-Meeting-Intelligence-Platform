"""
Knowledge Graph API Routes
Provides endpoints for organizational knowledge graph and learning analytics
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import structlog
from ..services.knowledge_graph_service import KnowledgeGraphService
from ..services.organizational_learning_analytics import OrganizationalLearningAnalytics
from ..security.auth import require_auth
from ..security.validation import validate_json_input
from ..security.rate_limiting import rate_limit

logger = structlog.get_logger(__name__)

# Create blueprint
knowledge_graph_bp = Blueprint('knowledge_graph', __name__, url_prefix='/api/knowledge-graph')

# Initialize services
knowledge_graph_service = KnowledgeGraphService()
learning_analytics = OrganizationalLearningAnalytics(knowledge_graph_service)

@knowledge_graph_bp.route('/process-meeting', methods=['POST'])
@require_auth
@rate_limit(limit=100, window=3600)  # 100 requests per hour
@validate_json_input
def process_meeting_knowledge():
    """
    Process meeting data to extract and update knowledge graph
    
    Expected JSON payload:
    {
        "meeting_data": {
            "meeting_id": "string",
            "date": "ISO datetime string",
            "participants": ["string"],
            "transcript_analysis": {...},
            "decisions": [...],
            "actions": [...],
            "strategic_implications": [...]
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
        
        logger.info("Processing meeting knowledge", meeting_id=meeting_data.get('meeting_id'))
        
        # Process meeting knowledge
        result = knowledge_graph_service.process_meeting_knowledge(meeting_data)
        
        logger.info("Meeting knowledge processing completed", 
                   meeting_id=meeting_data.get('meeting_id'),
                   concepts_processed=result.get('concepts_processed', 0))
        
        return jsonify({
            'status': 'success',
            'data': result,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error("Meeting knowledge processing failed", error=str(e))
        return jsonify({
            'error': 'Knowledge processing failed',
            'details': str(e),
            'status': 'error'
        }), 500

@knowledge_graph_bp.route('/summary', methods=['GET'])
@require_auth
@rate_limit(limit=200, window=3600)  # 200 requests per hour
def get_knowledge_graph_summary():
    """
    Get knowledge graph summary with statistics and top concepts
    """
    try:
        logger.info("Generating knowledge graph summary")
        
        summary = knowledge_graph_service.get_knowledge_graph_summary()
        
        return jsonify({
            'status': 'success',
            'data': summary,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error("Knowledge graph summary generation failed", error=str(e))
        return jsonify({
            'error': 'Summary generation failed',
            'details': str(e),
            'status': 'error'
        }), 500

@knowledge_graph_bp.route('/concepts', methods=['GET'])
@require_auth
@rate_limit(limit=300, window=3600)  # 300 requests per hour
def get_concepts():
    """
    Get concepts from knowledge graph with optional filtering
    
    Query parameters:
    - concept_type: Filter by concept type
    - min_importance: Minimum importance score (0-1)
    - min_mentions: Minimum mention count
    - search: Search term for concept names
    - limit: Maximum number of concepts to return (default: 50)
    - offset: Number of concepts to skip (default: 0)
    """
    try:
        # Get query parameters
        concept_type = request.args.get('concept_type')
        min_importance = float(request.args.get('min_importance', 0.0))
        min_mentions = int(request.args.get('min_mentions', 0))
        search_term = request.args.get('search', '').lower()
        limit = min(int(request.args.get('limit', 50)), 100)  # Max 100
        offset = int(request.args.get('offset', 0))
        
        # Get all concepts
        all_concepts = list(knowledge_graph_service.concepts.values())
        
        # Apply filters
        filtered_concepts = all_concepts
        
        if concept_type:
            filtered_concepts = [c for c in filtered_concepts if c.concept_type.value == concept_type]
        
        if min_importance > 0:
            filtered_concepts = [c for c in filtered_concepts if c.importance_score >= min_importance]
        
        if min_mentions > 0:
            filtered_concepts = [c for c in filtered_concepts if c.mention_count >= min_mentions]
        
        if search_term:
            filtered_concepts = [c for c in filtered_concepts if search_term in c.name.lower()]
        
        # Sort by importance score
        filtered_concepts.sort(key=lambda x: x.importance_score, reverse=True)
        
        # Apply pagination
        paginated_concepts = filtered_concepts[offset:offset + limit]
        
        # Serialize concepts
        serialized_concepts = [_serialize_concept(c) for c in paginated_concepts]
        
        return jsonify({
            'status': 'success',
            'data': {
                'concepts': serialized_concepts,
                'total_count': len(filtered_concepts),
                'returned_count': len(serialized_concepts),
                'offset': offset,
                'limit': limit
            },
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error("Concepts retrieval failed", error=str(e))
        return jsonify({
            'error': 'Concepts retrieval failed',
            'details': str(e),
            'status': 'error'
        }), 500

@knowledge_graph_bp.route('/relationships', methods=['GET'])
@require_auth
@rate_limit(limit=300, window=3600)  # 300 requests per hour
def get_relationships():
    """
    Get relationships from knowledge graph with optional filtering
    
    Query parameters:
    - relationship_type: Filter by relationship type
    - min_strength: Minimum relationship strength (0-1)
    - source_concept: Filter by source concept ID
    - target_concept: Filter by target concept ID
    - limit: Maximum number of relationships to return (default: 50)
    - offset: Number of relationships to skip (default: 0)
    """
    try:
        # Get query parameters
        relationship_type = request.args.get('relationship_type')
        min_strength = float(request.args.get('min_strength', 0.0))
        source_concept = request.args.get('source_concept')
        target_concept = request.args.get('target_concept')
        limit = min(int(request.args.get('limit', 50)), 100)  # Max 100
        offset = int(request.args.get('offset', 0))
        
        # Get all relationships
        all_relationships = list(knowledge_graph_service.relationships.values())
        
        # Apply filters
        filtered_relationships = all_relationships
        
        if relationship_type:
            filtered_relationships = [r for r in filtered_relationships if r.relationship_type.value == relationship_type]
        
        if min_strength > 0:
            filtered_relationships = [r for r in filtered_relationships if r.strength >= min_strength]
        
        if source_concept:
            filtered_relationships = [r for r in filtered_relationships if r.source_concept_id == source_concept]
        
        if target_concept:
            filtered_relationships = [r for r in filtered_relationships if r.target_concept_id == target_concept]
        
        # Sort by strength
        filtered_relationships.sort(key=lambda x: x.strength, reverse=True)
        
        # Apply pagination
        paginated_relationships = filtered_relationships[offset:offset + limit]
        
        # Serialize relationships
        serialized_relationships = [_serialize_relationship(r) for r in paginated_relationships]
        
        return jsonify({
            'status': 'success',
            'data': {
                'relationships': serialized_relationships,
                'total_count': len(filtered_relationships),
                'returned_count': len(serialized_relationships),
                'offset': offset,
                'limit': limit
            },
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error("Relationships retrieval failed", error=str(e))
        return jsonify({
            'error': 'Relationships retrieval failed',
            'details': str(e),
            'status': 'error'
        }), 500

@knowledge_graph_bp.route('/learning-analysis', methods=['POST'])
@require_auth
@rate_limit(limit=50, window=3600)  # 50 requests per hour
@validate_json_input
def analyze_meeting_learning():
    """
    Analyze learning that occurred in a meeting
    
    Expected JSON payload:
    {
        "meeting_data": {...},
        "knowledge_graph_result": {...}
    }
    """
    try:
        data = request.get_json()
        meeting_data = data.get('meeting_data')
        knowledge_graph_result = data.get('knowledge_graph_result', {})
        
        if not meeting_data:
            return jsonify({
                'error': 'Missing meeting_data in request',
                'status': 'error'
            }), 400
        
        logger.info("Analyzing meeting learning", meeting_id=meeting_data.get('meeting_id'))
        
        # Analyze learning
        result = learning_analytics.analyze_meeting_learning(meeting_data, knowledge_graph_result)
        
        logger.info("Meeting learning analysis completed",
                   meeting_id=meeting_data.get('meeting_id'),
                   learning_events=len(result.get('learning_events', [])))
        
        return jsonify({
            'status': 'success',
            'data': result,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error("Meeting learning analysis failed", error=str(e))
        return jsonify({
            'error': 'Learning analysis failed',
            'details': str(e),
            'status': 'error'
        }), 500

@knowledge_graph_bp.route('/wisdom-assessment', methods=['POST'])
@require_auth
@rate_limit(limit=10, window=3600)  # 10 requests per hour (expensive operation)
@validate_json_input
def assess_organizational_wisdom():
    """
    Assess organizational wisdom development
    
    Expected JSON payload:
    {
        "assessment_period_days": 90 (optional)
    }
    """
    try:
        data = request.get_json() or {}
        assessment_period_days = data.get('assessment_period_days', 90)
        
        # Validate assessment period
        if not isinstance(assessment_period_days, int) or assessment_period_days < 1 or assessment_period_days > 365:
            return jsonify({
                'error': 'assessment_period_days must be an integer between 1 and 365',
                'status': 'error'
            }), 400
        
        logger.info("Assessing organizational wisdom", period_days=assessment_period_days)
        
        # Perform wisdom assessment
        assessment = learning_analytics.assess_organizational_wisdom(assessment_period_days)
        
        # Serialize assessment
        serialized_assessment = _serialize_wisdom_assessment(assessment)
        
        logger.info("Organizational wisdom assessment completed",
                   overall_score=assessment.overall_wisdom_score)
        
        return jsonify({
            'status': 'success',
            'data': serialized_assessment,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error("Organizational wisdom assessment failed", error=str(e))
        return jsonify({
            'error': 'Wisdom assessment failed',
            'details': str(e),
            'status': 'error'
        }), 500

@knowledge_graph_bp.route('/learning-events', methods=['GET'])
@require_auth
@rate_limit(limit=200, window=3600)  # 200 requests per hour
def get_learning_events():
    """
    Get learning events with optional filtering
    
    Query parameters:
    - event_type: Filter by learning event type
    - min_impact: Minimum impact score (0-1)
    - participant: Filter by participant name
    - days_back: Number of days to look back (default: 30)
    - limit: Maximum number of events to return (default: 50)
    - offset: Number of events to skip (default: 0)
    """
    try:
        # Get query parameters
        event_type = request.args.get('event_type')
        min_impact = float(request.args.get('min_impact', 0.0))
        participant = request.args.get('participant')
        days_back = int(request.args.get('days_back', 30))
        limit = min(int(request.args.get('limit', 50)), 100)  # Max 100
        offset = int(request.args.get('offset', 0))
        
        # Calculate date threshold
        date_threshold = datetime.utcnow() - timedelta(days=days_back)
        
        # Get all learning events
        all_events = learning_analytics.learning_events
        
        # Apply filters
        filtered_events = all_events
        
        # Filter by date
        filtered_events = [e for e in filtered_events if e.timestamp >= date_threshold]
        
        if event_type:
            filtered_events = [e for e in filtered_events if e.event_type.value == event_type]
        
        if min_impact > 0:
            filtered_events = [e for e in filtered_events if e.impact_score >= min_impact]
        
        if participant:
            filtered_events = [e for e in filtered_events if participant in e.participants]
        
        # Sort by timestamp (most recent first)
        filtered_events.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Apply pagination
        paginated_events = filtered_events[offset:offset + limit]
        
        # Serialize events
        serialized_events = [learning_analytics._serialize_learning_event(e) for e in paginated_events]
        
        return jsonify({
            'status': 'success',
            'data': {
                'learning_events': serialized_events,
                'total_count': len(filtered_events),
                'returned_count': len(serialized_events),
                'offset': offset,
                'limit': limit
            },
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error("Learning events retrieval failed", error=str(e))
        return jsonify({
            'error': 'Learning events retrieval failed',
            'details': str(e),
            'status': 'error'
        }), 500

# Serialization helper functions
def _serialize_concept(concept):
    """Serialize Concept for JSON response"""
    return {
        'id': concept.id,
        'name': concept.name,
        'concept_type': concept.concept_type.value,
        'description': concept.description,
        'attributes': concept.attributes,
        'first_mentioned': concept.first_mentioned.isoformat(),
        'last_mentioned': concept.last_mentioned.isoformat(),
        'mention_count': concept.mention_count,
        'importance_score': concept.importance_score,
        'related_meetings': list(concept.related_meetings),
        'evolution_history_count': len(concept.evolution_history),
        'created_at': concept.created_at.isoformat()
    }

def _serialize_relationship(relationship):
    """Serialize Relationship for JSON response"""
    return {
        'id': relationship.id,
        'source_concept_id': relationship.source_concept_id,
        'target_concept_id': relationship.target_concept_id,
        'relationship_type': relationship.relationship_type.value,
        'strength': relationship.strength,
        'confidence': relationship.confidence,
        'evidence': relationship.evidence,
        'first_observed': relationship.first_observed.isoformat(),
        'last_observed': relationship.last_observed.isoformat(),
        'observation_count': relationship.observation_count,
        'context': relationship.context,
        'created_at': relationship.created_at.isoformat()
    }

def _serialize_wisdom_assessment(assessment):
    """Serialize WisdomAssessment for JSON response"""
    return {
        'id': assessment.id,
        'assessment_period': {
            'start': assessment.assessment_period['start'].isoformat(),
            'end': assessment.assessment_period['end'].isoformat()
        },
        'wisdom_indicators': {
            indicator.value: score for indicator, score in assessment.wisdom_indicators.items()
        },
        'collective_intelligence_score': assessment.collective_intelligence_score,
        'decision_quality_trend': assessment.decision_quality_trend,
        'learning_agility_score': assessment.learning_agility_score,
        'knowledge_integration_ability': assessment.knowledge_integration_ability,
        'contextual_awareness_level': assessment.contextual_awareness_level,
        'long_term_thinking_capacity': assessment.long_term_thinking_capacity,
        'ethical_reasoning_maturity': assessment.ethical_reasoning_maturity,
        'overall_wisdom_score': assessment.overall_wisdom_score,
        'improvement_recommendations': assessment.improvement_recommendations
    }