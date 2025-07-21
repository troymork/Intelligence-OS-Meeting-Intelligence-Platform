"""
Dart Integration API Routes
Handles action management, synchronization, and tracking endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, List, Optional, Any
from datetime import datetime
import structlog

from ..services.dart_integration_service import (
    DartIntegrationService, 
    ActionItem, 
    ActionPriority, 
    ActionStatus,
    ActionDependency
)
from ..security.auth import get_current_user
from ..security.validation import validate_request_data

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/dart", tags=["dart-integration"])

# Global service instance (in production, this would be dependency injected)
dart_service: Optional[DartIntegrationService] = None

def get_dart_service() -> DartIntegrationService:
    """Get Dart integration service instance"""
    global dart_service
    if dart_service is None:
        # In production, these would come from environment variables
        dart_api_url = "https://api.dart.example.com"
        api_key = "your-dart-api-key"
        dart_service = DartIntegrationService(dart_api_url, api_key)
    return dart_service

@router.post("/actions/generate")
async def generate_actions_from_meeting(
    meeting_data: Dict[str, Any],
    oracle_analysis: Dict[str, Any],
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user),
    service: DartIntegrationService = Depends(get_dart_service)
):
    """Generate action items from meeting data and Oracle analysis"""
    try:
        # Validate input data
        validate_request_data(meeting_data, {
            'id': str,
            'title': str,
            'date': str
        })
        
        # Generate actions
        actions = await service.generate_actions_from_meeting(meeting_data, oracle_analysis)
        
        # Schedule background sync to Dart
        background_tasks.add_task(sync_actions_to_dart, [action.id for action in actions])
        
        # Convert actions to response format
        action_responses = []
        for action in actions:
            action_responses.append({
                'id': action.id,
                'title': action.title,
                'description': action.description,
                'assignee': action.assignee,
                'priority': action.priority.value,
                'status': action.status.value,
                'due_date': action.due_date.isoformat() if action.due_date else None,
                'estimated_hours': action.estimated_hours,
                'tags': action.tags,
                'exponential_potential': action.exponential_potential,
                'velocity_estimate': action.velocity_estimate,
                'meeting_id': action.meeting_id,
                'created_at': action.created_at.isoformat()
            })
        
        logger.info("Generated actions from meeting",
                   meeting_id=meeting_data.get('id'),
                   action_count=len(actions),
                   user_id=current_user.get('id'))
        
        return {
            'success': True,
            'actions': action_responses,
            'count': len(actions),
            'meeting_id': meeting_data.get('id')
        }
        
    except Exception as e:
        logger.error("Failed to generate actions from meeting", 
                    meeting_id=meeting_data.get('id'),
                    error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to generate actions: {str(e)}")

@router.get("/actions")
async def get_actions(
    status: Optional[str] = None,
    assignee: Optional[str] = None,
    priority: Optional[str] = None,
    meeting_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: Dict = Depends(get_current_user),
    service: DartIntegrationService = Depends(get_dart_service)
):
    """Get actions with optional filtering"""
    try:
        # Get all actions from cache
        all_actions = list(service.action_cache.values())
        
        # Apply filters
        filtered_actions = all_actions
        
        if status:
            try:
                status_enum = ActionStatus(status.lower())
                filtered_actions = [a for a in filtered_actions if a.status == status_enum]
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
        
        if assignee:
            filtered_actions = [a for a in filtered_actions if a.assignee == assignee]
        
        if priority:
            try:
                priority_enum = ActionPriority(priority.lower())
                filtered_actions = [a for a in filtered_actions if a.priority == priority_enum]
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid priority: {priority}")
        
        if meeting_id:
            filtered_actions = [a for a in filtered_actions if a.meeting_id == meeting_id]
        
        # Sort by created_at descending
        filtered_actions.sort(key=lambda x: x.created_at, reverse=True)
        
        # Apply pagination
        total_count = len(filtered_actions)
        paginated_actions = filtered_actions[offset:offset + limit]
        
        # Convert to response format
        action_responses = []
        for action in paginated_actions:
            action_responses.append({
                'id': action.id,
                'title': action.title,
                'description': action.description,
                'assignee': action.assignee,
                'priority': action.priority.value,
                'status': action.status.value,
                'due_date': action.due_date.isoformat() if action.due_date else None,
                'estimated_hours': action.estimated_hours,
                'tags': action.tags,
                'exponential_potential': action.exponential_potential,
                'velocity_estimate': action.velocity_estimate,
                'meeting_id': action.meeting_id,
                'dart_id': action.dart_id,
                'created_at': action.created_at.isoformat(),
                'updated_at': action.updated_at.isoformat()
            })
        
        return {
            'success': True,
            'actions': action_responses,
            'total_count': total_count,
            'limit': limit,
            'offset': offset,
            'has_more': offset + limit < total_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get actions", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get actions: {str(e)}")

@router.get("/actions/{action_id}")
async def get_action(
    action_id: str,
    current_user: Dict = Depends(get_current_user),
    service: DartIntegrationService = Depends(get_dart_service)
):
    """Get a specific action by ID"""
    try:
        if action_id not in service.action_cache:
            raise HTTPException(status_code=404, detail="Action not found")
        
        action = service.action_cache[action_id]
        
        # Get dependencies
        dependencies = service.dependencies.get(action_id, [])
        
        return {
            'success': True,
            'action': {
                'id': action.id,
                'title': action.title,
                'description': action.description,
                'assignee': action.assignee,
                'priority': action.priority.value,
                'status': action.status.value,
                'due_date': action.due_date.isoformat() if action.due_date else None,
                'estimated_hours': action.estimated_hours,
                'tags': action.tags,
                'exponential_potential': action.exponential_potential,
                'velocity_estimate': action.velocity_estimate,
                'meeting_id': action.meeting_id,
                'dart_id': action.dart_id,
                'created_at': action.created_at.isoformat(),
                'updated_at': action.updated_at.isoformat(),
                'context': action.context
            },
            'dependencies': [
                {
                    'source_action_id': dep.source_action_id,
                    'target_action_id': dep.target_action_id,
                    'dependency_type': dep.dependency_type.value,
                    'description': dep.description,
                    'created_at': dep.created_at.isoformat()
                }
                for dep in dependencies
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get action", action_id=action_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get action: {str(e)}")

@router.put("/actions/{action_id}")
async def update_action(
    action_id: str,
    update_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user),
    service: DartIntegrationService = Depends(get_dart_service)
):
    """Update an action"""
    try:
        if action_id not in service.action_cache:
            raise HTTPException(status_code=404, detail="Action not found")
        
        action = service.action_cache[action_id]
        
        # Update allowed fields
        if 'title' in update_data:
            action.title = update_data['title']
        if 'description' in update_data:
            action.description = update_data['description']
        if 'assignee' in update_data:
            action.assignee = update_data['assignee']
        if 'priority' in update_data:
            try:
                action.priority = ActionPriority(update_data['priority'].lower())
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid priority: {update_data['priority']}")
        if 'status' in update_data:
            try:
                action.status = ActionStatus(update_data['status'].lower())
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status: {update_data['status']}")
        if 'due_date' in update_data:
            if update_data['due_date']:
                try:
                    action.due_date = datetime.fromisoformat(update_data['due_date'].replace('Z', '+00:00'))
                except ValueError:
                    raise HTTPException(status_code=400, detail="Invalid due_date format")
            else:
                action.due_date = None
        if 'estimated_hours' in update_data:
            action.estimated_hours = update_data['estimated_hours']
        if 'tags' in update_data:
            action.tags = update_data['tags']
        
        action.updated_at = datetime.utcnow()
        
        # Schedule background sync to Dart
        background_tasks.add_task(sync_actions_to_dart, [action_id])
        
        logger.info("Updated action", action_id=action_id, user_id=current_user.get('id'))
        
        return {
            'success': True,
            'message': 'Action updated successfully',
            'action_id': action_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update action", action_id=action_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to update action: {str(e)}")

@router.post("/actions/{action_id}/track")
async def track_action_progress(
    action_id: str,
    current_user: Dict = Depends(get_current_user),
    service: DartIntegrationService = Depends(get_dart_service)
):
    """Track progress of an action"""
    try:
        progress_data = await service.track_action_progress(action_id)
        
        if 'error' in progress_data:
            raise HTTPException(status_code=404, detail=progress_data['error'])
        
        return {
            'success': True,
            'progress': progress_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to track action progress", action_id=action_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to track action progress: {str(e)}")

@router.post("/actions/analyze-dependencies")
async def analyze_action_dependencies(
    action_ids: List[str],
    current_user: Dict = Depends(get_current_user),
    service: DartIntegrationService = Depends(get_dart_service)
):
    """Analyze dependencies between actions"""
    try:
        # Get actions from cache
        actions = []
        for action_id in action_ids:
            if action_id in service.action_cache:
                actions.append(service.action_cache[action_id])
        
        if not actions:
            raise HTTPException(status_code=400, detail="No valid actions found")
        
        # Analyze dependencies
        dependencies = await service.analyze_action_dependencies(actions)
        
        # Convert to response format
        dependency_responses = []
        for dep in dependencies:
            dependency_responses.append({
                'source_action_id': dep.source_action_id,
                'target_action_id': dep.target_action_id,
                'dependency_type': dep.dependency_type.value,
                'description': dep.description,
                'created_at': dep.created_at.isoformat()
            })
        
        logger.info("Analyzed action dependencies",
                   action_count=len(actions),
                   dependencies_found=len(dependencies),
                   user_id=current_user.get('id'))
        
        return {
            'success': True,
            'dependencies': dependency_responses,
            'count': len(dependencies),
            'analyzed_actions': len(actions)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to analyze action dependencies", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to analyze dependencies: {str(e)}")

@router.get("/resource-allocation/recommendations")
async def get_resource_allocation_recommendations(
    current_user: Dict = Depends(get_current_user),
    service: DartIntegrationService = Depends(get_dart_service)
):
    """Get resource allocation recommendations"""
    try:
        # Get all active actions
        active_actions = [
            action for action in service.action_cache.values()
            if action.status not in [ActionStatus.COMPLETED, ActionStatus.CANCELLED]
        ]
        
        recommendations = await service.generate_resource_allocation_recommendations(active_actions)
        
        if 'error' in recommendations:
            raise HTTPException(status_code=500, detail=recommendations['error'])
        
        return {
            'success': True,
            'recommendations': recommendations,
            'analyzed_actions': len(active_actions)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get resource allocation recommendations", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")

@router.post("/sync/to-dart")
async def sync_actions_to_dart_endpoint(
    action_ids: Optional[List[str]] = None,
    current_user: Dict = Depends(get_current_user),
    service: DartIntegrationService = Depends(get_dart_service)
):
    """Manually sync actions to Dart system"""
    try:
        if action_ids:
            # Sync specific actions
            actions_to_sync = [
                service.action_cache[action_id] 
                for action_id in action_ids 
                if action_id in service.action_cache
            ]
        else:
            # Sync all pending actions
            actions_to_sync = [
                service.action_cache[action_id] 
                for action_id in service.pending_sync 
                if action_id in service.action_cache
            ]
        
        sync_results = []
        for action in actions_to_sync:
            success = await service.sync_action_to_dart(action)
            sync_results.append({
                'action_id': action.id,
                'title': action.title,
                'success': success,
                'dart_id': action.dart_id
            })
            
            if success:
                service.pending_sync.discard(action.id)
        
        successful_syncs = sum(1 for result in sync_results if result['success'])
        
        logger.info("Manual sync to Dart completed",
                   total_actions=len(sync_results),
                   successful_syncs=successful_syncs,
                   user_id=current_user.get('id'))
        
        return {
            'success': True,
            'sync_results': sync_results,
            'total_actions': len(sync_results),
            'successful_syncs': successful_syncs,
            'failed_syncs': len(sync_results) - successful_syncs
        }
        
    except Exception as e:
        logger.error("Failed to sync actions to Dart", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to sync actions: {str(e)}")

@router.post("/sync/from-dart")
async def sync_actions_from_dart_endpoint(
    current_user: Dict = Depends(get_current_user),
    service: DartIntegrationService = Depends(get_dart_service)
):
    """Manually sync actions from Dart system"""
    try:
        updated_actions = await service.sync_actions_from_dart()
        
        logger.info("Manual sync from Dart completed",
                   updated_actions=len(updated_actions),
                   user_id=current_user.get('id'))
        
        return {
            'success': True,
            'updated_actions': len(updated_actions),
            'message': f'Successfully synced {len(updated_actions)} actions from Dart'
        }
        
    except Exception as e:
        logger.error("Failed to sync actions from Dart", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to sync from Dart: {str(e)}")

@router.get("/status/report")
async def get_action_status_report(
    current_user: Dict = Depends(get_current_user),
    service: DartIntegrationService = Depends(get_dart_service)
):
    """Get comprehensive action status report"""
    try:
        report = await service.get_action_status_report()
        
        if 'error' in report:
            raise HTTPException(status_code=500, detail=report['error'])
        
        return {
            'success': True,
            'report': report
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get action status report", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get status report: {str(e)}")

# Background task functions
async def sync_actions_to_dart(action_ids: List[str]):
    """Background task to sync actions to Dart"""
    try:
        service = get_dart_service()
        for action_id in action_ids:
            if action_id in service.action_cache:
                await service.sync_action_to_dart(service.action_cache[action_id])
                service.pending_sync.discard(action_id)
    except Exception as e:
        logger.error("Background sync to Dart failed", action_ids=action_ids, error=str(e))