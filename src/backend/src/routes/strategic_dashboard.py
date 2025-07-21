"""
Strategic Dashboard API Routes
Provides endpoints for strategic alignment visualization and tracking
"""

from fastapi import APIRouter, HTTPException, Query, Body
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import structlog

from ..services.strategic_dashboard_service import strategic_dashboard_service

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/strategic-dashboard", tags=["strategic-dashboard"])

# Request/Response Models
class DashboardRequest(BaseModel):
    """Request model for dashboard data"""
    dashboard_type: str = Field(..., description="Type of dashboard (overview, sdg_alignment, doughnut_economy, agreement_economy)")
    filters: Optional[Dict[str, Any]] = Field(None, description="Filters to apply to dashboard data")
    time_range: Optional[Dict[str, str]] = Field(None, description="Time range for dashboard data (start and end dates)")

class OpportunityMapRequest(BaseModel):
    """Request model for creating opportunity maps"""
    opportunity_id: str = Field(..., description="Unique identifier for the opportunity")
    name: str = Field(..., description="Name of the opportunity")
    impact_score: float = Field(..., ge=0.0, le=1.0, description="Impact score (0.0 to 1.0)")
    effort_score: float = Field(..., ge=0.0, le=1.0, description="Effort score (0.0 to 1.0)")
    priority_level: str = Field(..., description="Priority level (high, medium, low)")
    framework_alignment: Dict[str, float] = Field(..., description="Alignment scores for different frameworks")
    status: str = Field(default="identified", description="Current status of the opportunity")
    timeline: Optional[Dict[str, Any]] = Field(None, description="Timeline information")
    dependencies: Optional[List[str]] = Field(None, description="List of dependencies")

class ActionTrackingRequest(BaseModel):
    """Request model for action tracking"""
    action_id: str = Field(..., description="Unique identifier for the action")
    title: str = Field(..., description="Title of the action")
    description: Optional[str] = Field(None, description="Description of the action")
    owner: str = Field(..., description="Owner of the action")
    status: str = Field(default="not_started", description="Current status (not_started, in_progress, completed, blocked)")
    progress_percentage: float = Field(default=0.0, ge=0.0, le=1.0, description="Progress percentage (0.0 to 1.0)")
    due_date: Optional[str] = Field(None, description="Due date in ISO format")
    strategic_alignment: Optional[Dict[str, float]] = Field(None, description="Strategic alignment scores")
    impact_metrics: Optional[Dict[str, float]] = Field(None, description="Impact metrics")

class DashboardResponse(BaseModel):
    """Response model for dashboard data"""
    dashboard_id: str
    type: str
    title: str
    description: str
    generated_at: str
    sections: List[Dict[str, Any]]
    metrics: List[Dict[str, Any]]
    visualizations: List[Dict[str, Any]]
    insights: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]

# Dashboard Data Endpoints
@router.get("/dashboard/{dashboard_type}")
async def get_dashboard_data(
    dashboard_type: str,
    filters: Optional[str] = Query(None, description="JSON string of filters"),
    start_date: Optional[str] = Query(None, description="Start date in ISO format"),
    end_date: Optional[str] = Query(None, description="End date in ISO format")
):
    """
    Get comprehensive dashboard data for a specific dashboard type
    
    Dashboard types:
    - overview: High-level strategic alignment overview
    - sdg_alignment: SDG-specific alignment dashboard
    - doughnut_economy: Doughnut Economy indicators dashboard
    - agreement_economy: Agreement Economy collaboration dashboard
    """
    try:
        # Parse filters if provided
        parsed_filters = None
        if filters:
            import json
            try:
                parsed_filters = json.loads(filters)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid filters JSON format")
        
        # Parse time range if provided
        time_range = None
        if start_date or end_date:
            time_range = {}
            if start_date:
                try:
                    time_range['start'] = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                except ValueError:
                    raise HTTPException(status_code=400, detail="Invalid start_date format. Use ISO format.")
            if end_date:
                try:
                    time_range['end'] = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                except ValueError:
                    raise HTTPException(status_code=400, detail="Invalid end_date format. Use ISO format.")
        
        # Generate dashboard data
        dashboard_data = await strategic_dashboard_service.generate_dashboard_data(
            dashboard_type=dashboard_type,
            filters=parsed_filters,
            time_range=time_range
        )
        
        if 'error' in dashboard_data:
            raise HTTPException(status_code=500, detail=dashboard_data['error'])
        
        return JSONResponse(content=dashboard_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Dashboard data retrieval failed", error=str(e), dashboard_type=dashboard_type)
        raise HTTPException(status_code=500, detail=f"Failed to generate dashboard data: {str(e)}")

@router.post("/dashboard")
async def create_dashboard_data(request: DashboardRequest):
    """
    Create dashboard data with specific filters and time range
    """
    try:
        # Parse time range if provided
        time_range = None
        if request.time_range:
            time_range = {}
            if 'start' in request.time_range:
                time_range['start'] = datetime.fromisoformat(request.time_range['start'].replace('Z', '+00:00'))
            if 'end' in request.time_range:
                time_range['end'] = datetime.fromisoformat(request.time_range['end'].replace('Z', '+00:00'))
        
        # Generate dashboard data
        dashboard_data = await strategic_dashboard_service.generate_dashboard_data(
            dashboard_type=request.dashboard_type,
            filters=request.filters,
            time_range=time_range
        )
        
        if 'error' in dashboard_data:
            raise HTTPException(status_code=500, detail=dashboard_data['error'])
        
        return JSONResponse(content=dashboard_data)
        
    except Exception as e:
        logger.error("Dashboard creation failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to create dashboard: {str(e)}")

@router.get("/summary/{dashboard_type}")
async def get_dashboard_summary(dashboard_type: str):
    """
    Get a summary of key metrics and insights for a dashboard
    """
    try:
        summary = await strategic_dashboard_service.get_dashboard_summary(dashboard_type)
        
        if 'error' in summary:
            raise HTTPException(status_code=500, detail=summary['error'])
        
        return JSONResponse(content=summary)
        
    except Exception as e:
        logger.error("Dashboard summary retrieval failed", error=str(e), dashboard_type=dashboard_type)
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard summary: {str(e)}")

# Metrics Endpoints
@router.get("/metrics/{metric_type}")
async def get_metric_data(
    metric_type: str,
    filters: Optional[str] = Query(None, description="JSON string of filters"),
    start_date: Optional[str] = Query(None, description="Start date in ISO format"),
    end_date: Optional[str] = Query(None, description="End date in ISO format")
):
    """
    Get specific metric data with optional filters and time range
    
    Metric types:
    - overall_alignment: Overall strategic alignment score
    - sdg_alignment: SDG alignment scores
    - doughnut_alignment: Doughnut Economy alignment
    - agreement_alignment: Agreement Economy alignment
    - opportunity_count: Strategic opportunity metrics
    - action_progress: Action completion metrics
    """
    try:
        # Parse filters if provided
        parsed_filters = None
        if filters:
            import json
            try:
                parsed_filters = json.loads(filters)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid filters JSON format")
        
        # Parse time range if provided
        time_range = None
        if start_date or end_date:
            time_range = {}
            if start_date:
                time_range['start'] = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            if end_date:
                time_range['end'] = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        # Get metric calculator
        calculator = strategic_dashboard_service.metric_calculators.get(metric_type)
        if not calculator:
            raise HTTPException(status_code=404, detail=f"Metric type '{metric_type}' not found")
        
        # Calculate metric
        metric_data = await calculator(parsed_filters, time_range)
        
        return JSONResponse(content={
            'metric_type': metric_type,
            'data': metric_data,
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Metric data retrieval failed", error=str(e), metric_type=metric_type)
        raise HTTPException(status_code=500, detail=f"Failed to get metric data: {str(e)}")

# Visualization Endpoints
@router.get("/visualization/{viz_id}")
async def get_visualization_data(
    viz_id: str,
    dashboard_type: str = Query(..., description="Dashboard type context"),
    filters: Optional[str] = Query(None, description="JSON string of filters"),
    start_date: Optional[str] = Query(None, description="Start date in ISO format"),
    end_date: Optional[str] = Query(None, description="End date in ISO format")
):
    """
    Get data for a specific visualization
    
    Visualization IDs:
    - framework_radar: Framework comparison radar chart
    - opportunity_matrix: Strategic opportunity matrix
    - alignment_timeline: Alignment trends timeline
    - sdg_wheel: SDG alignment wheel
    - doughnut_chart: Doughnut economy chart
    - collaboration_network: Collaboration network graph
    """
    try:
        # Parse filters if provided
        parsed_filters = None
        if filters:
            import json
            try:
                parsed_filters = json.loads(filters)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid filters JSON format")
        
        # Parse time range if provided
        time_range = None
        if start_date or end_date:
            time_range = {}
            if start_date:
                time_range['start'] = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            if end_date:
                time_range['end'] = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        # Generate visualization data
        viz_data = await strategic_dashboard_service._generate_specific_visualization(
            viz_id, dashboard_type, parsed_filters, time_range
        )
        
        if not viz_data:
            raise HTTPException(status_code=404, detail=f"Visualization '{viz_id}' not found")
        
        return JSONResponse(content=viz_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Visualization data retrieval failed", error=str(e), viz_id=viz_id)
        raise HTTPException(status_code=500, detail=f"Failed to get visualization data: {str(e)}")

# Opportunity Management Endpoints
@router.post("/opportunities")
async def create_opportunity_map(request: OpportunityMapRequest):
    """
    Create a new strategic opportunity map
    """
    try:
        # Convert due_date if provided
        opportunity_data = request.dict()
        
        opportunity_id = await strategic_dashboard_service.create_opportunity_map(opportunity_data)
        
        return JSONResponse(content={
            'opportunity_id': opportunity_id,
            'message': 'Strategic opportunity map created successfully',
            'created_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error("Opportunity map creation failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to create opportunity map: {str(e)}")

@router.get("/opportunities")
async def get_opportunity_maps(
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority level")
):
    """
    Get all strategic opportunity maps with optional filters
    """
    try:
        opportunity_maps = strategic_dashboard_service.opportunity_maps
        
        # Apply filters
        filtered_maps = []
        for opp_id, opp_map in opportunity_maps.items():
            if status and opp_map.status != status:
                continue
            if priority and opp_map.priority_level != priority:
                continue
            
            filtered_maps.append({
                'id': opp_map.id,
                'opportunity_id': opp_map.opportunity_id,
                'name': opp_map.name,
                'impact_score': opp_map.impact_score,
                'effort_score': opp_map.effort_score,
                'priority_level': opp_map.priority_level,
                'framework_alignment': opp_map.framework_alignment,
                'status': opp_map.status,
                'timeline': opp_map.timeline,
                'dependencies': opp_map.dependencies
            })
        
        return JSONResponse(content={
            'opportunities': filtered_maps,
            'total_count': len(filtered_maps),
            'retrieved_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error("Opportunity maps retrieval failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get opportunity maps: {str(e)}")

# Action Tracking Endpoints
@router.post("/actions")
async def create_action_tracking(request: ActionTrackingRequest):
    """
    Create or update an action tracking item
    """
    try:
        # Convert due_date if provided
        action_data = request.dict()
        if action_data.get('due_date'):
            action_data['due_date'] = datetime.fromisoformat(action_data['due_date'].replace('Z', '+00:00'))
        
        action_id = await strategic_dashboard_service.track_action_progress(action_data)
        
        return JSONResponse(content={
            'action_id': action_id,
            'message': 'Action tracking item created successfully',
            'created_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error("Action tracking creation failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to create action tracking: {str(e)}")

@router.get("/actions")
async def get_action_tracking(
    status: Optional[str] = Query(None, description="Filter by status"),
    owner: Optional[str] = Query(None, description="Filter by owner")
):
    """
    Get all action tracking items with optional filters
    """
    try:
        action_items = strategic_dashboard_service.action_tracking
        
        # Apply filters
        filtered_actions = []
        for action_id, action_item in action_items.items():
            if status and action_item.status != status:
                continue
            if owner and action_item.owner != owner:
                continue
            
            filtered_actions.append({
                'id': action_item.id,
                'action_id': action_item.action_id,
                'title': action_item.title,
                'description': action_item.description,
                'owner': action_item.owner,
                'status': action_item.status,
                'progress_percentage': action_item.progress_percentage,
                'due_date': action_item.due_date.isoformat() if action_item.due_date else None,
                'strategic_alignment': action_item.strategic_alignment,
                'impact_metrics': action_item.impact_metrics,
                'last_updated': action_item.last_updated.isoformat()
            })
        
        return JSONResponse(content={
            'actions': filtered_actions,
            'total_count': len(filtered_actions),
            'retrieved_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error("Action tracking retrieval failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get action tracking: {str(e)}")

@router.put("/actions/{action_id}/progress")
async def update_action_progress(
    action_id: str,
    progress_data: Dict[str, Any] = Body(...)
):
    """
    Update progress for a specific action
    """
    try:
        # Find the action
        action_item = None
        for item_id, item in strategic_dashboard_service.action_tracking.items():
            if item.action_id == action_id:
                action_item = item
                break
        
        if not action_item:
            raise HTTPException(status_code=404, detail=f"Action '{action_id}' not found")
        
        # Update progress
        if 'progress_percentage' in progress_data:
            action_item.progress_percentage = progress_data['progress_percentage']
        if 'status' in progress_data:
            action_item.status = progress_data['status']
        if 'impact_metrics' in progress_data:
            action_item.impact_metrics.update(progress_data['impact_metrics'])
        
        action_item.last_updated = datetime.utcnow()
        
        return JSONResponse(content={
            'action_id': action_id,
            'message': 'Action progress updated successfully',
            'updated_at': action_item.last_updated.isoformat()
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Action progress update failed", error=str(e), action_id=action_id)
        raise HTTPException(status_code=500, detail=f"Failed to update action progress: {str(e)}")

# Health Check Endpoint
@router.get("/health")
async def health_check():
    """
    Health check endpoint for the strategic dashboard service
    """
    try:
        # Perform basic service checks
        service_status = {
            'service': 'strategic_dashboard',
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'components': {
                'dashboard_configs': len(strategic_dashboard_service.dashboard_configs),
                'metric_calculators': len(strategic_dashboard_service.metric_calculators),
                'opportunity_maps': len(strategic_dashboard_service.opportunity_maps),
                'action_tracking': len(strategic_dashboard_service.action_tracking),
                'cache_size': len(strategic_dashboard_service.cache)
            }
        }
        
        return JSONResponse(content=service_status)
        
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return JSONResponse(
            status_code=503,
            content={
                'service': 'strategic_dashboard',
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
        )