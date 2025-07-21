"""
Structural Extraction Performer for Intelligence OS
Handles explicit statements, decisions, and actions extraction
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import re
import json
import structlog

from .base_performer import BaseAIPerformer

logger = structlog.get_logger(__name__)

class StructuralExtractionPerformer(BaseAIPerformer):
    """AI Performer for structural extraction analysis"""
    
    def __init__(self):
        super().__init__(
            performer_id='structural_extractor',
            name='Structural Extraction AI',
            dimension='structural_extraction'
        )
        
        # Patterns for fallback extraction
        self.decision_patterns = [
            r'(?:we|they)\s+decided\s+to\s+([^.!?]+)[.!?]',
            r'(?:the|our)\s+decision\s+(?:is|was)\s+to\s+([^.!?]+)[.!?]',
            r'(?:we|they)\s+agreed\s+to\s+([^.!?]+)[.!?]',
            r'(?:we|they)\s+concluded\s+that\s+([^.!?]+)[.!?]'
        ]
        
        self.action_patterns = [
            r'(?:will|should|must|going to)\s+([^.!?]+)[.!?]',
            r'action\s+item[s]?:\s+([^.!?]+)[.!?]',
            r'task[s]?:\s+([^.!?]+)[.!?]',
            r'(?:assigned|tasked)\s+to\s+([^.!?]+)[.!?]'
        ]
        
        self.key_point_patterns = [
            r'key\s+point[s]?:\s+([^.!?]+)[.!?]',
            r'important\s+(?:to note|point):\s+([^.!?]+)[.!?]',
            r'critical\s+(?:that|to)\s+([^.!?]+)[.!?]',
            r'highlight\s+that\s+([^.!?]+)[.!?]'
        ]
    
    def _get_capabilities(self) -> Dict[str, Any]:
        """Get performer capabilities"""
        return {
            'extracts_decisions': True,
            'identifies_actions': True,
            'organizes_chronologically': True,
            'maps_agenda_items': True,
            'extracts_key_points': True,
            'identifies_participants': True
        }
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for the performer"""
        return """
        You are the Structural Extraction AI, a specialized component of the Oracle 9.1 Protocol system.
        Your role is to analyze meeting transcripts and extract explicit structural elements including:
        
        1. DECISIONS: Formal conclusions, agreements, and determinations made by participants
        2. ACTION ITEMS: Tasks, assignments, and follow-up activities with owners and timelines
        3. KEY POINTS: Important statements, facts, and explicit information shared
        4. PARTICIPANTS: People involved and their key contributions
        5. TOPICS: Subject matter discussed in chronological order
        
        For each element, provide specific implementation details and context.
        
        Your analysis should be factual, precise, and focus only on what was explicitly stated.
        Do not interpret implicit meanings, patterns, or emotional subtext - that's handled by other AI components.
        
        Always respond with properly formatted JSON containing the requested information.
        """
    
    async def _generate_user_prompt(self, input_data: Dict[str, Any]) -> str:
        """Generate user prompt based on input data"""
        transcript = input_data.get('transcript', '')
        meeting_title = input_data.get('meeting_title', 'Untitled Meeting')
        participants = input_data.get('participants', [])
        
        prompt = f"""
        Please analyze the following meeting transcript using the Oracle 9.1 Protocol's Structural Extraction dimension.
        
        Meeting Title: {meeting_title}
        Participants: {', '.join(participants) if participants else 'Unknown'}
        
        TRANSCRIPT:
        {transcript}
        
        Extract and organize the following elements:
        1. DECISIONS: All formal decisions made during the meeting with their rationale and stakeholders
        2. ACTION ITEMS: All action items with assignees, due dates (if mentioned), and priority
        3. KEY POINTS: Important explicit statements and information shared
        4. PARTICIPANTS: Key contributions from each participant
        5. TOPICS: Main topics discussed in chronological order
        
        Respond with JSON containing:
        - decisions: array of decision objects with text, rationale, and stakeholders
        - action_items: array of action objects with text, assignee, due_date, and priority
        - key_points: array of important statements
        - participants: object mapping participant names to their contributions
        - topics: array of topics in chronological order
        - confidence: your confidence score (0.0-1.0) in the extraction accuracy
        """
        
        return prompt
    
    async def _process_response(self, response_text: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process AI response"""
        try:
            # Extract JSON from response
            result = self._extract_json_from_text(response_text)
            
            if not result:
                # If JSON extraction failed, use fallback
                return await self._fallback_processing(input_data)
            
            # Ensure required fields exist
            required_fields = ['decisions', 'action_items', 'key_points', 'participants', 'topics']
            for field in required_fields:
                if field not in result:
                    result[field] = [] if field != 'participants' else {}
            
            # Set confidence if not provided
            if 'confidence' not in result:
                result['confidence'] = 0.8
            
            # Add metadata
            result['dimension'] = self.dimension
            result['timestamp'] = datetime.utcnow().isoformat()
            
            return result
            
        except Exception as e:
            logger.error("Response processing failed", error=str(e))
            return await self._fallback_processing(input_data)
    
    async def _fallback_processing(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback processing implementation"""
        try:
            transcript = input_data.get('transcript', '')
            
            # Extract decisions using regex patterns
            decisions = []
            for pattern in self.decision_patterns:
                matches = re.finditer(pattern, transcript, re.IGNORECASE)
                for match in matches:
                    decisions.append({
                        'text': match.group(1).strip(),
                        'rationale': '',
                        'stakeholders': []
                    })
            
            # Extract action items using regex patterns
            action_items = []
            for pattern in self.action_patterns:
                matches = re.finditer(pattern, transcript, re.IGNORECASE)
                for match in matches:
                    action_items.append({
                        'text': match.group(1).strip(),
                        'assignee': '',
                        'due_date': '',
                        'priority': 'medium'
                    })
            
            # Extract key points using regex patterns
            key_points = []
            for pattern in self.key_point_patterns:
                matches = re.finditer(pattern, transcript, re.IGNORECASE)
                for match in matches:
                    key_points.append(match.group(1).strip())
            
            # Extract participants (simple approach)
            participants = {}
            participant_list = input_data.get('participants', [])
            for participant in participant_list:
                # Find sentences containing this participant's name
                sentences = re.findall(f"[^.!?]*{participant}[^.!?]*[.!?]", transcript)
                if sentences:
                    participants[participant] = [s.strip() for s in sentences[:3]]  # Limit to 3 contributions
            
            # Extract topics (simple approach - use paragraph breaks)
            paragraphs = transcript.split('\n\n')
            topics = [p[:50].strip() + '...' for p in paragraphs if len(p.strip()) > 10][:5]  # First 5 topics
            
            return {
                'decisions': decisions,
                'action_items': action_items,
                'key_points': key_points,
                'participants': participants,
                'topics': topics,
                'confidence': 0.6,
                'dimension': self.dimension,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Fallback processing failed", error=str(e))
            
            # Return minimal result
            return {
                'decisions': [],
                'action_items': [],
                'key_points': [],
                'participants': {},
                'topics': [],
                'confidence': 0.3,
                'dimension': self.dimension,
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }