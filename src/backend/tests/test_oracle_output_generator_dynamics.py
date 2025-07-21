"""
Tests for Oracle Output Generator Discussion Dynamics and Human Needs Intelligence
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch
from src.services.oracle_output_generator import (
    OracleOutputGenerator, 
    DiscussionDynamics, 
    HumanNeedsIntelligence
)

class TestDiscussionDynamicsGeneration:
    """Test discussion dynamics generation functionality"""
    
    @pytest.fixture
    def generator(self):
        """Create Oracle output generator instance"""
        return OracleOutputGenerator()
    
    @pytest.fixture
    def sample_transcript_data(self):
        """Sample transcript data for testing"""
        return {
            'segments': [
                {
                    'speaker': 'Alice',
                    'text': 'I think we should move forward with the new plan. It\'s important that we get this right.',
                    'duration': 5.2,
                    'timestamp': '00:01:00'
                },
                {
                    'speaker': 'Bob',
                    'text': 'I agree with Alice. This is a great opportunity for us to grow and learn.',
                    'duration': 3.8,
                    'timestamp': '00:01:05'
                },
                {
                    'speaker': 'Charlie',
                    'text': 'Are we sure about the timeline? I need more certainty about the deadlines.',
                    'duration': 4.1,
                    'timestamp': '00:01:09'
                },
                {
                    'speaker': 'Alice',
                    'text': 'Let me clarify the schedule. We have clear milestones every two weeks.',
                    'duration': 4.5,
                    'timestamp': '00:01:13'
                },
                {
                    'speaker': 'Bob',
                    'text': 'What if we try a different approach? Maybe something more creative?',
                    'duration': 3.2,
                    'timestamp': '00:01:18'
                }
            ]
        }
    
    @pytest.fixture
    def sample_meeting_metadata(self):
        """Sample meeting metadata for testing"""
        return {
            'meeting_id': 'test-meeting-123',
            'title': 'Project Planning Meeting',
            'participants': ['Alice', 'Bob', 'Charlie'],
            'date': '2024-01-15T10:00:00Z',
            'duration_minutes': 60,
            'meeting_type': 'planning'
        }

    @pytest.mark.asyncio
    async def test_generate_discussion_dynamics_success(self, generator, sample_transcript_data, sample_meeting_metadata):
        """Test successful discussion dynamics generation"""
        analysis_data = {'transcript_analysis': sample_transcript_data}
        
        dynamics = await generator._generate_discussion_dynamics(analysis_data, sample_meeting_metadata)
        
        assert isinstance(dynamics, DiscussionDynamics)
        assert dynamics.id is not None
        assert 'participation_distribution' in dynamics.participation_analysis
        assert 'conversation_flow' in dynamics.communication_patterns
        assert 'overall_sentiment' in dynamics.sentiment_analysis
        assert dynamics.confidence_score > 0

    @pytest.mark.asyncio
    async def test_generate_discussion_dynamics_empty_transcript(self, generator, sample_meeting_metadata):
        """Test discussion dynamics generation with empty transcript"""
        analysis_data = {'transcript_analysis': {'segments': []}}
        
        dynamics = await generator._generate_discussion_dynamics(analysis_data, sample_meeting_metadata)
        
        assert isinstance(dynamics, DiscussionDynamics)
        assert dynamics.confidence_score < 0.5
        assert 'error' in str(dynamics.participation_analysis)

    def test_analyze_participation_patterns(self, generator, sample_transcript_data):
        """Test participation pattern analysis"""
        participants = ['Alice', 'Bob', 'Charlie']
        
        result = generator._analyze_participation_patterns(sample_transcript_data, participants)
        
        assert 'participation_distribution' in result
        assert 'Alice' in result['participation_distribution']
        assert 'Bob' in result['participation_distribution']
        assert 'Charlie' in result['participation_distribution']
        
        # Check Alice has highest participation (2 segments)
        alice_percentage = result['participation_distribution']['Alice']['speaking_time_percentage']
        bob_percentage = result['participation_distribution']['Bob']['speaking_time_percentage']
        assert alice_percentage > bob_percentage

    def test_analyze_communication_patterns(self, generator, sample_transcript_data):
        """Test communication pattern analysis"""
        result = generator._analyze_communication_patterns(sample_transcript_data)
        
        assert 'conversation_flow' in result
        assert 'topic_transitions' in result
        assert 'interruption_patterns' in result
        assert 'question_response_patterns' in result

    def test_analyze_discussion_sentiment(self, generator, sample_transcript_data):
        """Test sentiment analysis"""
        result = generator._analyze_discussion_sentiment(sample_transcript_data)
        
        assert 'overall_sentiment' in result
        assert 'speaker_sentiment' in result
        assert 'emotional_tone' in result
        
        # Should detect positive sentiment from "agree", "great", "opportunity"
        assert result['overall_sentiment']['positive_percentage'] > 0

    def test_analyze_power_dynamics(self, generator, sample_transcript_data):
        """Test power dynamics analysis"""
        participants = ['Alice', 'Bob', 'Charlie']
        
        result = generator._analyze_power_dynamics(sample_transcript_data, participants)
        
        assert 'influence_scores' in result
        assert 'influence_ranking' in result
        assert 'Alice' in result['influence_scores']
        
        # Alice should have higher influence (decision-making language)
        alice_score = result['influence_scores']['Alice']['total_influence_score']
        assert alice_score > 0

    def test_calculate_participation_balance(self, generator):
        """Test participation balance calculation"""
        # Balanced participation
        balanced_distribution = {
            'Alice': {'speaking_time_percentage': 33.3},
            'Bob': {'speaking_time_percentage': 33.3},
            'Charlie': {'speaking_time_percentage': 33.4}
        }
        
        balance_score = generator._calculate_participation_balance(balanced_distribution)
        assert balance_score > 0.8  # Should be highly balanced
        
        # Unbalanced participation
        unbalanced_distribution = {
            'Alice': {'speaking_time_percentage': 80.0},
            'Bob': {'speaking_time_percentage': 15.0},
            'Charlie': {'speaking_time_percentage': 5.0}
        }
        
        balance_score = generator._calculate_participation_balance(unbalanced_distribution)
        assert balance_score < 0.5  # Should be poorly balanced


class TestHumanNeedsIntelligenceGeneration:
    """Test human needs intelligence generation functionality"""
    
    @pytest.fixture
    def generator(self):
        """Create Oracle output generator instance"""
        return OracleOutputGenerator()
    
    @pytest.fixture
    def sample_transcript_data(self):
        """Sample transcript data with needs indicators"""
        return {
            'segments': [
                {
                    'speaker': 'Alice',
                    'text': 'I need to be sure about the timeline. Can we confirm the deadlines?',
                    'duration': 4.0
                },
                {
                    'speaker': 'Bob',
                    'text': 'What if we try something new and creative? I love exploring different approaches.',
                    'duration': 4.5
                },
                {
                    'speaker': 'Charlie',
                    'text': 'In my experience, this approach works well. I can lead this initiative.',
                    'duration': 4.2
                },
                {
                    'speaker': 'Alice',
                    'text': 'I want to learn more about this. How can we grow our skills?',
                    'duration': 3.8
                },
                {
                    'speaker': 'Bob',
                    'text': 'This will really help our team connect and work together better.',
                    'duration': 3.5
                }
            ]
        }
    
    @pytest.fixture
    def sample_meeting_metadata(self):
        """Sample meeting metadata"""
        return {
            'participants': ['Alice', 'Bob', 'Charlie'],
            'meeting_id': 'test-meeting-456'
        }

    @pytest.mark.asyncio
    async def test_generate_human_needs_intelligence_success(self, generator, sample_transcript_data, sample_meeting_metadata):
        """Test successful human needs intelligence generation"""
        analysis_data = {'transcript_analysis': sample_transcript_data}
        
        needs_intel = await generator._generate_human_needs_intelligence(analysis_data, sample_meeting_metadata)
        
        assert isinstance(needs_intel, HumanNeedsIntelligence)
        assert needs_intel.id is not None
        assert len(needs_intel.individual_analyses) > 0
        assert 'team_need_averages' in needs_intel.team_analysis
        assert needs_intel.confidence_score > 0

    def test_analyze_individual_needs(self, generator, sample_transcript_data):
        """Test individual needs analysis"""
        participants = ['Alice', 'Bob', 'Charlie']
        
        result = generator._analyze_individual_needs(sample_transcript_data, participants)
        
        assert len(result) == 3  # One analysis per participant
        
        # Check Alice's analysis (should show certainty needs)
        alice_analysis = next((a for a in result if a['participant'] == 'Alice'), None)
        assert alice_analysis is not None
        assert alice_analysis['certainty_indicators']['confirmation_requests'] > 0
        
        # Check Bob's analysis (should show variety needs)
        bob_analysis = next((a for a in result if a['participant'] == 'Bob'), None)
        assert bob_analysis is not None
        assert bob_analysis['variety_indicators']['creative_suggestions'] > 0

    def test_identify_certainty_indicators(self, generator):
        """Test certainty need indicators identification"""
        segments = [
            {'text': 'I need to be sure about this plan', 'duration': 3.0},
            {'text': 'Can we confirm the timeline?', 'duration': 2.5},
            {'text': 'I want a clear structure for this project', 'duration': 4.0}
        ]
        
        indicators = generator._identify_certainty_indicators(segments)
        
        assert indicators['keyword_count'] > 0
        assert indicators['confirmation_requests'] > 0
        assert indicators['structure_seeking'] > 0

    def test_identify_variety_indicators(self, generator):
        """Test variety need indicators identification"""
        segments = [
            {'text': 'What if we try something new and different?', 'duration': 3.0},
            {'text': 'I love creative approaches to challenges', 'duration': 3.5},
            {'text': 'Let\'s experiment with innovative solutions', 'duration': 4.0}
        ]
        
        indicators = generator._identify_variety_indicators(segments)
        
        assert indicators['keyword_count'] > 0
        assert indicators['creative_suggestions'] > 0
        assert indicators['change_advocacy'] > 0

    def test_identify_significance_indicators(self, generator):
        """Test significance need indicators identification"""
        segments = [
            {'text': 'In my experience, this is the best approach', 'duration': 4.0},
            {'text': 'I can lead this important initiative', 'duration': 3.0},
            {'text': 'I want recognition for my expertise', 'duration': 3.5}
        ]
        
        indicators = generator._identify_significance_indicators(segments)
        
        assert indicators['keyword_count'] > 0
        assert indicators['expertise_demonstration'] > 0
        assert indicators['leadership_taking'] > 0

    def test_calculate_individual_need_scores(self, generator):
        """Test individual need score calculation"""
        needs_analysis = {
            'certainty_indicators': {
                'keyword_count': 5,
                'question_count': 2,
                'structure_seeking': 3,
                'confirmation_requests': 1
            },
            'variety_indicators': {
                'keyword_count': 2,
                'change_advocacy': 1,
                'creative_suggestions': 1,
                'challenge_seeking': 0
            },
            'significance_indicators': {
                'keyword_count': 3,
                'expertise_demonstration': 2,
                'leadership_taking': 1,
                'recognition_seeking': 0
            },
            'connection_indicators': {},
            'growth_indicators': {},
            'contribution_indicators': {}
        }
        
        scores = generator._calculate_individual_need_scores(needs_analysis)
        
        assert 'certainty' in scores
        assert 'variety' in scores
        assert 'significance' in scores
        assert scores['certainty'] > scores['variety']  # Should have higher certainty score

    def test_analyze_team_needs(self, generator):
        """Test team needs analysis"""
        individual_analyses = [
            {
                'participant': 'Alice',
                'need_scores': {'certainty': 8.0, 'variety': 2.0, 'significance': 3.0},
                'primary_need': 'certainty'
            },
            {
                'participant': 'Bob',
                'need_scores': {'certainty': 1.0, 'variety': 7.0, 'significance': 4.0},
                'primary_need': 'variety'
            },
            {
                'participant': 'Charlie',
                'need_scores': {'certainty': 3.0, 'variety': 2.0, 'significance': 8.0},
                'primary_need': 'significance'
            }
        ]
        
        result = generator._analyze_team_needs(individual_analyses, {})
        
        assert 'team_need_averages' in result
        assert 'dominant_team_needs' in result
        assert 'need_complementarity' in result
        assert result['team_need_averages']['certainty'] == 4.0  # (8+1+3)/3

    def test_analyze_need_complementarity(self, generator):
        """Test need complementarity analysis"""
        individual_analyses = [
            {'primary_need': 'certainty'},
            {'primary_need': 'variety'},
            {'primary_need': 'significance'}
        ]
        
        result = generator._analyze_need_complementarity(individual_analyses)
        
        assert 'need_distribution' in result
        assert 'need_diversity_score' in result
        assert 'complementarity_level' in result
        assert result['need_diversity_score'] == 0.5  # 3 different needs out of 6 total

if __name__ == '__main__':
    pytest.main([__file__])