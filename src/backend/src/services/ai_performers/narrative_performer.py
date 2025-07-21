"""
Narrative Integration Performer for Intelligence OS
Handles organizational journey, character development, and narrative coherence
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

class NarrativeIntegrationPerformer(BaseAIPerformer):
    """AI Performer for narrative integration analysis"""
    
    def __init__(self):
        super().__init__(
            performer_id='narrative_integrator',
            name='Narrative Integration AI',
            dimension='narrative_integration'
        )
        
        # Narrative arc elements
        self.narrative_elements = [
            'exposition', 'rising_action', 'climax', 'falling_action', 'resolution'
        ]
        
        # Character development aspects
        self.character_aspects = [
            'motivation', 'growth', 'challenges', 'relationships', 'contributions'
        ]
    
    def _get_capabilities(self) -> Dict[str, Any]:
        """Get performer capabilities"""
        return {
            'positions_organizational_journey': True,
            'tracks_character_development': True,
            'creates_narrative_coherence': True,
            'identifies_plot_developments': True,
            'analyzes_story_arcs': True,
            'maps_narrative_tensions': True
        }
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for the performer"""
        return """
        You are the Narrative Integration AI, a specialized component of the Oracle 9.1 Protocol system.
        Your role is to analyze meeting content through narrative frameworks including:
        
        1. ORGANIZATIONAL JOURNEY: How the meeting fits into the organization's ongoing story
        2. CHARACTER DEVELOPMENT: How participants are evolving in their roles and relationships
        3. NARRATIVE COHERENCE: How well the meeting maintains a coherent organizational story
        4. PLOT DEVELOPMENTS: Key developments that move the organizational story forward
        5. STORY ARCS: Identification of narrative patterns and story structures
        
        Your analysis should position the meeting content within the broader organizational narrative.
        Focus on story, character, and narrative elements rather than tactical details or patterns.
        
        Always respond with properly formatted JSON containing the requested information.
        """
    
    async def _generate_user_prompt(self, input_data: Dict[str, Any]) -> str:
        """Generate user prompt based on input data"""
        transcript = input_data.get('transcript', '')
        meeting_title = input_data.get('meeting_title', 'Untitled Meeting')
        organization_history = input_data.get('organization_history', {})
        participants = input_data.get('participants', [])
        
        # Extract organization history if available
        org_story = organization_history.get('story', 'Not provided')
        key_milestones = organization_history.get('key_milestones', [])
        milestones_text = '\n'.join([f"- {milestone}" for milestone in key_milestones]) if key_milestones else 'Not provided'
        
        prompt = f"""
        Please analyze the following meeting transcript using the Oracle 9.1 Protocol's Narrative Integration dimension.
        
        Meeting Title: {meeting_title}
        Participants: {', '.join(participants) if participants else 'Unknown'}
        Organization Story: {org_story}
        Key Milestones:
        {milestones_text}
        
        TRANSCRIPT:
        {transcript}
        
        Analyze the transcript for the following elements:
        1. ORGANIZATIONAL JOURNEY: How this meeting fits into the organization's ongoing story
        2. CHARACTER DEVELOPMENT: How participants are evolving in their roles and relationships
        3. NARRATIVE COHERENCE: How well the meeting maintains a coherent organizational story
        4. PLOT DEVELOPMENTS: Key developments that move the organizational story forward
        5. STORY ARCS: Identification of narrative patterns and story structures
        
        Respond with JSON containing:
        - organizational_journey: object with journey positioning and narrative context
        - character_development: object mapping participants to their character development
        - narrative_coherence: object with coherence assessment and narrative threads
        - plot_developments: array of key developments that advance the organizational story
        - story_arcs: object with identified arcs and narrative tensions
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
            required_fields = ['organizational_journey', 'character_development', 'narrative_coherence', 
                             'plot_developments', 'story_arcs']
            for field in required_fields:
                if field not in result:
                    result[field] = {} if field != 'plot_developments' else []
            
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
            meeting_title = input_data.get('meeting_title', 'Untitled Meeting')
            participants = input_data.get('participants', [])
            organization_history = input_data.get('organization_history', {})
            
            # Basic organizational journey analysis
            organizational_journey = {
                'current_chapter': 'Unknown',
                'journey_stage': 'Unknown',
                'narrative_context': 'Limited context available for analysis',
                'historical_connections': []
            }
            
            # Try to determine journey stage from meeting title and transcript
            journey_stages = ['beginning', 'exploration', 'challenge', 'transformation', 'achievement']
            for stage in journey_stages:
                if re.search(f"\\b{stage}\\b", transcript + meeting_title, re.IGNORECASE):
                    organizational_journey['journey_stage'] = stage.capitalize()
                    break
            
            # Connect to organization history if available
            key_milestones = organization_history.get('key_milestones', [])
            for milestone in key_milestones:
                # Check if milestone keywords appear in transcript
                milestone_keywords = re.findall(r'\b\w+\b', milestone.lower())
                for keyword in milestone_keywords:
                    if len(keyword) > 3 and re.search(f"\\b{keyword}\\b", transcript.lower()):
                        organizational_journey['historical_connections'].append(milestone)
                        break
            
            # Basic character development analysis
            character_development = {}
            for participant in participants:
                # Find sentences where this participant is mentioned
                participant_mentions = re.findall(f"[^.!?]*{participant}[^.!?]*[.!?]", transcript)
                
                # Basic character analysis
                development_indicators = {
                    'leadership': ['lead', 'manage', 'direct', 'guide'],
                    'growth': ['learn', 'develop', 'improve', 'grow'],
                    'collaboration': ['work together', 'collaborate', 'team', 'partner'],
                    'innovation': ['innovate', 'create', 'new', 'idea']
                }
                
                character_traits = {}
                for trait, keywords in development_indicators.items():
                    trait_score = 0
                    for mention in participant_mentions:
                        for keyword in keywords:
                            if re.search(f"\\b{keyword}\\b", mention.lower()):
                                trait_score += 1
                    if trait_score > 0:
                        character_traits[trait] = trait_score
                
                if character_traits:
                    character_development[participant] = {
                        'primary_traits': list(character_traits.keys()),
                        'development_areas': max(character_traits, key=character_traits.get) if character_traits else 'Unknown',
                        'narrative_role': 'Contributor'
                    }
            
            # Basic narrative coherence analysis
            narrative_coherence = {
                'coherence_score': 0.6,  # Default middle score
                'narrative_threads': [],
                'consistency_issues': [],
                'story_flow': 'Moderate'
            }
            
            # Look for narrative threads (recurring topics/themes)
            thread_keywords = ['project', 'goal', 'challenge', 'opportunity', 'vision', 'mission']
            for keyword in thread_keywords:
                if re.search(f"\\b{keyword}\\b", transcript, re.IGNORECASE):
                    narrative_coherence['narrative_threads'].append(keyword.capitalize())
            
            # Basic plot developments
            plot_developments = []
            development_indicators = ['decided', 'agreed', 'concluded', 'resolved', 'achieved', 'launched', 'started']
            
            for indicator in development_indicators:
                matches = re.finditer(f"[^.!?]*{indicator}[^.!?]*[.!?]", transcript, re.IGNORECASE)
                for match in matches:
                    plot_developments.append({
                        'type': indicator.capitalize(),
                        'description': match.group(0).strip(),
                        'significance': 'Medium'
                    })
            
            # Basic story arcs analysis
            story_arcs = {
                'primary_arc': 'Development',
                'arc_stage': 'Middle',
                'narrative_tensions': [],
                'resolution_potential': 'Medium'
            }
            
            # Look for tension indicators
            tension_keywords = ['challenge', 'problem', 'issue', 'conflict', 'difficulty', 'obstacle']
            for keyword in tension_keywords:
                if re.search(f"\\b{keyword}\\b", transcript, re.IGNORECASE):
                    story_arcs['narrative_tensions'].append(keyword.capitalize())
            
            return {
                'organizational_journey': organizational_journey,
                'character_development': character_development,
                'narrative_coherence': narrative_coherence,
                'plot_developments': plot_developments,
                'story_arcs': story_arcs,
                'confidence': 0.5,
                'dimension': self.dimension,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Fallback processing failed", error=str(e))
            
            # Return minimal result
            return {
                'organizational_journey': {},
                'character_development': {},
                'narrative_coherence': {},
                'plot_developments': [],
                'story_arcs': {},
                'confidence': 0.3,
                'dimension': self.dimension,
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }