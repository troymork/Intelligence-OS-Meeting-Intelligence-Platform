"""
Intent Service for Intelligence OS
Handles specific meeting-related intent processing and actions
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
import structlog

logger = structlog.get_logger(__name__)

class IntentStatus(Enum):
    """Intent processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REQUIRES_INPUT = "requires_input"

@dataclass
class IntentAction:
    """Action to be taken for an intent"""
    action_type: str
    parameters: Dict[str, Any]
    priority: int = 1
    requires_confirmation: bool = False
    timeout_seconds: int = 300

@dataclass
class IntentResult:
    """Result of intent processing"""
    intent_name: str
    status: IntentStatus
    actions_taken: List[str]
    data_created: Dict[str, Any]
    next_steps: List[str]
    confidence: float
    processing_time: float
    metadata: Dict[str, Any]

class IntentService:
    """Service for processing meeting-related intents"""
    
    def __init__(self):
        self.intent_handlers: Dict[str, Callable] = {}
        self.active_intents: Dict[str, Dict[str, Any]] = {}
        self.intent_history: List[Dict[str, Any]] = []
        
        # Register intent handlers
        self._register_intent_handlers()
    
    def _register_intent_handlers(self):
        """Register handlers for different intents"""
        self.intent_handlers = {
            'start_meeting': self._handle_start_meeting,
            'end_meeting': self._handle_end_meeting,
            'create_action': self._handle_create_action,
            'make_decision': self._handle_make_decision,
            'identify_issue': self._handle_identify_issue,
            'request_summary': self._handle_request_summary,
            'ask_question': self._handle_ask_question,
            'provide_update': self._handle_provide_update,
            'schedule_followup': self._handle_schedule_followup,
            'analyze_sentiment': self._handle_analyze_sentiment
        }
    
    async def initialize(self):
        """Initialize the intent service"""
        try:
            logger.info("Intent service initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize intent service", error=str(e))
            raise
    
    async def process_intent(self, intent_name: str, entities: Dict[str, Any], 
                           context: Dict[str, Any] = None, session_id: str = None) -> IntentResult:
        """Process an intent with extracted entities"""
        start_time = datetime.utcnow()
        
        try:
            logger.info("Processing intent", 
                       intent=intent_name, 
                       entities=list(entities.keys()),
                       session_id=session_id)
            
            # Check if handler exists
            if intent_name not in self.intent_handlers:
                return IntentResult(
                    intent_name=intent_name,
                    status=IntentStatus.FAILED,
                    actions_taken=[],
                    data_created={},
                    next_steps=[],
                    confidence=0.0,
                    processing_time=0.0,
                    metadata={'error': f'No handler for intent: {intent_name}'}
                )
            
            # Create intent tracking entry
            intent_id = f"{intent_name}_{int(datetime.utcnow().timestamp())}"
            self.active_intents[intent_id] = {
                'intent_name': intent_name,
                'entities': entities,
                'context': context or {},
                'session_id': session_id,
                'start_time': start_time,
                'status': IntentStatus.PROCESSING
            }
            
            # Process intent
            handler = self.intent_handlers[intent_name]
            result = await handler(entities, context or {}, session_id)
            
            # Update tracking
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            result.processing_time = processing_time
            
            self.active_intents[intent_id]['status'] = result.status
            self.active_intents[intent_id]['result'] = result
            
            # Add to history
            self.intent_history.append({
                'intent_id': intent_id,
                'intent_name': intent_name,
                'timestamp': start_time.isoformat(),
                'processing_time': processing_time,
                'status': result.status.value,
                'session_id': session_id
            })
            
            # Clean up completed intents
            if result.status in [IntentStatus.COMPLETED, IntentStatus.FAILED]:
                del self.active_intents[intent_id]
            
            logger.info("Intent processing completed", 
                       intent=intent_name,
                       status=result.status.value,
                       processing_time=processing_time)
            
            return result
            
        except Exception as e:
            logger.error("Intent processing failed", intent=intent_name, error=str(e))
            return IntentResult(
                intent_name=intent_name,
                status=IntentStatus.FAILED,
                actions_taken=[],
                data_created={},
                next_steps=[],
                confidence=0.0,
                processing_time=(datetime.utcnow() - start_time).total_seconds(),
                metadata={'error': str(e)}
            )
    
    async def _handle_start_meeting(self, entities: Dict[str, Any], 
                                  context: Dict[str, Any], session_id: str) -> IntentResult:
        """Handle start meeting intent"""
        try:
            actions_taken = []
            data_created = {}
            next_steps = []
            
            # Extract meeting information
            meeting_title = entities.get('meeting_title', 'Untitled Meeting')
            participants = entities.get('participants', [])
            agenda = entities.get('agenda', [])
            
            # Create meeting record
            meeting_data = {
                'title': meeting_title,
                'start_time': datetime.utcnow().isoformat(),
                'participants': participants,
                'agenda': agenda,
                'session_id': session_id,
                'status': 'active'
            }
            
            data_created['meeting'] = meeting_data
            actions_taken.append('meeting_created')
            
            # Start recording if requested
            if context.get('auto_record', True):
                actions_taken.append('recording_started')
                data_created['recording'] = {
                    'status': 'active',
                    'start_time': datetime.utcnow().isoformat()
                }
            
            # Initialize analysis
            actions_taken.append('analysis_initialized')
            data_created['analysis'] = {
                'status': 'active',
                'dimensions': ['structural', 'pattern', 'strategic', 'narrative', 'solution', 'human_needs']
            }
            
            # Determine next steps
            if not participants:
                next_steps.append('add_participants')
            if not agenda:
                next_steps.append('set_agenda')
            next_steps.append('begin_discussion')
            
            return IntentResult(
                intent_name='start_meeting',
                status=IntentStatus.COMPLETED,
                actions_taken=actions_taken,
                data_created=data_created,
                next_steps=next_steps,
                confidence=0.9,
                processing_time=0.0,
                metadata={'meeting_id': meeting_data.get('id')}
            )
            
        except Exception as e:
            logger.error("Start meeting intent failed", error=str(e))
            raise
    
    async def _handle_end_meeting(self, entities: Dict[str, Any], 
                                context: Dict[str, Any], session_id: str) -> IntentResult:
        """Handle end meeting intent"""
        try:
            actions_taken = []
            data_created = {}
            next_steps = []
            
            # Stop recording
            actions_taken.append('recording_stopped')
            data_created['recording'] = {
                'status': 'completed',
                'end_time': datetime.utcnow().isoformat()
            }
            
            # Finalize analysis
            actions_taken.append('analysis_finalized')
            data_created['analysis'] = {
                'status': 'completed',
                'completion_time': datetime.utcnow().isoformat()
            }
            
            # Generate summary
            actions_taken.append('summary_generated')
            data_created['summary'] = {
                'type': 'meeting_summary',
                'generated_at': datetime.utcnow().isoformat(),
                'status': 'pending'
            }
            
            # Extract action items and next steps from entities
            action_items = entities.get('action_items', [])
            if action_items:
                data_created['action_items'] = action_items
                actions_taken.append('action_items_extracted')
            
            # Set next steps
            next_steps.extend([
                'review_summary',
                'distribute_action_items',
                'schedule_followup'
            ])
            
            return IntentResult(
                intent_name='end_meeting',
                status=IntentStatus.COMPLETED,
                actions_taken=actions_taken,
                data_created=data_created,
                next_steps=next_steps,
                confidence=0.9,
                processing_time=0.0,
                metadata={'session_id': session_id}
            )
            
        except Exception as e:
            logger.error("End meeting intent failed", error=str(e))
            raise
    
    async def _handle_create_action(self, entities: Dict[str, Any], 
                                  context: Dict[str, Any], session_id: str) -> IntentResult:
        """Handle create action intent"""
        try:
            actions_taken = []
            data_created = {}
            next_steps = []
            
            # Extract action information
            description = entities.get('description', 'New action item')
            assignee = entities.get('assignee')
            due_date = entities.get('due_date')
            priority = entities.get('priority', 'medium')
            
            # Create action item
            action_item = {
                'id': f"action_{int(datetime.utcnow().timestamp())}",
                'description': description,
                'assignee': assignee,
                'due_date': due_date,
                'priority': priority,
                'status': 'pending',
                'created_at': datetime.utcnow().isoformat(),
                'session_id': session_id
            }
            
            data_created['action_item'] = action_item
            actions_taken.append('action_item_created')
            
            # Determine next steps based on missing information
            if not assignee:
                next_steps.append('assign_owner')
            if not due_date:
                next_steps.append('set_due_date')
            
            next_steps.extend([
                'confirm_action_details',
                'add_to_tracking_system'
            ])
            
            return IntentResult(
                intent_name='create_action',
                status=IntentStatus.COMPLETED if assignee and due_date else IntentStatus.REQUIRES_INPUT,
                actions_taken=actions_taken,
                data_created=data_created,
                next_steps=next_steps,
                confidence=0.8,
                processing_time=0.0,
                metadata={'action_id': action_item['id']}
            )
            
        except Exception as e:
            logger.error("Create action intent failed", error=str(e))
            raise
    
    async def _handle_make_decision(self, entities: Dict[str, Any], 
                                  context: Dict[str, Any], session_id: str) -> IntentResult:
        """Handle make decision intent"""
        try:
            actions_taken = []
            data_created = {}
            next_steps = []
            
            # Extract decision information
            decision_text = entities.get('decision_text', 'Decision made')
            rationale = entities.get('rationale', '')
            stakeholders = entities.get('stakeholders', [])
            
            # Create decision record
            decision = {
                'id': f"decision_{int(datetime.utcnow().timestamp())}",
                'text': decision_text,
                'rationale': rationale,
                'stakeholders': stakeholders,
                'made_at': datetime.utcnow().isoformat(),
                'status': 'recorded',
                'session_id': session_id
            }
            
            data_created['decision'] = decision
            actions_taken.append('decision_recorded')
            
            # Create related actions if needed
            if 'implementation' in decision_text.lower():
                actions_taken.append('implementation_actions_identified')
                next_steps.append('create_implementation_plan')
            
            # Set next steps
            next_steps.extend([
                'notify_stakeholders',
                'document_decision',
                'track_implementation'
            ])
            
            return IntentResult(
                intent_name='make_decision',
                status=IntentStatus.COMPLETED,
                actions_taken=actions_taken,
                data_created=data_created,
                next_steps=next_steps,
                confidence=0.85,
                processing_time=0.0,
                metadata={'decision_id': decision['id']}
            )
            
        except Exception as e:
            logger.error("Make decision intent failed", error=str(e))
            raise
    
    async def _handle_identify_issue(self, entities: Dict[str, Any], 
                                   context: Dict[str, Any], session_id: str) -> IntentResult:
        """Handle identify issue intent"""
        try:
            actions_taken = []
            data_created = {}
            next_steps = []
            
            # Extract issue information
            issue_type = entities.get('issue_type', 'general')
            severity = entities.get('severity', 'medium')
            impact = entities.get('impact', 'unknown')
            description = entities.get('description', 'Issue identified')
            
            # Create issue record
            issue = {
                'id': f"issue_{int(datetime.utcnow().timestamp())}",
                'type': issue_type,
                'severity': severity,
                'impact': impact,
                'description': description,
                'identified_at': datetime.utcnow().isoformat(),
                'status': 'open',
                'session_id': session_id
            }
            
            data_created['issue'] = issue
            actions_taken.append('issue_recorded')
            
            # Suggest resolution actions based on severity
            if severity in ['high', 'critical']:
                next_steps.extend([
                    'escalate_issue',
                    'assign_immediate_owner',
                    'create_resolution_plan'
                ])
            else:
                next_steps.extend([
                    'analyze_root_cause',
                    'assign_owner',
                    'schedule_resolution'
                ])
            
            return IntentResult(
                intent_name='identify_issue',
                status=IntentStatus.COMPLETED,
                actions_taken=actions_taken,
                data_created=data_created,
                next_steps=next_steps,
                confidence=0.8,
                processing_time=0.0,
                metadata={'issue_id': issue['id']}
            )
            
        except Exception as e:
            logger.error("Identify issue intent failed", error=str(e))
            raise
    
    async def _handle_request_summary(self, entities: Dict[str, Any], 
                                    context: Dict[str, Any], session_id: str) -> IntentResult:
        """Handle request summary intent"""
        try:
            actions_taken = []
            data_created = {}
            next_steps = []
            
            # Extract summary parameters
            summary_type = entities.get('summary_type', 'general')
            time_range = entities.get('time_range', 'current_meeting')
            
            # Generate summary request
            summary_request = {
                'id': f"summary_{int(datetime.utcnow().timestamp())}",
                'type': summary_type,
                'time_range': time_range,
                'requested_at': datetime.utcnow().isoformat(),
                'status': 'generating',
                'session_id': session_id
            }
            
            data_created['summary_request'] = summary_request
            actions_taken.append('summary_generation_started')
            
            # Set next steps
            next_steps.extend([
                'compile_meeting_data',
                'generate_summary',
                'present_summary'
            ])
            
            return IntentResult(
                intent_name='request_summary',
                status=IntentStatus.PROCESSING,
                actions_taken=actions_taken,
                data_created=data_created,
                next_steps=next_steps,
                confidence=0.9,
                processing_time=0.0,
                metadata={'summary_id': summary_request['id']}
            )
            
        except Exception as e:
            logger.error("Request summary intent failed", error=str(e))
            raise
    
    async def _handle_ask_question(self, entities: Dict[str, Any], 
                                 context: Dict[str, Any], session_id: str) -> IntentResult:
        """Handle ask question intent"""
        try:
            actions_taken = []
            data_created = {}
            next_steps = []
            
            # Extract question information
            question_topic = entities.get('question_topic', 'general')
            question_context = entities.get('context', '')
            
            # Create question record
            question = {
                'id': f"question_{int(datetime.utcnow().timestamp())}",
                'topic': question_topic,
                'context': question_context,
                'asked_at': datetime.utcnow().isoformat(),
                'status': 'pending_answer',
                'session_id': session_id
            }
            
            data_created['question'] = question
            actions_taken.append('question_recorded')
            
            # Set next steps
            next_steps.extend([
                'search_knowledge_base',
                'provide_answer',
                'suggest_resources'
            ])
            
            return IntentResult(
                intent_name='ask_question',
                status=IntentStatus.PROCESSING,
                actions_taken=actions_taken,
                data_created=data_created,
                next_steps=next_steps,
                confidence=0.8,
                processing_time=0.0,
                metadata={'question_id': question['id']}
            )
            
        except Exception as e:
            logger.error("Ask question intent failed", error=str(e))
            raise
    
    async def _handle_provide_update(self, entities: Dict[str, Any], 
                                   context: Dict[str, Any], session_id: str) -> IntentResult:
        """Handle provide update intent"""
        try:
            actions_taken = []
            data_created = {}
            next_steps = []
            
            # Extract update information
            project = entities.get('project', 'general')
            status = entities.get('status', 'in_progress')
            metrics = entities.get('metrics', {})
            
            # Create update record
            update = {
                'id': f"update_{int(datetime.utcnow().timestamp())}",
                'project': project,
                'status': status,
                'metrics': metrics,
                'provided_at': datetime.utcnow().isoformat(),
                'session_id': session_id
            }
            
            data_created['update'] = update
            actions_taken.append('update_recorded')
            
            # Set next steps
            next_steps.extend([
                'update_project_status',
                'notify_stakeholders',
                'schedule_next_update'
            ])
            
            return IntentResult(
                intent_name='provide_update',
                status=IntentStatus.COMPLETED,
                actions_taken=actions_taken,
                data_created=data_created,
                next_steps=next_steps,
                confidence=0.85,
                processing_time=0.0,
                metadata={'update_id': update['id']}
            )
            
        except Exception as e:
            logger.error("Provide update intent failed", error=str(e))
            raise
    
    async def _handle_schedule_followup(self, entities: Dict[str, Any], 
                                      context: Dict[str, Any], session_id: str) -> IntentResult:
        """Handle schedule followup intent"""
        try:
            actions_taken = []
            data_created = {}
            next_steps = []
            
            # Extract scheduling information
            date = entities.get('date')
            time = entities.get('time')
            participants = entities.get('participants', [])
            purpose = entities.get('purpose', 'Follow-up meeting')
            
            # Create followup record
            followup = {
                'id': f"followup_{int(datetime.utcnow().timestamp())}",
                'date': date,
                'time': time,
                'participants': participants,
                'purpose': purpose,
                'scheduled_at': datetime.utcnow().isoformat(),
                'status': 'scheduled' if date and time else 'pending_details',
                'session_id': session_id
            }
            
            data_created['followup'] = followup
            actions_taken.append('followup_scheduled')
            
            # Determine next steps based on available information
            if not date:
                next_steps.append('set_date')
            if not time:
                next_steps.append('set_time')
            if not participants:
                next_steps.append('invite_participants')
            
            next_steps.extend([
                'send_calendar_invites',
                'prepare_agenda'
            ])
            
            return IntentResult(
                intent_name='schedule_followup',
                status=IntentStatus.COMPLETED if date and time else IntentStatus.REQUIRES_INPUT,
                actions_taken=actions_taken,
                data_created=data_created,
                next_steps=next_steps,
                confidence=0.8,
                processing_time=0.0,
                metadata={'followup_id': followup['id']}
            )
            
        except Exception as e:
            logger.error("Schedule followup intent failed", error=str(e))
            raise
    
    async def _handle_analyze_sentiment(self, entities: Dict[str, Any], 
                                      context: Dict[str, Any], session_id: str) -> IntentResult:
        """Handle analyze sentiment intent"""
        try:
            actions_taken = []
            data_created = {}
            next_steps = []
            
            # Extract sentiment analysis parameters
            sentiment_target = entities.get('sentiment_target', 'general')
            time_period = entities.get('time_period', 'current_meeting')
            
            # Create sentiment analysis request
            sentiment_analysis = {
                'id': f"sentiment_{int(datetime.utcnow().timestamp())}",
                'target': sentiment_target,
                'time_period': time_period,
                'requested_at': datetime.utcnow().isoformat(),
                'status': 'analyzing',
                'session_id': session_id
            }
            
            data_created['sentiment_analysis'] = sentiment_analysis
            actions_taken.append('sentiment_analysis_started')
            
            # Set next steps
            next_steps.extend([
                'analyze_conversation_tone',
                'identify_sentiment_patterns',
                'generate_sentiment_report'
            ])
            
            return IntentResult(
                intent_name='analyze_sentiment',
                status=IntentStatus.PROCESSING,
                actions_taken=actions_taken,
                data_created=data_created,
                next_steps=next_steps,
                confidence=0.8,
                processing_time=0.0,
                metadata={'analysis_id': sentiment_analysis['id']}
            )
            
        except Exception as e:
            logger.error("Analyze sentiment intent failed", error=str(e))
            raise
    
    async def get_active_intents(self) -> List[Dict[str, Any]]:
        """Get list of currently active intents"""
        return [
            {
                'intent_id': intent_id,
                'intent_name': data['intent_name'],
                'status': data['status'].value,
                'start_time': data['start_time'].isoformat(),
                'session_id': data['session_id']
            }
            for intent_id, data in self.active_intents.items()
        ]
    
    async def get_intent_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get intent processing history"""
        return self.intent_history[-limit:]
    
    async def cancel_intent(self, intent_id: str) -> bool:
        """Cancel an active intent"""
        if intent_id in self.active_intents:
            self.active_intents[intent_id]['status'] = IntentStatus.FAILED
            del self.active_intents[intent_id]
            logger.info("Intent cancelled", intent_id=intent_id)
            return True
        return False

# Global intent service instance
intent_service = IntentService()