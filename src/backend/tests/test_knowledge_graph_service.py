"""
Tests for Knowledge Graph Service
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from src.services.knowledge_graph_service import (
    KnowledgeGraphService,
    Concept,
    Relationship,
    ConceptType,
    RelationshipType,
    KnowledgeEvolution,
    EvolutionType
)

class TestKnowledgeGraphService:
    """Test knowledge graph service functionality"""
    
    @pytest.fixture
    def service(self):
        """Create knowledge graph service instance"""
        return KnowledgeGraphService()
    
    @pytest.fixture
    def sample_meeting_data(self):
        """Sample meeting data for testing"""
        return {
            'meeting_id': 'test-meeting-001',
            'date': '2024-01-15T10:00:00Z',
            'participants': ['Alice', 'Bob', 'Charlie'],
            'transcript_analysis': {
                'segments': [
                    {
                        'speaker': 'Alice',
                        'text': 'We need to implement a new deployment process to solve our reliability issues',
                        'timestamp': '2024-01-15T10:05:00Z'
                    },
                    {
                        'speaker': 'Bob',
                        'text': 'The current system has scalability problems that affect performance',
                        'timestamp': '2024-01-15T10:06:00Z'
                    },
                    {
                        'speaker': 'Charlie',
                        'text': 'Our team should focus on automation and continuous integration',
                        'timestamp': '2024-01-15T10:07:00Z'
                    }
                ]
            },
            'decisions': [
                {
                    'title': 'Implement CI/CD Pipeline',
                    'description': 'Set up continuous integration and deployment',
                    'confidence_score': 0.8,
                    'priority': 'high',
                    'stakeholders': ['DevOps Team', 'Development Team']
                }
            ],
            'actions': [
                {
                    'title': 'Research CI/CD Tools',
                    'description': 'Evaluate different CI/CD solutions',
                    'owner': 'Alice',
                    'confidence_score': 0.75,
                    'exponential_potential': 0.6
                }
            ]
        }

    @pytest.mark.asyncio
    async def test_process_meeting_knowledge_success(self, service, sample_meeting_data):
        """Test successful meeting knowledge processing"""
        result = await service.process_meeting_knowledge(sample_meeting_data)
        
        assert 'meeting_id' in result
        assert 'concepts_processed' in result
        assert 'relationships_processed' in result
        assert 'knowledge_graph_stats' in result
        assert result['meeting_id'] == 'test-meeting-001'
        assert result['concepts_processed'] >= 0

    @pytest.mark.asyncio
    async def test_extract_concepts_from_meeting(self, service, sample_meeting_data):
        """Test concept extraction from meeting"""
        concepts = await service._extract_concepts_from_meeting(sample_meeting_data)
        
        assert isinstance(concepts, list)
        assert len(concepts) > 0
        
        # Check concept structure
        concept = concepts[0]
        assert 'name' in concept
        assert 'type' in concept
        assert 'relevance_score' in concept

    @pytest.mark.asyncio
    async def test_extract_concepts_from_transcript(self, service, sample_meeting_data):
        """Test concept extraction from transcript"""
        concepts = await service._extract_concepts_from_transcript(sample_meeting_data)
        
        assert isinstance(concepts, list)
        # Should extract concepts like 'deployment', 'process', 'system', etc.

    @pytest.mark.asyncio
    async def test_extract_concepts_from_decisions(self, service, sample_meeting_data):
        """Test concept extraction from decisions"""
        concepts = await service._extract_concepts_from_decisions(sample_meeting_data)
        
        assert isinstance(concepts, list)
        assert len(concepts) > 0
        
        # Should include the decision itself as a concept
        decision_concepts = [c for c in concepts if c.get('type') == ConceptType.DECISION]
        assert len(decision_concepts) > 0

    @pytest.mark.asyncio
    async def test_extract_concepts_from_actions(self, service, sample_meeting_data):
        """Test concept extraction from actions"""
        concepts = await service._extract_concepts_from_actions(sample_meeting_data)
        
        assert isinstance(concepts, list)
        assert len(concepts) > 0
        
        # Should include the action itself as a concept
        action_concepts = [c for c in concepts if c.get('type') == ConceptType.ACTION]
        assert len(action_concepts) > 0

    def test_classify_concept_type(self, service):
        """Test concept type classification"""
        # Test decision classification
        assert service._classify_concept_type('decision', 'we need to decide') == ConceptType.DECISION
        
        # Test action classification
        assert service._classify_concept_type('implement', 'we should implement') == ConceptType.ACTION
        
        # Test challenge classification
        assert service._classify_concept_type('problem', 'this is a problem') == ConceptType.CHALLENGE
        
        # Test solution classification
        assert service._classify_concept_type('solution', 'here is the solution') == ConceptType.SOLUTION
        
        # Test default classification
        assert service._classify_concept_type('random_term', 'some context') == ConceptType.TOPIC

    def test_extract_concept_context(self, service):
        """Test concept context extraction"""
        segments = [
            {'text': 'We need to implement a new deployment process', 'speaker': 'Alice'},
            {'text': 'The deployment system is working well', 'speaker': 'Bob'}
        ]
        
        context = service._extract_concept_context('deployment', segments)
        assert isinstance(context, str)
        assert len(context) > 0

    def test_extract_named_entities(self, service):
        """Test named entity extraction"""
        segments = [
            {'text': 'Alice mentioned the new system', 'speaker': 'Alice'},
            {'text': 'Bob suggested a different approach', 'speaker': 'Bob'}
        ]
        
        entities = service._extract_named_entities(segments)
        
        assert isinstance(entities, list)
        # Should extract speakers as person entities
        person_entities = [e for e in entities if e.get('type') == ConceptType.PERSON]
        assert len(person_entities) >= 2

    def test_extract_important_terms(self, service):
        """Test important terms extraction"""
        text = "We need to implement a comprehensive deployment automation system"
        
        terms = service._extract_important_terms(text)
        
        assert isinstance(terms, list)
        assert len(terms) > 0
        
        # Check term structure
        term, score = terms[0]
        assert isinstance(term, str)
        assert isinstance(score, float)
        assert score > 0

    def test_deduplicate_concepts(self, service):
        """Test concept deduplication"""
        concepts = [
            {'name': 'Deployment', 'relevance_score': 0.8, 'context': 'First context'},
            {'name': 'deployment', 'relevance_score': 0.6, 'context': 'Second context'},
            {'name': 'System', 'relevance_score': 0.7, 'context': 'System context'}
        ]
        
        deduplicated = service._deduplicate_concepts(concepts)
        
        assert len(deduplicated) == 2  # 'Deployment' and 'System'
        
        # Check that higher relevance score is preserved
        deployment_concept = next(c for c in deduplicated if c['name'].lower() == 'deployment')
        assert deployment_concept['relevance_score'] == 0.8

    def test_rank_concepts(self, service):
        """Test concept ranking"""
        concepts = [
            {'name': 'Low Score', 'relevance_score': 0.3},
            {'name': 'High Score', 'relevance_score': 0.9},
            {'name': 'Medium Score', 'relevance_score': 0.6}
        ]
        
        ranked = service._rank_concepts(concepts)
        
        assert len(ranked) == 3
        assert ranked[0]['name'] == 'High Score'
        assert ranked[1]['name'] == 'Medium Score'
        assert ranked[2]['name'] == 'Low Score'

    @pytest.mark.asyncio
    async def test_update_concepts_new_concept(self, service):
        """Test updating concepts with new concept"""
        extracted_concepts = [
            {
                'name': 'New Concept',
                'type': ConceptType.TOPIC,
                'relevance_score': 0.8,
                'context': 'Test context'
            }
        ]
        
        meeting_id = 'test-meeting-001'
        meeting_date = datetime.utcnow()
        
        updated_concepts = await service._update_concepts(extracted_concepts, meeting_id, meeting_date)
        
        assert len(updated_concepts) == 1
        assert updated_concepts[0].name == 'New Concept'
        assert updated_concepts[0].mention_count == 1
        assert meeting_id in updated_concepts[0].related_meetings

    @pytest.mark.asyncio
    async def test_update_concepts_existing_concept(self, service):
        """Test updating concepts with existing concept"""
        # First, create an existing concept
        existing_concept = Concept(
            id='existing-001',
            name='Existing Concept',
            concept_type=ConceptType.TOPIC,
            description='Original description',
            attributes={},
            first_mentioned=datetime.utcnow() - timedelta(days=1),
            last_mentioned=datetime.utcnow() - timedelta(days=1),
            mention_count=1,
            importance_score=0.5,
            evolution_history=[],
            related_meetings={'old-meeting'}
        )
        
        service.concepts[existing_concept.id] = existing_concept
        
        # Now update with new mention
        extracted_concepts = [
            {
                'name': 'Existing Concept',
                'type': ConceptType.TOPIC,
                'relevance_score': 0.7,
                'context': 'New context'
            }
        ]
        
        meeting_id = 'test-meeting-002'
        meeting_date = datetime.utcnow()
        
        updated_concepts = await service._update_concepts(extracted_concepts, meeting_id, meeting_date)
        
        assert len(updated_concepts) == 1
        updated_concept = updated_concepts[0]
        assert updated_concept.mention_count == 2
        assert meeting_id in updated_concept.related_meetings
        assert 'old-meeting' in updated_concept.related_meetings

    def test_find_concept_by_name(self, service):
        """Test finding concept by name"""
        # Add a concept to the service
        concept = Concept(
            id='test-001',
            name='Test Concept',
            concept_type=ConceptType.TOPIC,
            description='Test',
            attributes={},
            first_mentioned=datetime.utcnow(),
            last_mentioned=datetime.utcnow(),
            mention_count=1,
            importance_score=0.5,
            evolution_history=[],
            related_meetings=set()
        )
        
        service.concepts[concept.id] = concept
        
        # Test finding by exact name
        found = service._find_concept_by_name('Test Concept')
        assert found is not None
        assert found.id == 'test-001'
        
        # Test finding by case-insensitive name
        found_case_insensitive = service._find_concept_by_name('test concept')
        assert found_case_insensitive is not None
        assert found_case_insensitive.id == 'test-001'
        
        # Test not finding non-existent concept
        not_found = service._find_concept_by_name('Non-existent Concept')
        assert not_found is None

    @pytest.mark.asyncio
    async def test_get_knowledge_graph_summary(self, service):
        """Test knowledge graph summary generation"""
        # Add some test data
        concept = Concept(
            id='test-001',
            name='Test Concept',
            concept_type=ConceptType.TOPIC,
            description='Test',
            attributes={},
            first_mentioned=datetime.utcnow(),
            last_mentioned=datetime.utcnow(),
            mention_count=5,
            importance_score=0.8,
            evolution_history=[],
            related_meetings=set()
        )
        
        service.concepts[concept.id] = concept
        
        summary = await service.get_knowledge_graph_summary()
        
        assert 'total_concepts' in summary
        assert 'total_relationships' in summary
        assert 'concept_type_distribution' in summary
        assert 'top_concepts' in summary
        assert 'connectivity_metrics' in summary
        
        assert summary['total_concepts'] == 1
        assert len(summary['top_concepts']) == 1
        assert summary['top_concepts'][0]['name'] == 'Test Concept'

    @pytest.mark.asyncio
    async def test_calculate_connectivity_metrics_empty_graph(self, service):
        """Test connectivity metrics calculation with empty graph"""
        metrics = await service._calculate_connectivity_metrics()
        
        assert 'density' in metrics
        assert 'average_clustering' in metrics
        assert 'average_path_length' in metrics
        
        assert metrics['density'] == 0.0
        assert metrics['average_clustering'] == 0.0
        assert metrics['average_path_length'] == 0.0

    @pytest.mark.asyncio
    async def test_calculate_connectivity_metrics_with_nodes(self, service):
        """Test connectivity metrics calculation with nodes"""
        # Add nodes to the graph
        service.graph.add_node('concept1')
        service.graph.add_node('concept2')
        service.graph.add_edge('concept1', 'concept2')
        
        metrics = await service._calculate_connectivity_metrics()
        
        assert isinstance(metrics['density'], float)
        assert isinstance(metrics['average_clustering'], float)
        assert isinstance(metrics['average_path_length'], float)
        
        assert metrics['density'] > 0


class TestKnowledgeGraphDataStructures:
    """Test knowledge graph data structures"""
    
    def test_concept_creation(self):
        """Test Concept creation"""
        concept = Concept(
            id='test-001',
            name='Test Concept',
            concept_type=ConceptType.DECISION,
            description='Test concept description',
            attributes={'priority': 'high'},
            first_mentioned=datetime.utcnow(),
            last_mentioned=datetime.utcnow(),
            mention_count=3,
            importance_score=0.8,
            evolution_history=[],
            related_meetings={'meeting-001', 'meeting-002'}
        )
        
        assert concept.id == 'test-001'
        assert concept.concept_type == ConceptType.DECISION
        assert concept.mention_count == 3
        assert len(concept.related_meetings) == 2

    def test_relationship_creation(self):
        """Test Relationship creation"""
        relationship = Relationship(
            id='rel-001',
            source_concept_id='concept-001',
            target_concept_id='concept-002',
            relationship_type=RelationshipType.CAUSES,
            strength=0.8,
            confidence=0.9,
            evidence=['Evidence 1', 'Evidence 2'],
            first_observed=datetime.utcnow(),
            last_observed=datetime.utcnow(),
            observation_count=2,
            context={'meeting_id': 'meeting-001'}
        )
        
        assert relationship.id == 'rel-001'
        assert relationship.relationship_type == RelationshipType.CAUSES
        assert relationship.strength == 0.8
        assert len(relationship.evidence) == 2

    def test_knowledge_evolution_creation(self):
        """Test KnowledgeEvolution creation"""
        evolution = KnowledgeEvolution(
            id='evo-001',
            concept_id='concept-001',
            evolution_type=EvolutionType.GROWTH,
            timestamp=datetime.utcnow(),
            description='Concept evolved through growth',
            before_state={'importance': 0.5},
            after_state={'importance': 0.8},
            triggers=['New evidence', 'Additional mentions'],
            impact_score=0.7,
            confidence=0.8,
            metadata={'meeting_id': 'meeting-001'}
        )
        
        assert evolution.id == 'evo-001'
        assert evolution.evolution_type == EvolutionType.GROWTH
        assert evolution.impact_score == 0.7
        assert len(evolution.triggers) == 2


if __name__ == '__main__':
    pytest.main([__file__])