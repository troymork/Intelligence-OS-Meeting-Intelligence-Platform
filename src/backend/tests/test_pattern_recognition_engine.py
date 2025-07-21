"""
Tests for Pattern Recognition Engine
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from src.services.pattern_recognition_engine import (
    PatternRecognitionEngine,
    DetectedPattern,
    BestPractice,
    EmotionalFatigueIndicator,
    SystemicIssue,
    PatternType,
    PatternSeverity,
    PatternTrend
)

class TestPatternRecognitionEngine:
    """Test pattern recognition engine functionality"""
    
    @pytest.fixture
    def engine(self):
        """Create pattern recognition engine instance"""
        return PatternRecognitionEngine()
    
    @pytest.fixture
    def sample_meeting_data(self):
        """Sample meeting data for testing"""
        return {
            'meeting_id': 'test-meeting-001',
            'date': '2024-01-15T10:00:00Z',
            'transcript_analysis': {
                'segments': [
                    {
                        'speaker': 'Alice',
                        'text': 'We keep having the same problem with our deployment process',
                        'timestamp': '2024-01-15T10:05:00Z',
                        'duration': 4.0
                    },
                    {
                        'speaker': 'Bob',
                        'text': 'This issue is blocking us again, just like last week',
                        'timestamp': '2024-01-15T10:06:00Z',
                        'duration': 3.5
                    },
                    {
                        'speaker': 'Charlie',
                        'text': 'I feel overwhelmed by all these recurring challenges',
                        'timestamp': '2024-01-15T10:07:00Z',
                        'duration': 3.0
                    }
                ]
            },
            'decisions': [
                {
                    'title': 'Fix Deployment Process',
                    'confidence_score': 0.8,
                    'priority': 'high'
                }
            ],
            'actions': [
                {
                    'title': 'Investigate Deployment Issues',
                    'confidence_score': 0.75,
                    'owner': 'DevOps Team'
                }
            ],
            'discussion_dynamics': {
                'participation_analysis': {
                    'participation_balance': 0.7
                },
                'sentiment_analysis': {
                    'overall_sentiment': {
                        'positive_percentage': 30,
                        'negative_percentage': 50,
                        'neutral_percentage': 20
                    }
                }
            }
        }
    
    @pytest.fixture
    def multiple_meetings_data(self):
        """Multiple meetings data for cross-meeting analysis"""
        base_meeting = {
            'date': '2024-01-15T10:00:00Z',
            'transcript_analysis': {
                'segments': [
                    {
                        'speaker': 'Alice',
                        'text': 'We have the same deployment problem again',
                        'timestamp': '2024-01-15T10:05:00Z'
                    }
                ]
            },
            'decisions': [{'title': 'Fix Issue', 'confidence_score': 0.8}],
            'discussion_dynamics': {
                'participation_analysis': {'participation_balance': 0.7},
                'sentiment_analysis': {'overall_sentiment': {'positive_percentage': 60}}
            }
        }
        
        meetings = []
        for i in range(5):
            meeting = base_meeting.copy()
            meeting['meeting_id'] = f'meeting-{i:03d}'
            meeting['date'] = (datetime(2024, 1, 15) + timedelta(days=i*7)).isoformat() + 'Z'
            meetings.append(meeting)
        
        return meetings

    @pytest.mark.asyncio
    async def test_analyze_meeting_patterns_success(self, engine, sample_meeting_data):
        """Test successful meeting pattern analysis"""
        result = await engine.analyze_meeting_patterns(sample_meeting_data)
        
        assert 'meeting_id' in result
        assert 'current_meeting_patterns' in result
        assert 'cross_meeting_patterns' in result
        assert 'confidence_score' in result
        assert result['meeting_id'] == 'test-meeting-001'
        assert isinstance(result['current_meeting_patterns'], list)

    @pytest.mark.asyncio
    async def test_detect_current_meeting_patterns(self, engine, sample_meeting_data):
        """Test current meeting pattern detection"""
        patterns = await engine._detect_current_meeting_patterns(sample_meeting_data)
        
        assert isinstance(patterns, list)
        # Should detect recurring challenge pattern
        challenge_patterns = [p for p in patterns if p.get('type') == PatternType.RECURRING_CHALLENGE.value]
        assert len(challenge_patterns) > 0

    def test_detect_challenge_patterns(self, engine, sample_meeting_data):
        """Test challenge pattern detection"""
        segments = sample_meeting_data['transcript_analysis']['segments']
        patterns = engine._detect_challenge_patterns(segments, sample_meeting_data)
        
        assert isinstance(patterns, list)
        assert len(patterns) > 0
        
        # Check first pattern
        pattern = patterns[0]
        assert pattern['type'] == PatternType.RECURRING_CHALLENGE.value
        assert 'Alice' in pattern['title']
        assert 'evidence' in pattern

    def test_detect_behavioral_patterns(self, engine, sample_meeting_data):
        """Test behavioral pattern detection"""
        segments = sample_meeting_data['transcript_analysis']['segments']
        patterns = engine._detect_behavioral_patterns(segments, sample_meeting_data)
        
        assert isinstance(patterns, list)
        # Behavioral patterns might not be detected in this simple example

    def test_analyze_communication_styles(self, engine):
        """Test communication style analysis"""
        segments = [
            {
                'speaker': 'Alice',
                'text': 'But wait, I think we should consider a different approach',
                'timestamp': '2024-01-15T10:05:00Z'
            },
            {
                'speaker': 'Alice',
                'text': 'Actually, let me interrupt here with another idea',
                'timestamp': '2024-01-15T10:06:00Z'
            }
        ]
        
        behavioral_template = engine.pattern_templates['behavioral_patterns']
        patterns = engine._analyze_communication_styles(segments, behavioral_template)
        
        assert isinstance(patterns, list)
        # Should detect interrupting pattern for Alice

    @pytest.mark.asyncio
    async def test_analyze_cross_meeting_patterns_insufficient_data(self, engine):
        """Test cross-meeting analysis with insufficient data"""
        # Only one meeting in history
        engine.meeting_history = [{'meeting_id': 'test-001'}]
        
        patterns = await engine._analyze_cross_meeting_patterns()
        
        assert isinstance(patterns, list)
        assert len(patterns) == 0  # Should return empty list

    @pytest.mark.asyncio
    async def test_analyze_cross_meeting_patterns_sufficient_data(self, engine, multiple_meetings_data):
        """Test cross-meeting analysis with sufficient data"""
        # Add multiple meetings to history
        engine.meeting_history = multiple_meetings_data
        
        patterns = await engine._analyze_cross_meeting_patterns()
        
        assert isinstance(patterns, list)
        # Should detect patterns across meetings

    def test_extract_meeting_challenges(self, engine, sample_meeting_data):
        """Test challenge extraction from meeting"""
        challenges = engine._extract_meeting_challenges(sample_meeting_data)
        
        assert isinstance(challenges, list)
        assert len(challenges) > 0
        
        # Check challenge structure
        challenge = challenges[0]
        assert 'text' in challenge
        assert 'speaker' in challenge
        assert 'meeting_id' in challenge

    def test_cluster_similar_challenges(self, engine):
        """Test challenge clustering"""
        challenges = [
            {
                'text': 'Deployment process is broken and causing delays',
                'speaker': 'Alice',
                'meeting_id': 'meeting-001'
            },
            {
                'text': 'Our deployment system has issues again',
                'speaker': 'Bob',
                'meeting_id': 'meeting-002'
            },
            {
                'text': 'Database connection problems in production',
                'speaker': 'Charlie',
                'meeting_id': 'meeting-003'
            }
        ]
        
        clusters = engine._cluster_similar_challenges(challenges)
        
        assert isinstance(clusters, dict)
        # Should group similar deployment challenges together

    def test_calculate_meeting_success_score(self, engine, sample_meeting_data):
        """Test meeting success score calculation"""
        score = engine._calculate_meeting_success_score(sample_meeting_data)
        
        assert isinstance(score, float)
        assert 0 <= score <= 1
        # This meeting should have moderate success due to mixed indicators

    @pytest.mark.asyncio
    async def test_detect_best_practices_insufficient_data(self, engine):
        """Test best practice detection with insufficient data"""
        engine.meeting_history = [{'meeting_id': 'test-001'}]  # Only one meeting
        
        practices = await engine._detect_best_practices()
        
        assert isinstance(practices, list)
        assert len(practices) == 0  # Should return empty list

    def test_identify_successful_meetings(self, engine, multiple_meetings_data):
        """Test successful meeting identification"""
        # Modify meetings to have high success indicators
        for meeting in multiple_meetings_data:
            meeting['discussion_dynamics']['sentiment_analysis']['overall_sentiment']['positive_percentage'] = 80
            meeting['discussion_dynamics']['participation_analysis']['participation_balance'] = 0.9
        
        engine.meeting_history = multiple_meetings_data
        successful_meetings = engine._identify_successful_meetings()
        
        assert isinstance(successful_meetings, list)
        # Should identify meetings with high success scores

    @pytest.mark.asyncio
    async def test_detect_emotional_fatigue_insufficient_data(self, engine):
        """Test emotional fatigue detection with insufficient data"""
        engine.meeting_history = [{'meeting_id': 'test-001'}]  # Only one meeting
        
        indicators = await engine._detect_emotional_fatigue()
        
        assert isinstance(indicators, list)
        assert len(indicators) == 0  # Should return empty list

    def test_analyze_fatigue_patterns(self, engine):
        """Test fatigue pattern analysis"""
        meetings = [
            {
                'meeting_id': 'meeting-001',
                'transcript_analysis': {
                    'segments': [
                        {
                            'speaker': 'Alice',
                            'text': 'I feel really tired and overwhelmed by all this work',
                            'timestamp': '2024-01-15T10:05:00Z'
                        }
                    ]
                }
            },
            {
                'meeting_id': 'meeting-002',
                'transcript_analysis': {
                    'segments': [
                        {
                            'speaker': 'Alice',
                            'text': 'I am exhausted and burned out from these issues',
                            'timestamp': '2024-01-22T10:05:00Z'
                        }
                    ]
                }
            }
        ]
        
        indicators = engine._analyze_fatigue_patterns(meetings)
        
        assert isinstance(indicators, list)
        # Should detect fatigue pattern for Alice

    @pytest.mark.asyncio
    async def test_identify_systemic_issues_insufficient_data(self, engine):
        """Test systemic issue identification with insufficient data"""
        engine.meeting_history = [{'meeting_id': 'test-001'}] * 3  # Only 3 meetings
        
        issues = await engine._identify_systemic_issues()
        
        assert isinstance(issues, list)
        assert len(issues) == 0  # Should return empty list

    def test_detect_communication_breakdowns(self, engine):
        """Test communication breakdown detection"""
        # Create meetings with communication issues
        meetings_with_issues = []
        for i in range(5):
            meeting = {
                'meeting_id': f'meeting-{i:03d}',
                'discussion_dynamics': {
                    'participation_analysis': {
                        'participation_balance': 0.2  # Poor balance
                    },
                    'communication_patterns': {
                        'interruption_patterns': {
                            'interruption_rate': 0.5  # High interruptions
                        }
                    }
                }
            }
            meetings_with_issues.append(meeting)
        
        engine.meeting_history = meetings_with_issues
        issues = engine._detect_communication_breakdowns()
        
        assert isinstance(issues, list)
        # Should detect systemic communication issues

    def test_assess_challenge_severity(self, engine):
        """Test challenge severity assessment"""
        template = engine.pattern_templates['recurring_challenges']
        
        # Test high severity
        high_severity_text = "This is a critical blocker that's urgent"
        severity = engine._assess_challenge_severity(high_severity_text, template)
        assert severity == 'high'
        
        # Test medium severity (default)
        medium_severity_text = "We have a problem that needs attention"
        severity = engine._assess_challenge_severity(medium_severity_text, template)
        assert severity == 'medium'

    def test_check_style_context(self, engine):
        """Test communication style context checking"""
        # Test interrupting style
        interrupting_text = "But wait, let me say something here"
        assert engine._check_style_context(interrupting_text, 'interrupting') == True
        
        # Test collaborative style
        collaborative_text = "What do you think about this approach?"
        assert engine._check_style_context(collaborative_text, 'collaborative') == True
        
        # Test non-matching style
        assert engine._check_style_context("Hello everyone", 'interrupting') == False

    def test_calculate_analysis_confidence(self, engine):
        """Test analysis confidence calculation"""
        # Test with sufficient data
        engine.meeting_history = [{'meeting_id': f'meeting-{i}'} for i in range(5)]
        current_patterns = [{'type': 'test'}]
        cross_patterns = [Mock(confidence_score=0.8)]
        
        confidence = engine._calculate_analysis_confidence(current_patterns, cross_patterns)
        
        assert isinstance(confidence, float)
        assert 0 <= confidence <= 1
        assert confidence > 0.5  # Should be reasonably confident with good data


class TestPatternDataStructures:
    """Test pattern-related data structures"""
    
    def test_detected_pattern_creation(self):
        """Test DetectedPattern creation"""
        pattern = DetectedPattern(
            id='test-pattern-001',
            pattern_type=PatternType.RECURRING_CHALLENGE,
            title='Test Pattern',
            description='Test pattern description',
            frequency=3,
            severity=PatternSeverity.HIGH,
            trend=PatternTrend.WORSENING,
            first_occurrence=datetime.utcnow(),
            last_occurrence=datetime.utcnow(),
            instances=[],
            affected_participants=set(['Alice', 'Bob']),
            root_causes=['Root cause 1'],
            impact_analysis={'impact': 'high'},
            intervention_recommendations=['Recommendation 1'],
            confidence_score=0.8
        )
        
        assert pattern.id == 'test-pattern-001'
        assert pattern.pattern_type == PatternType.RECURRING_CHALLENGE
        assert pattern.frequency == 3
        assert 'Alice' in pattern.affected_participants

    def test_best_practice_creation(self):
        """Test BestPractice creation"""
        practice = BestPractice(
            id='test-practice-001',
            title='Test Best Practice',
            description='Test practice description',
            category='communication',
            success_indicators=['Indicator 1'],
            implementation_guidance='Implementation guide',
            applicable_contexts=['Context 1'],
            evidence_meetings=['meeting-001'],
            effectiveness_score=0.9,
            adoption_recommendations=['Recommendation 1']
        )
        
        assert practice.id == 'test-practice-001'
        assert practice.effectiveness_score == 0.9
        assert len(practice.success_indicators) == 1

    def test_emotional_fatigue_indicator_creation(self):
        """Test EmotionalFatigueIndicator creation"""
        indicator = EmotionalFatigueIndicator(
            id='test-indicator-001',
            indicator_type='fatigue',
            severity=PatternSeverity.HIGH,
            affected_participants=['Alice'],
            symptoms=['Exhaustion', 'Overwhelm'],
            contributing_factors=['Workload', 'Stress'],
            intervention_urgency='immediate',
            recommended_actions=['Action 1'],
            monitoring_metrics=['Metric 1']
        )
        
        assert indicator.id == 'test-indicator-001'
        assert indicator.severity == PatternSeverity.HIGH
        assert 'Alice' in indicator.affected_participants

    def test_systemic_issue_creation(self):
        """Test SystemicIssue creation"""
        issue = SystemicIssue(
            id='test-issue-001',
            issue_title='Test Systemic Issue',
            issue_description='Test issue description',
            root_causes=['Cause 1'],
            affected_areas=['Area 1'],
            impact_assessment={'impact': 'high'},
            urgency_level=PatternSeverity.CRITICAL,
            intervention_strategy={'strategy': 'test'},
            success_metrics=['Metric 1'],
            timeline_recommendations={'immediate': 'Action 1'},
            stakeholder_involvement=['Stakeholder 1']
        )
        
        assert issue.id == 'test-issue-001'
        assert issue.urgency_level == PatternSeverity.CRITICAL
        assert len(issue.root_causes) == 1


if __name__ == '__main__':
    pytest.main([__file__])