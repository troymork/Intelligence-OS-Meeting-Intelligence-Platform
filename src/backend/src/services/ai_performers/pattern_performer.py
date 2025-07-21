"""
Pattern Analysis Performer for Intelligence OS
Handles implicit patterns, emotional subtext, and recurring themes
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

class PatternAnalysisPerformer(BaseAIPerformer):
    """AI Performer for pattern and subtext analysis"""
    
    def __init__(self):
        super().__init__(
            performer_id='pattern_analyzer',
            name='Pattern Analysis AI',
            dimension='pattern_subtext'
        )
        
        # Emotion keywords for basic sentiment analysis
        self.emotion_keywords = {
            'positive': ['happy', 'excited', 'great', 'excellent', 'good', 'love', 'like', 'amazing', 'wonderful', 'fantastic'],
            'negative': ['sad', 'angry', 'frustrated', 'bad', 'terrible', 'hate', 'dislike', 'awful', 'horrible', 'disappointed'],
            'neutral': ['okay', 'fine', 'normal', 'average', 'standard', 'typical', 'regular', 'usual']
        }
        
        # Recurring theme patterns
        self.theme_patterns = [
            r'(?:always|constantly|repeatedly|keeps)\s+([^.!?]+)[.!?]',
            r'(?:again|once more|another time)\s+([^.!?]+)[.!?]',
            r'(?:pattern|trend|recurring|theme)\s+of\s+([^.!?]+)[.!?]',
            r'(?:every time|each time)\s+([^.!?]+)[.!?]'
        ]
        
        # Assumption patterns
        self.assumption_patterns = [
            r'(?:assume|assuming|assumption)\s+that\s+([^.!?]+)[.!?]',
            r'(?:presume|presuming|presumption)\s+that\s+([^.!?]+)[.!?]',
            r'(?:believe|believing|belief)\s+that\s+([^.!?]+)[.!?]',
            r'(?:expect|expecting|expectation)\s+that\s+([^.!?]+)[.!?]'
        ]
    
    def _get_capabilities(self) -> Dict[str, Any]:
        """Get performer capabilities"""
        return {
            'detects_implicit_patterns': True,
            'analyzes_emotional_subtext': True,
            'identifies_assumptions': True,
            'tracks_recurring_themes': True,
            'detects_communication_styles': True,
            'identifies_group_dynamics': True
        }
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for the performer"""
        return """
        You are the Pattern Analysis AI, a specialized component of the Oracle 9.1 Protocol system.
        Your role is to analyze meeting transcripts for implicit patterns and subtext including:
        
        1. IMPLICIT PATTERNS: Unstated dynamics, behaviors, and interactions that form patterns
        2. EMOTIONAL SUBTEXT: Underlying emotions, tensions, and psychological dynamics
        3. RECURRING THEMES: Topics, concerns, or ideas that repeatedly emerge
        4. UNSTATED ASSUMPTIONS: Beliefs and expectations that are implied but not explicitly stated
        5. COMMUNICATION STYLES: How participants communicate, interact, and respond to each other
        
        Your analysis should focus on what's happening beneath the surface - the implicit rather than explicit content.
        Do not focus on structural elements like decisions and action items - that's handled by other AI components.
        
        Always respond with properly formatted JSON containing the requested information.
        """
    
    async def _generate_user_prompt(self, input_data: Dict[str, Any]) -> str:
        """Generate user prompt based on input data"""
        transcript = input_data.get('transcript', '')
        meeting_title = input_data.get('meeting_title', 'Untitled Meeting')
        participants = input_data.get('participants', [])
        
        prompt = f"""
        Please analyze the following meeting transcript using the Oracle 9.1 Protocol's Pattern Subtext dimension.
        
        Meeting Title: {meeting_title}
        Participants: {', '.join(participants) if participants else 'Unknown'}
        
        TRANSCRIPT:
        {transcript}
        
        Analyze the transcript for the following elements:
        1. IMPLICIT PATTERNS: Unstated dynamics, behaviors, and interactions that form patterns
        2. EMOTIONAL SUBTEXT: Underlying emotions, tensions, and psychological dynamics
        3. RECURRING THEMES: Topics, concerns, or ideas that repeatedly emerge
        4. UNSTATED ASSUMPTIONS: Beliefs and expectations that are implied but not explicitly stated
        5. COMMUNICATION STYLES: How participants communicate, interact, and respond to each other
        
        Respond with JSON containing:
        - implicit_patterns: array of pattern objects with description and evidence
        - emotional_subtext: object mapping emotions to evidence and intensity
        - recurring_themes: array of theme objects with description and occurrences
        - unstated_assumptions: array of assumption objects with description and basis
        - communication_styles: object mapping participants to their communication style analysis
        - confidence: your confidence score (0.0-1.0) in the analysis accuracy
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
            required_fields = ['implicit_patterns', 'emotional_subtext', 'recurring_themes', 
                             'unstated_assumptions', 'communication_styles']
            for field in required_fields:
                if field not in result:
                    result[field] = [] if field != 'emotional_subtext' and field != 'communication_styles' else {}
            
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
            
            # Analyze emotional subtext using keyword matching
            emotional_subtext = {}
            for emotion, keywords in self.emotion_keywords.items():
                evidence = []
                for keyword in keywords:
                    # Find sentences containing this emotion keyword
                    sentences = re.findall(f"[^.!?]*{keyword}[^.!?]*[.!?]", transcript, re.IGNORECASE)
                    evidence.extend([s.strip() for s in sentences])
                
                if evidence:
                    emotional_subtext[emotion] = {
                        'evidence': evidence[:3],  # Limit to 3 examples
                        'intensity': min(1.0, len(evidence) / 5)  # Scale intensity based on occurrences
                    }
            
            # Extract recurring themes using regex patterns
            recurring_themes = []
            for pattern in self.theme_patterns:
                matches = re.finditer(pattern, transcript, re.IGNORECASE)
                for match in matches:
                    recurring_themes.append({
                        'description': match.group(1).strip(),
                        'occurrences': 1
                    })
            
            # Deduplicate themes
            unique_themes = {}
            for theme in recurring_themes:
                if theme['description'] in unique_themes:
                    unique_themes[theme['description']]['occurrences'] += 1
                else:
                    unique_themes[theme['description']] = theme
            recurring_themes = list(unique_themes.values())
            
            # Extract unstated assumptions using regex patterns
            unstated_assumptions = []
            for pattern in self.assumption_patterns:
                matches = re.finditer(pattern, transcript, re.IGNORECASE)
                for match in matches:
                    unstated_assumptions.append({
                        'description': match.group(1).strip(),
                        'basis': 'Explicit statement of assumption'
                    })
            
            # Simple communication styles analysis
            communication_styles = {}
            participant_list = input_data.get('participants', [])
            for participant in participant_list:
                # Find sentences spoken by this participant
                sentences = re.findall(f"{participant}[^.!?]*[.!?]", transcript)
                if sentences:
                    # Very basic style analysis
                    question_count = sum(1 for s in sentences if '?' in s)
                    exclamation_count = sum(1 for s in sentences if '!' in s)
                    avg_length = sum(len(s) for s in sentences) / len(sentences) if sentences else 0
                    
                    style = 'Neutral'
                    if question_count > len(sentences) * 0.3:
                        style = 'Inquisitive'
                    elif exclamation_count > len(sentences) * 0.3:
                        style = 'Emphatic'
                    elif avg_length > 100:
                        style = 'Detailed'
                    elif avg_length < 30:
                        style = 'Concise'
                    
                    communication_styles[participant] = {
                        'style': style,
                        'question_ratio': question_count / len(sentences) if sentences else 0,
                        'emphasis_ratio': exclamation_count / len(sentences) if sentences else 0,
                        'avg_statement_length': avg_length
                    }
            
            # Identify implicit patterns (very basic approach)
            implicit_patterns = []
            if len(recurring_themes) > 0:
                implicit_patterns.append({
                    'description': 'Recurring discussion patterns',
                    'evidence': [theme['description'] for theme in recurring_themes[:2]]
                })
            
            if 'negative' in emotional_subtext and emotional_subtext['negative']['intensity'] > 0.5:
                implicit_patterns.append({
                    'description': 'Underlying tension or frustration',
                    'evidence': emotional_subtext['negative']['evidence'][:2]
                })
            
            return {
                'implicit_patterns': implicit_patterns,
                'emotional_subtext': emotional_subtext,
                'recurring_themes': recurring_themes,
                'unstated_assumptions': unstated_assumptions,
                'communication_styles': communication_styles,
                'confidence': 0.6,
                'dimension': self.dimension,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Fallback processing failed", error=str(e))
            
            # Return minimal result
            return {
                'implicit_patterns': [],
                'emotional_subtext': {},
                'recurring_themes': [],
                'unstated_assumptions': [],
                'communication_styles': {},
                'confidence': 0.3,
                'dimension': self.dimension,
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }