"""
Git Integration API Routes
Handles version control, collaboration, and change tracking endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, UploadFile, File
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import structlog

from ..services.git_integration_service import (
    GitIntegrationService,
    GitChange,
    ChangeType,
    ConflictResolutionStrategy,
    BranchType,
    MergeConflict
)
from ..security.auth import get_current_user
from ..security.validation import validate_request_data

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/git", tags=["git-integration"])

# Global service instance (in production, this would be dependency injected)
git_service: Optional[GitIntegrationService] = None

def get_git_service() -> GitIntegrationService:
    """Get Git integration service instance"""
    global git_service
    if git_service is None:
        # In production, these would come from environment variables
        repo_path = "/app/data/repository"
        remote_url = None  # Optional remote repository URL
        git_service = GitIntegrationService(repo_path, remote_url)
    return git_service

@router.post("/commit")
async def commit_generated_output(
    commit_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user),
    service: GitIntegrationService = Depends(get_git_service)
):
    """Commit a generated output file to the repository"""
    try:
        # Validate input data
        validate_request_data(commit_data, {
            'file_path': str,
            'content': str,
            'commit_message': str
        })
        
        file_path = commit_data['file_path']
        content = commit_data['content']
        commit_message = commit_data['commit_message']
        author = current_user.get('email', current_user.get('username', 'unknown'))
        metadata = commit_data.get('metadata', {})
        
        # Add user info to metadata
        metadata.update({
            'user_id': current_user.get('id'),
            'user_email': current_user.get('email'),
            'commit_source': 'api'
        })
        
        # Commit the file
        change = await service.commit_generated_output(
            file_path=file_path,
            content=content,
            author=author,
            commit_message=commit_message,
            metadata=metadata
        )
        
        logger.info("Committed file via API",
                   file_path=file_path,
                   change_id=change.id,
                   user_id=current_user.get('id'))
        
        return {
            'success': True,
            'change_id': change.id,
            'commit_hash': change.commit_hash,
            'file_path': file_path,
            'change_type': change.change_type.value,
            'timestamp': change.timestamp.isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to commit file", 
                    file_path=commit_data.get('file_path'),
                    error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to commit file: {str(e)}")

@router.post("/branches/meeting")
async def create_meeting_branch(
    branch_data: Dict[str, Any],
    current_user: Dict = Depends(get_current_user),
    service: GitIntegrationService = Depends(get_git_service)
):
    """Create a new branch for a meeting"""
    try:
        # Validate input data
        validate_request_data(branch_data, {
            'meeting_id': str,
            'meeting_title': str
        })
        
        meeting_id = branch_data['meeting_id']
        meeting_title = branch_data['meeting_title']
        author = current_user.get('email', current_user.get('username', 'unknown'))
        
        # Create meeting branch
        branch_name = await service.create_meeting_branch(
            meeting_id=meeting_id,
            meeting_title=meeting_title,
            author=author
        )
        
        logger.info("Created meeting branch via API",
                   branch_name=branch_name,
                   meeting_id=meeting_id,
                   user_id=current_user.get('id'))
        
        return {
            'success': True,
            'branch_name': branch_name,
            'meeting_id': meeting_id,
            'created_by': author
        }
        
    except Exception as e:
        logger.error("Failed to create meeting branch", 
                    meeting_id=branch_data.get('meeting_id'),
                    error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to create meeting branch: {str(e)}")

@router.post("/branches/analysis")
async def create_analysis_branch(
    branch_data: Dict[str, Any],
    current_user: Dict = Depends(get_current_user),
    service: GitIntegrationService = Depends(get_git_service)
):
    """Create a new branch for analysis work"""
    try:
        # Validate input data
        validate_request_data(branch_data, {
            'analysis_id': str,
            'analysis_type': str
        })
        
        analysis_id = branch_data['analysis_id']
        analysis_type = branch_data['analysis_type']
        base_branch = branch_data.get('base_branch', 'main')
        author = current_user.get('email', current_user.get('username', 'unknown'))
        
        # Create analysis branch
        branch_name = await service.create_analysis_branch(
            analysis_id=analysis_id,
            analysis_type=analysis_type,
            base_branch=base_branch,
            author=author
        )
        
        logger.info("Created analysis branch via API",
                   branch_name=branch_name,
                   analysis_id=analysis_id,
                   user_id=current_user.get('id'))
        
        return {
            'success': True,
            'branch_name': branch_name,
            'analysis_id': analysis_id,
            'base_branch': base_branch,
            'created_by': author
        }
        
    except Exception as e:
        logger.error("Failed to create analysis branch", 
                    analysis_id=branch_data.get('analysis_id'),
                    error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to create analysis branch: {str(e)}")

@router.post("/branches/review")
async def create_review_branch(
    branch_data: Dict[str, Any],
    current_user: Dict = Depends(get_current_user),
    service: GitIntegrationService = Depends(get_git_service)
):
    """Create a review branch for collaborative editing"""
    try:
        # Validate input data
        validate_request_data(branch_data, {
            'source_branch': str,
            'review_purpose': str
        })
        
        source_branch = branch_data['source_branch']
        review_purpose = branch_data['review_purpose']
        reviewer = current_user.get('email', current_user.get('username', 'unknown'))
        
        # Create review branch
        branch_name = await service.create_review_branch(
            source_branch=source_branch,
            reviewer=reviewer,
            review_purpose=review_purpose
        )
        
        logger.info("Created review branch via API",
                   branch_name=branch_name,
                   source_branch=source_branch,
                   user_id=current_user.get('id'))
        
        return {
            'success': True,
            'branch_name': branch_name,
            'source_branch': source_branch,
            'review_purpose': review_purpose,
            'created_by': reviewer
        }
        
    except Exception as e:
        logger.error("Failed to create review branch", 
                    source_branch=branch_data.get('source_branch'),
                    error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to create review branch: {str(e)}")

@router.get("/branches")
async def get_branches(
    branch_type: Optional[str] = None,
    active_only: bool = True,
    current_user: Dict = Depends(get_current_user),
    service: GitIntegrationService = Depends(get_git_service)
):
    """Get list of branches with optional filtering"""
    try:
        branches = []
        
        for branch_name, branch_info in service.branches.items():
            # Apply filters
            if branch_type and branch_info.branch_type.value != branch_type:
                continue
            
            if active_only and not branch_info.is_active:
                continue
            
            branches.append({
                'name': branch_info.name,
                'type': branch_info.branch_type.value,
                'created_by': branch_info.created_by,
                'created_at': branch_info.created_at.isoformat(),
                'base_branch': branch_info.base_branch,
                'description': branch_info.description,
                'meeting_id': branch_info.meeting_id,
                'analysis_id': branch_info.analysis_id,
                'is_active': branch_info.is_active,
                'last_commit': branch_info.last_commit
            })
        
        # Sort by creation date (newest first)
        branches.sort(key=lambda x: x['created_at'], reverse=True)
        
        return {
            'success': True,
            'branches': branches,
            'total_count': len(branches)
        }
        
    except Exception as e:
        logger.error("Failed to get branches", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get branches: {str(e)}")

@router.post("/merge")
async def merge_branches(
    merge_data: Dict[str, Any],
    current_user: Dict = Depends(get_current_user),
    service: GitIntegrationService = Depends(get_git_service)
):
    """Merge branches with conflict detection"""
    try:
        # Validate input data
        validate_request_data(merge_data, {
            'source_branch': str,
            'target_branch': str
        })
        
        source_branch = merge_data['source_branch']
        target_branch = merge_data['target_branch']
        merge_message = merge_data.get('merge_message')
        author = current_user.get('email', current_user.get('username', 'unknown'))
        
        # Attempt merge
        success, conflicts = await service.merge_branch(
            source_branch=source_branch,
            target_branch=target_branch,
            author=author,
            merge_message=merge_message
        )
        
        if success:
            logger.info("Successfully merged branches via API",
                       source_branch=source_branch,
                       target_branch=target_branch,
                       user_id=current_user.get('id'))
            
            return {
                'success': True,
                'message': f'Successfully merged {source_branch} into {target_branch}',
                'conflicts': []
            }
        else:
            logger.warning("Merge failed with conflicts",
                          source_branch=source_branch,
                          target_branch=target_branch,
                          conflict_count=len(conflicts))
            
            # Convert conflicts to response format
            conflict_data = []
            for conflict in conflicts:
                conflict_data.append({
                    'file_path': conflict.file_path,
                    'conflict_markers': conflict.conflict_markers,
                    'our_content_preview': conflict.our_content[:500] + '...' if len(conflict.our_content) > 500 else conflict.our_content,
                    'their_content_preview': conflict.their_content[:500] + '...' if len(conflict.their_content) > 500 else conflict.their_content
                })
            
            return {
                'success': False,
                'message': f'Merge conflicts detected between {source_branch} and {target_branch}',
                'conflicts': conflict_data,
                'conflict_count': len(conflicts)
            }
        
    except Exception as e:
        logger.error("Failed to merge branches", 
                    source_branch=merge_data.get('source_branch'),
                    target_branch=merge_data.get('target_branch'),
                    error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to merge branches: {str(e)}")

@router.post("/conflicts/resolve")
async def resolve_merge_conflict(
    resolution_data: Dict[str, Any],
    current_user: Dict = Depends(get_current_user),
    service: GitIntegrationService = Depends(get_git_service)
):
    """Resolve a merge conflict"""
    try:
        # Validate input data
        validate_request_data(resolution_data, {
            'file_path': str,
            'resolution_strategy': str
        })
        
        file_path = resolution_data['file_path']
        strategy_str = resolution_data['resolution_strategy']
        resolved_content = resolution_data.get('resolved_content')
        resolver = current_user.get('email', current_user.get('username', 'unknown'))
        
        # Convert strategy string to enum
        try:
            strategy = ConflictResolutionStrategy(strategy_str.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid resolution strategy: {strategy_str}")
        
        # Resolve conflict
        success = await service.resolve_merge_conflict(
            file_path=file_path,
            resolution_strategy=strategy,
            resolved_content=resolved_content,
            resolver=resolver
        )
        
        if success:
            logger.info("Resolved merge conflict via API",
                       file_path=file_path,
                       strategy=strategy_str,
                       user_id=current_user.get('id'))
            
            return {
                'success': True,
                'message': f'Successfully resolved conflict in {file_path}',
                'file_path': file_path,
                'resolution_strategy': strategy_str,
                'resolved_by': resolver
            }
        else:
            raise HTTPException(status_code=400, detail=f"Failed to resolve conflict in {file_path}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to resolve merge conflict", 
                    file_path=resolution_data.get('file_path'),
                    error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to resolve conflict: {str(e)}")

@router.get("/conflicts")
async def get_merge_conflicts(
    current_user: Dict = Depends(get_current_user),
    service: GitIntegrationService = Depends(get_git_service)
):
    """Get current merge conflicts"""
    try:
        conflicts = []
        
        for file_path, conflict in service.merge_conflicts.items():
            conflicts.append({
                'file_path': conflict.file_path,
                'conflict_markers': conflict.conflict_markers,
                'our_content_preview': conflict.our_content[:500] + '...' if len(conflict.our_content) > 500 else conflict.our_content,
                'their_content_preview': conflict.their_content[:500] + '...' if len(conflict.their_content) > 500 else conflict.their_content,
                'resolution_strategy': conflict.resolution_strategy.value if conflict.resolution_strategy else None,
                'resolved_by': conflict.resolved_by,
                'resolved_at': conflict.resolved_at.isoformat() if conflict.resolved_at else None
            })
        
        return {
            'success': True,
            'conflicts': conflicts,
            'total_count': len(conflicts)
        }
        
    except Exception as e:
        logger.error("Failed to get merge conflicts", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get conflicts: {str(e)}")

@router.get("/history")
async def get_change_history(
    file_path: Optional[str] = None,
    author: Optional[str] = None,
    since_days: Optional[int] = None,
    limit: int = 100,
    current_user: Dict = Depends(get_current_user),
    service: GitIntegrationService = Depends(get_git_service)
):
    """Get change history with optional filtering"""
    try:
        since = None
        if since_days:
            since = datetime.utcnow() - timedelta(days=since_days)
        
        changes = await service.get_change_history(
            file_path=file_path,
            author=author,
            since=since,
            limit=limit
        )
        
        # Convert to response format
        change_data = []
        for change in changes:
            change_data.append({
                'id': change.id,
                'file_path': change.file_path,
                'change_type': change.change_type.value,
                'author': change.author,
                'timestamp': change.timestamp.isoformat(),
                'commit_hash': change.commit_hash,
                'branch': change.branch,
                'message': change.message,
                'metadata': change.metadata
            })
        
        return {
            'success': True,
            'changes': change_data,
            'total_count': len(change_data),
            'filters': {
                'file_path': file_path,
                'author': author,
                'since_days': since_days,
                'limit': limit
            }
        }
        
    except Exception as e:
        logger.error("Failed to get change history", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get change history: {str(e)}")

@router.get("/diff/{commit1}/{commit2}")
async def get_file_diff(
    commit1: str,
    commit2: str,
    file_path: str,
    current_user: Dict = Depends(get_current_user),
    service: GitIntegrationService = Depends(get_git_service)
):
    """Get diff between two commits for a specific file"""
    try:
        diff_data = await service.get_file_diff(file_path, commit1, commit2)
        
        if 'error' in diff_data:
            raise HTTPException(status_code=400, detail=diff_data['error'])
        
        return {
            'success': True,
            'diff_data': diff_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get file diff", 
                    file_path=file_path,
                    commit1=commit1,
                    commit2=commit2,
                    error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get file diff: {str(e)}")

@router.post("/backup")
async def create_backup(
    backup_data: Optional[Dict[str, Any]] = None,
    current_user: Dict = Depends(get_current_user),
    service: GitIntegrationService = Depends(get_git_service)
):
    """Create a backup of the repository"""
    try:
        backup_name = None
        if backup_data:
            backup_name = backup_data.get('backup_name')
        
        backup_file = await service.create_backup(backup_name)
        
        logger.info("Created repository backup via API",
                   backup_file=backup_file,
                   user_id=current_user.get('id'))
        
        return {
            'success': True,
            'backup_file': backup_file,
            'message': 'Repository backup created successfully'
        }
        
    except Exception as e:
        logger.error("Failed to create backup", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to create backup: {str(e)}")

@router.get("/status")
async def get_repository_status(
    current_user: Dict = Depends(get_current_user),
    service: GitIntegrationService = Depends(get_git_service)
):
    """Get comprehensive repository status"""
    try:
        status = await service.get_repository_status()
        
        if 'error' in status:
            raise HTTPException(status_code=500, detail=status['error'])
        
        return {
            'success': True,
            'status': status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get repository status", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get repository status: {str(e)}")

@router.get("/files/{file_path:path}")
async def get_file_content(
    file_path: str,
    commit: Optional[str] = None,
    current_user: Dict = Depends(get_current_user),
    service: GitIntegrationService = Depends(get_git_service)
):
    """Get content of a file at a specific commit"""
    try:
        if commit:
            # Get file content at specific commit
            commit_obj = service.repo.commit(commit)
            try:
                content = commit_obj.tree[file_path].data_stream.read().decode('utf-8')
            except KeyError:
                raise HTTPException(status_code=404, detail=f"File not found at commit {commit}")
        else:
            # Get current file content
            full_path = service.repo_path / file_path
            if not full_path.exists():
                raise HTTPException(status_code=404, detail="File not found")
            content = full_path.read_text()
        
        return {
            'success': True,
            'file_path': file_path,
            'commit': commit,
            'content': content,
            'size_bytes': len(content.encode('utf-8'))
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get file content", 
                    file_path=file_path,
                    commit=commit,
                    error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get file content: {str(e)}")

@router.post("/files/{file_path:path}")
async def update_file_content(
    file_path: str,
    file_data: Dict[str, Any],
    current_user: Dict = Depends(get_current_user),
    service: GitIntegrationService = Depends(get_git_service)
):
    """Update file content and commit changes"""
    try:
        # Validate input data
        validate_request_data(file_data, {
            'content': str,
            'commit_message': str
        })
        
        content = file_data['content']
        commit_message = file_data['commit_message']
        author = current_user.get('email', current_user.get('username', 'unknown'))
        metadata = file_data.get('metadata', {})
        
        # Add user info to metadata
        metadata.update({
            'user_id': current_user.get('id'),
            'user_email': current_user.get('email'),
            'update_source': 'api_file_update'
        })
        
        # Commit the updated file
        change = await service.commit_generated_output(
            file_path=file_path,
            content=content,
            author=author,
            commit_message=commit_message,
            metadata=metadata
        )
        
        logger.info("Updated file via API",
                   file_path=file_path,
                   change_id=change.id,
                   user_id=current_user.get('id'))
        
        return {
            'success': True,
            'change_id': change.id,
            'commit_hash': change.commit_hash,
            'file_path': file_path,
            'change_type': change.change_type.value,
            'timestamp': change.timestamp.isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to update file", 
                    file_path=file_path,
                    error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to update file: {str(e)}")