"""
Inter-AI Communication and Collaboration Framework for Intelligence OS
Enables AI performers to share insights and collaborate on complex analysis
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
import structlog
from abc import ABC, abstractmethod

logger = structlog.get_logger(__name__)

class MessageType(Enum):
    """Types of inter-AI messages"""
    INSIGHT_SHARE = "insight_share"
    ANALYSIS_REQUEST = "analysis_request"
    COLLABORATION_INVITE = "collaboration_invite"
    CONFLICT_RESOLUTION = "conflict_resolution"
    VALIDATION_REQUEST = "validation_request"
    SYNTHESIS_PROPOSAL = "synthesis_proposal"
    RESOURCE_REQUEST = "resource_request"
    STATUS_UPDATE = "status_update"

class MessagePriority(Enum):
    """Message priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class CollaborationStatus(Enum):
    """Status of collaboration sessions"""
    INITIATED = "initiated"
    ACTIVE = "active"
    CONSENSUS_REACHED = "consensus_reached"
    CONFLICT_DETECTED = "conflict_detected"
    RESOLVED = "resolved"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class AIMessage:
    """Standardized message format for inter-AI communication"""
    id: str
    sender_id: str
    recipient_id: Optional[str]  # None for broadcast messages
    message_type: MessageType
    priority: MessagePriority
    content: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    requires_response: bool = False
    correlation_id: Optional[str] = None  # For linking related messages
    session_id: Optional[str] = None

@dataclass
class CollaborationSession:
    """Represents a collaborative analysis session between AI performers"""
    id: str
    initiator_id: str
    participants: List[str]
    topic: str
    objective: str
    status: CollaborationStatus
    messages: List[AIMessage] = field(default_factory=list)
    insights: Dict[str, Any] = field(default_factory=dict)
    consensus: Optional[Dict[str, Any]] = None
    conflicts: List[Dict[str, Any]] = field(default_factory=list)
    resolution: Optional[Dict[str, Any]] = None
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class AIMessageHandler(ABC):
    """Abstract base class for AI message handlers"""
    
    @abstractmethod
    async def handle_message(self, message: AIMessage) -> Optional[AIMessage]:
        """Handle an incoming message and optionally return a response"""
        pass
    
    @abstractmethod
    def can_handle(self, message_type: MessageType) -> bool:
        """Check if this handler can process the given message type"""
        pass

class AICommunicationHub:
    """Central hub for inter-AI communication and collaboration"""
    
    def __init__(self):
        self.message_handlers: Dict[str, AIMessageHandler] = {}
        self.active_sessions: Dict[str, CollaborationSession] = {}
        self.message_queue: List[AIMessage] = []
        self.message_history: List[AIMessage] = []
        self.performer_registry: Dict[str, Dict[str, Any]] = {}
        
        # Configuration
        self.max_message_history = 1000
        self.message_retention_days = 7
        self.max_collaboration_duration = timedelta(hours=2)
        
        # Performance metrics
        self.metrics = {
            'messages_sent': 0,
            'messages_received': 0,
            'collaborations_initiated': 0,
            'collaborations_successful': 0,
            'conflicts_resolved': 0,
            'average_response_time': 0.0
        }
    
    async def initialize(self):
        """Initialize the communication hub"""
        try:
            # Start background message processor
            self.processing_task = asyncio.create_task(self._background_processor())
            
            logger.info("AI Communication Hub initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize AI Communication Hub", error=str(e))
            raise
    
    def register_performer(self, performer_id: str, capabilities: Dict[str, Any], 
                          message_handler: AIMessageHandler):
        """Register an AI performer with the communication hub"""
        try:
            self.performer_registry[performer_id] = {
                'capabilities': capabilities,
                'handler': message_handler,
                'last_activity': datetime.utcnow(),
                'messages_sent': 0,
                'messages_received': 0,
                'collaborations_participated': 0
            }
            
            self.message_handlers[performer_id] = message_handler
            
            logger.info("AI performer registered", performer_id=performer_id)
            
        except Exception as e:
            logger.error("Failed to register performer", performer_id=performer_id, error=str(e))
            raise
    
    async def send_message(self, message: AIMessage) -> bool:
        """Send a message to one or more AI performers"""
        try:
            # Validate message
            if not self._validate_message(message):
                logger.error("Invalid message", message_id=message.id)
                return False
            
            # Add to queue for processing
            self.message_queue.append(message)
            self.message_history.append(message)
            
            # Update metrics
            self.metrics['messages_sent'] += 1
            if message.sender_id in self.performer_registry:
                self.performer_registry[message.sender_id]['messages_sent'] += 1
            
            logger.debug("Message queued for delivery", 
                        message_id=message.id,
                        sender=message.sender_id,
                        recipient=message.recipient_id,
                        type=message.message_type.value)
            
            return True
            
        except Exception as e:
            logger.error("Failed to send message", message_id=message.id, error=str(e))
            return False
    
    async def broadcast_message(self, sender_id: str, message_type: MessageType, 
                              content: Dict[str, Any], priority: MessagePriority = MessagePriority.MEDIUM,
                              exclude_performers: List[str] = None) -> bool:
        """Broadcast a message to all registered performers"""
        try:
            exclude_performers = exclude_performers or []
            exclude_performers.append(sender_id)  # Don't send to sender
            
            message = AIMessage(
                id=str(uuid.uuid4()),
                sender_id=sender_id,
                recipient_id=None,  # Broadcast
                message_type=message_type,
                priority=priority,
                content=content,
                metadata={'broadcast': True, 'excluded': exclude_performers}
            )
            
            return await self.send_message(message)
            
        except Exception as e:
            logger.error("Failed to broadcast message", sender_id=sender_id, error=str(e))
            return False
    
    async def initiate_collaboration(self, initiator_id: str, participants: List[str], 
                                   topic: str, objective: str) -> Optional[CollaborationSession]:
        """Initiate a collaborative analysis session"""
        try:
            session_id = str(uuid.uuid4())
            
            session = CollaborationSession(
                id=session_id,
                initiator_id=initiator_id,
                participants=participants,
                topic=topic,
                objective=objective,
                status=CollaborationStatus.INITIATED
            )
            
            self.active_sessions[session_id] = session
            
            # Send collaboration invites
            for participant_id in participants:
                if participant_id != initiator_id:
                    invite_message = AIMessage(
                        id=str(uuid.uuid4()),
                        sender_id=initiator_id,
                        recipient_id=participant_id,
                        message_type=MessageType.COLLABORATION_INVITE,
                        priority=MessagePriority.HIGH,
                        content={
                            'session_id': session_id,
                            'topic': topic,
                            'objective': objective,
                            'participants': participants
                        },
                        requires_response=True,
                        session_id=session_id
                    )
                    
                    await self.send_message(invite_message)
            
            # Update metrics
            self.metrics['collaborations_initiated'] += 1
            if initiator_id in self.performer_registry:
                self.performer_registry[initiator_id]['collaborations_participated'] += 1
            
            logger.info("Collaboration session initiated", 
                       session_id=session_id,
                       initiator=initiator_id,
                       participants=participants,
                       topic=topic)
            
            return session
            
        except Exception as e:
            logger.error("Failed to initiate collaboration", 
                        initiator_id=initiator_id,
                        error=str(e))
            return None
    
    async def resolve_conflict(self, session_id: str, conflict_data: Dict[str, Any]) -> bool:
        """Resolve a conflict in a collaboration session"""
        try:
            if session_id not in self.active_sessions:
                logger.error("Collaboration session not found", session_id=session_id)
                return False
            
            session = self.active_sessions[session_id]
            session.conflicts.append(conflict_data)
            session.status = CollaborationStatus.CONFLICT_DETECTED
            
            # Implement conflict resolution logic
            resolution = await self._resolve_collaboration_conflict(session, conflict_data)
            
            if resolution:
                session.resolution = resolution
                session.status = CollaborationStatus.RESOLVED
                
                # Notify participants of resolution
                for participant_id in session.participants:
                    resolution_message = AIMessage(
                        id=str(uuid.uuid4()),
                        sender_id='communication_hub',
                        recipient_id=participant_id,
                        message_type=MessageType.CONFLICT_RESOLUTION,
                        priority=MessagePriority.HIGH,
                        content={
                            'session_id': session_id,
                            'resolution': resolution,
                            'conflict_data': conflict_data
                        },
                        session_id=session_id
                    )
                    
                    await self.send_message(resolution_message)
                
                self.metrics['conflicts_resolved'] += 1
                
                logger.info("Conflict resolved", session_id=session_id)
                return True
            else:
                session.status = CollaborationStatus.FAILED
                logger.error("Failed to resolve conflict", session_id=session_id)
                return False
                
        except Exception as e:
            logger.error("Error resolving conflict", session_id=session_id, error=str(e))
            return False
    
    async def _background_processor(self):
        """Background processor for handling messages and maintaining sessions"""
        while True:
            try:
                await asyncio.sleep(0.1)  # Process every 100ms
                
                # Process message queue
                await self._process_message_queue()
                
                # Check collaboration sessions
                await self._check_collaboration_sessions()
                
                # Clean up old messages
                await self._cleanup_old_messages()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Background processor error", error=str(e))
                await asyncio.sleep(1)  # Wait before retrying
    
    async def _process_message_queue(self):
        """Process pending messages in the queue"""
        try:
            messages_to_process = self.message_queue.copy()
            self.message_queue.clear()
            
            for message in messages_to_process:
                await self._deliver_message(message)
                
        except Exception as e:
            logger.error("Message queue processing failed", error=str(e))
    
    async def _deliver_message(self, message: AIMessage):
        """Deliver a message to its intended recipient(s)"""
        try:
            start_time = datetime.utcnow()
            
            if message.recipient_id:
                # Direct message
                if message.recipient_id in self.message_handlers:
                    handler = self.message_handlers[message.recipient_id]
                    response = await handler.handle_message(message)
                    
                    # Update recipient metrics
                    if message.recipient_id in self.performer_registry:
                        self.performer_registry[message.recipient_id]['messages_received'] += 1
                        self.performer_registry[message.recipient_id]['last_activity'] = datetime.utcnow()
                    
                    # Handle response if provided
                    if response:
                        await self.send_message(response)
                else:
                    logger.warning("Recipient not found", recipient_id=message.recipient_id)
            else:
                # Broadcast message
                excluded = message.metadata.get('excluded', [])
                
                for performer_id, handler in self.message_handlers.items():
                    if performer_id not in excluded:
                        try:
                            response = await handler.handle_message(message)
                            
                            # Update recipient metrics
                            if performer_id in self.performer_registry:
                                self.performer_registry[performer_id]['messages_received'] += 1
                                self.performer_registry[performer_id]['last_activity'] = datetime.utcnow()
                            
                            # Handle response if provided
                            if response:
                                await self.send_message(response)
                                
                        except Exception as e:
                            logger.error("Failed to deliver broadcast message", 
                                       performer_id=performer_id,
                                       error=str(e))
            
            # Update response time metrics
            response_time = (datetime.utcnow() - start_time).total_seconds()
            self.metrics['average_response_time'] = (
                (self.metrics['average_response_time'] * self.metrics['messages_received'] + response_time) /
                (self.metrics['messages_received'] + 1)
            )
            self.metrics['messages_received'] += 1
            
        except Exception as e:
            logger.error("Message delivery failed", message_id=message.id, error=str(e))
    
    async def _check_collaboration_sessions(self):
        """Check and update collaboration sessions"""
        try:
            current_time = datetime.utcnow()
            sessions_to_remove = []
            
            for session_id, session in self.active_sessions.items():
                # Check for timeout
                if current_time - session.start_time > self.max_collaboration_duration:
                    session.status = CollaborationStatus.FAILED
                    session.end_time = current_time
                    sessions_to_remove.append(session_id)
                    
                    logger.warning("Collaboration session timed out", session_id=session_id)
                
                # Check for completion
                elif session.status in [CollaborationStatus.RESOLVED, 
                                      CollaborationStatus.CONSENSUS_REACHED,
                                      CollaborationStatus.FAILED,
                                      CollaborationStatus.CANCELLED]:
                    if not session.end_time:
                        session.end_time = current_time
                    
                    # Keep completed sessions for a while before cleanup
                    if current_time - session.end_time > timedelta(hours=1):
                        sessions_to_remove.append(session_id)
            
            # Remove completed/failed sessions
            for session_id in sessions_to_remove:
                del self.active_sessions[session_id]
                
        except Exception as e:
            logger.error("Collaboration session check failed", error=str(e))
    
    async def _cleanup_old_messages(self):
        """Clean up old messages from history"""
        try:
            if len(self.message_history) > self.max_message_history:
                # Keep only the most recent messages
                self.message_history = self.message_history[-self.max_message_history:]
            
            # Remove expired messages
            current_time = datetime.utcnow()
            cutoff_time = current_time - timedelta(days=self.message_retention_days)
            
            self.message_history = [
                msg for msg in self.message_history
                if msg.timestamp > cutoff_time
            ]
            
        except Exception as e:
            logger.error("Message cleanup failed", error=str(e))
    
    async def _resolve_collaboration_conflict(self, session: CollaborationSession, 
                                            conflict_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Resolve conflicts in collaboration sessions"""
        try:
            # Simple conflict resolution strategy
            # In a real implementation, this would be more sophisticated
            
            conflict_type = conflict_data.get('type', 'unknown')
            
            if conflict_type == 'confidence_disagreement':
                # Use weighted average based on performer confidence scores
                conflicting_insights = conflict_data.get('insights', [])
                
                if len(conflicting_insights) >= 2:
                    total_weight = sum(insight.get('confidence', 0.5) for insight in conflicting_insights)
                    
                    if total_weight > 0:
                        weighted_result = {}
                        for insight in conflicting_insights:
                            weight = insight.get('confidence', 0.5) / total_weight
                            # Merge insights with weights (simplified)
                            for key, value in insight.get('data', {}).items():
                                if key not in weighted_result:
                                    weighted_result[key] = value * weight
                                else:
                                    weighted_result[key] += value * weight
                        
                        return {
                            'resolution_type': 'weighted_average',
                            'result': weighted_result,
                            'confidence': total_weight / len(conflicting_insights)
                        }
            
            elif conflict_type == 'methodology_disagreement':
                # Use the methodology with higher success rate
                methodologies = conflict_data.get('methodologies', [])
                
                if methodologies:
                    best_methodology = max(methodologies, 
                                         key=lambda m: m.get('success_rate', 0.0))
                    
                    return {
                        'resolution_type': 'best_methodology',
                        'chosen_methodology': best_methodology,
                        'rationale': f"Selected methodology with highest success rate: {best_methodology.get('success_rate', 0.0)}"
                    }
            
            # Default resolution: flag for human review
            return {
                'resolution_type': 'human_review_required',
                'conflict_data': conflict_data,
                'recommendation': 'Complex conflict requires human intervention'
            }
            
        except Exception as e:
            logger.error("Conflict resolution failed", error=str(e))
            return None
    
    def _validate_message(self, message: AIMessage) -> bool:
        """Validate message format and content"""
        try:
            # Basic validation
            if not message.id or not message.sender_id:
                return False
            
            if not isinstance(message.content, dict):
                return False
            
            # Check if sender is registered
            if message.sender_id not in self.performer_registry and message.sender_id != 'communication_hub':
                return False
            
            # Check if recipient exists (for direct messages)
            if message.recipient_id and message.recipient_id not in self.performer_registry:
                return False
            
            # Check expiration
            if message.expires_at and datetime.utcnow() > message.expires_at:
                return False
            
            return True
            
        except Exception as e:
            logger.error("Message validation failed", error=str(e))
            return False
    
    async def get_communication_status(self) -> Dict[str, Any]:
        """Get communication hub status and metrics"""
        try:
            return {
                'status': 'active',
                'registered_performers': len(self.performer_registry),
                'active_collaborations': len(self.active_sessions),
                'queued_messages': len(self.message_queue),
                'message_history_size': len(self.message_history),
                'metrics': self.metrics,
                'performer_stats': {
                    performer_id: {
                        'last_activity': stats['last_activity'].isoformat(),
                        'messages_sent': stats['messages_sent'],
                        'messages_received': stats['messages_received'],
                        'collaborations_participated': stats['collaborations_participated']
                    }
                    for performer_id, stats in self.performer_registry.items()
                },
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Failed to get communication status", error=str(e))
            return {'status': 'error', 'error': str(e)}

# Global communication hub instance
ai_communication_hub = AICommunicationHub()