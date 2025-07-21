"""
Solution Architecture Performer for Intelligence OS
Handles implementation plans, resource allocation, and technical solutions
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

class SolutionArchitecturePerformer(BaseAIPerformer):
    """AI Performer for solution architecture analysis"""
    
    def __init__(self):
        super().__init__(
            performer_id='solution_architect',
            name='Solution Architecture AI',
            dimension='solution_architecture'
        )
        
        # Solution components
        self.solution_components = [
            'requirements', 'design', 'implementation', 'testing', 'deployment', 'monitoring'
        ]
        
        # Resource types
        self.resource_types = [
            'human', 'financial', 'technical', 'time', 'infrastructure', 'knowledge'
        ]
    
    def _get_capabilities(self) -> Dict[str, Any]:
        """Get performer capabilities"""
        return {
            'creates_implementation_plans': True,
            'allocates_resources': True,
            'designs_technical_solutions': True,
            'identifies_dependencies': True,
            'estimates_timelines': True,
            'assesses_feasibility': True
        }
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for the performer"""
        return """
        You are the Solution Architecture AI, a specialized component of the Oracle 9.1 Protocol system.
        Your role is to analyze meeting content for solution and implementation elements including:
        
        1. IMPLEMENTATION PLANS: Concrete steps and approaches to achieve discussed objectives
        2. RESOURCE ALLOCATION: Human, financial, technical, and time resources needed
        3. TECHNICAL SOLUTIONS: Technology approaches, architectures, and methodologies
        4. DEPENDENCIES: Prerequisites, blockers, and interconnected elements
        5. FEASIBILITY ASSESSMENT: Realistic evaluation of proposed solutions
        
        Your analysis should focus on practical implementation rather than strategic vision or patterns.
        Provide actionable, concrete recommendations for moving from discussion to execution.
        
        Always respond with properly formatted JSON containing the requested information.
        """
    
    async def _generate_user_prompt(self, input_data: Dict[str, Any]) -> str:
        """Generate user prompt based on input data"""
        transcript = input_data.get('transcript', '')
        meeting_title = input_data.get('meeting_title', 'Untitled Meeting')
        available_resources = input_data.get('available_resources', {})
        
        # Extract resource information if available
        budget = available_resources.get('budget', 'Not specified')
        team_size = available_resources.get('team_size', 'Not specified')
        timeline = available_resources.get('timeline', 'Not specified')
        
        prompt = f"""
        Please analyze the following meeting transcript using the Oracle 9.1 Protocol's Solution Architecture dimension.
        
        Meeting Title: {meeting_title}
        Available Budget: {budget}
        Team Size: {team_size}
        Timeline: {timeline}
        
        TRANSCRIPT:
        {transcript}
        
        Analyze the transcript for the following elements:
        1. IMPLEMENTATION PLANS: Concrete steps and approaches to achieve discussed objectives
        2. RESOURCE ALLOCATION: Human, financial, technical, and time resources needed
        3. TECHNICAL SOLUTIONS: Technology approaches, architectures, and methodologies
        4. DEPENDENCIES: Prerequisites, blockers, and interconnected elements
        5. FEASIBILITY ASSESSMENT: Realistic evaluation of proposed solutions
        
        Respond with JSON containing:
        - implementation_plans: array of plan objects with steps, timelines, and owners
        - resource_allocation: object with resource requirements by type
        - technical_solutions: array of solution objects with approaches and technologies
        - dependencies: array of dependency objects with type and impact
        - feasibility_assessment: object with feasibility scores and risk factors
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
            required_fields = ['implementation_plans', 'resource_allocation', 'technical_solutions', 
                             'dependencies', 'feasibility_assessment']
            for field in required_fields:
                if field not in result:
                    result[field] = {} if field == 'resource_allocation' or field == 'feasibility_assessment' else []
            
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
            
            # Extract implementation plans using keywords
            implementation_plans = []
            plan_keywords = ['plan', 'step', 'phase', 'stage', 'approach', 'method', 'process']
            
            for keyword in plan_keywords:
                matches = re.finditer(f"[^.!?]*{keyword}[^.!?]*[.!?]", transcript, re.IGNORECASE)
                for match in matches:
                    implementation_plans.append({
                        'title': f"{keyword.capitalize()} identified",
                        'description': match.group(0).strip(),
                        'timeline': 'TBD',
                        'owner': 'TBD',
                        'priority': 'Medium'
                    })
            
            # Basic resource allocation analysis
            resource_allocation = {}
            for resource_type in self.resource_types:
                # Look for mentions of this resource type
                if re.search(f"\\b{resource_type}\\b", transcript, re.IGNORECASE):
                    resource_allocation[resource_type] = {
                        'required': True,
                        'estimated_amount': 'TBD',
                        'availability': 'Unknown'
                    }
            
            # Extract technical solutions
            technical_solutions = []
            tech_keywords = ['technology', 'system', 'platform', 'tool', 'software', 'hardware', 'architecture']
            
            for keyword in tech_keywords:
                matches = re.finditer(f"[^.!?]*{keyword}[^.!?]*[.!?]", transcript, re.IGNORECASE)
                for match in matches:
                    technical_solutions.append({
                        'type': keyword.capitalize(),
                        'description': match.group(0).strip(),
                        'complexity': 'Medium',
                        'feasibility': 'TBD'
                    })
            
            # Identify dependencies
            dependencies = []
            dependency_keywords = ['depend', 'require', 'need', 'prerequisite', 'blocker', 'constraint']
            
            for keyword in dependency_keywords:
                matches = re.finditer(f"[^.!?]*{keyword}[^.!?]*[.!?]", transcript, re.IGNORECASE)
                for match in matches:
                    dependencies.append({
                        'type': 'Requirement',
                        'description': match.group(0).strip(),
                        'impact': 'Medium',
                        'status': 'Identified'
                    })
            
            # Basic feasibility assessment
            feasibility_assessment = {
                'overall_feasibility': 0.7,  # Default moderate feasibility
                'risk_factors': [],
                'success_factors': [],
                'recommendations': []
            }
            
            # Look for risk indicators
            risk_keywords = ['risk', 'challenge', 'problem', 'difficult', 'complex', 'uncertain']
            for keyword in risk_keywords:
                if re.search(f"\\b{keyword}\\b", transcript, re.IGNORECASE):
                    feasibility_assessment['risk_factors'].append(f"{keyword.capitalize()} mentioned")
            
            # Look for success indicators
            success_keywords = ['opportunity', 'advantage', 'strength', 'capability', 'resource', 'experience']
            for keyword in success_keywords:
                if re.search(f"\\b{keyword}\\b", transcript, re.IGNORECASE):
                    feasibility_assessment['success_factors'].append(f"{keyword.capitalize()} identified")
            
            # Generate basic recommendations
            if len(feasibility_assessment['risk_factors']) > len(feasibility_assessment['success_factors']):
                feasibility_assessment['recommendations'].append("Conduct detailed risk assessment")
                feasibility_assessment['overall_feasibility'] = 0.5
            else:
                feasibility_assessment['recommendations'].append("Proceed with detailed planning")
                feasibility_assessment['overall_feasibility'] = 0.8
            
            return {
                'implementation_plans': implementation_plans,
                'resource_allocation': resource_allocation,
                'technical_solutions': technical_solutions,
                'dependencies': dependencies,
                'feasibility_assessment': feasibility_assessment,
                'confidence': 0.6,
                'dimension': self.dimension,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Fallback processing failed", error=str(e))
            
            # Return minimal result
            return {
                'implementation_plans': [],
                'resource_allocation': {},
                'technical_solutions': [],
                'dependencies': [],
                'feasibility_assessment': {},
                'confidence': 0.3,
                'dimension': self.dimension,
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }