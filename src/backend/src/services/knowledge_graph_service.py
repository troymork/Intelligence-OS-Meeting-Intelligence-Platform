"""
Knowledge Graph Service
Tracks concept relationships and evolution over time for organizational learning
"""

import os
import asyncio
import logging
import uuid
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import structlog
from collections import defaultdict, Counter
import networkx as nx
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = structlog.get_logger(__name__)

class ConceptType(Enum):
    """Types of concepts in the knowledge graph"""
    TOPIC = "topic"
    DECISION = "decision"
    ACTION = "action"
    CHALLENGE = "challenge"
    SOLUTION = "solution"
    PERSON = "person"
    PROCESS = "process"
    GOAL = "goal"
    RISK = "risk"
    OPPORTUNITY = "opportunity"
    SKILL = "skill"
    RESOURCE = "resource"

class RelationshipType(Enum):
    """Types of relationships between concepts"""
    RELATES_TO = "relates_to"
    CAUSES = "causes"
    SOLVES = "solves"
    DEPENDS_ON = "depends_on"
    LEADS_TO = "leads_to"
    CONFLICTS_WITH = "conflicts_with"
    SUPPORTS = "supports"
    IMPLEMENTS = "implements"
    MENTIONS = "mentions"
    PARTICIPATES_IN = "participates_in"
    OWNS = "owns"
    REQUIRES = "requires"

class EvolutionType(Enum):
    """Types of concept evolution"""
    EMERGENCE = "emergence"
    GROWTH = "growth"
    DECLINE = "decline"
    TRANSFORMATION = "transformation"
    MERGER = "merger"
    SPLIT = "split"
    STABILIZATION = "stabilization"

@dataclass
class Concept:
    """A concept in the knowledge graph"""
    id: str
    name: str
    concept_type: ConceptType
    description: str
    attributes: Dict[str, Any]
    first_mentioned: datetime
    last_mentioned: datetime
    mention_count: int
    importance_score: float
    evolution_history: List[Dict[str, Any]]
    related_meetings: Set[str]
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Relationship:
    """A relationship between concepts"""
    id: str
    source_concept_id: str
    target_concept_id: str
    relationship_type: RelationshipType
    strength: float  # 0-1 scale
    confidence: float  # 0-1 scale
    evidence: List[str]  # Supporting evidence
    first_observed: datetime
    last_observed: datetime
    observation_count: int
    context: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class KnowledgeEvolution:
    """Tracks how knowledge evolves over time"""
    id: str
    concept_id: str
    evolution_type: EvolutionType
    timestamp: datetime
    description: str
    before_state: Dict[str, Any]
    after_state: Dict[str, Any]
    triggers: List[str]  # What caused this evolution
    impact_score: float
    confidence: float
    metadata: Dict[str, Any]

@dataclass
class LearningMetrics:
    """Metrics for organizational learning"""
    period_start: datetime
    period_end: datetime
    new_concepts_discovered: int
    concepts_evolved: int
    relationships_formed: int
    knowledge_depth_score: float  # How deep the knowledge is
    knowledge_breadth_score: float  # How broad the knowledge is
    knowledge_connectivity_score: float  # How connected concepts are
    learning_velocity: float  # Rate of knowledge acquisition
    wisdom_indicators: Dict[str, float]
    collective_intelligence_score: float

class KnowledgeGraphService:
    """Service for managing organizational knowledge graph"""
    
    def __init__(self):
        self.graph = nx.DiGraph()  # Directed graph for concepts and relationships
        self.concepts = {}  # concept_id -> Concept
        self.relationships = {}  # relationship_id -> Relationship
        self.evolution_history = []  # List of KnowledgeEvolution
        self.learning_metrics_history = []  # Historical learning metrics
        
        # Text analysis for concept extraction
        self.vectorizer = TfidfVectorizer(
            max_features=500,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        # Configuration
        self.config = {
            'min_mention_threshold': 2,  # Minimum mentions to create concept
            'relationship_strength_threshold': 0.3,  # Minimum strength for relationships
            'evolution_detection_window_days': 30,  # Window for detecting evolution
            'importance_decay_factor': 0.95,  # Daily decay for concept importance
            'max_concepts_per_meeting': 20  # Maximum concepts to extract per meeting
        }
    
    async def process_meeting_knowledge(self, meeting_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a meeting to extract and update knowledge graph"""
        try:
            meeting_id = meeting_data.get('meeting_id', str(uuid.uuid4()))
            meeting_date = datetime.fromisoformat(meeting_data.get('date', datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            
            logger.info("Processing meeting knowledge", meeting_id=meeting_id)
            
            # Extract concepts from meeting
            extracted_concepts = await self._extract_concepts_from_meeting(meeting_data)
            
            # Update or create concepts in graph
            updated_concepts = await self._update_concepts(extracted_concepts, meeting_id, meeting_date)
            
            # Extract and update relationships
            new_relationships = await self._extract_relationships(meeting_data, updated_concepts)
            updated_relationships = await self._update_relationships(new_relationships, meeting_id, meeting_date)
            
            # Detect knowledge evolution
            evolutions = await self._detect_knowledge_evolution(updated_concepts, meeting_date)
            
            # Update graph structure
            await self._update_graph_structure(updated_concepts, updated_relationships)
            
            # Calculate learning metrics
            learning_metrics = await self._calculate_learning_metrics(meeting_date)
            
            result = {
                'meeting_id': meeting_id,
                'concepts_processed': len(updated_concepts),
                'relationships_processed': len(updated_relationships),
                'evolutions_detected': len(evolutions),
                'learning_metrics': learning_metrics,
                'knowledge_graph_stats': await self._get_graph_statistics(),
                'processing_timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info("Meeting knowledge processing completed",
                       meeting_id=meeting_id,
                       concepts_count=len(updated_concepts),
                       relationships_count=len(updated_relationships))
            
            return result
            
        except Exception as e:
            logger.error("Meeting knowledge processing failed", error=str(e))
            raise
    
    async def _extract_concepts_from_meeting(self, meeting_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract concepts from meeting data"""
        try:
            concepts = []
            
            # Extract from transcript
            transcript_concepts = await self._extract_concepts_from_transcript(meeting_data)
            concepts.extend(transcript_concepts)
            
            # Extract from decisions
            decision_concepts = await self._extract_concepts_from_decisions(meeting_data)
            concepts.extend(decision_concepts)
            
            # Extract from actions
            action_concepts = await self._extract_concepts_from_actions(meeting_data)
            concepts.extend(action_concepts)
            
            # Extract from strategic implications
            strategic_concepts = await self._extract_concepts_from_strategic_data(meeting_data)
            concepts.extend(strategic_concepts)
            
            # Deduplicate and rank concepts
            deduplicated_concepts = self._deduplicate_concepts(concepts)
            ranked_concepts = self._rank_concepts(deduplicated_concepts)
            
            # Return top concepts
            return ranked_concepts[:self.config['max_concepts_per_meeting']]
            
        except Exception as e:
            logger.error("Concept extraction failed", error=str(e))
            return []
    
    async def _extract_concepts_from_transcript(self, meeting_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract concepts from meeting transcript"""
        concepts = []
        
        try:
            transcript_data = meeting_data.get('transcript_analysis', {})
            segments = transcript_data.get('segments', [])
            
            if not segments:
                return concepts
            
            # Combine all text
            all_text = ' '.join([segment.get('text', '') for segment in segments])
            
            # Extract key terms using TF-IDF
            try:
                tfidf_matrix = self.vectorizer.fit_transform([all_text])
                feature_names = self.vectorizer.get_feature_names_out()
                tfidf_scores = tfidf_matrix.toarray()[0]
                
                # Get top terms
                top_indices = np.argsort(tfidf_scores)[-20:]  # Top 20 terms
                
                for idx in top_indices:
                    if tfidf_scores[idx] > 0.1:  # Minimum relevance threshold
                        term = feature_names[idx]
                        concepts.append({
                            'name': term,
                            'type': self._classify_concept_type(term, all_text),
                            'relevance_score': float(tfidf_scores[idx]),
                            'context': self._extract_concept_context(term, segments),
                            'source': 'transcript'
                        })
            
            except ValueError:
                # Handle case where text is insufficient for TF-IDF
                pass
            
            # Extract named entities (simplified approach)
            entity_concepts = self._extract_named_entities(segments)
            concepts.extend(entity_concepts)
            
            return concepts
            
        except Exception as e:
            logger.error("Transcript concept extraction failed", error=str(e))
            return []
    
    async def _extract_concepts_from_decisions(self, meeting_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract concepts from meeting decisions"""
        concepts = []
        
        try:
            decisions = meeting_data.get('decisions', [])
            
            for decision in decisions:
                # Decision itself as a concept
                concepts.append({
                    'name': decision.get('title', 'Unnamed Decision'),
                    'type': ConceptType.DECISION,
                    'relevance_score': decision.get('confidence_score', 0.5),
                    'context': decision.get('description', ''),
                    'source': 'decisions',
                    'attributes': {
                        'priority': decision.get('priority'),
                        'status': decision.get('status'),
                        'stakeholders': decision.get('stakeholders', [])
                    }
                })
                
                # Extract concepts from decision description
                description = decision.get('description', '') + ' ' + decision.get('rationale', '')
                if description.strip():
                    desc_concepts = self._extract_concepts_from_text(description, 'decision_context')
                    concepts.extend(desc_concepts)
            
            return concepts
            
        except Exception as e:
            logger.error("Decision concept extraction failed", error=str(e))
            return []
    
    async def _extract_concepts_from_actions(self, meeting_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract concepts from meeting actions"""
        concepts = []
        
        try:
            actions = meeting_data.get('actions', [])
            
            for action in actions:
                # Action itself as a concept
                concepts.append({
                    'name': action.get('title', 'Unnamed Action'),
                    'type': ConceptType.ACTION,
                    'relevance_score': action.get('confidence_score', 0.5),
                    'context': action.get('description', ''),
                    'source': 'actions',
                    'attributes': {
                        'owner': action.get('owner'),
                        'priority': action.get('priority'),
                        'due_date': action.get('due_date'),
                        'exponential_potential': action.get('exponential_potential', 0)
                    }
                })
                
                # Extract concepts from action description
                description = action.get('description', '')
                if description.strip():
                    desc_concepts = self._extract_concepts_from_text(description, 'action_context')
                    concepts.extend(desc_concepts)
            
            return concepts
            
        except Exception as e:
            logger.error("Action concept extraction failed", error=str(e))
            return []
    
    def _classify_concept_type(self, term: str, context: str) -> ConceptType:
        """Classify the type of a concept based on term and context"""
        term_lower = term.lower()
        context_lower = context.lower()
        
        # Decision indicators
        if any(word in term_lower for word in ['decision', 'decide', 'choose', 'select']):
            return ConceptType.DECISION
        
        # Action indicators
        if any(word in term_lower for word in ['action', 'task', 'implement', 'execute', 'do']):
            return ConceptType.ACTION
        
        # Challenge indicators
        if any(word in term_lower for word in ['problem', 'issue', 'challenge', 'obstacle', 'blocker']):
            return ConceptType.CHALLENGE
        
        # Solution indicators
        if any(word in term_lower for word in ['solution', 'fix', 'resolve', 'answer', 'approach']):
            return ConceptType.SOLUTION
        
        # Process indicators
        if any(word in term_lower for word in ['process', 'workflow', 'procedure', 'method', 'system']):
            return ConceptType.PROCESS
        
        # Goal indicators
        if any(word in term_lower for word in ['goal', 'objective', 'target', 'aim', 'purpose']):
            return ConceptType.GOAL
        
        # Risk indicators
        if any(word in term_lower for word in ['risk', 'threat', 'danger', 'concern', 'vulnerability']):
            return ConceptType.RISK
        
        # Opportunity indicators
        if any(word in term_lower for word in ['opportunity', 'chance', 'potential', 'possibility']):
            return ConceptType.OPPORTUNITY
        
        # Default to topic
        return ConceptType.TOPIC
    
    def _extract_concept_context(self, term: str, segments: List[Dict[str, Any]]) -> str:
        """Extract context for a concept from transcript segments"""
        contexts = []
        
        for segment in segments:
            text = segment.get('text', '').lower()
            if term.lower() in text:
                contexts.append(segment.get('text', ''))
        
        # Return first context or empty string
        return contexts[0] if contexts else ""
    
    def _extract_named_entities(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract named entities as concepts (simplified approach)"""
        concepts = []
        
        # Simple pattern-based entity extraction
        person_patterns = [
            r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # First Last
            r'\b[A-Z][a-z]+\b(?=\s+(?:said|mentioned|suggested|proposed))'  # Name before speech verbs
        ]
        
        for segment in segments:
            text = segment.get('text', '')
            speaker = segment.get('speaker', '')
            
            # Add speaker as person concept
            if speaker and speaker != 'Unknown':
                concepts.append({
                    'name': speaker,
                    'type': ConceptType.PERSON,
                    'relevance_score': 0.8,
                    'context': f"Participant in meeting",
                    'source': 'speaker_identification'
                })
        
        return concepts
    
    def _extract_concepts_from_text(self, text: str, source: str) -> List[Dict[str, Any]]:
        """Extract concepts from arbitrary text"""
        concepts = []
        
        try:
            # Simple keyword extraction
            important_terms = self._extract_important_terms(text)
            
            for term, score in important_terms:
                concepts.append({
                    'name': term,
                    'type': self._classify_concept_type(term, text),
                    'relevance_score': score,
                    'context': text[:200],  # First 200 chars as context
                    'source': source
                })
            
            return concepts
            
        except Exception as e:
            logger.error("Text concept extraction failed", error=str(e))
            return []
    
    def _extract_important_terms(self, text: str) -> List[Tuple[str, float]]:
        """Extract important terms from text with scores"""
        # Simple approach: split by common delimiters and score by length and capitalization
        words = text.replace(',', ' ').replace('.', ' ').replace(';', ' ').split()
        
        term_scores = {}
        for word in words:
            cleaned_word = word.strip('.,!?;:"()[]{}')
            if len(cleaned_word) > 3 and cleaned_word.isalpha():
                score = len(cleaned_word) / 20.0  # Length-based scoring
                if cleaned_word[0].isupper():
                    score += 0.2  # Bonus for capitalization
                term_scores[cleaned_word] = max(term_scores.get(cleaned_word, 0), score)
        
        # Return top terms
        sorted_terms = sorted(term_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_terms[:10]  # Top 10 terms
    
    def _deduplicate_concepts(self, concepts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate concepts and merge similar ones"""
        deduplicated = {}
        
        for concept in concepts:
            name = concept['name'].lower().strip()
            
            if name in deduplicated:
                # Merge with existing concept
                existing = deduplicated[name]
                existing['relevance_score'] = max(existing['relevance_score'], concept['relevance_score'])
                if concept.get('context') and len(concept['context']) > len(existing.get('context', '')):
                    existing['context'] = concept['context']
            else:
                deduplicated[name] = concept.copy()
                deduplicated[name]['name'] = concept['name']  # Preserve original case
        
        return list(deduplicated.values())
    
    def _rank_concepts(self, concepts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank concepts by relevance and importance"""
        # Sort by relevance score
        return sorted(concepts, key=lambda x: x.get('relevance_score', 0), reverse=True)
    
    async def _update_concepts(self, extracted_concepts: List[Dict[str, Any]], 
                             meeting_id: str, meeting_date: datetime) -> List[Concept]:
        """Update or create concepts in the knowledge graph"""
        updated_concepts = []
        
        try:
            for concept_data in extracted_concepts:
                concept_name = concept_data['name']
                concept_type = concept_data.get('type', ConceptType.TOPIC)
                
                # Check if concept already exists
                existing_concept = self._find_concept_by_name(concept_name)
                
                if existing_concept:
                    # Update existing concept
                    existing_concept.last_mentioned = meeting_date
                    existing_concept.mention_count += 1
                    existing_concept.related_meetings.add(meeting_id)
                    
                    # Update importance score
                    relevance = concept_data.get('relevance_score', 0.5)
                    existing_concept.importance_score = (existing_concept.importance_score * 0.8) + (relevance * 0.2)
                    
                    # Update attributes
                    if concept_data.get('attributes'):
                        existing_concept.attributes.update(concept_data['attributes'])
                    
                    updated_concepts.append(existing_concept)
                else:
                    # Create new concept
                    new_concept = Concept(
                        id=str(uuid.uuid4()),
                        name=concept_name,
                        concept_type=concept_type if isinstance(concept_type, ConceptType) else ConceptType.TOPIC,
                        description=concept_data.get('context', ''),
                        attributes=concept_data.get('attributes', {}),
                        first_mentioned=meeting_date,
                        last_mentioned=meeting_date,
                        mention_count=1,
                        importance_score=concept_data.get('relevance_score', 0.5),
                        evolution_history=[],
                        related_meetings={meeting_id}
                    )
                    
                    self.concepts[new_concept.id] = new_concept
                    updated_concepts.append(new_concept)
            
            return updated_concepts
            
        except Exception as e:
            logger.error("Concept update failed", error=str(e))
            return []
    
    def _find_concept_by_name(self, name: str) -> Optional[Concept]:
        """Find a concept by name (case-insensitive)"""
        name_lower = name.lower()
        for concept in self.concepts.values():
            if concept.name.lower() == name_lower:
                return concept
        return None
    
    async def get_knowledge_graph_summary(self) -> Dict[str, Any]:
        """Get a summary of the current knowledge graph"""
        try:
            # Basic statistics
            total_concepts = len(self.concepts)
            total_relationships = len(self.relationships)
            
            # Concept type distribution
            concept_types = defaultdict(int)
            for concept in self.concepts.values():
                concept_types[concept.concept_type.value] += 1
            
            # Relationship type distribution
            relationship_types = defaultdict(int)
            for relationship in self.relationships.values():
                relationship_types[relationship.relationship_type.value] += 1
            
            # Top concepts by importance
            top_concepts = sorted(
                self.concepts.values(),
                key=lambda x: x.importance_score,
                reverse=True
            )[:10]
            
            # Recent evolutions
            recent_evolutions = sorted(
                self.evolution_history,
                key=lambda x: x.timestamp,
                reverse=True
            )[:5]
            
            # Graph connectivity metrics
            connectivity_metrics = await self._calculate_connectivity_metrics()
            
            return {
                'total_concepts': total_concepts,
                'total_relationships': total_relationships,
                'concept_type_distribution': dict(concept_types),
                'relationship_type_distribution': dict(relationship_types),
                'top_concepts': [
                    {
                        'name': c.name,
                        'type': c.concept_type.value,
                        'importance_score': c.importance_score,
                        'mention_count': c.mention_count
                    } for c in top_concepts
                ],
                'recent_evolutions': [
                    {
                        'concept_id': e.concept_id,
                        'evolution_type': e.evolution_type.value,
                        'description': e.description,
                        'timestamp': e.timestamp.isoformat()
                    } for e in recent_evolutions
                ],
                'connectivity_metrics': connectivity_metrics,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Knowledge graph summary generation failed", error=str(e))
            return {'error': 'Summary generation failed'}
    
    async def _calculate_connectivity_metrics(self) -> Dict[str, float]:
        """Calculate graph connectivity metrics"""
        try:
            if not self.graph.nodes():
                return {'density': 0.0, 'average_clustering': 0.0, 'average_path_length': 0.0}
            
            # Graph density
            density = nx.density(self.graph)
            
            # Average clustering coefficient
            clustering = nx.average_clustering(self.graph.to_undirected())
            
            # Average shortest path length (for connected components)
            try:
                if nx.is_connected(self.graph.to_undirected()):
                    avg_path_length = nx.average_shortest_path_length(self.graph.to_undirected())
                else:
                    # Calculate for largest connected component
                    largest_cc = max(nx.connected_components(self.graph.to_undirected()), key=len)
                    subgraph = self.graph.subgraph(largest_cc).to_undirected()
                    avg_path_length = nx.average_shortest_path_length(subgraph)
            except:
                avg_path_length = 0.0
            
            return {
                'density': density,
                'average_clustering': clustering,
                'average_path_length': avg_path_length
            }
            
        except Exception as e:
            logger.error("Connectivity metrics calculation failed", error=str(e))
            return {'density': 0.0, 'average_clustering': 0.0, 'average_path_length': 0.0}

# Global service instance
knowledge_graph_service = KnowledgeGraphService()