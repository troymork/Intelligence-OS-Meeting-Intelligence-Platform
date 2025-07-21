"""
Pattern Visualization Service
Creates visual representations of organizational patterns and trends
"""

import asyncio
import logging
import uuid
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import structlog
from collections import defaultdict, Counter
import numpy as np
import json

logger = structlog.get_logger(__name__)

class VisualizationType(Enum):
    """Types of pattern visualizations"""
    TIMELINE = "timeline"
    NETWORK_GRAPH = "network_graph"
    HEATMAP = "heatmap"
    TREND_CHART = "trend_chart"
    SANKEY_DIAGRAM = "sankey_diagram"
    SCATTER_PLOT = "scatter_plot"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    TREEMAP = "treemap"
    FORCE_DIRECTED_GRAPH = "force_directed_graph"

class DashboardSection(Enum):
    """Dashboard sections for pattern visualization"""
    PATTERN_OVERVIEW = "pattern_overview"
    TREND_ANALYSIS = "trend_analysis"
    INTERVENTION_TRACKING = "intervention_tracking"
    PREDICTIVE_ANALYTICS = "predictive_analytics"
    KNOWLEDGE_EVOLUTION = "knowledge_evolution"
    LEARNING_METRICS = "learning_metrics"
    ORGANIZATIONAL_HEALTH = "organizational_health"
    STRATEGIC_ALIGNMENT = "strategic_alignment"

@dataclass
class VisualizationConfig:
    """Configuration for a visualization"""
    id: str
    title: str
    visualization_type: VisualizationType
    data_source: str
    filters: Dict[str, Any]
    styling: Dict[str, Any]
    interactivity: Dict[str, Any]
    refresh_interval: int  # seconds
    auto_refresh: bool
    export_formats: List[str]

@dataclass
class ChartData:
    """Data structure for chart visualization"""
    labels: List[str]
    datasets: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    last_updated: datetime
    data_quality_score: float

@dataclass
class NetworkGraphData:
    """Data structure for network graph visualization"""
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    layout_config: Dict[str, Any]
    interaction_config: Dict[str, Any]
    styling_config: Dict[str, Any]

@dataclass
class DashboardWidget:
    """Individual dashboard widget"""
    id: str
    title: str
    description: str
    widget_type: str
    position: Dict[str, int]  # x, y, width, height
    visualization_config: VisualizationConfig
    data: Any  # ChartData, NetworkGraphData, etc.
    last_updated: datetime
    update_frequency: int  # minutes
    is_active: bool

@dataclass
class Dashboard:
    """Complete dashboard configuration"""
    id: str
    name: str
    description: str
    category: DashboardSection
    widgets: List[DashboardWidget]
    layout_config: Dict[str, Any]
    access_permissions: List[str]
    auto_refresh_enabled: bool
    refresh_interval: int  # seconds
    created_by: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_modified: datetime = field(default_factory=datetime.utcnow)

class PatternVisualizationService:
    """Service for creating pattern visualizations and dashboards"""
    
    def __init__(self):
        self.dashboards = {}  # dashboard_id -> Dashboard
        self.widgets = {}  # widget_id -> DashboardWidget
        self.visualization_templates = self._initialize_visualization_templates()
        self.dashboard_templates = self._initialize_dashboard_templates()
        
        # Visualization configuration
        self.config = {
            'max_data_points': 1000,  # Maximum data points per visualization
            'default_refresh_interval': 300,  # 5 minutes
            'cache_duration': 600,  # 10 minutes
            'max_widgets_per_dashboard': 20,
            'supported_export_formats': ['png', 'svg', 'pdf', 'json', 'csv']
        }
    
    def _initialize_visualization_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize visualization templates"""
        return {
            'pattern_frequency_timeline': {
                'type': VisualizationType.TIMELINE,
                'title': 'Pattern Frequency Over Time',
                'description': 'Shows how pattern occurrences change over time',
                'data_requirements': ['timestamps', 'pattern_counts'],
                'styling': {
                    'color_scheme': 'viridis',
                    'line_width': 2,
                    'marker_size': 6,
                    'grid': True
                }
            },
            'concept_relationship_network': {
                'type': VisualizationType.NETWORK_GRAPH,
                'title': 'Concept Relationship Network',
                'description': 'Network visualization of concept relationships',
                'data_requirements': ['nodes', 'edges', 'weights'],
                'styling': {
                    'node_size_range': [10, 50],
                    'edge_width_range': [1, 5],
                    'color_by': 'importance',
                    'layout': 'force_directed'
                }
            },
            'learning_velocity_heatmap': {
                'type': VisualizationType.HEATMAP,
                'title': 'Learning Velocity Heatmap',
                'description': 'Heatmap showing learning intensity across time and topics',
                'data_requirements': ['time_periods', 'topics', 'learning_scores'],
                'styling': {
                    'color_scale': 'RdYlBu',
                    'show_values': True,
                    'cell_aspect': 'auto'
                }
            },
            'intervention_effectiveness_trends': {
                'type': VisualizationType.TREND_CHART,
                'title': 'Intervention Effectiveness Trends',
                'description': 'Tracks effectiveness of interventions over time',
                'data_requirements': ['interventions', 'effectiveness_scores', 'timestamps'],
                'styling': {
                    'multi_line': True,
                    'confidence_bands': True,
                    'annotations': True
                }
            },
            'knowledge_flow_sankey': {
                'type': VisualizationType.SANKEY_DIAGRAM,
                'title': 'Knowledge Flow Diagram',
                'description': 'Shows knowledge transfer pathways',
                'data_requirements': ['sources', 'targets', 'flow_values'],
                'styling': {
                    'node_padding': 10,
                    'link_opacity': 0.7,
                    'color_by_group': True
                }
            }
        }
    
    def _initialize_dashboard_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize dashboard templates"""
        return {
            'executive_overview': {
                'name': 'Executive Pattern Overview',
                'description': 'High-level view of organizational patterns and trends',
                'category': DashboardSection.PATTERN_OVERVIEW,
                'widgets': [
                    'pattern_summary_metrics',
                    'trend_indicators',
                    'critical_alerts',
                    'strategic_alignment_gauge'
                ]
            },
            'learning_analytics': {
                'name': 'Organizational Learning Analytics',
                'description': 'Detailed analysis of learning patterns and knowledge evolution',
                'category': DashboardSection.LEARNING_METRICS,
                'widgets': [
                    'learning_velocity_chart',
                    'knowledge_growth_timeline',
                    'wisdom_development_radar',
                    'collective_intelligence_trends'
                ]
            },
            'intervention_management': {
                'name': 'Intervention Management Dashboard',
                'description': 'Track and manage organizational interventions',
                'category': DashboardSection.INTERVENTION_TRACKING,
                'widgets': [
                    'active_interventions_list',
                    'effectiveness_tracking',
                    'intervention_pipeline',
                    'success_metrics_dashboard'
                ]
            },
            'predictive_insights': {
                'name': 'Predictive Analytics Dashboard',
                'description': 'Forecasts and predictive insights',
                'category': DashboardSection.PREDICTIVE_ANALYTICS,
                'widgets': [
                    'pattern_forecasts',
                    'risk_predictions',
                    'opportunity_identification',
                    'trend_extrapolation'
                ]
            }
        }
    
    async def create_pattern_timeline_visualization(self, 
                                                  pattern_data: List[Dict[str, Any]],
                                                  time_range: Tuple[datetime, datetime]) -> ChartData:
        """Create timeline visualization for pattern frequency"""
        try:
            start_date, end_date = time_range
            
            # Group patterns by date
            daily_counts = defaultdict(int)
            pattern_types = defaultdict(lambda: defaultdict(int))
            
            for pattern in pattern_data:
                if 'instances' in pattern:
                    for instance in pattern['instances']:
                        timestamp = datetime.fromisoformat(instance['timestamp'].replace('Z', '+00:00'))
                        if start_date <= timestamp <= end_date:
                            date_key = timestamp.date().isoformat()
                            daily_counts[date_key] += 1
                            pattern_types[pattern['pattern_type']][date_key] += 1
            
            # Create timeline data
            dates = []
            current_date = start_date.date()
            while current_date <= end_date.date():
                dates.append(current_date.isoformat())
                current_date += timedelta(days=1)
            
            # Prepare datasets
            datasets = []
            
            # Overall pattern count
            overall_counts = [daily_counts.get(date, 0) for date in dates]
            datasets.append({
                'label': 'Total Patterns',
                'data': overall_counts,
                'borderColor': '#3498db',
                'backgroundColor': 'rgba(52, 152, 219, 0.1)',
                'fill': True
            })
            
            # Individual pattern types
            colors = ['#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
            for i, (pattern_type, type_counts) in enumerate(pattern_types.items()):
                type_data = [type_counts.get(date, 0) for date in dates]
                datasets.append({
                    'label': pattern_type.replace('_', ' ').title(),
                    'data': type_data,
                    'borderColor': colors[i % len(colors)],
                    'backgroundColor': f"{colors[i % len(colors)]}20",
                    'fill': False
                })
            
            return ChartData(
                labels=dates,
                datasets=datasets,
                metadata={
                    'total_patterns': len(pattern_data),
                    'date_range': {'start': start_date.isoformat(), 'end': end_date.isoformat()},
                    'pattern_types': list(pattern_types.keys())
                },
                last_updated=datetime.utcnow(),
                data_quality_score=0.9
            )
            
        except Exception as e:
            logger.error("Pattern timeline visualization creation failed", error=str(e))
            raise
    
    async def create_concept_network_visualization(self, 
                                                 concepts: List[Dict[str, Any]],
                                                 relationships: List[Dict[str, Any]]) -> NetworkGraphData:
        """Create network graph visualization for concept relationships"""
        try:
            # Prepare nodes
            nodes = []
            for concept in concepts:
                node_size = min(max(concept.get('importance_score', 0.5) * 50, 10), 50)
                nodes.append({
                    'id': concept['id'],
                    'label': concept['name'],
                    'size': node_size,
                    'color': self._get_concept_color(concept.get('concept_type', 'topic')),
                    'group': concept.get('concept_type', 'topic'),
                    'title': f"{concept['name']}\nType: {concept.get('concept_type', 'topic')}\nImportance: {concept.get('importance_score', 0.5):.2f}",
                    'metadata': {
                        'mention_count': concept.get('mention_count', 0),
                        'importance_score': concept.get('importance_score', 0.5),
                        'concept_type': concept.get('concept_type', 'topic')
                    }
                })
            
            # Prepare edges
            edges = []
            for relationship in relationships:
                edge_width = max(relationship.get('strength', 0.5) * 5, 1)
                edges.append({
                    'from': relationship['source_concept_id'],
                    'to': relationship['target_concept_id'],
                    'width': edge_width,
                    'color': self._get_relationship_color(relationship.get('relationship_type', 'relates_to')),
                    'label': relationship.get('relationship_type', '').replace('_', ' '),
                    'title': f"Relationship: {relationship.get('relationship_type', '')}\nStrength: {relationship.get('strength', 0.5):.2f}",
                    'arrows': 'to',
                    'metadata': {
                        'strength': relationship.get('strength', 0.5),
                        'confidence': relationship.get('confidence', 0.5),
                        'relationship_type': relationship.get('relationship_type', 'relates_to')
                    }
                })
            
            return NetworkGraphData(
                nodes=nodes,
                edges=edges,
                layout_config={
                    'algorithm': 'forceAtlas2Based',
                    'gravitationalConstant': -50,
                    'centralGravity': 0.01,
                    'springLength': 100,
                    'springConstant': 0.08,
                    'damping': 0.4
                },
                interaction_config={
                    'dragNodes': True,
                    'dragView': True,
                    'zoomView': True,
                    'selectConnectedEdges': True,
                    'hover': True
                },
                styling_config={
                    'nodes': {
                        'borderWidth': 2,
                        'borderWidthSelected': 4,
                        'font': {'size': 12, 'color': '#333333'}
                    },
                    'edges': {
                        'smooth': {'type': 'continuous'},
                        'font': {'size': 10, 'color': '#666666'}
                    }
                }
            )
            
        except Exception as e:
            logger.error("Concept network visualization creation failed", error=str(e))
            raise
    
    async def create_learning_velocity_heatmap(self, 
                                             learning_data: List[Dict[str, Any]],
                                             time_periods: List[str],
                                             topics: List[str]) -> ChartData:
        """Create heatmap visualization for learning velocity"""
        try:
            # Initialize heatmap matrix
            heatmap_data = []
            
            for topic in topics:
                topic_row = []
                for period in time_periods:
                    # Calculate learning velocity for this topic-period combination
                    velocity = self._calculate_learning_velocity(learning_data, topic, period)
                    topic_row.append(velocity)
                heatmap_data.append(topic_row)
            
            # Prepare chart data
            datasets = [{
                'label': 'Learning Velocity',
                'data': heatmap_data,
                'backgroundColor': self._generate_heatmap_colors(heatmap_data),
                'borderColor': '#ffffff',
                'borderWidth': 1
            }]
            
            return ChartData(
                labels=time_periods,
                datasets=datasets,
                metadata={
                    'topics': topics,
                    'value_range': {
                        'min': min(min(row) for row in heatmap_data),
                        'max': max(max(row) for row in heatmap_data)
                    },
                    'total_data_points': len(topics) * len(time_periods)
                },
                last_updated=datetime.utcnow(),
                data_quality_score=0.85
            )
            
        except Exception as e:
            logger.error("Learning velocity heatmap creation failed", error=str(e))
            raise
    
    async def create_intervention_effectiveness_chart(self, 
                                                    interventions: List[Dict[str, Any]]) -> ChartData:
        """Create chart showing intervention effectiveness over time"""
        try:
            # Group interventions by type and track effectiveness over time
            intervention_types = defaultdict(list)
            
            for intervention in interventions:
                intervention_type = intervention.get('type', 'unknown')
                effectiveness_history = intervention.get('effectiveness_history', [])
                
                for record in effectiveness_history:
                    intervention_types[intervention_type].append({
                        'timestamp': record['timestamp'],
                        'effectiveness': record['effectiveness_score']
                    })
            
            # Create time series data
            datasets = []
            colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6']
            
            for i, (intervention_type, records) in enumerate(intervention_types.items()):
                # Sort by timestamp
                records.sort(key=lambda x: x['timestamp'])
                
                timestamps = [record['timestamp'] for record in records]
                effectiveness_scores = [record['effectiveness'] for record in records]
                
                datasets.append({
                    'label': intervention_type.replace('_', ' ').title(),
                    'data': effectiveness_scores,
                    'borderColor': colors[i % len(colors)],
                    'backgroundColor': f"{colors[i % len(colors)]}20",
                    'fill': False,
                    'tension': 0.4
                })
            
            # Use timestamps from first intervention type as labels
            labels = []
            if intervention_types:
                first_type_records = list(intervention_types.values())[0]
                labels = [record['timestamp'] for record in first_type_records]
            
            return ChartData(
                labels=labels,
                datasets=datasets,
                metadata={
                    'intervention_types': list(intervention_types.keys()),
                    'total_interventions': len(interventions),
                    'tracking_period': {
                        'start': min(labels) if labels else None,
                        'end': max(labels) if labels else None
                    }
                },
                last_updated=datetime.utcnow(),
                data_quality_score=0.8
            )
            
        except Exception as e:
            logger.error("Intervention effectiveness chart creation failed", error=str(e))
            raise
    
    async def create_dashboard(self, dashboard_template: str, 
                             user_id: str, 
                             custom_config: Optional[Dict[str, Any]] = None) -> Dashboard:
        """Create a new dashboard from template"""
        try:
            template = self.dashboard_templates.get(dashboard_template)
            if not template:
                raise ValueError(f"Dashboard template '{dashboard_template}' not found")
            
            dashboard_id = str(uuid.uuid4())
            
            # Create widgets for the dashboard
            widgets = []
            for i, widget_template in enumerate(template['widgets']):
                widget = await self._create_widget_from_template(widget_template, i)
                widgets.append(widget)
                self.widgets[widget.id] = widget
            
            # Apply custom configuration if provided
            config = template.copy()
            if custom_config:
                config.update(custom_config)
            
            dashboard = Dashboard(
                id=dashboard_id,
                name=config['name'],
                description=config['description'],
                category=DashboardSection(config['category']),
                widgets=widgets,
                layout_config=config.get('layout_config', self._get_default_layout_config()),
                access_permissions=[user_id],  # Creator has access by default
                auto_refresh_enabled=config.get('auto_refresh_enabled', True),
                refresh_interval=config.get('refresh_interval', self.config['default_refresh_interval']),
                created_by=user_id
            )
            
            self.dashboards[dashboard_id] = dashboard
            
            logger.info("Dashboard created successfully", 
                       dashboard_id=dashboard_id,
                       template=dashboard_template,
                       widgets_count=len(widgets))
            
            return dashboard
            
        except Exception as e:
            logger.error("Dashboard creation failed", error=str(e))
            raise
    
    def _get_concept_color(self, concept_type: str) -> str:
        """Get color for concept type"""
        color_map = {
            'topic': '#3498db',
            'decision': '#e74c3c',
            'action': '#2ecc71',
            'challenge': '#f39c12',
            'solution': '#9b59b6',
            'person': '#1abc9c',
            'process': '#34495e',
            'goal': '#e67e22',
            'risk': '#c0392b',
            'opportunity': '#27ae60',
            'skill': '#8e44ad',
            'resource': '#16a085'
        }
        return color_map.get(concept_type, '#95a5a6')
    
    def _get_relationship_color(self, relationship_type: str) -> str:
        """Get color for relationship type"""
        color_map = {
            'relates_to': '#bdc3c7',
            'causes': '#e74c3c',
            'solves': '#2ecc71',
            'depends_on': '#f39c12',
            'leads_to': '#3498db',
            'conflicts_with': '#c0392b',
            'supports': '#27ae60',
            'implements': '#8e44ad',
            'mentions': '#95a5a6',
            'participates_in': '#1abc9c',
            'owns': '#34495e',
            'requires': '#e67e22'
        }
        return color_map.get(relationship_type, '#95a5a6')
    
    def _calculate_learning_velocity(self, learning_data: List[Dict[str, Any]], 
                                   topic: str, period: str) -> float:
        """Calculate learning velocity for a specific topic and time period"""
        try:
            # Filter learning events for the topic and period
            relevant_events = []
            for event in learning_data:
                if (topic.lower() in event.get('description', '').lower() and
                    period in event.get('timestamp', '')):
                    relevant_events.append(event)
            
            if not relevant_events:
                return 0.0
            
            # Calculate velocity based on learning depth and frequency
            total_depth = sum(event.get('learning_depth', 0) for event in relevant_events)
            event_count = len(relevant_events)
            
            # Velocity = average depth * frequency factor
            avg_depth = total_depth / event_count if event_count > 0 else 0
            frequency_factor = min(event_count / 10, 1.0)  # Normalize frequency
            
            return avg_depth * frequency_factor
            
        except Exception as e:
            logger.error("Learning velocity calculation failed", error=str(e))
            return 0.0
    
    def _generate_heatmap_colors(self, data: List[List[float]]) -> List[List[str]]:
        """Generate colors for heatmap based on data values"""
        try:
            # Flatten data to find min/max
            flat_data = [val for row in data for val in row]
            min_val = min(flat_data)
            max_val = max(flat_data)
            
            # Generate colors
            colors = []
            for row in data:
                color_row = []
                for val in row:
                    # Normalize value to 0-1 range
                    normalized = (val - min_val) / (max_val - min_val) if max_val > min_val else 0
                    
                    # Generate color based on normalized value
                    if normalized < 0.33:
                        color = f'rgba(52, 152, 219, {0.3 + normalized * 0.4})'  # Blue
                    elif normalized < 0.66:
                        color = f'rgba(241, 196, 15, {0.3 + normalized * 0.4})'  # Yellow
                    else:
                        color = f'rgba(231, 76, 60, {0.3 + normalized * 0.4})'   # Red
                    
                    color_row.append(color)
                colors.append(color_row)
            
            return colors
            
        except Exception as e:
            logger.error("Heatmap color generation failed", error=str(e))
            return [['rgba(149, 165, 166, 0.5)' for _ in row] for row in data]

# Global service instance
pattern_visualization_service = PatternVisualizationService()