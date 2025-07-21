"""
Human Needs Performer for Intelligence OS
Handles human needs analysis, fulfillment strategies, and intervention recommendations
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
from ..human_needs_engine import human_needs_engine

logger = structlog.get_logger(__name__)

class HumanNeedsPerformer(BaseAIPerformer):
    """AI Performer for human needs dynamics analysis"""
    
    def __init__(self):
        super().__init__(
            performer_id='human_needs_analyzer',
            name='Human Needs Dynamics AI',
            dimension='human_needs_dynamics'
        )
        
        # Maslow's hierarchy of needs
        self.maslow_needs = {
            'physiological': ['food', 'water', 'shelter', 'sleep', 'health'],
            'safety': ['security', 'stability', 'protection', 'order', 'law'],
            'love_belonging': ['friendship', 'intimacy', 'family', 'connection', 'community'],
            'esteem': ['respect', 'recognition', 'achievement', 'confidence', 'status'],
            'self_actualization': ['creativity', 'problem_solving', 'morality', 'acceptance', 'meaning']
        }
        
        # Max-Neef fundamental human needs
        self.max_neef_needs = [
            'subsistence', 'protection', 'affection', 'understanding', 'participation',
            'leisure', 'creation', 'identity', 'freedom'
        ]
        
        # Intervention types
        self.intervention_types = [
            'individual', 'team', 'organizational', 'systemic', 'cultural'
        ]
    
    def _get_capabilities(self) -> Dict[str, Any]:
        """Get performer capabilities"""
        return {
            'analyzes_human_needs': True,
            'identifies_fulfillment_gaps': True,
            'recommends_interventions': True,
            'maps_need_satisfaction': True,
            'assesses_wellbeing_factors': True,
            'designs_support_strategies': True
        }
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for the performer"""
        return """
        You are the Human Needs Dynamics AI, a specialized component of the Oracle 9.1 Protocol system.
        Your role is to analyze meeting content for human needs and wellbeing elements including:
        
        1. HUMAN NEEDS ANALYSIS: Identification of expressed and unexpressed human needs
        2. FULFILLMENT ASSESSMENT: How well current approaches meet human needs
        3. INTERVENTION STRATEGIES: Recommendations to better support human flourishing
        4. WELLBEING FACTORS: Elements that contribute to or detract from wellbeing
        5. SUPPORT MECHANISMS: Systems and approaches to enhance human needs fulfillment
        
        Use frameworks like Maslow's hierarchy and Max-Neef's fundamental human needs.
        Focus on human-centered analysis rather than technical or strategic elements.
        
        Always respond with properly formatted JSON containing the requested information.
        """
    
    async def _generate_user_prompt(self, input_data: Dict[str, Any]) -> str:
        """Generate user prompt based on input data"""
        transcript = input_data.get('transcript', '')
        meeting_title = input_data.get('meeting_title', 'Untitled Meeting')
        participants = input_data.get('participants', [])
        team_context = input_data.get('team_context', {})
        
        # Extract team context if available
        team_size = team_context.get('size', 'Unknown')
        team_dynamics = team_context.get('dynamics', 'Unknown')
        
        prompt = f"""
        Please analyze the following meeting transcript using the Oracle 9.1 Protocol's Human Needs Dynamics dimension.
        
        Meeting Title: {meeting_title}
        Participants: {', '.join(participants) if participants else 'Unknown'}
        Team Size: {team_size}
        Team Dynamics: {team_dynamics}
        
        TRANSCRIPT:
        {transcript}
        
        Analyze the transcript for the following elements:
        1. HUMAN NEEDS ANALYSIS: Identification of expressed and unexpressed human needs
        2. FULFILLMENT ASSESSMENT: How well current approaches meet human needs
        3. INTERVENTION STRATEGIES: Recommendations to better support human flourishing
        4. WELLBEING FACTORS: Elements that contribute to or detract from wellbeing
        5. SUPPORT MECHANISMS: Systems and approaches to enhance human needs fulfillment
        
        Use frameworks like Maslow's hierarchy and Max-Neef's fundamental human needs in your analysis.
        
        Respond with JSON containing:
        - human_needs_analysis: object mapping need categories to identified needs and evidence
        - fulfillment_assessment: object with fulfillment scores and gaps by need category
        - intervention_strategies: array of intervention objects with type, target, and approach
        - wellbeing_factors: object with positive and negative wellbeing influences
        - support_mechanisms: array of support system recommendations
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
            required_fields = ['human_needs_analysis', 'fulfillment_assessment', 'intervention_strategies', 
                             'wellbeing_factors', 'support_mechanisms']
            for field in required_fields:
                if field not in result:
                    result[field] = {} if field in ['human_needs_analysis', 'fulfillment_assessment', 'wellbeing_factors'] else []
            
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
        """Fallback processing implementation using the Human Needs Engine"""
        try:
            transcript = input_data.get('transcript', '')
            participants = input_data.get('participants', [])
            
            # Use the comprehensive Human Needs Engine for analysis
            analysis_results = await human_needs_engine.analyze_conversation(
                transcript=transcript,
                participants=participants,
                context=input_data
            )
            
            # Transform results to match expected format
            return {
                'human_needs_analysis': analysis_results.get('individual_assessments', {}),
                'fulfillment_assessment': analysis_results.get('collective_assessment', {}),
                'intervention_strategies': analysis_results.get('recommendations', []),
                'wellbeing_factors': self._extract_wellbeing_factors(analysis_results),
                'support_mechanisms': self._extract_support_mechanisms(analysis_results),
                'confidence': analysis_results.get('confidence', 0.6),
                'dimension': self.dimension,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Fallback processing failed", error=str(e))
            
            # Return minimal result
            return {
                'human_needs_analysis': {},
                'fulfillment_assessment': {},
                'intervention_strategies': [],
                'wellbeing_factors': {},
                'support_mechanisms': [],
                'confidence': 0.3,
                'dimension': self.dimension,
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }
    
    def _extract_wellbeing_factors(self, analysis_results: Dict[str, Any]) -> Dict[str, List[str]]:
        """Extract wellbeing factors from analysis results"""
        try:
            wellbeing_factors = {
                'positive_factors': [],
                'negative_factors': []
            }
            
            # Extract from collective assessment
            collective_assessment = analysis_results.get('collective_assessment', {})
            collective_strengths = collective_assessment.get('collective_strengths', [])
            collective_risks = collective_assessment.get('collective_risks', [])
            
            wellbeing_factors['positive_factors'] = collective_strengths
            wellbeing_factors['negative_factors'] = collective_risks
            
            return wellbeing_factors
            
        except Exception as e:
            logger.error("Wellbeing factors extraction failed", error=str(e))
            return {'positive_factors': [], 'negative_factors': []}
    
    def _extract_support_mechanisms(self, analysis_results: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract support mechanisms from analysis results"""
        try:
            support_mechanisms = []
            
            # Extract from recommendations
            recommendations = analysis_results.get('recommendations', [])
            
            for rec in recommendations:
                if rec.get('type') in ['team', 'organizational']:
                    support_mechanisms.append({
                        'type': rec.get('need', 'General').title() + ' Support',
                        'description': rec.get('recommendation', ''),
                        'target_group': rec.get('target', 'Team')
                    })
            
            return support_mechanisms[:5]  # Limit to top 5
            
        except Exception as e:
            logger.error("Support mechanisms extraction failed", error=str(e))
            return []