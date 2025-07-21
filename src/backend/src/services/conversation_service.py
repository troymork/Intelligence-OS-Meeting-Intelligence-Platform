"""
Conversation Service for Intelligence OS
Handles dialogue management, context tracking, and conversation flow
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import openai
import structlog

logger = structlog.get_logger(__name__)

class ConversationState(Enum):
    """Conversation states"""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    RESPONDING = "responding"
    WAITING_FOR_INPUT = "waiting_for_input"
    ERROR = "error"

class DialogueAct(Enum):
    """Dialogue acts for conversation management"""
    GREETING = "greeting"
    QUESTION = "question"
    ANSWER = "answer"
    REQUEST = "request"
    CONFIRMATION = "confirmation"
    CLARIFICATION = "clarification"
    ACKNOWLEDGMENT = "acknowledgment"
    GOODBYE = "goodbye"

@dataclass
class ConversationTurn:
    """Individual conversation turn"""
    turn_id: str
    timestamp: datetime
    speaker: Optional[str]
    text: str
    intent: Optional[str]
    entities: Dict[str, Any]
    dialogue_act: DialogueAct
    confidence: float
    response: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConversationSession:
    """Complete conversation session"""
    session_id: str
    meeting_id: Optional[str]
    participants: List[str]
    start_time: datetime
    end_time: Optional[datetime]
    state: ConversationState
    turns: List[ConversationTurn]
    context: Dict[str, Any]
    summary: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class ConversationService:
    """Conversation management service"""
    
    def __init__(self):
        self.openai_client = None
        self.active_sessions: Dict[str, ConversationSession] = {}
        self.conversation_history: Dict[str, List[ConversationTurn]] = {}
        
        # Conversation flow templates
        self.conversation_flows = {
            'meeting_start': {
                'initial_state': ConversationState.LISTENING,
                'expected_intents': ['start_meeting', 'greeting'],
                'required_entities': ['meeting_title', 'participants'],
                'next_actions': ['confirm_meeting_details', 'begin_recording']
            },
            'action_creation': {
                'initial_state': ConversationState.WAITING_FOR_INPUT,
                'expected_intents': ['create_action'],
                'required_entities': ['assignee', 'description'],
                'next_actions': ['confirm_action', 'set_due_date']
            },
            'decision_making': {
                'initial_state': ConversationState.PROCESSING,
                'expected_intents': ['make_decision'],
                'required_entities': ['decision_text', 'stakeholders'],
                'next_actions': ['record_decision', 'notify_stakeholders']
            },
            'meeting_summary': {
                'initial_state': ConversationState.PROCESSING,
                'expected_intents': ['request_summary'],
                'required_entities': ['summary_type'],
                'next_actions': ['generate_summary', 'present_summary']
            }
        }
        
        # Response templates
        self.response_templates = {
            'greeting': [
                "Hello! I'm ready to help with your meeting.",
                "Good to see you! How can I assist with today's meeting?",
                "Welcome! I'm here to help capture and analyze your discussion."
            ],
            'confirmation': [
                "I understand. Let me confirm: {details}",
                "Got it. So you want to {action}. Is that correct?",
                "Perfect. I've noted that {information}."
            ],
            'clarification': [
                "Could you please clarify {unclear_point}?",
                "I need a bit more information about {topic}.",
                "Can you help me understand {context} better?"
            ],
            'acknowledgment': [
                "Understood.",
                "I've got that recorded.",
                "Thanks for the information."
            ],
            'error': [
                "I'm sorry, I didn't catch that. Could you repeat?",
                "I'm having trouble understanding. Can you rephrase?",
                "Let me try again. What did you say?"
            ]
        }
    
    async def initialize(self):
        """Initialize the conversation service"""
        try:
            # Initialize OpenAI client
            openai_api_key = os.getenv('OPENAI_API_KEY')
            if openai_api_key:
                self.openai_client = openai.AsyncOpenAI(api_key=openai_api_key)
                logger.info("OpenAI client initialized for conversation service")
            
            logger.info("Conversation service initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize conversation service", error=str(e))
            raise
    
    async def start_conversation(self, session_id: str, meeting_id: str = None, 
                               participants: List[str] = None) -> ConversationSession:
        """Start a new conversation session"""
        try:
            session = ConversationSession(
                session_id=session_id,
                meeting_id=meeting_id,
                participants=participants or [],
                start_time=datetime.utcnow(),
                end_time=None,
                state=ConversationState.IDLE,
                turns=[],
                context={}
            )
            
            self.active_sessions[session_id] = session
            self.conversation_history[session_id] = []
            
            logger.info("Conversation session started", 
                       session_id=session_id, 
                       meeting_id=meeting_id,
                       participants=len(participants) if participants else 0)
            
            return session
            
        except Exception as e:
            logger.error("Failed to start conversation", error=str(e))
            raise
    
    async def process_conversation_turn(self, session_id: str, text: str, 
                                     speaker: str = None, intent: str = None,
                                     entities: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a conversation turn"""
        try:
            if session_id not in self.active_sessions:
                raise ValueError(f"No active session found: {session_id}")
            
            session = self.active_sessions[session_id]
            session.state = ConversationState.PROCESSING
            
            # Create conversation turn
            turn = ConversationTurn(
                turn_id=f"turn_{len(session.turns)}",
                timestamp=datetime.utcnow(),
                speaker=speaker,
                text=text,
                intent=intent,
                entities=entities or {},
                dialogue_act=await self._classify_dialogue_act(text, intent),
                confidence=0.8  # Placeholder
            )
            
            # Determine appropriate response
            response_data = await self._generate_contextual_response(session, turn)
            turn.response = response_data['text']
            turn.metadata = response_data.get('metadata', {})
            
            # Add turn to session
            session.turns.append(turn)
            self.conversation_history[session_id].append(turn)
            
            # Update conversation context
            await self._update_conversation_context(session, turn)
            
            # Update session state
            session.state = ConversationState.LISTENING
            
            logger.info("Conversation turn processed", 
                       session_id=session_id,
                       turn_id=turn.turn_id,
                       intent=intent,
                       dialogue_act=turn.dialogue_act.value)
            
            return {
                'turn_id': turn.turn_id,
                'response': turn.response,
                'dialogue_act': turn.dialogue_act.value,
                'next_actions': response_data.get('next_actions', []),
                'context_updates': response_data.get('context_updates', {}),
                'session_state': session.state.value
            }
            
        except Exception as e:
            logger.error("Failed to process conversation turn", error=str(e))
            if session_id in self.active_sessions:
                self.active_sessions[session_id].state = ConversationState.ERROR
            raise
    
    async def _classify_dialogue_act(self, text: str, intent: str = None) -> DialogueAct:
        """Classify the dialogue act of the utterance"""
        try:
            text_lower = text.lower().strip()
            
            # Simple rule-based classification
            if any(greeting in text_lower for greeting in ['hello', 'hi', 'good morning', 'good afternoon']):
                return DialogueAct.GREETING
            elif text_lower.endswith('?') or text_lower.startswith(('what', 'how', 'why', 'when', 'where', 'who')):
                return DialogueAct.QUESTION
            elif any(confirm in text_lower for confirm in ['yes', 'correct', 'right', 'exactly', 'that\'s right']):
                return DialogueAct.CONFIRMATION
            elif any(clarify in text_lower for clarify in ['what do you mean', 'can you clarify', 'i don\'t understand']):
                return DialogueAct.CLARIFICATION
            elif any(goodbye in text_lower for goodbye in ['bye', 'goodbye', 'see you', 'thanks', 'that\'s all']):
                return DialogueAct.GOODBYE
            elif intent in ['create_action', 'make_decision', 'schedule_followup']:
                return DialogueAct.REQUEST
            else:
                return DialogueAct.ANSWER
                
        except Exception as e:
            logger.error("Dialogue act classification failed", error=str(e))
            return DialogueAct.ACKNOWLEDGMENT
    
    async def _generate_contextual_response(self, session: ConversationSession, 
                                          turn: ConversationTurn) -> Dict[str, Any]:
        """Generate contextual response based on conversation state and history"""
        try:
            # Use OpenAI for sophisticated response generation if available
            if self.openai_client:
                return await self._generate_response_with_openai(session, turn)
            else:
                return await self._generate_response_with_templates(session, turn)
                
        except Exception as e:
            logger.error("Response generation failed", error=str(e))
            return {
                'text': "I understand. Please continue.",
                'metadata': {'generation_method': 'fallback'},
                'next_actions': [],
                'context_updates': {}
            }
    
    async def _generate_response_with_openai(self, session: ConversationSession, 
                                           turn: ConversationTurn) -> Dict[str, Any]:
        """Generate response using OpenAI"""
        try:
            # Build conversation context
            recent_turns = session.turns[-5:] if len(session.turns) > 5 else session.turns
            conversation_context = "\n".join([
                f"{t.speaker or 'User'}: {t.text}" + (f"\nAssistant: {t.response}" if t.response else "")
                for t in recent_turns
            ])
            
            prompt = f"""
            You are an AI meeting assistant helping to facilitate and analyze conversations.
            
            Current conversation context:
            {conversation_context}
            
            Latest input: "{turn.text}"
            Intent: {turn.intent}
            Dialogue Act: {turn.dialogue_act.value}
            Entities: {turn.entities}
            
            Session context:
            - Meeting ID: {session.meeting_id}
            - Participants: {', '.join(session.participants)}
            - Session state: {session.state.value}
            - Turn count: {len(session.turns)}
            
            Generate an appropriate response that:
            1. Acknowledges the input appropriately
            2. Provides helpful information or asks clarifying questions
            3. Suggests next actions if relevant
            4. Maintains professional and helpful tone
            
            Respond with JSON containing:
            - text: the response text
            - next_actions: array of suggested actions
            - context_updates: any context information to update
            - confidence: confidence in the response (0.0-1.0)
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional AI meeting assistant focused on helping teams collaborate effectively."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            # Parse response
            result_text = response.choices[0].message.content
            
            try:
                # Try to extract JSON from response
                json_start = result_text.find('{')
                json_end = result_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    result_json = json.loads(result_text[json_start:json_end])
                    return {
                        'text': result_json.get('text', result_text),
                        'next_actions': result_json.get('next_actions', []),
                        'context_updates': result_json.get('context_updates', {}),
                        'metadata': {
                            'generation_method': 'openai',
                            'confidence': result_json.get('confidence', 0.8)
                        }
                    }
            except:
                pass
            
            # Fallback to using the raw text
            return {
                'text': result_text,
                'next_actions': [],
                'context_updates': {},
                'metadata': {'generation_method': 'openai_fallback'}
            }
            
        except Exception as e:
            logger.error("OpenAI response generation failed", error=str(e))
            return await self._generate_response_with_templates(session, turn)
    
    async def _generate_response_with_templates(self, session: ConversationSession, 
                                             turn: ConversationTurn) -> Dict[str, Any]:
        """Generate response using templates"""
        try:
            response_type = turn.dialogue_act.value
            templates = self.response_templates.get(response_type, self.response_templates['acknowledgment'])
            
            # Select appropriate template
            template = templates[0]  # Simple selection for now
            
            # Fill in template variables
            response_text = template
            if '{' in template:
                # Simple template filling
                context_vars = {
                    'details': str(turn.entities),
                    'action': turn.intent or 'continue',
                    'information': turn.text[:50] + '...' if len(turn.text) > 50 else turn.text
                }
                
                for var, value in context_vars.items():
                    response_text = response_text.replace(f'{{{var}}}', str(value))
            
            # Determine next actions based on intent
            next_actions = []
            if turn.intent == 'start_meeting':
                next_actions = ['confirm_participants', 'set_agenda']
            elif turn.intent == 'create_action':
                next_actions = ['set_assignee', 'set_due_date']
            elif turn.intent == 'make_decision':
                next_actions = ['record_decision', 'notify_stakeholders']
            
            return {
                'text': response_text,
                'next_actions': next_actions,
                'context_updates': {},
                'metadata': {'generation_method': 'template'}
            }
            
        except Exception as e:
            logger.error("Template response generation failed", error=str(e))
            return {
                'text': "I understand.",
                'next_actions': [],
                'context_updates': {},
                'metadata': {'generation_method': 'fallback'}
            }
    
    async def _update_conversation_context(self, session: ConversationSession, turn: ConversationTurn):
        """Update conversation context with new information"""
        try:
            # Update participant tracking
            if turn.speaker and turn.speaker not in session.participants:
                session.participants.append(turn.speaker)
            
            # Update context with entities
            for entity_type, entity_value in turn.entities.items():
                if entity_type not in session.context:
                    session.context[entity_type] = []
                session.context[entity_type].append({
                    'value': entity_value,
                    'turn_id': turn.turn_id,
                    'timestamp': turn.timestamp.isoformat()
                })
            
            # Update intent tracking
            if turn.intent:
                if 'intents' not in session.context:
                    session.context['intents'] = []
                session.context['intents'].append({
                    'intent': turn.intent,
                    'turn_id': turn.turn_id,
                    'confidence': turn.confidence
                })
            
            # Update dialogue flow state
            session.context['last_dialogue_act'] = turn.dialogue_act.value
            session.context['turn_count'] = len(session.turns)
            
        except Exception as e:
            logger.error("Context update failed", error=str(e))
    
    async def end_conversation(self, session_id: str) -> Dict[str, Any]:
        """End a conversation session"""
        try:
            if session_id not in self.active_sessions:
                raise ValueError(f"No active session found: {session_id}")
            
            session = self.active_sessions[session_id]
            session.end_time = datetime.utcnow()
            session.state = ConversationState.IDLE
            
            # Generate conversation summary
            summary = await self._generate_conversation_summary(session)
            session.summary = summary
            
            # Archive session
            archived_session = {
                'session_id': session.session_id,
                'meeting_id': session.meeting_id,
                'participants': session.participants,
                'start_time': session.start_time.isoformat(),
                'end_time': session.end_time.isoformat(),
                'turn_count': len(session.turns),
                'summary': session.summary,
                'context': session.context
            }
            
            # Remove from active sessions
            del self.active_sessions[session_id]
            
            logger.info("Conversation session ended", 
                       session_id=session_id,
                       duration=(session.end_time - session.start_time).total_seconds(),
                       turns=len(session.turns))
            
            return archived_session
            
        except Exception as e:
            logger.error("Failed to end conversation", error=str(e))
            raise
    
    async def _generate_conversation_summary(self, session: ConversationSession) -> str:
        """Generate a summary of the conversation"""
        try:
            if not session.turns:
                return "No conversation content to summarize."
            
            # Extract key information
            key_intents = []
            key_entities = {}
            
            for turn in session.turns:
                if turn.intent:
                    key_intents.append(turn.intent)
                for entity_type, entity_value in turn.entities.items():
                    if entity_type not in key_entities:
                        key_entities[entity_type] = []
                    key_entities[entity_type].append(entity_value)
            
            # Create summary
            summary_parts = []
            summary_parts.append(f"Conversation with {len(session.participants)} participants")
            summary_parts.append(f"Duration: {(session.end_time - session.start_time).total_seconds():.0f} seconds")
            summary_parts.append(f"Total turns: {len(session.turns)}")
            
            if key_intents:
                intent_counts = {}
                for intent in key_intents:
                    intent_counts[intent] = intent_counts.get(intent, 0) + 1
                summary_parts.append(f"Main intents: {', '.join(intent_counts.keys())}")
            
            if key_entities:
                summary_parts.append(f"Key entities discussed: {', '.join(key_entities.keys())}")
            
            return ". ".join(summary_parts) + "."
            
        except Exception as e:
            logger.error("Conversation summary generation failed", error=str(e))
            return "Summary generation failed."
    
    async def get_conversation_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get current conversation state"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            return {
                'session_id': session.session_id,
                'state': session.state.value,
                'participants': session.participants,
                'turn_count': len(session.turns),
                'last_activity': session.turns[-1].timestamp.isoformat() if session.turns else session.start_time.isoformat(),
                'context_summary': {
                    'intents': list(set(turn.intent for turn in session.turns if turn.intent)),
                    'entities': list(session.context.keys()),
                    'dialogue_acts': list(set(turn.dialogue_act.value for turn in session.turns))
                }
            }
        return None
    
    async def get_conversation_history(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get conversation history for a session"""
        if session_id in self.conversation_history:
            turns = self.conversation_history[session_id][-limit:]
            return [
                {
                    'turn_id': turn.turn_id,
                    'timestamp': turn.timestamp.isoformat(),
                    'speaker': turn.speaker,
                    'text': turn.text,
                    'intent': turn.intent,
                    'dialogue_act': turn.dialogue_act.value,
                    'response': turn.response,
                    'confidence': turn.confidence
                }
                for turn in turns
            ]
        return []

# Global conversation service instance
conversation_service = ConversationService()