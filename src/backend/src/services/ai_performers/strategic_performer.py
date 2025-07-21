"""
Strategic Synthesis Performer for Intelligence OS
Handles strategic context, organizational alignment, and recommendations
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

class StrategicSynthesisPerformer(BaseAIPerformer):
    """AI Performer for strategic synthesis analysis"""
    
    def __init__(self):
        super().__init__(
            performer_id='strategic_synthesizer',
            name='Strategic Synthesis AI',
            dimension='strategic_synthesis'
        )
        
        # Strategic frameworks
        self.strategic_frameworks = {
            'sdg': [
                'No Poverty', 'Zero Hunger', 'Good Health and Well-being', 'Quality Education',
                'Gender Equality', 'Clean Water and Sanitation', 'Affordable and Clean Energy',
                'Decent Work and Economic Growth', 'Industry, Innovation and Infrastructure',
                'Reduced Inequality', 'Sustainable Cities and Communities',
                'Responsible Consumption and Production', 'Climate Action',
                'Life Below Water', 'Life on Land', 'Peace, Justice and Strong Institutions',
                'Partnerships for the Goals'
            ],
            'doughnut_economy': [
                'Water', 'Food', 'Health', 'Education', 'Income & Work', 'Peace & Justice',
                'Political Voice', 'Social Equity', 'Gender Equality', 'Housing', 'Networks',
                'Energy', 'Climate Change', 'Ocean Acidification', 'Chemical Pollution',
                'Nitrogen & Phosphorus Loading', 'Freshwater Withdrawals', 'Land Conversion',
                'Biodiversity Loss', 'Air Pollution', 'Ozone Layer Depletion'
            ],
            'agreement_economy': [
                'Value Creation', 'Value Distribution', 'Collaborative Governance',
                'Shared Resources', 'Collective Intelligence', 'Regenerative Practices',
                'Transparent Accountability', 'Inclusive Participation'
            ]
        }
    
    def _get_capabilities(self) -> Dict[str, Any]:
        """Get performer capabilities"""
        return {
            'connects_strategic_context': True,
            'generates_recommendations': True,
            'assesses_alignment': True,
            'evaluates_exponential_potential': True,
            'identifies_strategic_opportunities': True,
            'analyzes_framework_compatibility': True
        }
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for the performer"""
        return """
        You are the Strategic Synthesis AI, a specialized component of the Oracle 9.1 Protocol system.
        Your role is to analyze meeting content through strategic frameworks including:
        
        1. STRATEGIC CONTEXT: How the meeting content connects to broader organizational strategy
        2. ORGANIZATIONAL ALIGNMENT: How well the discussion aligns with stated goals and frameworks
        3. STRATEGIC FRAMEWORKS: Analysis through SDGs, Doughnut Economy, and Agreement Economy lenses
        4. RECOMMENDATIONS: Strategic suggestions to enhance alignment and impact
        5. EXPONENTIAL POTENTIAL: Opportunities for non-linear growth and transformation
        
        Your analysis should connect meeting content to strategic frameworks and identify opportunities.
        Focus on strategic implications rather than tactical details - those are handled by other AI components.
        
        Always respond with properly formatted JSON containing the requested information.
        """
    
    async def _generate_user_prompt(self, input_data: Dict[str, Any]) -> str:
        """Generate user prompt based on input data"""
        transcript = input_data.get('transcript', '')
        meeting_title = input_data.get('meeting_title', 'Untitled Meeting')
        organization_context = input_data.get('organization_context', {})
        
        # Extract organization details if available
        org_mission = organization_context.get('mission', 'Not provided')
        org_goals = organization_context.get('goals', [])
        org_goals_text = '\n'.join([f"- {goal}" for goal in org_goals]) if org_goals else 'Not provided'
        
        prompt = f"""
        Please analyze the following meeting transcript using the Oracle 9.1 Protocol's Strategic Synthesis dimension.
        
        Meeting Title: {meeting_title}
        Organization Mission: {org_mission}
        Organization Goals:
        {org_goals_text}
        
        TRANSCRIPT:
        {transcript}
        
        Analyze the transcript for the following elements:
        1. STRATEGIC CONTEXT: How the meeting content connects to broader organizational strategy
        2. ORGANIZATIONAL ALIGNMENT: How well the discussion aligns with stated goals and frameworks
        3. STRATEGIC FRAMEWORKS: Analysis through SDGs, Doughnut Economy, and Agreement Economy lenses
        4. RECOMMENDATIONS: Strategic suggestions to enhance alignment and impact
        5. EXPONENTIAL POTENTIAL: Opportunities for non-linear growth and transformation
        
        Respond with JSON containing:
        - strategic_context: object with key insights about strategic positioning
        - organizational_alignment: object with alignment assessment and gaps
        - framework_analysis: object with SDG, doughnut_economy, and agreement_economy assessments
        - recommendations: array of strategic recommendation objects
        - exponential_potential: object with opportunities and transformation paths
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
            required_fields = ['strategic_context', 'organizational_alignment', 'framework_analysis', 
                             'recommendations', 'exponential_potential']
            for field in required_fields:
                if field not in result:
                    result[field] = {} if field != 'recommendations' else []
            
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
            organization_context = input_data.get('organization_context', {})
            
            # Basic strategic context analysis
            strategic_context = {
                'key_focus_areas': [],
                'strategic_positioning': 'Unknown',
                'market_context': 'Unknown'
            }
            
            # Extract potential focus areas from transcript
            focus_areas = ['growth', 'innovation', 'efficiency', 'customer', 'market', 
                          'competition', 'product', 'service', 'technology', 'sustainability']
            
            for area in focus_areas:
                if re.search(f"\\b{area}\\b", transcript, re.IGNORECASE):
                    strategic_context['key_focus_areas'].append(area.capitalize())
            
            # Basic organizational alignment
            organizational_alignment = {
                'alignment_score': 0.5,  # Default middle score
                'aligned_elements': [],
                'misaligned_elements': [],
                'alignment_gaps': ['Insufficient data for detailed alignment analysis']
            }
            
            # Check alignment with organization goals if available
            org_goals = organization_context.get('goals', [])
            if org_goals:
                for goal in org_goals:
                    # Simple check if goal keywords appear in transcript
                    goal_keywords = re.findall(r'\b\w+\b', goal.lower())
                    matches = sum(1 for keyword in goal_keywords if re.search(f"\\b{keyword}\\b", transcript.lower()))
                    alignment_ratio = matches / len(goal_keywords) if goal_keywords else 0
                    
                    if alignment_ratio > 0.3:
                        organizational_alignment['aligned_elements'].append(goal)
                    else:
                        organizational_alignment['misaligned_elements'].append(goal)
            
            # Basic framework analysis
            framework_analysis = {
                'sdg': self._analyze_framework_alignment('sdg', transcript),
                'doughnut_economy': self._analyze_framework_alignment('doughnut_economy', transcript),
                'agreement_economy': self._analyze_framework_alignment('agreement_economy', transcript)
            }
            
            # Generate basic recommendations
            recommendations = []
            if len(strategic_context['key_focus_areas']) > 0:
                recommendations.append({
                    'title': f"Strengthen focus on {strategic_context['key_focus_areas'][0]}",
                    'description': f"Build on existing momentum in {strategic_context['key_focus_areas'][0]} area",
                    'expected_impact': 'Medium',
                    'implementation_complexity': 'Medium'
                })
            
            if len(organizational_alignment['misaligned_elements']) > 0:
                recommendations.append({
                    'title': 'Address alignment gaps',
                    'description': f"Realign activities with organizational goal: {organizational_alignment['misaligned_elements'][0]}",
                    'expected_impact': 'High',
                    'implementation_complexity': 'Medium'
                })
            
            # Basic exponential potential
            exponential_potential = {
                'opportunities': [],
                'transformation_paths': [],
                'exponential_score': 0.3  # Default low score for fallback
            }
            
            # Look for keywords suggesting exponential potential
            exponential_keywords = ['scale', 'exponential', 'transform', 'disrupt', 'revolution', 
                                   'breakthrough', 'platform', 'network effect', 'ecosystem']
            
            for keyword in exponential_keywords:
                if re.search(f"\\b{keyword}\\b", transcript, re.IGNORECASE):
                    # Find the sentence containing this keyword
                    sentences = re.findall(f"[^.!?]*{keyword}[^.!?]*[.!?]", transcript, re.IGNORECASE)
                    if sentences:
                        exponential_potential['opportunities'].append({
                            'area': keyword.capitalize(),
                            'description': sentences[0].strip()
                        })
            
            return {
                'strategic_context': strategic_context,
                'organizational_alignment': organizational_alignment,
                'framework_analysis': framework_analysis,
                'recommendations': recommendations,
                'exponential_potential': exponential_potential,
                'confidence': 0.5,
                'dimension': self.dimension,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Fallback processing failed", error=str(e))
            
            # Return minimal result
            return {
                'strategic_context': {},
                'organizational_alignment': {},
                'framework_analysis': {},
                'recommendations': [],
                'exponential_potential': {},
                'confidence': 0.3,
                'dimension': self.dimension,
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }
    
    def _analyze_framework_alignment(self, framework: str, transcript: str) -> Dict[str, Any]:
        """Analyze alignment with a specific strategic framework"""
        try:
            framework_elements = self.strategic_frameworks.get(framework, [])
            aligned_elements = []
            
            for element in framework_elements:
                # Check if element keywords appear in transcript
                element_keywords = re.findall(r'\b\w+\b', element.lower())
                for keyword in element_keywords:
                    if len(keyword) > 3 and re.search(f"\\b{keyword}\\b", transcript.lower()):
                        aligned_elements.append(element)
                        break
            
            # Calculate alignment score
            alignment_score = len(aligned_elements) / len(framework_elements) if framework_elements else 0
            
            return {
                'alignment_score': alignment_score,
                'aligned_elements': aligned_elements,
                'primary_focus': aligned_elements[0] if aligned_elements else None
            }
            
        except Exception as e:
            logger.error(f"Framework alignment analysis failed for {framework}", error=str(e))
            return {
                'alignment_score': 0.0,
                'aligned_elements': [],
                'primary_focus': None
            }