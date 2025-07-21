"""
Message Handlers for AI Performers
Enables AI performers to participate in inter-AI communication and collaboration
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json
import structlog

from ..ai_communication import AIMessage, AIMessageHandler, MessageType, MessagePriority

logger = structlog.get_logger(__name__)

class BasePerformerMessageHandler(AIMessageHandler):
    """Base message handler for AI performers"""
    
    def __init__(self, performer_id: str, performer_instance):
        self.performer_id = performer_id
        self.performer = performer_instance
        self.collaboration_insights = {}
        self.pending_requests = {}
    
    async def handle_message(self, message: AIMessage) -> Optional[AIMessage]:
        """Handle an incoming message and optionally return a response"""
        try:
            logger.debug(f"{self.performer_id} received message", 
                        message_id=message.id,
                        type=message.message_type.value,
                        sender=message.sender_id)
            
            if message.message_type == MessageType.INSIGHT_SHARE:
                return await self._handle_insight_share(message)
            elif message.message_type == MessageType.ANALYSIS_REQUEST:
                return await self._handle_analysis_request(message)
            elif message.message_type == MessageType.COLLABORATION_INVITE:
                return await self._handle_collaboration_invite(message)
            elif message.message_type == MessageType.VALIDATION_REQUEST:
                return await self._handle_validation_request(message)
            elif message.message_type == MessageType.SYNTHESIS_PROPOSAL:
                return await self._handle_synthesis_proposal(message)
            elif message.message_type == MessageType.CONFLICT_RESOLUTION:
                return await self._handle_conflict_resolution(message)
            else:
                logger.warning(f"{self.performer_id} cannot handle message type", 
                             type=message.message_type.value)
                return None
                
        except Exception as e:
            logger.error(f"{self.performer_id} message handling failed", 
                        message_id=message.id,
                        error=str(e))
            return None
    
    def can_handle(self, message_type: MessageType) -> bool:
        """Check if this handler can process the given message type"""
        return message_type in [
            MessageType.INSIGHT_SHARE,
            MessageType.ANALYSIS_REQUEST,
            MessageType.COLLABORATION_INVITE,
            MessageType.VALIDATION_REQUEST,
            MessageType.SYNTHESIS_PROPOSAL,
            MessageType.CONFLICT_RESOLUTION
        ]
    
    async def _handle_insight_share(self, message: AIMessage) -> Optional[AIMessage]:
        """Handle shared insights from other performers"""
        try:
            insight_data = message.content.get('insight', {})
            dimension = message.content.get('dimension')
            confidence = message.content.get('confidence', 0.5)
            
            # Store the insight for potential use in future analysis
            if message.session_id:
                if message.session_id not in self.collaboration_insights:
                    self.collaboration_insights[message.session_id] = {}
                
                self.collaboration_insights[message.session_id][message.sender_id] = {
                    'dimension': dimension,
                    'insight': insight_data,
                    'confidence': confidence,
                    'timestamp': message.timestamp
                }
            
            # Analyze if this insight is relevant to our dimension
            relevance = await self._assess_insight_relevance(insight_data, dimension)
            
            if relevance > 0.7 and message.requires_response:
                # Send acknowledgment with our perspective
                return AIMessage(
                    id=f"response_{message.id}",
                    sender_id=self.performer_id,
                    recipient_id=message.sender_id,
                    message_type=MessageType.INSIGHT_SHARE,
                    priority=MessagePriority.MEDIUM,
                    content={
                        'acknowledgment': True,
                        'relevance_score': relevance,
                        'our_perspective': await self._get_perspective_on_insight(insight_data),
                        'dimension': self.performer.dimension
                    },
                    correlation_id=message.id,
                    session_id=message.session_id
                )
            
            return None
            
        except Exception as e:
            logger.error(f"{self.performer_id} insight share handling failed", error=str(e))
            return None
    
    async def _handle_analysis_request(self, message: AIMessage) -> Optional[AIMessage]:
        """Handle requests for additional analysis"""
        try:
            request_data = message.content.get('request', {})
            analysis_type = request_data.get('type')
            input_data = request_data.get('input_data', {})
            
            # Check if we can fulfill this request
            if not await self._can_fulfill_request(analysis_type, input_data):
                return AIMessage(
                    id=f"response_{message.id}",
                    sender_id=self.performer_id,
                    recipient_id=message.sender_id,
                    message_type=MessageType.ANALYSIS_REQUEST,
                    priority=MessagePriority.MEDIUM,
                    content={
                        'status': 'declined',
                        'reason': f"Cannot fulfill {analysis_type} request",
                        'capabilities': list(self.performer.capabilities.keys())
                    },
                    correlation_id=message.id,
                    session_id=message.session_id
                )
            
            # Perform the requested analysis
            try:
                result = await self.performer.process_task(
                    f"collab_{message.id}",
                    input_data
                )
                
                return AIMessage(
                    id=f"response_{message.id}",
                    sender_id=self.performer_id,
                    recipient_id=message.sender_id,
                    message_type=MessageType.ANALYSIS_REQUEST,
                    priority=MessagePriority.HIGH,
                    content={
                        'status': 'completed',
                        'result': result,
                        'analysis_type': analysis_type
                    },
                    correlation_id=message.id,
                    session_id=message.session_id
                )
                
            except Exception as e:
                return AIMessage(
                    id=f"response_{message.id}",
                    sender_id=self.performer_id,
                    recipient_id=message.sender_id,
                    message_type=MessageType.ANALYSIS_REQUEST,
                    priority=MessagePriority.MEDIUM,
                    content={
                        'status': 'failed',
                        'error': str(e)
                    },
                    correlation_id=message.id,
                    session_id=message.session_id
                )
                
        except Exception as e:
            logger.error(f"{self.performer_id} analysis request handling failed", error=str(e))
            return None
    
    async def _handle_collaboration_invite(self, message: AIMessage) -> Optional[AIMessage]:
        """Handle collaboration invitations"""
        try:
            session_id = message.content.get('session_id')
            topic = message.content.get('topic')
            objective = message.content.get('objective')
            participants = message.content.get('participants', [])
            
            # Assess if we should participate
            should_participate = await self._should_participate_in_collaboration(
                topic, objective, participants
            )
            
            return AIMessage(
                id=f"response_{message.id}",
                sender_id=self.performer_id,
                recipient_id=message.sender_id,
                message_type=MessageType.COLLABORATION_INVITE,
                priority=MessagePriority.HIGH,
                content={
                    'response': 'accept' if should_participate else 'decline',
                    'session_id': session_id,
                    'capabilities_offered': list(self.performer.capabilities.keys()) if should_participate else [],
                    'reason': 'Relevant to my expertise' if should_participate else 'Outside my domain'
                },
                correlation_id=message.id,
                session_id=session_id
            )
            
        except Exception as e:
            logger.error(f"{self.performer_id} collaboration invite handling failed", error=str(e))
            return None
    
    async def _handle_validation_request(self, message: AIMessage) -> Optional[AIMessage]:
        """Handle requests to validate analysis results"""
        try:
            analysis_to_validate = message.content.get('analysis', {})
            dimension = message.content.get('dimension')
            
            # Perform validation based on our expertise
            validation_result = await self._validate_analysis(analysis_to_validate, dimension)
            
            return AIMessage(
                id=f"response_{message.id}",
                sender_id=self.performer_id,
                recipient_id=message.sender_id,
                message_type=MessageType.VALIDATION_REQUEST,
                priority=MessagePriority.HIGH,
                content={
                    'validation_result': validation_result,
                    'validator_dimension': self.performer.dimension,
                    'confidence': validation_result.get('confidence', 0.5)
                },
                correlation_id=message.id,
                session_id=message.session_id
            )
            
        except Exception as e:
            logger.error(f"{self.performer_id} validation request handling failed", error=str(e))
            return None
    
    async def _handle_synthesis_proposal(self, message: AIMessage) -> Optional[AIMessage]:
        """Handle synthesis proposals from other performers"""
        try:
            proposal = message.content.get('proposal', {})
            contributing_insights = message.content.get('insights', [])
            
            # Evaluate the synthesis proposal
            evaluation = await self._evaluate_synthesis_proposal(proposal, contributing_insights)
            
            return AIMessage(
                id=f"response_{message.id}",
                sender_id=self.performer_id,
                recipient_id=message.sender_id,
                message_type=MessageType.SYNTHESIS_PROPOSAL,
                priority=MessagePriority.HIGH,
                content={
                    'evaluation': evaluation,
                    'agreement_level': evaluation.get('agreement_score', 0.5),
                    'suggested_modifications': evaluation.get('modifications', [])
                },
                correlation_id=message.id,
                session_id=message.session_id
            )
            
        except Exception as e:
            logger.error(f"{self.performer_id} synthesis proposal handling failed", error=str(e))
            return None
    
    async def _handle_conflict_resolution(self, message: AIMessage) -> Optional[AIMessage]:
        """Handle conflict resolution notifications"""
        try:
            resolution = message.content.get('resolution', {})
            session_id = message.content.get('session_id')
            
            # Update our collaboration insights with the resolution
            if session_id in self.collaboration_insights:
                self.collaboration_insights[session_id]['resolution'] = resolution
            
            # Acknowledge the resolution
            return AIMessage(
                id=f"response_{message.id}",
                sender_id=self.performer_id,
                recipient_id=message.sender_id,
                message_type=MessageType.CONFLICT_RESOLUTION,
                priority=MessagePriority.MEDIUM,
                content={
                    'acknowledgment': True,
                    'resolution_accepted': True
                },
                correlation_id=message.id,
                session_id=session_id
            )
            
        except Exception as e:
            logger.error(f"{self.performer_id} conflict resolution handling failed", error=str(e))
            return None
    
    async def _assess_insight_relevance(self, insight_data: Dict[str, Any], 
                                      source_dimension: str) -> float:
        """Assess how relevant an insight is to this performer's dimension"""
        try:
            # Simple relevance scoring based on dimension compatibility
            dimension_compatibility = {
                'structural_extraction': {
                    'pattern_subtext': 0.6,
                    'strategic_synthesis': 0.7,
                    'narrative_integration': 0.5,
                    'solution_architecture': 0.8,
                    'human_needs_dynamics': 0.4
                },
                'pattern_subtext': {
                    'structural_extraction': 0.6,
                    'strategic_synthesis': 0.5,
                    'narrative_integration': 0.8,
                    'solution_architecture': 0.4,
                    'human_needs_dynamics': 0.9
                },
                'strategic_synthesis': {
                    'structural_extraction': 0.7,
                    'pattern_subtext': 0.5,
                    'narrative_integration': 0.6,
                    'solution_architecture': 0.9,
                    'human_needs_dynamics': 0.6
                },
                'narrative_integration': {
                    'structural_extraction': 0.5,
                    'pattern_subtext': 0.8,
                    'strategic_synthesis': 0.6,
                    'solution_architecture': 0.4,
                    'human_needs_dynamics': 0.7
                },
                'solution_architecture': {
                    'structural_extraction': 0.8,
                    'pattern_subtext': 0.4,
                    'strategic_synthesis': 0.9,
                    'narrative_integration': 0.4,
                    'human_needs_dynamics': 0.5
                },
                'human_needs_dynamics': {
                    'structural_extraction': 0.4,
                    'pattern_subtext': 0.9,
                    'strategic_synthesis': 0.6,
                    'narrative_integration': 0.7,
                    'solution_architecture': 0.5
                }
            }
            
            our_dimension = self.performer.dimension
            base_relevance = dimension_compatibility.get(our_dimension, {}).get(source_dimension, 0.3)
            
            # Adjust based on insight content (simplified)
            content_relevance = 0.5
            if isinstance(insight_data, dict):
                # Look for keywords relevant to our dimension
                insight_text = json.dumps(insight_data).lower()
                
                dimension_keywords = {
                    'structural_extraction': ['decision', 'action', 'task', 'explicit', 'statement'],
                    'pattern_subtext': ['pattern', 'emotion', 'implicit', 'theme', 'assumption'],
                    'strategic_synthesis': ['strategy', 'alignment', 'framework', 'recommendation'],
                    'narrative_integration': ['story', 'journey', 'character', 'development', 'narrative'],
                    'solution_architecture': ['solution', 'implementation', 'resource', 'plan', 'architecture'],
                    'human_needs_dynamics': ['needs', 'fulfillment', 'wellbeing', 'intervention', 'human']
                }
                
                our_keywords = dimension_keywords.get(our_dimension, [])
                keyword_matches = sum(1 for keyword in our_keywords if keyword in insight_text)
                content_relevance = min(1.0, keyword_matches / len(our_keywords)) if our_keywords else 0.5
            
            return (base_relevance + content_relevance) / 2
            
        except Exception as e:
            logger.error(f"{self.performer_id} relevance assessment failed", error=str(e))
            return 0.3
    
    async def _get_perspective_on_insight(self, insight_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get this performer's perspective on a shared insight"""
        try:
            # This would be implemented differently for each performer type
            return {
                'dimension': self.performer.dimension,
                'perspective': f"From {self.performer.dimension} viewpoint",
                'additional_considerations': [],
                'confidence': 0.6
            }
            
        except Exception as e:
            logger.error(f"{self.performer_id} perspective generation failed", error=str(e))
            return {}
    
    async def _can_fulfill_request(self, analysis_type: str, input_data: Dict[str, Any]) -> bool:
        """Check if this performer can fulfill an analysis request"""
        try:
            # Check if the request type matches our capabilities
            our_capabilities = self.performer.capabilities
            
            # Simple capability matching
            capability_keywords = {
                'structural_analysis': ['extracts_decisions', 'identifies_actions', 'extracts_key_points'],
                'pattern_analysis': ['detects_implicit_patterns', 'analyzes_emotional_subtext'],
                'strategic_analysis': ['connects_strategic_context', 'generates_recommendations'],
                'narrative_analysis': ['positions_organizational_journey', 'tracks_character_development'],
                'solution_analysis': ['creates_implementation_plans', 'allocates_resources'],
                'human_needs_analysis': ['analyzes_human_needs', 'identifies_fulfillment_gaps']
            }
            
            required_capabilities = capability_keywords.get(analysis_type, [])
            
            if not required_capabilities:
                return False
            
            # Check if we have at least one required capability
            return any(our_capabilities.get(cap, False) for cap in required_capabilities)
            
        except Exception as e:
            logger.error(f"{self.performer_id} request fulfillment check failed", error=str(e))
            return False
    
    async def _should_participate_in_collaboration(self, topic: str, objective: str, 
                                                 participants: List[str]) -> bool:
        """Decide whether to participate in a collaboration"""
        try:
            # Simple decision logic based on topic relevance
            topic_lower = topic.lower()
            objective_lower = objective.lower()
            
            dimension_keywords = {
                'structural_extraction': ['decision', 'action', 'structure', 'explicit'],
                'pattern_subtext': ['pattern', 'behavior', 'emotion', 'implicit'],
                'strategic_synthesis': ['strategy', 'alignment', 'framework', 'synthesis'],
                'narrative_integration': ['story', 'narrative', 'journey', 'character'],
                'solution_architecture': ['solution', 'implementation', 'architecture', 'plan'],
                'human_needs_dynamics': ['needs', 'human', 'wellbeing', 'fulfillment']
            }
            
            our_keywords = dimension_keywords.get(self.performer.dimension, [])
            
            # Check if topic/objective contains our keywords
            relevance_score = 0
            for keyword in our_keywords:
                if keyword in topic_lower or keyword in objective_lower:
                    relevance_score += 1
            
            # Participate if relevance score is high enough
            return relevance_score >= 1
            
        except Exception as e:
            logger.error(f"{self.performer_id} collaboration decision failed", error=str(e))
            return False
    
    async def _validate_analysis(self, analysis: Dict[str, Any], dimension: str) -> Dict[str, Any]:
        """Validate analysis results from another performer"""
        try:
            # Basic validation logic
            validation_result = {
                'is_valid': True,
                'confidence': 0.7,
                'issues': [],
                'suggestions': []
            }
            
            # Check for basic structure
            if not isinstance(analysis, dict):
                validation_result['is_valid'] = False
                validation_result['issues'].append('Analysis is not a dictionary')
                validation_result['confidence'] = 0.1
                return validation_result
            
            # Check for confidence score
            if 'confidence' not in analysis:
                validation_result['issues'].append('Missing confidence score')
                validation_result['confidence'] -= 0.1
            elif analysis.get('confidence', 0) < 0.3:
                validation_result['issues'].append('Low confidence score')
                validation_result['confidence'] -= 0.2
            
            # Dimension-specific validation would go here
            # This is a simplified version
            
            return validation_result
            
        except Exception as e:
            logger.error(f"{self.performer_id} analysis validation failed", error=str(e))
            return {
                'is_valid': False,
                'confidence': 0.1,
                'issues': [f'Validation error: {str(e)}'],
                'suggestions': []
            }
    
    async def _evaluate_synthesis_proposal(self, proposal: Dict[str, Any], 
                                         insights: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate a synthesis proposal"""
        try:
            evaluation = {
                'agreement_score': 0.6,
                'strengths': [],
                'weaknesses': [],
                'modifications': []
            }
            
            # Basic evaluation logic
            if not isinstance(proposal, dict):
                evaluation['agreement_score'] = 0.1
                evaluation['weaknesses'].append('Invalid proposal format')
                return evaluation
            
            # Check if proposal includes insights from our dimension
            our_dimension = self.performer.dimension
            our_insights_included = any(
                insight.get('dimension') == our_dimension 
                for insight in insights
            )
            
            if our_insights_included:
                evaluation['agreement_score'] += 0.2
                evaluation['strengths'].append('Includes our dimensional insights')
            else:
                evaluation['agreement_score'] -= 0.1
                evaluation['modifications'].append(f'Consider including {our_dimension} insights')
            
            return evaluation
            
        except Exception as e:
            logger.error(f"{self.performer_id} synthesis evaluation failed", error=str(e))
            return {
                'agreement_score': 0.3,
                'strengths': [],
                'weaknesses': [f'Evaluation error: {str(e)}'],
                'modifications': []
            }