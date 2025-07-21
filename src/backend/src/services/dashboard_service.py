"""
Dashboard Service for Human Needs Visualization
Handles data processing and visualization logic for human needs dashboards
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json
import structlog
from collections import defaultdict
import numpy as np

from .human_needs_engine import human_needs_engine, HumanNeed
from .need_imbalance_detector import need_imbalance_detector
from .intervention_engine import intervention_engine

logger = structlog.get_logger(__name__)

@dataclass
class DashboardConfig:
    """Configuration for dashboard generation"""
    privacy_level: str = 'team'
    time_range_days: int = 30
    include_trends: bool = True
    include_interventions: bool = True
    include_predictions: bool = False
    anonymize_data: bool = False

class DashboardService:
    """Service for generating human needs dashboards and visualizations"""
    
    def __init__(self):
        self.cached_data = {}
        self.cache_ttl = timedelta(minutes=15)
        self.privacy_levels = ['public', 'team', 'manager', 'private', 'anonymous']
        
    async def generate_individual_dashboard(self, participant_id: str, 
                                          config: DashboardConfig) -> Dict[str, Any]:
        """Generate comprehensive individual dashboard"""
        try:
            dashboard = {
                'participant_id': participant_id,
                'generated_at': datetime.utcnow().isoformat(),
                'config': config.__dict__,
                'needs_overview': await self._get_needs_overview(participant_id),
                'current_status': await self._get_current_status(participant_id),
                'trends': await self._get_individual_trends(participant_id, config),
                'interventions': await self._get_individual_interventions(participant_id, config),
                'recommendations': await self._get_individual_recommendations(participant_id),
                'privacy_protected': config.privacy_level != 'public'
            }
            
            return dashboard
            
        except Exception as e:
            logger.error("Individual dashboard generation failed", 
                        participant_id=participant_id, error=str(e))
            return {'error': str(e)}
    
    async def generate_team_dashboard(self, team_id: str, 
                                    config: DashboardConfig) -> Dict[str, Any]:
        """Generate comprehensive team dashboard"""
        try:
            dashboard = {
                'team_id': team_id,
                'generated_at': datetime.utcnow().isoformat(),
                'config': config.__dict__,
                'team_overview': await self._get_team_overview(team_id),
                'collective_needs': await self._get_collective_needs(team_id),
                'team_dynamics': await self._get_team_dynamics(team_id),
                'trends': await self._get_team_trends(team_id, config),
                'interventions': await self._get_team_interventions(team_id, config),
                'risk_indicators': await self._get_risk_indicators(team_id),
                'recommendations': await self._get_team_recommendations(team_id)
            }
            
            return dashboard
            
        except Exception as e:
            logger.error("Team dashboard generation failed", 
                        team_id=team_id, error=str(e))
            return {'error': str(e)}
    
    async def _get_needs_overview(self, participant_id: str) -> Dict[str, Any]:
        """Get individual needs overview"""
        try:
            # This would integrate with actual stored assessment data
            needs_data = {
                'certainty': {'score': 0.7, 'level': 'fulfilled', 'change': 0.05},
                'variety': {'score': 0.4, 'level': 'lacking', 'change': -0.1},
                'significance': {'score': 0.8, 'level': 'fulfilled', 'change': 0.15},
                'connection': {'score': 0.6, 'level': 'moderate', 'change': 0.0},
                'growth': {'score': 0.5, 'level': 'moderate', 'change': 0.2},
                'contribution': {'score': 0.9, 'level': 'overemphasized', 'change': -0.05}
            }
            
            # Calculate overall balance
            scores = [data['score'] for data in needs_data.values()]
            balance_score = 1.0 - np.std(scores)
            
            return {
                'needs_data': needs_data,
                'balance_score': balance_score,
                'dominant_needs': ['contribution', 'significance'],
                'suppressed_needs': ['variety'],
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Needs overview generation failed", error=str(e))
            return {}

# Global dashboard service instance
dashboard_service = DashboardService()    
   
 async def _get_current_status(self, participant_id: str) -> Dict[str, Any]:
        """Get current status summary for individual"""
        try:
            return {
                'overall_health': 0.72,
                'active_imbalances': 2,
                'improvement_trend': 'positive',
                'intervention_participation': 'active',
                'last_assessment': (datetime.utcnow() - timedelta(days=7)).isoformat(),
                'next_check_in': (datetime.utcnow() + timedelta(days=14)).isoformat()
            }
        except Exception as e:
            logger.error("Current status generation failed", error=str(e))
            return {}
    
    async def _get_individual_trends(self, participant_id: str, 
                                   config: DashboardConfig) -> Dict[str, Any]:
        """Get individual trend data"""
        try:
            if not config.include_trends:
                return {}
            
            # Generate sample trend data
            time_points = self._generate_time_series(config.time_range_days)
            
            trends = {}
            for need in ['certainty', 'variety', 'significance', 'connection', 'growth', 'contribution']:
                trends[need] = {
                    'data_points': [
                        {'date': point['date'], 'value': 0.5 + (i * 0.02) + np.random.normal(0, 0.05)}
                        for i, point in enumerate(time_points)
                    ],
                    'trend_direction': 'improving' if need in ['growth', 'significance'] else 'stable',
                    'volatility': 'low',
                    'correlation_score': 0.7
                }
            
            return {
                'time_range_days': config.time_range_days,
                'trends': trends,
                'key_insights': [
                    'Growth needs showing consistent improvement',
                    'Variety needs remain below optimal level'
                ]
            }
            
        except Exception as e:
            logger.error("Individual trends generation failed", error=str(e))
            return {}
    
    async def _get_individual_interventions(self, participant_id: str, 
                                          config: DashboardConfig) -> Dict[str, Any]:
        """Get individual intervention data"""
        try:
            if not config.include_interventions:
                return {}
            
            return {
                'active_interventions': [
                    {
                        'id': 'int_001',
                        'name': 'Variety Enhancement Program',
                        'target_need': 'variety',
                        'progress': 0.65,
                        'effectiveness': 0.7,
                        'start_date': (datetime.utcnow() - timedelta(days=20)).isoformat(),
                        'expected_completion': (datetime.utcnow() + timedelta(days=15)).isoformat()
                    }
                ],
                'completed_interventions': [
                    {
                        'id': 'int_002',
                        'name': 'Growth Mindset Workshop',
                        'target_need': 'growth',
                        'effectiveness_rating': 'high',
                        'completion_date': (datetime.utcnow() - timedelta(days=45)).isoformat()
                    }
                ],
                'recommended_interventions': [
                    {
                        'name': 'Connection Building Activities',
                        'target_need': 'connection',
                        'priority': 'medium',
                        'estimated_duration': '4 weeks'
                    }
                ]
            }
            
        except Exception as e:
            logger.error("Individual interventions generation failed", error=str(e))
            return {}
    
    async def _get_individual_recommendations(self, participant_id: str) -> List[Dict[str, Any]]:
        """Get individual recommendations"""
        try:
            return [
                {
                    'type': 'immediate',
                    'priority': 'high',
                    'category': 'variety',
                    'title': 'Increase Task Variety',
                    'description': 'Seek opportunities for diverse work assignments',
                    'expected_impact': 'medium'
                },
                {
                    'type': 'ongoing',
                    'priority': 'medium',
                    'category': 'connection',
                    'title': 'Strengthen Team Relationships',
                    'description': 'Participate in team building activities',
                    'expected_impact': 'high'
                }
            ]
            
        except Exception as e:
            logger.error("Individual recommendations generation failed", error=str(e))
            return []
    
    async def _get_team_overview(self, team_id: str) -> Dict[str, Any]:
        """Get team overview data"""
        try:
            return {
                'team_size': 8,
                'overall_health_score': 0.68,
                'needs_balance_score': 0.72,
                'active_interventions': 3,
                'members_with_imbalances': 4,
                'improvement_trend': 'positive',
                'last_team_assessment': (datetime.utcnow() - timedelta(days=14)).isoformat()
            }
            
        except Exception as e:
            logger.error("Team overview generation failed", error=str(e))
            return {}
    
    async def _get_collective_needs(self, team_id: str) -> Dict[str, Any]:
        """Get collective team needs data"""
        try:
            return {
                'certainty': {
                    'average_score': 0.65,
                    'distribution': {'low': 0.2, 'moderate': 0.5, 'high': 0.3},
                    'team_trend': 'stable'
                },
                'variety': {
                    'average_score': 0.45,
                    'distribution': {'low': 0.5, 'moderate': 0.3, 'high': 0.2},
                    'team_trend': 'improving'
                },
                'significance': {
                    'average_score': 0.75,
                    'distribution': {'low': 0.1, 'moderate': 0.4, 'high': 0.5},
                    'team_trend': 'stable'
                },
                'connection': {
                    'average_score': 0.55,
                    'distribution': {'low': 0.3, 'moderate': 0.4, 'high': 0.3},
                    'team_trend': 'improving'
                },
                'growth': {
                    'average_score': 0.6,
                    'distribution': {'low': 0.2, 'moderate': 0.5, 'high': 0.3},
                    'team_trend': 'improving'
                },
                'contribution': {
                    'average_score': 0.8,
                    'distribution': {'low': 0.1, 'moderate': 0.2, 'high': 0.7},
                    'team_trend': 'stable'
                }
            }
            
        except Exception as e:
            logger.error("Collective needs generation failed", error=str(e))
            return {}
    
    async def _get_team_dynamics(self, team_id: str) -> Dict[str, Any]:
        """Get team dynamics data"""
        try:
            return {
                'collaboration_level': 0.7,
                'innovation_capacity': 0.6,
                'stability_level': 0.8,
                'conflict_potential': 0.3,
                'growth_orientation': 0.65,
                'purpose_alignment': 0.85,
                'communication_effectiveness': 0.72,
                'trust_level': 0.78,
                'psychological_safety': 0.68
            }
            
        except Exception as e:
            logger.error("Team dynamics generation failed", error=str(e))
            return {}
    
    def _generate_time_series(self, days: int) -> List[Dict[str, Any]]:
        """Generate time series data points"""
        try:
            points = []
            for i in range(0, days, max(1, days // 30)):  # Max 30 points
                date = datetime.utcnow() - timedelta(days=days-i)
                points.append({
                    'date': date.isoformat(),
                    'timestamp': date.timestamp()
                })
            return points
            
        except Exception as e:
            logger.error("Time series generation failed", error=str(e))
            return []