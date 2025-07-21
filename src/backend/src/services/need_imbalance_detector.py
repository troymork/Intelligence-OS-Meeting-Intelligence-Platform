"""
Need Imbalance Detection System for Intelligence OS
Detects overemphasis and underemphasis of human needs with early warning systems
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import structlog
import numpy as np
from collections import defaultdict

from .human_needs_engine import human_needs_engine, HumanNeed, NeedFulfillmentLevel

logger = structlog.get_logger(__name__)

class ImbalanceType(Enum):
    """Types of need imbalances"""
    UNDEREMPHASIS = "underemphasis"
    OVEREMPHASIS = "overemphasis"
    COMPETING_NEEDS = "competing_needs"
    NEED_CONFLICT = "need_conflict"
    CHRONIC_IMBALANCE = "chronic_imbalance"

class ImbalanceSeverity(Enum):
    """Severity levels of imbalances"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class NeedImbalance:
    """Represents a detected need imbalance"""
    id: str
    imbalance_type: ImbalanceType
    severity: ImbalanceSeverity
    affected_needs: List[HumanNeed]
    affected_individuals: List[str]
    description: str
    evidence: List[str]
    impact_assessment: Dict[str, Any]
    recommended_interventions: List[str]
    detection_timestamp: datetime = field(default_factory=datetime.utcnow)
    resolution_status: str = "detected"
    resolution_timestamp: Optional[datetime] = None

@dataclass
class ImbalancePattern:
    """Represents a recurring imbalance pattern"""
    pattern_id: str
    pattern_type: str
    frequency: int
    affected_needs: List[HumanNeed]
    common_triggers: List[str]
    typical_duration: timedelta
    success_interventions: List[str]
    first_detected: datetime
    last_occurrence: datetime

class NeedImbalanceDetector:
    """System for detecting and tracking human need imbalances"""
    
    def __init__(self):
        self.detected_imbalances: List[NeedImbalance] = []
        self.imbalance_patterns: List[ImbalancePattern] = []
        self.individual_histories: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.team_histories: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        # Detection thresholds
        self.severe_imbalance_threshold = 0.2  # Below this is severe underemphasis
        self.overemphasis_threshold = 0.8      # Above this is overemphasis
        self.chronic_duration_threshold = timedelta(days=30)  # Chronic if lasting this long
        self.pattern_frequency_threshold = 3   # Pattern if occurs this many times
        
        # Intervention effectiveness tracking
        self.intervention_outcomes: Dict[str, Dict[str, Any]] = {}
    
    async def analyze_for_imbalances(self, analysis_results: Dict[str, Any], 
                                   session_id: str = None) -> Dict[str, Any]:
        """Analyze results for need imbalances and patterns"""
        try:
            detected_imbalances = []
            early_warnings = []
            
            # Analyze individual imbalances
            individual_assessments = analysis_results.get('individual_assessments', {})
            for participant_id, assessment in individual_assessments.items():
                individual_imbalances = await self._detect_individual_imbalances(
                    participant_id, assessment, session_id
                )
                detected_imbalances.extend(individual_imbalances)
                
                # Check for early warning signs
                warnings = await self._check_early_warnings(participant_id, assessment)
                early_warnings.extend(warnings)
            
            # Analyze collective imbalances
            collective_assessment = analysis_results.get('collective_assessment', {})
            if collective_assessment:
                collective_imbalances = await self._detect_collective_imbalances(
                    collective_assessment, session_id
                )
                detected_imbalances.extend(collective_imbalances)
            
            # Detect competing needs and conflicts
            need_conflicts = await self._detect_need_conflicts(analysis_results)
            detected_imbalances.extend(need_conflicts)
            
            # Update imbalance patterns
            await self._update_imbalance_patterns(detected_imbalances)
            
            # Generate comprehensive report
            return {
                'detected_imbalances': [self._serialize_imbalance(imb) for imb in detected_imbalances],
                'early_warnings': early_warnings,
                'imbalance_patterns': [self._serialize_pattern(pat) for pat in self.imbalance_patterns[-5:]],
                'risk_assessment': await self._assess_overall_risk(detected_imbalances),
                'intervention_priorities': await self._prioritize_interventions(detected_imbalances),
                'timestamp': datetime.utcnow().isoformat(),
                'session_id': session_id
            }
            
        except Exception as e:
            logger.error("Imbalance analysis failed", error=str(e))
            return {
                'detected_imbalances': [],
                'early_warnings': [],
                'imbalance_patterns': [],
                'risk_assessment': {},
                'intervention_priorities': [],
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _detect_individual_imbalances(self, participant_id: str, 
                                          assessment: Dict[str, Any],
                                          session_id: str = None) -> List[NeedImbalance]:
        """Detect imbalances for an individual participant"""
        try:
            imbalances = []
            need_assessments = assessment.get('need_assessments', {})
            
            # Store individual history
            self.individual_histories[participant_id].append({
                'timestamp': datetime.utcnow(),
                'assessment': need_assessments,
                'session_id': session_id
            })
            
            # Detect severe underemphasis
            for need_name, need_data in need_assessments.items():
                score = need_data.get('score', 0.5)
                
                if score < self.severe_imbalance_threshold:
                    imbalance = NeedImbalance(
                        id=f"underemphasis_{participant_id}_{need_name}_{datetime.utcnow().timestamp()}",
                        imbalance_type=ImbalanceType.UNDEREMPHASIS,
                        severity=self._calculate_severity(score, 'underemphasis'),
                        affected_needs=[HumanNeed(need_name)],
                        affected_individuals=[participant_id],
                        description=f"Severe underemphasis of {need_name} need",
                        evidence=need_data.get('evidence', []),
                        impact_assessment=await self._assess_imbalance_impact(need_name, score, 'underemphasis'),
                        recommended_interventions=need_data.get('recommendations', [])
                    )
                    imbalances.append(imbalance)
                
                elif score > self.overemphasis_threshold:
                    imbalance = NeedImbalance(
                        id=f"overemphasis_{participant_id}_{need_name}_{datetime.utcnow().timestamp()}",
                        imbalance_type=ImbalanceType.OVEREMPHASIS,
                        severity=self._calculate_severity(score, 'overemphasis'),
                        affected_needs=[HumanNeed(need_name)],
                        affected_individuals=[participant_id],
                        description=f"Overemphasis of {need_name} need",
                        evidence=need_data.get('evidence', []),
                        impact_assessment=await self._assess_imbalance_impact(need_name, score, 'overemphasis'),
                        recommended_interventions=need_data.get('recommendations', [])
                    )
                    imbalances.append(imbalance)
            
            # Check for chronic imbalances
            chronic_imbalances = await self._detect_chronic_imbalances(participant_id)
            imbalances.extend(chronic_imbalances)
            
            return imbalances
            
        except Exception as e:
            logger.error("Individual imbalance detection failed", participant=participant_id, error=str(e))
            return []
    
    async def _detect_collective_imbalances(self, collective_assessment: Dict[str, Any],
                                          session_id: str = None) -> List[NeedImbalance]:
        """Detect imbalances at the collective/team level"""
        try:
            imbalances = []
            collective_assessments = collective_assessment.get('collective_assessments', {})
            team_dynamics = collective_assessment.get('team_dynamics', {})
            
            # Store team history
            team_id = session_id or 'default_team'
            self.team_histories[team_id].append({
                'timestamp': datetime.utcnow(),
                'assessment': collective_assessments,
                'dynamics': team_dynamics,
                'session_id': session_id
            })
            
            # Detect team-level imbalances
            for need_name, need_data in collective_assessments.items():
                score = need_data.get('score', 0.5)
                
                if score < self.severe_imbalance_threshold:
                    imbalance = NeedImbalance(
                        id=f"team_underemphasis_{need_name}_{datetime.utcnow().timestamp()}",
                        imbalance_type=ImbalanceType.UNDEREMPHASIS,
                        severity=self._calculate_severity(score, 'underemphasis'),
                        affected_needs=[HumanNeed(need_name)],
                        affected_individuals=['team'],
                        description=f"Team-wide underemphasis of {need_name} need",
                        evidence=need_data.get('evidence', []),
                        impact_assessment=await self._assess_team_imbalance_impact(need_name, score, team_dynamics),
                        recommended_interventions=need_data.get('recommendations', [])
                    )
                    imbalances.append(imbalance)
            
            # Detect team dynamics issues
            if team_dynamics.get('conflict_potential', 0.3) > 0.7:
                imbalance = NeedImbalance(
                    id=f"team_conflict_{datetime.utcnow().timestamp()}",
                    imbalance_type=ImbalanceType.NEED_CONFLICT,
                    severity=ImbalanceSeverity.HIGH,
                    affected_needs=[need for need in HumanNeed],  # All needs potentially affected
                    affected_individuals=['team'],
                    description="High potential for team conflicts due to need imbalances",
                    evidence=[f"Conflict potential score: {team_dynamics.get('conflict_potential', 0.3)}"],
                    impact_assessment={'team_cohesion': 'at_risk', 'productivity': 'declining'},
                    recommended_interventions=[
                        'Implement conflict resolution processes',
                        'Address individual need imbalances',
                        'Facilitate team alignment sessions'
                    ]
                )
                imbalances.append(imbalance)
            
            return imbalances
            
        except Exception as e:
            logger.error("Collective imbalance detection failed", error=str(e))
            return []
    
    async def _detect_need_conflicts(self, analysis_results: Dict[str, Any]) -> List[NeedImbalance]:
        """Detect conflicts between competing needs"""
        try:
            conflicts = []
            need_interactions = analysis_results.get('need_interactions', [])
            
            for interaction in need_interactions:
                if interaction.get('interaction_type') == 'competing' and interaction.get('strength', 0) > 0.7:
                    conflict = NeedImbalance(
                        id=f"need_conflict_{interaction.get('need1')}_{interaction.get('need2')}_{datetime.utcnow().timestamp()}",
                        imbalance_type=ImbalanceType.COMPETING_NEEDS,
                        severity=ImbalanceSeverity.MODERATE,
                        affected_needs=[HumanNeed(interaction.get('need1')), HumanNeed(interaction.get('need2'))],
                        affected_individuals=interaction.get('observed_in_individuals', []),
                        description=f"Competing needs conflict: {interaction.get('need1')} vs {interaction.get('need2')}",
                        evidence=interaction.get('evidence', []),
                        impact_assessment={'conflict_type': 'competing_needs', 'strength': interaction.get('strength')},
                        recommended_interventions=[
                            f"Balance {interaction.get('need1')} and {interaction.get('need2')} fulfillment",
                            'Create structured approach to need prioritization',
                            'Implement need-aware decision making processes'
                        ]
                    )
                    conflicts.append(conflict)
            
            return conflicts
            
        except Exception as e:
            logger.error("Need conflict detection failed", error=str(e))
            return []
    
    async def _detect_chronic_imbalances(self, participant_id: str) -> List[NeedImbalance]:
        """Detect chronic imbalances that persist over time"""
        try:
            chronic_imbalances = []
            history = self.individual_histories.get(participant_id, [])
            
            if len(history) < 3:  # Need at least 3 data points
                return chronic_imbalances
            
            # Check for persistent imbalances
            for need in HumanNeed:
                need_scores = []
                for record in history[-10:]:  # Last 10 records
                    assessment = record.get('assessment', {})
                    need_data = assessment.get(need.value, {})
                    score = need_data.get('score', 0.5)
                    need_scores.append((record.get('timestamp'), score))
                
                if len(need_scores) >= 3:
                    # Check if consistently low or high
                    recent_scores = [score for _, score in need_scores[-3:]]
                    
                    if all(score < self.severe_imbalance_threshold for score in recent_scores):
                        # Check duration
                        first_low = next((timestamp for timestamp, score in need_scores if score < self.severe_imbalance_threshold), None)
                        if first_low and datetime.utcnow() - first_low > self.chronic_duration_threshold:
                            chronic_imbalance = NeedImbalance(
                                id=f"chronic_{participant_id}_{need.value}_{datetime.utcnow().timestamp()}",
                                imbalance_type=ImbalanceType.CHRONIC_IMBALANCE,
                                severity=ImbalanceSeverity.CRITICAL,
                                affected_needs=[need],
                                affected_individuals=[participant_id],
                                description=f"Chronic underemphasis of {need.value} need lasting {datetime.utcnow() - first_low}",
                                evidence=[f"Consistently low scores over {len(recent_scores)} assessments"],
                                impact_assessment={'duration': str(datetime.utcnow() - first_low), 'trend': 'persistent'},
                                recommended_interventions=[
                                    f"Urgent intervention required for {need.value} need",
                                    'Consider professional support or coaching',
                                    'Implement systematic need fulfillment plan'
                                ]
                            )
                            chronic_imbalances.append(chronic_imbalance)
            
            return chronic_imbalances
            
        except Exception as e:
            logger.error("Chronic imbalance detection failed", participant=participant_id, error=str(e))
            return []
    
    async def _check_early_warnings(self, participant_id: str, assessment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for early warning signs of developing imbalances"""
        try:
            warnings = []
            need_assessments = assessment.get('need_assessments', {})
            
            for need_name, need_data in need_assessments.items():
                score = need_data.get('score', 0.5)
                confidence = need_data.get('confidence', 0.5)
                
                # Warning for declining scores
                if 0.3 <= score <= 0.4 and confidence > 0.6:
                    warnings.append({
                        'type': 'declining_need',
                        'participant': participant_id,
                        'need': need_name,
                        'current_score': score,
                        'warning': f"{need_name} need showing signs of decline",
                        'recommended_action': 'Monitor closely and consider preventive interventions'
                    })
                
                # Warning for increasing overemphasis
                elif 0.7 <= score <= 0.75 and confidence > 0.6:
                    warnings.append({
                        'type': 'increasing_emphasis',
                        'participant': participant_id,
                        'need': need_name,
                        'current_score': score,
                        'warning': f"{need_name} need showing signs of overemphasis",
                        'recommended_action': 'Consider balancing with other needs'
                    })
            
            # Check balance score
            balance_score = assessment.get('balance_score', 0.5)
            if balance_score < 0.4:
                warnings.append({
                    'type': 'overall_imbalance',
                    'participant': participant_id,
                    'need': 'overall',
                    'current_score': balance_score,
                    'warning': 'Overall need balance declining',
                    'recommended_action': 'Comprehensive need assessment and intervention planning'
                })
            
            return warnings
            
        except Exception as e:
            logger.error("Early warning check failed", participant=participant_id, error=str(e))
            return []
    
    def _calculate_severity(self, score: float, imbalance_type: str) -> ImbalanceSeverity:
        """Calculate severity of an imbalance"""
        try:
            if imbalance_type == 'underemphasis':
                if score < 0.1:
                    return ImbalanceSeverity.CRITICAL
                elif score < 0.2:
                    return ImbalanceSeverity.HIGH
                elif score < 0.3:
                    return ImbalanceSeverity.MODERATE
                else:
                    return ImbalanceSeverity.LOW
            
            elif imbalance_type == 'overemphasis':
                if score > 0.9:
                    return ImbalanceSeverity.CRITICAL
                elif score > 0.85:
                    return ImbalanceSeverity.HIGH
                elif score > 0.8:
                    return ImbalanceSeverity.MODERATE
                else:
                    return ImbalanceSeverity.LOW
            
            return ImbalanceSeverity.MODERATE
            
        except Exception as e:
            logger.error("Severity calculation failed", error=str(e))
            return ImbalanceSeverity.MODERATE
    
    async def _assess_imbalance_impact(self, need_name: str, score: float, 
                                     imbalance_type: str) -> Dict[str, Any]:
        """Assess the impact of a need imbalance"""
        try:
            impact = {
                'need': need_name,
                'score': score,
                'type': imbalance_type,
                'severity_level': self._calculate_severity(score, imbalance_type).value
            }
            
            # Need-specific impacts
            if need_name == 'certainty':
                if imbalance_type == 'underemphasis':
                    impact.update({
                        'stress_level': 'high',
                        'decision_making': 'impaired',
                        'productivity': 'declining'
                    })
                else:
                    impact.update({
                        'adaptability': 'low',
                        'innovation': 'blocked',
                        'change_resistance': 'high'
                    })
            
            elif need_name == 'connection':
                if imbalance_type == 'underemphasis':
                    impact.update({
                        'isolation_risk': 'high',
                        'collaboration': 'impaired',
                        'team_cohesion': 'declining'
                    })
                else:
                    impact.update({
                        'independence': 'low',
                        'boundary_issues': 'present',
                        'codependency_risk': 'elevated'
                    })
            
            elif need_name == 'significance':
                if imbalance_type == 'underemphasis':
                    impact.update({
                        'motivation': 'low',
                        'engagement': 'declining',
                        'self_worth': 'at_risk'
                    })
                else:
                    impact.update({
                        'ego_conflicts': 'likely',
                        'teamwork': 'impaired',
                        'humility': 'lacking'
                    })
            
            return impact
            
        except Exception as e:
            logger.error("Impact assessment failed", error=str(e))
            return {'error': str(e)}
    
    async def _assess_team_imbalance_impact(self, need_name: str, score: float, 
                                         team_dynamics: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the impact of team-level imbalances"""
        try:
            impact = await self._assess_imbalance_impact(need_name, score, 'underemphasis')
            
            # Add team-specific impacts
            impact.update({
                'team_collaboration': team_dynamics.get('collaboration_level', 0.5),
                'team_innovation': team_dynamics.get('innovation_capacity', 0.5),
                'team_stability': team_dynamics.get('stability_level', 0.5),
                'conflict_potential': team_dynamics.get('conflict_potential', 0.3)
            })
            
            return impact
            
        except Exception as e:
            logger.error("Team impact assessment failed", error=str(e))
            return {'error': str(e)}
    
    async def _update_imbalance_patterns(self, detected_imbalances: List[NeedImbalance]):
        """Update patterns based on detected imbalances"""
        try:
            # Group imbalances by type and affected needs
            pattern_groups = defaultdict(list)
            
            for imbalance in detected_imbalances:
                pattern_key = (imbalance.imbalance_type.value, tuple(sorted([need.value for need in imbalance.affected_needs])))
                pattern_groups[pattern_key].append(imbalance)
            
            # Update or create patterns
            for pattern_key, imbalances in pattern_groups.items():
                imbalance_type, affected_needs = pattern_key
                
                # Find existing pattern
                existing_pattern = next(
                    (p for p in self.imbalance_patterns 
                     if p.pattern_type == imbalance_type and 
                     tuple(sorted([need.value for need in p.affected_needs])) == affected_needs),
                    None
                )
                
                if existing_pattern:
                    existing_pattern.frequency += len(imbalances)
                    existing_pattern.last_occurrence = datetime.utcnow()
                else:
                    # Create new pattern
                    new_pattern = ImbalancePattern(
                        pattern_id=f"pattern_{imbalance_type}_{hash(affected_needs)}",
                        pattern_type=imbalance_type,
                        frequency=len(imbalances),
                        affected_needs=[HumanNeed(need) for need in affected_needs],
                        common_triggers=[],  # Would be populated with more data
                        typical_duration=timedelta(days=7),  # Default
                        success_interventions=[],
                        first_detected=datetime.utcnow(),
                        last_occurrence=datetime.utcnow()
                    )
                    self.imbalance_patterns.append(new_pattern)
            
        except Exception as e:
            logger.error("Pattern update failed", error=str(e))
    
    async def _assess_overall_risk(self, detected_imbalances: List[NeedImbalance]) -> Dict[str, Any]:
        """Assess overall risk level based on detected imbalances"""
        try:
            if not detected_imbalances:
                return {'risk_level': 'low', 'risk_score': 0.1}
            
            # Calculate risk score
            severity_weights = {
                ImbalanceSeverity.LOW: 0.25,
                ImbalanceSeverity.MODERATE: 0.5,
                ImbalanceSeverity.HIGH: 0.75,
                ImbalanceSeverity.CRITICAL: 1.0
            }
            
            total_risk = sum(severity_weights.get(imb.severity, 0.5) for imb in detected_imbalances)
            risk_score = min(1.0, total_risk / len(detected_imbalances))
            
            # Determine risk level
            if risk_score < 0.3:
                risk_level = 'low'
            elif risk_score < 0.6:
                risk_level = 'moderate'
            elif risk_score < 0.8:
                risk_level = 'high'
            else:
                risk_level = 'critical'
            
            return {
                'risk_level': risk_level,
                'risk_score': risk_score,
                'total_imbalances': len(detected_imbalances),
                'critical_imbalances': sum(1 for imb in detected_imbalances if imb.severity == ImbalanceSeverity.CRITICAL),
                'affected_individuals': len(set(ind for imb in detected_imbalances for ind in imb.affected_individuals))
            }
            
        except Exception as e:
            logger.error("Risk assessment failed", error=str(e))
            return {'risk_level': 'unknown', 'error': str(e)}
    
    async def _prioritize_interventions(self, detected_imbalances: List[NeedImbalance]) -> List[Dict[str, Any]]:
        """Prioritize interventions based on severity and impact"""
        try:
            # Sort by severity and impact
            sorted_imbalances = sorted(
                detected_imbalances,
                key=lambda x: (x.severity.value, len(x.affected_individuals)),
                reverse=True
            )
            
            priorities = []
            for i, imbalance in enumerate(sorted_imbalances[:10]):  # Top 10
                priorities.append({
                    'priority_rank': i + 1,
                    'imbalance_id': imbalance.id,
                    'severity': imbalance.severity.value,
                    'affected_needs': [need.value for need in imbalance.affected_needs],
                    'affected_individuals': imbalance.affected_individuals,
                    'recommended_interventions': imbalance.recommended_interventions,
                    'urgency': 'immediate' if imbalance.severity == ImbalanceSeverity.CRITICAL else 'high'
                })
            
            return priorities
            
        except Exception as e:
            logger.error("Intervention prioritization failed", error=str(e))
            return []
    
    def _serialize_imbalance(self, imbalance: NeedImbalance) -> Dict[str, Any]:
        """Serialize imbalance for JSON response"""
        return {
            'id': imbalance.id,
            'type': imbalance.imbalance_type.value,
            'severity': imbalance.severity.value,
            'affected_needs': [need.value for need in imbalance.affected_needs],
            'affected_individuals': imbalance.affected_individuals,
            'description': imbalance.description,
            'evidence': imbalance.evidence,
            'impact_assessment': imbalance.impact_assessment,
            'recommended_interventions': imbalance.recommended_interventions,
            'detection_timestamp': imbalance.detection_timestamp.isoformat(),
            'resolution_status': imbalance.resolution_status
        }
    
    def _serialize_pattern(self, pattern: ImbalancePattern) -> Dict[str, Any]:
        """Serialize pattern for JSON response"""
        return {
            'pattern_id': pattern.pattern_id,
            'pattern_type': pattern.pattern_type,
            'frequency': pattern.frequency,
            'affected_needs': [need.value for need in pattern.affected_needs],
            'first_detected': pattern.first_detected.isoformat(),
            'last_occurrence': pattern.last_occurrence.isoformat(),
            'success_interventions': pattern.success_interventions
        }

# Global need imbalance detector instance
need_imbalance_detector = NeedImbalanceDetector()