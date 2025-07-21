"""
Natural Language Understanding Service for Intelligence OS
Handles intent recognition, entity extraction, and conversation context
"""

import os
import re
import json
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import openai
from dataclasses import dataclass
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import structlog

logger = structlog.get_logger(__name__)

@dataclass
class Intent:
    """Intent classification result"""
    name: str
    confidence: float
    entities: Dict[str, Any]
    context: Dict[str, Any]

@dataclass
class Entity:
    """Named entity extraction result"""
    text: str
    label: str
    start: int
    end: int
    confidence: float
    metadata: Dict[str, Any]

@dataclass
class ConversationContext:
    """Conversation context tracking"""
    session_id: str
    user_id: Optional[str]
    current_intent: Optional[str]
    entities: Dict[str, Any]
    conversation_history: List[Dict[str, Any]]
    meeting_context: Optional[Dict[str, Any]]
    last_updated: datetime

class NLUService:
    """Natural Language Understanding Service"""
    
    def __init__(self):
        self.openai_client = None
        self.spacy_model = None
        self.intent_classifier = None
        self.entity_extractor = None
        self.conversation_contexts: Dict[str, ConversationContext] = {}
        
        # Predefined intents for meeting intelligence
        self.meeting_intents = {
            'start_meeting': {
                'patterns': [
                    'start meeting', 'begin meeting', 'let\'s start', 'commence meeting',
                    'start recording', 'begin session', 'initiate meeting'
                ],
                'entities': ['meeting_title', 'participants', 'agenda']
            },
            'end_meeting': {
                'patterns': [
                    'end meeting', 'finish meeting', 'conclude meeting', 'stop recording',
                    'wrap up', 'meeting over', 'that\'s all'
                ],
                'entities': ['action_items', 'next_steps']
            },
            'create_action': {
                'patterns': [
                    'create action', 'add task', 'assign to', 'action item',
                    'follow up', 'todo', 'task for'
                ],
                'entities': ['assignee', 'due_date', 'priority', 'description']
            },
            'make_decision': {
                'patterns': [
                    'we decided', 'decision made', 'agreed on', 'consensus',
                    'resolved', 'concluded', 'determined'
                ],
                'entities': ['decision_text', 'rationale', 'stakeholders']
            },
            'identify_issue': {
                'patterns': [
                    'problem with', 'issue', 'concern', 'challenge',
                    'blocker', 'obstacle', 'difficulty'
                ],
                'entities': ['issue_type', 'severity', 'impact']
            },
            'request_summary': {
                'patterns': [
                    'summarize', 'summary', 'recap', 'overview',
                    'what did we discuss', 'key points'
                ],
                'entities': ['summary_type', 'time_range']
            },
            'ask_question': {
                'patterns': [
                    'what is', 'how do', 'why', 'when', 'where',
                    'can you explain', 'help me understand'
                ],
                'entities': ['question_topic', 'context']
            },
            'provide_update': {
                'patterns': [
                    'update on', 'status update', 'progress report',
                    'current status', 'where we stand'
                ],
                'entities': ['project', 'status', 'metrics']
            },
            'schedule_followup': {
                'patterns': [
                    'schedule', 'follow up', 'next meeting', 'book time',
                    'calendar', 'set up meeting'
                ],
                'entities': ['date', 'time', 'participants', 'purpose']
            },
            'analyze_sentiment': {
                'patterns': [
                    'how do people feel', 'team sentiment', 'mood',
                    'satisfaction', 'concerns', 'feedback'
                ],
                'entities': ['sentiment_target', 'time_period']
            }
        }
        
        # Entity patterns for extraction
        self.entity_patterns = {
            'person': r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'date': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b',
            'time': r'\b\d{1,2}:\d{2}(?:\s?[AaPp][Mm])?\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'url': r'https?://[^\s]+',
            'money': r'\$\d+(?:,\d{3})*(?:\.\d{2})?',
            'percentage': r'\d+(?:\.\d+)?%'
        }
    
    async def initialize(self):
        """Initialize the NLU service"""
        try:
            # Initialize OpenAI client
            openai_api_key = os.getenv('OPENAI_API_KEY')
            if openai_api_key:
                self.openai_client = openai.AsyncOpenAI(api_key=openai_api_key)
                logger.info("OpenAI client initialized for NLU")
            
            # Initialize spaCy model
            try:
                self.spacy_model = spacy.load("en_core_web_sm")
                logger.info("spaCy model loaded")
            except OSError:
                logger.warning("spaCy model not found, using basic NER")
                self.spacy_model = None
            
            # Initialize intent classifier
            await self._initialize_intent_classifier()
            
            logger.info("NLU service initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize NLU service", error=str(e))
            raise
    
    async def _initialize_intent_classifier(self):
        """Initialize the intent classification system"""
        try:
            # Create training data from predefined intents
            training_texts = []
            training_labels = []
            
            for intent_name, intent_data in self.meeting_intents.items():
                for pattern in intent_data['patterns']:
                    training_texts.append(pattern)
                    training_labels.append(intent_name)
            
            # Initialize TF-IDF vectorizer
            self.intent_vectorizer = TfidfVectorizer(
                ngram_range=(1, 3),
                max_features=1000,
                stop_words='english'
            )
            
            # Fit vectorizer on training data
            self.intent_vectors = self.intent_vectorizer.fit_transform(training_texts)
            self.intent_labels = training_labels
            
            logger.info("Intent classifier initialized", 
                       intents=len(self.meeting_intents),
                       patterns=len(training_texts))
            
        except Exception as e:
            logger.error("Failed to initialize intent classifier", error=str(e))
            raise
    
    async def process_text(self, text: str, session_id: str = None, user_id: str = None, 
                          meeting_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process text for NLU analysis"""
        try:
            logger.info("Processing text for NLU", text_length=len(text), session_id=session_id)
            
            # Get or create conversation context
            context = await self._get_conversation_context(session_id, user_id, meeting_context)
            
            # Perform intent classification
            intent = await self._classify_intent(text, context)
            
            # Extract entities
            entities = await self._extract_entities(text, intent)
            
            # Update conversation context
            await self._update_conversation_context(context, text, intent, entities)
            
            # Generate response based on intent
            response = await self._generate_response(intent, entities, context)
            
            result = {
                'intent': {
                    'name': intent.name,
                    'confidence': intent.confidence,
                    'entities': intent.entities
                },
                'entities': [
                    {
                        'text': entity.text,
                        'label': entity.label,
                        'start': entity.start,
                        'end': entity.end,
                        'confidence': entity.confidence
                    } for entity in entities
                ],
                'response': response,
                'context': {
                    'session_id': context.session_id,
                    'current_intent': context.current_intent,
                    'conversation_turn': len(context.conversation_history)
                }
            }
            
            logger.info("NLU processing completed", 
                       intent=intent.name,
                       entities_found=len(entities),
                       confidence=intent.confidence)
            
            return result
            
        except Exception as e:
            logger.error("NLU processing failed", error=str(e))
            raise
    
    async def _get_conversation_context(self, session_id: str, user_id: str = None, 
                                      meeting_context: Dict[str, Any] = None) -> ConversationContext:
        """Get or create conversation context"""
        if session_id not in self.conversation_contexts:
            self.conversation_contexts[session_id] = ConversationContext(
                session_id=session_id,
                user_id=user_id,
                current_intent=None,
                entities={},
                conversation_history=[],
                meeting_context=meeting_context,
                last_updated=datetime.utcnow()
            )
        
        return self.conversation_contexts[session_id]
    
    async def _classify_intent(self, text: str, context: ConversationContext) -> Intent:
        """Classify intent from text"""
        try:
            # Use OpenAI for sophisticated intent classification if available
            if self.openai_client:
                return await self._classify_intent_with_openai(text, context)
            else:
                return await self._classify_intent_with_tfidf(text, context)
                
        except Exception as e:
            logger.error("Intent classification failed", error=str(e))
            # Return default intent
            return Intent(
                name='unknown',
                confidence=0.0,
                entities={},
                context={}
            )
    
    async def _classify_intent_with_openai(self, text: str, context: ConversationContext) -> Intent:
        """Classify intent using OpenAI"""
        try:
            # Create prompt for intent classification
            intent_list = list(self.meeting_intents.keys())
            
            prompt = f"""
            Analyze the following text and classify the intent for a meeting intelligence system.
            
            Text: "{text}"
            
            Available intents: {', '.join(intent_list)}
            
            Consider the conversation context:
            - Current intent: {context.current_intent}
            - Recent conversation: {context.conversation_history[-3:] if context.conversation_history else 'None'}
            - Meeting context: {context.meeting_context}
            
            Respond with JSON containing:
            - intent: the most likely intent name
            - confidence: confidence score (0.0-1.0)
            - entities: any relevant entities extracted
            - reasoning: brief explanation
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert at understanding meeting-related intents and extracting relevant information."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            # Parse response
            result_text = response.choices[0].message.content
            
            # Try to extract JSON from response
            try:
                import json
                # Find JSON in the response
                json_start = result_text.find('{')
                json_end = result_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    result_json = json.loads(result_text[json_start:json_end])
                    
                    return Intent(
                        name=result_json.get('intent', 'unknown'),
                        confidence=float(result_json.get('confidence', 0.5)),
                        entities=result_json.get('entities', {}),
                        context={'reasoning': result_json.get('reasoning', '')}
                    )
            except:
                pass
            
            # Fallback to TF-IDF if OpenAI parsing fails
            return await self._classify_intent_with_tfidf(text, context)
            
        except Exception as e:
            logger.error("OpenAI intent classification failed", error=str(e))
            return await self._classify_intent_with_tfidf(text, context)
    
    async def _classify_intent_with_tfidf(self, text: str, context: ConversationContext) -> Intent:
        """Classify intent using TF-IDF similarity"""
        try:
            # Vectorize input text
            text_vector = self.intent_vectorizer.transform([text.lower()])
            
            # Calculate similarities
            similarities = cosine_similarity(text_vector, self.intent_vectors)[0]
            
            # Find best match
            best_idx = np.argmax(similarities)
            best_score = similarities[best_idx]
            best_intent = self.intent_labels[best_idx]
            
            # Apply context boost
            if context.current_intent and context.current_intent == best_intent:
                best_score = min(1.0, best_score * 1.2)  # Boost continuing intent
            
            return Intent(
                name=best_intent,
                confidence=float(best_score),
                entities={},
                context={'method': 'tfidf'}
            )
            
        except Exception as e:
            logger.error("TF-IDF intent classification failed", error=str(e))
            return Intent(
                name='unknown',
                confidence=0.0,
                entities={},
                context={}
            )
    
    async def _extract_entities(self, text: str, intent: Intent) -> List[Entity]:
        """Extract entities from text"""
        entities = []
        
        try:
            # Use spaCy for named entity recognition if available
            if self.spacy_model:
                entities.extend(await self._extract_entities_with_spacy(text))
            
            # Use regex patterns for specific entities
            entities.extend(await self._extract_entities_with_regex(text))
            
            # Use OpenAI for context-aware entity extraction
            if self.openai_client and intent.name != 'unknown':
                openai_entities = await self._extract_entities_with_openai(text, intent)
                entities.extend(openai_entities)
            
            # Remove duplicates and merge overlapping entities
            entities = await self._merge_entities(entities)
            
            return entities
            
        except Exception as e:
            logger.error("Entity extraction failed", error=str(e))
            return []
    
    async def _extract_entities_with_spacy(self, text: str) -> List[Entity]:
        """Extract entities using spaCy"""
        entities = []
        
        try:
            doc = self.spacy_model(text)
            
            for ent in doc.ents:
                entities.append(Entity(
                    text=ent.text,
                    label=ent.label_,
                    start=ent.start_char,
                    end=ent.end_char,
                    confidence=0.8,  # spaCy doesn't provide confidence scores
                    metadata={'source': 'spacy'}
                ))
                
        except Exception as e:
            logger.error("spaCy entity extraction failed", error=str(e))
        
        return entities
    
    async def _extract_entities_with_regex(self, text: str) -> List[Entity]:
        """Extract entities using regex patterns"""
        entities = []
        
        try:
            for entity_type, pattern in self.entity_patterns.items():
                matches = re.finditer(pattern, text, re.IGNORECASE)
                
                for match in matches:
                    entities.append(Entity(
                        text=match.group(),
                        label=entity_type,
                        start=match.start(),
                        end=match.end(),
                        confidence=0.9,
                        metadata={'source': 'regex', 'pattern': pattern}
                    ))
                    
        except Exception as e:
            logger.error("Regex entity extraction failed", error=str(e))
        
        return entities
    
    async def _extract_entities_with_openai(self, text: str, intent: Intent) -> List[Entity]:
        """Extract entities using OpenAI with intent context"""
        entities = []
        
        try:
            # Get expected entities for this intent
            expected_entities = self.meeting_intents.get(intent.name, {}).get('entities', [])
            
            if not expected_entities:
                return entities
            
            prompt = f"""
            Extract the following types of entities from the text:
            
            Text: "{text}"
            Intent: {intent.name}
            Expected entities: {', '.join(expected_entities)}
            
            For each entity found, provide:
            - text: the exact text span
            - type: the entity type
            - start: character start position
            - end: character end position
            - confidence: confidence score (0.0-1.0)
            
            Respond with JSON array of entities.
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert at extracting structured information from meeting conversations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=300
            )
            
            # Parse response
            result_text = response.choices[0].message.content
            
            try:
                # Find JSON array in response
                json_start = result_text.find('[')
                json_end = result_text.rfind(']') + 1
                if json_start >= 0 and json_end > json_start:
                    entities_json = json.loads(result_text[json_start:json_end])
                    
                    for entity_data in entities_json:
                        entities.append(Entity(
                            text=entity_data.get('text', ''),
                            label=entity_data.get('type', 'unknown'),
                            start=int(entity_data.get('start', 0)),
                            end=int(entity_data.get('end', 0)),
                            confidence=float(entity_data.get('confidence', 0.5)),
                            metadata={'source': 'openai'}
                        ))
            except:
                pass
                
        except Exception as e:
            logger.error("OpenAI entity extraction failed", error=str(e))
        
        return entities
    
    async def _merge_entities(self, entities: List[Entity]) -> List[Entity]:
        """Merge overlapping entities and remove duplicates"""
        if not entities:
            return entities
        
        # Sort by start position
        entities.sort(key=lambda x: x.start)
        
        merged = []
        current = entities[0]
        
        for next_entity in entities[1:]:
            # Check for overlap
            if next_entity.start <= current.end:
                # Merge entities - keep the one with higher confidence
                if next_entity.confidence > current.confidence:
                    current = Entity(
                        text=next_entity.text,
                        label=next_entity.label,
                        start=min(current.start, next_entity.start),
                        end=max(current.end, next_entity.end),
                        confidence=next_entity.confidence,
                        metadata={**current.metadata, **next_entity.metadata}
                    )
                else:
                    current = Entity(
                        text=current.text,
                        label=current.label,
                        start=min(current.start, next_entity.start),
                        end=max(current.end, next_entity.end),
                        confidence=current.confidence,
                        metadata={**current.metadata, **next_entity.metadata}
                    )
            else:
                merged.append(current)
                current = next_entity
        
        merged.append(current)
        return merged
    
    async def _update_conversation_context(self, context: ConversationContext, 
                                         text: str, intent: Intent, entities: List[Entity]):
        """Update conversation context with new information"""
        # Add to conversation history
        context.conversation_history.append({
            'timestamp': datetime.utcnow().isoformat(),
            'text': text,
            'intent': intent.name,
            'confidence': intent.confidence,
            'entities': [{'text': e.text, 'label': e.label} for e in entities]
        })
        
        # Keep only last 10 turns
        if len(context.conversation_history) > 10:
            context.conversation_history = context.conversation_history[-10:]
        
        # Update current intent
        context.current_intent = intent.name
        
        # Update entities
        for entity in entities:
            if entity.label not in context.entities:
                context.entities[entity.label] = []
            context.entities[entity.label].append({
                'text': entity.text,
                'confidence': entity.confidence,
                'timestamp': datetime.utcnow().isoformat()
            })
        
        # Update timestamp
        context.last_updated = datetime.utcnow()
    
    async def _generate_response(self, intent: Intent, entities: List[Entity], 
                               context: ConversationContext) -> Dict[str, Any]:
        """Generate appropriate response based on intent and entities"""
        response = {
            'type': 'acknowledgment',
            'message': 'I understand.',
            'actions': [],
            'suggestions': []
        }
        
        try:
            if intent.name == 'start_meeting':
                response.update({
                    'type': 'meeting_control',
                    'message': 'Starting meeting recording and analysis.',
                    'actions': ['start_recording', 'initialize_analysis'],
                    'suggestions': ['Set meeting agenda', 'Add participants']
                })
            
            elif intent.name == 'end_meeting':
                response.update({
                    'type': 'meeting_control',
                    'message': 'Ending meeting and generating summary.',
                    'actions': ['stop_recording', 'generate_summary'],
                    'suggestions': ['Review action items', 'Schedule follow-up']
                })
            
            elif intent.name == 'create_action':
                response.update({
                    'type': 'action_creation',
                    'message': 'Creating action item.',
                    'actions': ['create_action_item'],
                    'suggestions': ['Set due date', 'Assign owner', 'Set priority']
                })
            
            elif intent.name == 'make_decision':
                response.update({
                    'type': 'decision_tracking',
                    'message': 'Recording decision.',
                    'actions': ['record_decision'],
                    'suggestions': ['Document rationale', 'Identify stakeholders']
                })
            
            elif intent.name == 'request_summary':
                response.update({
                    'type': 'information_request',
                    'message': 'Generating summary.',
                    'actions': ['generate_summary'],
                    'suggestions': ['Specify time range', 'Choose summary type']
                })
            
            elif intent.name == 'ask_question':
                response.update({
                    'type': 'question_answering',
                    'message': 'Let me help you with that.',
                    'actions': ['search_knowledge', 'provide_answer'],
                    'suggestions': ['Provide more context', 'Ask follow-up questions']
                })
            
            # Add entity-specific information to response
            if entities:
                response['extracted_info'] = {
                    entity.label: entity.text for entity in entities
                }
            
        except Exception as e:
            logger.error("Response generation failed", error=str(e))
        
        return response
    
    async def get_conversation_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation context for a session"""
        if session_id in self.conversation_contexts:
            context = self.conversation_contexts[session_id]
            return {
                'session_id': context.session_id,
                'user_id': context.user_id,
                'current_intent': context.current_intent,
                'entities': context.entities,
                'conversation_turns': len(context.conversation_history),
                'last_updated': context.last_updated.isoformat()
            }
        return None
    
    async def clear_conversation_context(self, session_id: str):
        """Clear conversation context for a session"""
        if session_id in self.conversation_contexts:
            del self.conversation_contexts[session_id]
            logger.info("Conversation context cleared", session_id=session_id)

# Global NLU service instance
nlu_service = NLUService()