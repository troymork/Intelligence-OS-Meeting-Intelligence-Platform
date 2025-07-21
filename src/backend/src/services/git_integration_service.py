"""
Git Repository Integration Service
Handles version control, collaboration, and change tracking for all generated outputs
"""

import asyncio
import logging
import os
import shutil
import tempfile
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import structlog
import git
from git import Repo, GitCommandError
import json
import hashlib
from pathlib import Path
import difflib
import re

logger = structlog.get_logger(__name__)

class ChangeType(Enum):
    """Types of changes that can be tracked"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    MOVE = "move"
    MERGE = "merge"

class ConflictResolutionStrategy(Enum):
    """Strategies for resolving merge conflicts"""
    MANUAL = "manual"
    OURS = "ours"
    THEIRS = "theirs"
    MERGE_TOOL = "merge_tool"
    INTELLIGENT = "intelligent"

class BranchType(Enum):
    """Types of branches in the collaboration workflow"""
    MAIN = "main"
    FEATURE = "feature"
    MEETING = "meeting"
    ANALYSIS = "analysis"
    REVIEW = "review"
    HOTFIX = "hotfix"

@dataclass
class GitChange:
    """Represents a change in the Git repository"""
    id: str
    file_path: str
    change_type: ChangeType
    content_before: Optional[str] = None
    content_after: Optional[str] = None
    author: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    commit_hash: Optional[str] = None
    branch: str = "main"
    message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MergeConflict:
    """Represents a merge conflict"""
    file_path: str
    conflict_markers: List[str]
    our_content: str
    their_content: str
    base_content: Optional[str] = None
    resolution_strategy: Optional[ConflictResolutionStrategy] = None
    resolved_content: Optional[str] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None

@dataclass
class BranchInfo:
    """Information about a Git branch"""
    name: str
    branch_type: BranchType
    created_by: str
    created_at: datetime
    base_branch: str = "main"
    description: str = ""
    meeting_id: Optional[str] = None
    analysis_id: Optional[str] = None
    is_active: bool = True
    last_commit: Optional[str] = None

class GitIntegrationService:
    """Service for Git repository integration and collaboration"""
    
    def __init__(self, repo_path: str, remote_url: Optional[str] = None):
        self.repo_path = Path(repo_path)
        self.remote_url = remote_url
        self.repo: Optional[Repo] = None
        
        # Configuration
        self.config = {
            'auto_commit_enabled': True,
            'auto_push_enabled': False,  # Disabled by default for safety
            'branch_cleanup_days': 30,
            'max_file_size_mb': 10,
            'excluded_patterns': ['.git', '__pycache__', '*.pyc', '.env', 'node_modules'],
            'commit_message_template': '[{type}] {summary}\n\n{details}',
            'merge_conflict_timeout_minutes': 30,
            'backup_retention_days': 90
        }
        
        # Change tracking
        self.changes_log = []  # List[GitChange]
        self.pending_changes = {}  # file_path -> GitChange
        self.merge_conflicts = {}  # file_path -> MergeConflict
        
        # Branch management
        self.branches = {}  # branch_name -> BranchInfo
        self.active_branches = set()
        
        # Initialize repository
        self._initialize_repository()
        
        # Start background processes
        self._start_background_processes()
    
    def _initialize_repository(self):
        """Initialize or connect to Git repository"""
        try:
            if self.repo_path.exists() and (self.repo_path / '.git').exists():
                # Connect to existing repository
                self.repo = Repo(str(self.repo_path))
                logger.info("Connected to existing Git repository", path=str(self.repo_path))
            else:
                # Create new repository
                self.repo_path.mkdir(parents=True, exist_ok=True)
                self.repo = Repo.init(str(self.repo_path))
                
                # Create initial commit
                self._create_initial_structure()
                
                # Add remote if provided
                if self.remote_url:
                    try:
                        self.repo.create_remote('origin', self.remote_url)
                    except Exception as e:
                        logger.warning("Failed to add remote", remote_url=self.remote_url, error=str(e))
                
                logger.info("Initialized new Git repository", path=str(self.repo_path))
            
            # Load existing branches
            self._load_existing_branches()
            
        except Exception as e:
            logger.error("Failed to initialize Git repository", path=str(self.repo_path), error=str(e))
            raise
    
    def _create_initial_structure(self):
        """Create initial repository structure"""
        try:
            # Create directory structure
            directories = [
                'meetings',
                'analyses',
                'outputs',
                'templates',
                'docs',
                'backups'
            ]
            
            for directory in directories:
                (self.repo_path / directory).mkdir(exist_ok=True)
                # Create .gitkeep file to ensure directory is tracked
                (self.repo_path / directory / '.gitkeep').touch()
            
            # Create README
            readme_content = """# Intelligence OS Platform Repository

This repository contains all generated outputs, analyses, and meeting data from the Intelligence OS Platform.

## Structure

- `meetings/` - Meeting transcripts and metadata
- `analyses/` - Oracle 9.1 Protocol analyses
- `outputs/` - Generated reports and summaries
- `templates/` - Document templates
- `docs/` - Documentation and guides
- `backups/` - Automated backups

## Collaboration Workflow

1. Each meeting creates a new feature branch
2. Analysis outputs are committed automatically
3. Review branches are created for collaborative editing
4. Changes are merged back to main after review

## Version Control

All changes are automatically tracked with detailed metadata including:
- Author information
- Timestamp
- Change type and description
- Associated meeting or analysis ID
"""
            
            (self.repo_path / 'README.md').write_text(readme_content)
            
            # Create .gitignore
            gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
.env

# Node.js
node_modules/
npm-debug.log*

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Temporary files
*.tmp
*.temp
*.log

# Large files
*.zip
*.tar.gz
*.rar
"""
            
            (self.repo_path / '.gitignore').write_text(gitignore_content)
            
            # Initial commit
            self.repo.index.add(['.'])
            self.repo.index.commit("Initial repository setup")
            
        except Exception as e:
            logger.error("Failed to create initial repository structure", error=str(e))
            raise
    
    def _load_existing_branches(self):
        """Load information about existing branches"""
        try:
            for branch in self.repo.branches:
                branch_info = self._analyze_branch(branch.name)
                self.branches[branch.name] = branch_info
                if branch_info.is_active:
                    self.active_branches.add(branch.name)
            
            logger.info("Loaded existing branches", count=len(self.branches))
            
        except Exception as e:
            logger.error("Failed to load existing branches", error=str(e))
    
    def _analyze_branch(self, branch_name: str) -> BranchInfo:
        """Analyze a branch to determine its type and metadata"""
        try:
            branch = self.repo.branches[branch_name]
            
            # Determine branch type from name
            if branch_name == 'main' or branch_name == 'master':
                branch_type = BranchType.MAIN
            elif branch_name.startswith('feature/'):
                branch_type = BranchType.FEATURE
            elif branch_name.startswith('meeting/'):
                branch_type = BranchType.MEETING
            elif branch_name.startswith('analysis/'):
                branch_type = BranchType.ANALYSIS
            elif branch_name.startswith('review/'):
                branch_type = BranchType.REVIEW
            elif branch_name.startswith('hotfix/'):
                branch_type = BranchType.HOTFIX
            else:
                branch_type = BranchType.FEATURE
            
            # Get branch metadata from commit messages or branch description
            last_commit = branch.commit
            created_at = datetime.fromtimestamp(last_commit.committed_date)
            created_by = last_commit.author.email
            
            # Extract meeting/analysis ID from branch name
            meeting_id = None
            analysis_id = None
            if '/' in branch_name:
                parts = branch_name.split('/')
                if len(parts) >= 2:
                    if branch_type == BranchType.MEETING:
                        meeting_id = parts[1]
                    elif branch_type == BranchType.ANALYSIS:
                        analysis_id = parts[1]
            
            return BranchInfo(
                name=branch_name,
                branch_type=branch_type,
                created_by=created_by,
                created_at=created_at,
                meeting_id=meeting_id,
                analysis_id=analysis_id,
                last_commit=last_commit.hexsha,
                is_active=True
            )
            
        except Exception as e:
            logger.error("Failed to analyze branch", branch_name=branch_name, error=str(e))
            return BranchInfo(
                name=branch_name,
                branch_type=BranchType.FEATURE,
                created_by="unknown",
                created_at=datetime.utcnow()
            )
    
    async def commit_generated_output(self, 
                                    file_path: str, 
                                    content: str, 
                                    author: str,
                                    commit_message: str,
                                    metadata: Optional[Dict[str, Any]] = None) -> GitChange:
        """Commit a generated output file to the repository"""
        try:
            full_path = self.repo_path / file_path
            
            # Ensure directory exists
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Check if file exists to determine change type
            change_type = ChangeType.UPDATE if full_path.exists() else ChangeType.CREATE
            content_before = full_path.read_text() if full_path.exists() else None
            
            # Write content to file
            full_path.write_text(content)
            
            # Create change record
            change = GitChange(
                id=self._generate_change_id(),
                file_path=file_path,
                change_type=change_type,
                content_before=content_before,
                content_after=content,
                author=author,
                message=commit_message,
                metadata=metadata or {}
            )
            
            if self.config['auto_commit_enabled']:
                # Stage and commit the file
                self.repo.index.add([str(full_path)])
                
                # Create detailed commit message
                detailed_message = self._create_commit_message(change)
                
                commit = self.repo.index.commit(detailed_message, author=git.Actor(author, author))
                change.commit_hash = commit.hexsha
                change.branch = self.repo.active_branch.name
                
                logger.info("Committed generated output",
                           file_path=file_path,
                           commit_hash=commit.hexsha,
                           author=author)
            else:
                # Add to pending changes
                self.pending_changes[file_path] = change
                
                logger.info("Added to pending changes",
                           file_path=file_path,
                           author=author)
            
            # Add to changes log
            self.changes_log.append(change)
            
            return change
            
        except Exception as e:
            logger.error("Failed to commit generated output", 
                        file_path=file_path, 
                        author=author, 
                        error=str(e))
            raise
    
    async def create_meeting_branch(self, 
                                  meeting_id: str, 
                                  meeting_title: str,
                                  author: str) -> str:
        """Create a new branch for a meeting"""
        try:
            # Generate branch name
            safe_title = re.sub(r'[^a-zA-Z0-9\-_]', '-', meeting_title.lower())[:50]
            branch_name = f"meeting/{meeting_id}-{safe_title}"
            
            # Ensure we're on main branch
            self.repo.heads.main.checkout()
            
            # Create new branch
            new_branch = self.repo.create_head(branch_name)
            new_branch.checkout()
            
            # Create branch info
            branch_info = BranchInfo(
                name=branch_name,
                branch_type=BranchType.MEETING,
                created_by=author,
                created_at=datetime.utcnow(),
                meeting_id=meeting_id,
                description=f"Meeting branch for: {meeting_title}"
            )
            
            self.branches[branch_name] = branch_info
            self.active_branches.add(branch_name)
            
            # Create initial meeting directory structure
            meeting_dir = self.repo_path / 'meetings' / meeting_id
            meeting_dir.mkdir(parents=True, exist_ok=True)
            
            # Create meeting metadata file
            metadata = {
                'meeting_id': meeting_id,
                'title': meeting_title,
                'branch': branch_name,
                'created_by': author,
                'created_at': datetime.utcnow().isoformat(),
                'status': 'active'
            }
            
            metadata_file = meeting_dir / 'metadata.json'
            metadata_file.write_text(json.dumps(metadata, indent=2))
            
            # Commit initial structure
            self.repo.index.add([str(metadata_file)])
            commit_message = f"Create meeting branch for: {meeting_title}"
            self.repo.index.commit(commit_message, author=git.Actor(author, author))
            
            logger.info("Created meeting branch",
                       branch_name=branch_name,
                       meeting_id=meeting_id,
                       author=author)
            
            return branch_name
            
        except Exception as e:
            logger.error("Failed to create meeting branch", 
                        meeting_id=meeting_id, 
                        error=str(e))
            raise
    
    async def create_analysis_branch(self, 
                                   analysis_id: str, 
                                   analysis_type: str,
                                   base_branch: str,
                                   author: str) -> str:
        """Create a new branch for analysis work"""
        try:
            # Generate branch name
            branch_name = f"analysis/{analysis_id}-{analysis_type}"
            
            # Checkout base branch
            self.repo.heads[base_branch].checkout()
            
            # Create new branch
            new_branch = self.repo.create_head(branch_name)
            new_branch.checkout()
            
            # Create branch info
            branch_info = BranchInfo(
                name=branch_name,
                branch_type=BranchType.ANALYSIS,
                created_by=author,
                created_at=datetime.utcnow(),
                base_branch=base_branch,
                analysis_id=analysis_id,
                description=f"Analysis branch for: {analysis_type}"
            )
            
            self.branches[branch_name] = branch_info
            self.active_branches.add(branch_name)
            
            logger.info("Created analysis branch",
                       branch_name=branch_name,
                       analysis_id=analysis_id,
                       base_branch=base_branch,
                       author=author)
            
            return branch_name
            
        except Exception as e:
            logger.error("Failed to create analysis branch", 
                        analysis_id=analysis_id, 
                        error=str(e))
            raise
    
    async def create_review_branch(self, 
                                 source_branch: str, 
                                 reviewer: str,
                                 review_purpose: str) -> str:
        """Create a review branch for collaborative editing"""
        try:
            # Generate branch name
            timestamp = datetime.utcnow().strftime('%Y%m%d-%H%M%S')
            branch_name = f"review/{source_branch.replace('/', '-')}-{timestamp}"
            
            # Checkout source branch
            self.repo.heads[source_branch].checkout()
            
            # Create new branch
            new_branch = self.repo.create_head(branch_name)
            new_branch.checkout()
            
            # Create branch info
            branch_info = BranchInfo(
                name=branch_name,
                branch_type=BranchType.REVIEW,
                created_by=reviewer,
                created_at=datetime.utcnow(),
                base_branch=source_branch,
                description=f"Review branch: {review_purpose}"
            )
            
            self.branches[branch_name] = branch_info
            self.active_branches.add(branch_name)
            
            logger.info("Created review branch",
                       branch_name=branch_name,
                       source_branch=source_branch,
                       reviewer=reviewer)
            
            return branch_name
            
        except Exception as e:
            logger.error("Failed to create review branch", 
                        source_branch=source_branch, 
                        error=str(e))
            raise    
  
  async def merge_branch(self, 
                         source_branch: str, 
                         target_branch: str,
                         author: str,
                         merge_message: Optional[str] = None) -> Tuple[bool, List[MergeConflict]]:
        """Merge a branch with conflict detection and resolution"""
        try:
            # Checkout target branch
            self.repo.heads[target_branch].checkout()
            
            # Get the source branch
            source = self.repo.heads[source_branch]
            
            # Attempt merge
            try:
                merge_base = self.repo.merge_base(self.repo.head.commit, source.commit)[0]
                self.repo.index.merge_tree(source.commit, base=merge_base)
                
                # Check for conflicts
                conflicts = self._detect_merge_conflicts()
                
                if conflicts:
                    logger.warning("Merge conflicts detected",
                                 source_branch=source_branch,
                                 target_branch=target_branch,
                                 conflict_count=len(conflicts))
                    return False, conflicts
                
                # Complete merge if no conflicts
                commit_message = merge_message or f"Merge {source_branch} into {target_branch}"
                merge_commit = self.repo.index.commit(
                    commit_message,
                    parent_commits=(self.repo.head.commit, source.commit),
                    author=git.Actor(author, author)
                )
                
                # Record merge change
                merge_change = GitChange(
                    id=self._generate_change_id(),
                    file_path="<merge>",
                    change_type=ChangeType.MERGE,
                    author=author,
                    commit_hash=merge_commit.hexsha,
                    branch=target_branch,
                    message=commit_message,
                    metadata={
                        'source_branch': source_branch,
                        'target_branch': target_branch,
                        'merge_base': merge_base.hexsha
                    }
                )
                
                self.changes_log.append(merge_change)
                
                logger.info("Successfully merged branches",
                           source_branch=source_branch,
                           target_branch=target_branch,
                           commit_hash=merge_commit.hexsha)
                
                return True, []
                
            except GitCommandError as e:
                # Handle merge conflicts
                conflicts = self._detect_merge_conflicts()
                logger.warning("Merge failed with conflicts",
                             source_branch=source_branch,
                             target_branch=target_branch,
                             error=str(e))
                return False, conflicts
                
        except Exception as e:
            logger.error("Failed to merge branches", 
                        source_branch=source_branch,
                        target_branch=target_branch,
                        error=str(e))
            raise
    
    def _detect_merge_conflicts(self) -> List[MergeConflict]:
        """Detect and analyze merge conflicts"""
        conflicts = []
        
        try:
            # Get unmerged paths
            unmerged = self.repo.index.unmerged_blobs()
            
            for file_path, stages in unmerged.items():
                # Extract content from different stages
                base_content = None
                our_content = None
                their_content = None
                
                for stage, blob in stages.items():
                    content = blob.data_stream.read().decode('utf-8')
                    if stage == 1:  # Base (common ancestor)
                        base_content = content
                    elif stage == 2:  # Ours (current branch)
                        our_content = content
                    elif stage == 3:  # Theirs (merging branch)
                        their_content = content
                
                # Find conflict markers in the working tree
                try:
                    working_content = (self.repo_path / file_path).read_text()
                    conflict_markers = self._extract_conflict_markers(working_content)
                except Exception:
                    conflict_markers = []
                
                conflict = MergeConflict(
                    file_path=file_path,
                    conflict_markers=conflict_markers,
                    our_content=our_content or "",
                    their_content=their_content or "",
                    base_content=base_content
                )
                
                conflicts.append(conflict)
                self.merge_conflicts[file_path] = conflict
            
            return conflicts
            
        except Exception as e:
            logger.error("Failed to detect merge conflicts", error=str(e))
            return []
    
    def _extract_conflict_markers(self, content: str) -> List[str]:
        """Extract conflict markers from file content"""
        markers = []
        lines = content.split('\n')
        
        in_conflict = False
        current_conflict = []
        
        for line in lines:
            if line.startswith('<<<<<<<'):
                in_conflict = True
                current_conflict = [line]
            elif line.startswith('=======') and in_conflict:
                current_conflict.append(line)
            elif line.startswith('>>>>>>>') and in_conflict:
                current_conflict.append(line)
                markers.append('\n'.join(current_conflict))
                current_conflict = []
                in_conflict = False
            elif in_conflict:
                current_conflict.append(line)
        
        return markers
    
    async def resolve_merge_conflict(self, 
                                   file_path: str, 
                                   resolution_strategy: ConflictResolutionStrategy,
                                   resolved_content: Optional[str] = None,
                                   resolver: str = "") -> bool:
        """Resolve a merge conflict using the specified strategy"""
        try:
            if file_path not in self.merge_conflicts:
                logger.error("No conflict found for file", file_path=file_path)
                return False
            
            conflict = self.merge_conflicts[file_path]
            
            if resolution_strategy == ConflictResolutionStrategy.OURS:
                final_content = conflict.our_content
            elif resolution_strategy == ConflictResolutionStrategy.THEIRS:
                final_content = conflict.their_content
            elif resolution_strategy == ConflictResolutionStrategy.INTELLIGENT:
                final_content = await self._intelligent_merge_resolution(conflict)
            elif resolution_strategy == ConflictResolutionStrategy.MANUAL:
                if not resolved_content:
                    logger.error("Manual resolution requires resolved_content")
                    return False
                final_content = resolved_content
            else:
                logger.error("Unsupported resolution strategy", strategy=resolution_strategy)
                return False
            
            # Write resolved content
            full_path = self.repo_path / file_path
            full_path.write_text(final_content)
            
            # Stage the resolved file
            self.repo.index.add([str(full_path)])
            
            # Update conflict record
            conflict.resolution_strategy = resolution_strategy
            conflict.resolved_content = final_content
            conflict.resolved_by = resolver
            conflict.resolved_at = datetime.utcnow()
            
            logger.info("Resolved merge conflict",
                       file_path=file_path,
                       strategy=resolution_strategy.value,
                       resolver=resolver)
            
            return True
            
        except Exception as e:
            logger.error("Failed to resolve merge conflict", 
                        file_path=file_path, 
                        error=str(e))
            return False
    
    async def _intelligent_merge_resolution(self, conflict: MergeConflict) -> str:
        """Attempt intelligent merge conflict resolution"""
        try:
            # For JSON files, try to merge objects intelligently
            if conflict.file_path.endswith('.json'):
                return await self._merge_json_content(conflict)
            
            # For Markdown files, try to merge sections
            elif conflict.file_path.endswith('.md'):
                return await self._merge_markdown_content(conflict)
            
            # For other files, use line-based merging
            else:
                return await self._merge_line_based(conflict)
                
        except Exception as e:
            logger.error("Intelligent merge resolution failed", 
                        file_path=conflict.file_path, 
                        error=str(e))
            # Fall back to "ours" strategy
            return conflict.our_content
    
    async def _merge_json_content(self, conflict: MergeConflict) -> str:
        """Merge JSON content intelligently"""
        try:
            our_data = json.loads(conflict.our_content)
            their_data = json.loads(conflict.their_content)
            
            # Merge dictionaries recursively
            merged_data = self._merge_dict_recursive(our_data, their_data)
            
            return json.dumps(merged_data, indent=2)
            
        except Exception as e:
            logger.error("Failed to merge JSON content", error=str(e))
            return conflict.our_content
    
    def _merge_dict_recursive(self, dict1: dict, dict2: dict) -> dict:
        """Recursively merge two dictionaries"""
        result = dict1.copy()
        
        for key, value in dict2.items():
            if key in result:
                if isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = self._merge_dict_recursive(result[key], value)
                elif isinstance(result[key], list) and isinstance(value, list):
                    # Merge lists by extending (could be made smarter)
                    result[key] = result[key] + [item for item in value if item not in result[key]]
                else:
                    # For conflicting values, prefer "theirs" (could be configurable)
                    result[key] = value
            else:
                result[key] = value
        
        return result
    
    async def _merge_markdown_content(self, conflict: MergeConflict) -> str:
        """Merge Markdown content by sections"""
        try:
            our_sections = self._parse_markdown_sections(conflict.our_content)
            their_sections = self._parse_markdown_sections(conflict.their_content)
            
            # Merge sections
            merged_sections = {}
            
            # Add all our sections
            for section, content in our_sections.items():
                merged_sections[section] = content
            
            # Add their sections, merging where possible
            for section, content in their_sections.items():
                if section in merged_sections:
                    # Try to merge section content
                    merged_sections[section] = self._merge_section_content(
                        merged_sections[section], content
                    )
                else:
                    merged_sections[section] = content
            
            # Reconstruct markdown
            return self._reconstruct_markdown(merged_sections)
            
        except Exception as e:
            logger.error("Failed to merge Markdown content", error=str(e))
            return conflict.our_content
    
    def _parse_markdown_sections(self, content: str) -> Dict[str, str]:
        """Parse Markdown content into sections"""
        sections = {}
        current_section = "header"
        current_content = []
        
        for line in content.split('\n'):
            if line.startswith('#'):
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content)
                
                # Start new section
                current_section = line.strip()
                current_content = [line]
            else:
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def _merge_section_content(self, content1: str, content2: str) -> str:
        """Merge content within a section"""
        # Simple approach: combine unique lines
        lines1 = set(content1.split('\n'))
        lines2 = set(content2.split('\n'))
        
        # Preserve order from content1, add unique lines from content2
        result_lines = content1.split('\n')
        for line in content2.split('\n'):
            if line not in lines1 and line.strip():
                result_lines.append(line)
        
        return '\n'.join(result_lines)
    
    def _reconstruct_markdown(self, sections: Dict[str, str]) -> str:
        """Reconstruct Markdown from sections"""
        # Sort sections by header level and name
        sorted_sections = sorted(sections.items(), key=lambda x: (
            len(x[0].split('#')) if x[0].startswith('#') else 0,
            x[0]
        ))
        
        return '\n\n'.join(content for _, content in sorted_sections)
    
    async def _merge_line_based(self, conflict: MergeConflict) -> str:
        """Merge content using line-based approach"""
        try:
            our_lines = conflict.our_content.split('\n')
            their_lines = conflict.their_content.split('\n')
            base_lines = conflict.base_content.split('\n') if conflict.base_content else []
            
            # Use difflib to create a unified diff
            differ = difflib.unified_diff(
                base_lines, our_lines, 
                fromfile='base', tofile='ours', 
                lineterm=''
            )
            
            # Apply changes intelligently
            merged_lines = []
            for line in difflib.unified_diff(our_lines, their_lines, lineterm=''):
                if not line.startswith('@@') and not line.startswith('---') and not line.startswith('+++'):
                    if line.startswith('+'):
                        merged_lines.append(line[1:])
                    elif not line.startswith('-'):
                        merged_lines.append(line)
            
            return '\n'.join(merged_lines)
            
        except Exception as e:
            logger.error("Line-based merge failed", error=str(e))
            return conflict.our_content
    
    async def get_change_history(self, 
                               file_path: Optional[str] = None,
                               author: Optional[str] = None,
                               since: Optional[datetime] = None,
                               limit: int = 100) -> List[GitChange]:
        """Get change history with optional filtering"""
        try:
            filtered_changes = self.changes_log
            
            # Apply filters
            if file_path:
                filtered_changes = [c for c in filtered_changes if c.file_path == file_path]
            
            if author:
                filtered_changes = [c for c in filtered_changes if c.author == author]
            
            if since:
                filtered_changes = [c for c in filtered_changes if c.timestamp >= since]
            
            # Sort by timestamp (newest first) and limit
            filtered_changes.sort(key=lambda x: x.timestamp, reverse=True)
            
            return filtered_changes[:limit]
            
        except Exception as e:
            logger.error("Failed to get change history", error=str(e))
            return []
    
    async def get_file_diff(self, 
                          file_path: str, 
                          commit1: str, 
                          commit2: str) -> Dict[str, Any]:
        """Get diff between two commits for a specific file"""
        try:
            commit1_obj = self.repo.commit(commit1)
            commit2_obj = self.repo.commit(commit2)
            
            # Get file content at each commit
            try:
                content1 = commit1_obj.tree[file_path].data_stream.read().decode('utf-8')
            except KeyError:
                content1 = ""
            
            try:
                content2 = commit2_obj.tree[file_path].data_stream.read().decode('utf-8')
            except KeyError:
                content2 = ""
            
            # Generate diff
            diff_lines = list(difflib.unified_diff(
                content1.splitlines(keepends=True),
                content2.splitlines(keepends=True),
                fromfile=f"{file_path}@{commit1[:8]}",
                tofile=f"{file_path}@{commit2[:8]}"
            ))
            
            # Calculate statistics
            additions = sum(1 for line in diff_lines if line.startswith('+') and not line.startswith('+++'))
            deletions = sum(1 for line in diff_lines if line.startswith('-') and not line.startswith('---'))
            
            return {
                'file_path': file_path,
                'commit1': commit1,
                'commit2': commit2,
                'diff': ''.join(diff_lines),
                'additions': additions,
                'deletions': deletions,
                'total_changes': additions + deletions
            }
            
        except Exception as e:
            logger.error("Failed to get file diff", 
                        file_path=file_path, 
                        commit1=commit1, 
                        commit2=commit2, 
                        error=str(e))
            return {'error': str(e)}
    
    async def create_backup(self, backup_name: Optional[str] = None) -> str:
        """Create a backup of the repository"""
        try:
            if not backup_name:
                backup_name = f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            backup_dir = self.repo_path / 'backups' / backup_name
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Create archive of repository (excluding .git for size)
            import tarfile
            
            backup_file = backup_dir / f"{backup_name}.tar.gz"
            
            with tarfile.open(backup_file, 'w:gz') as tar:
                for item in self.repo_path.iterdir():
                    if item.name != '.git' and item.name != 'backups':
                        tar.add(item, arcname=item.name)
            
            # Create backup metadata
            metadata = {
                'backup_name': backup_name,
                'created_at': datetime.utcnow().isoformat(),
                'repository_path': str(self.repo_path),
                'current_branch': self.repo.active_branch.name,
                'current_commit': self.repo.head.commit.hexsha,
                'file_count': len(list(self.repo_path.rglob('*'))),
                'backup_size_bytes': backup_file.stat().st_size
            }
            
            metadata_file = backup_dir / 'metadata.json'
            metadata_file.write_text(json.dumps(metadata, indent=2))
            
            logger.info("Created repository backup",
                       backup_name=backup_name,
                       backup_file=str(backup_file),
                       size_mb=round(metadata['backup_size_bytes'] / 1024 / 1024, 2))
            
            return str(backup_file)
            
        except Exception as e:
            logger.error("Failed to create backup", error=str(e))
            raise
    
    def _create_commit_message(self, change: GitChange) -> str:
        """Create a detailed commit message from a change"""
        template = self.config['commit_message_template']
        
        # Determine change type description
        type_descriptions = {
            ChangeType.CREATE: "CREATE",
            ChangeType.UPDATE: "UPDATE", 
            ChangeType.DELETE: "DELETE",
            ChangeType.MOVE: "MOVE",
            ChangeType.MERGE: "MERGE"
        }
        
        change_type = type_descriptions.get(change.change_type, "CHANGE")
        
        # Create summary
        summary = f"{change.file_path} - {change.message}" if change.message else change.file_path
        
        # Create details
        details_parts = []
        details_parts.append(f"Author: {change.author}")
        details_parts.append(f"Timestamp: {change.timestamp.isoformat()}")
        
        if change.metadata:
            for key, value in change.metadata.items():
                details_parts.append(f"{key}: {value}")
        
        details = '\n'.join(details_parts)
        
        return template.format(
            type=change_type,
            summary=summary,
            details=details
        )
    
    def _generate_change_id(self) -> str:
        """Generate a unique change ID"""
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')
        return f"change_{timestamp}"
    
    def _start_background_processes(self):
        """Start background processes for maintenance"""
        async def cleanup_worker():
            while True:
                try:
                    await self._cleanup_old_branches()
                    await self._cleanup_old_backups()
                    await asyncio.sleep(24 * 3600)  # Run daily
                except Exception as e:
                    logger.error("Background cleanup error", error=str(e))
                    await asyncio.sleep(3600)  # Wait 1 hour before retrying
        
        # Start the background task
        asyncio.create_task(cleanup_worker())
    
    async def _cleanup_old_branches(self):
        """Clean up old inactive branches"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.config['branch_cleanup_days'])
            
            branches_to_delete = []
            for branch_name, branch_info in self.branches.items():
                if (branch_info.branch_type != BranchType.MAIN and 
                    branch_info.created_at < cutoff_date and
                    not branch_info.is_active):
                    branches_to_delete.append(branch_name)
            
            for branch_name in branches_to_delete:
                try:
                    self.repo.delete_head(branch_name, force=True)
                    del self.branches[branch_name]
                    self.active_branches.discard(branch_name)
                    logger.info("Deleted old branch", branch_name=branch_name)
                except Exception as e:
                    logger.error("Failed to delete branch", branch_name=branch_name, error=str(e))
            
        except Exception as e:
            logger.error("Failed to cleanup old branches", error=str(e))
    
    async def _cleanup_old_backups(self):
        """Clean up old backup files"""
        try:
            backup_dir = self.repo_path / 'backups'
            if not backup_dir.exists():
                return
            
            cutoff_date = datetime.utcnow() - timedelta(days=self.config['backup_retention_days'])
            
            for backup_subdir in backup_dir.iterdir():
                if backup_subdir.is_dir():
                    metadata_file = backup_subdir / 'metadata.json'
                    if metadata_file.exists():
                        try:
                            metadata = json.loads(metadata_file.read_text())
                            created_at = datetime.fromisoformat(metadata['created_at'])
                            
                            if created_at < cutoff_date:
                                shutil.rmtree(backup_subdir)
                                logger.info("Deleted old backup", backup_name=backup_subdir.name)
                        except Exception as e:
                            logger.error("Failed to process backup metadata", 
                                       backup_dir=str(backup_subdir), 
                                       error=str(e))
            
        except Exception as e:
            logger.error("Failed to cleanup old backups", error=str(e))
    
    async def get_repository_status(self) -> Dict[str, Any]:
        """Get comprehensive repository status"""
        try:
            # Basic repository info
            status = {
                'repository_path': str(self.repo_path),
                'current_branch': self.repo.active_branch.name,
                'current_commit': self.repo.head.commit.hexsha,
                'total_commits': len(list(self.repo.iter_commits())),
                'total_branches': len(self.branches),
                'active_branches': len(self.active_branches),
                'pending_changes': len(self.pending_changes),
                'merge_conflicts': len(self.merge_conflicts),
                'changes_logged': len(self.changes_log)
            }
            
            # Branch breakdown
            branch_types = {}
            for branch_info in self.branches.values():
                branch_type = branch_info.branch_type.value
                branch_types[branch_type] = branch_types.get(branch_type, 0) + 1
            
            status['branch_types'] = branch_types
            
            # Recent activity
            recent_changes = await self.get_change_history(limit=10)
            status['recent_changes'] = [
                {
                    'id': change.id,
                    'file_path': change.file_path,
                    'change_type': change.change_type.value,
                    'author': change.author,
                    'timestamp': change.timestamp.isoformat(),
                    'message': change.message
                }
                for change in recent_changes
            ]
            
            # Repository size
            total_size = sum(f.stat().st_size for f in self.repo_path.rglob('*') if f.is_file())
            status['repository_size_mb'] = round(total_size / 1024 / 1024, 2)
            
            return status
            
        except Exception as e:
            logger.error("Failed to get repository status", error=str(e))
            return {'error': str(e)}
    
    async def close(self):
        """Close the Git integration service"""
        try:
            # Commit any pending changes
            if self.pending_changes and self.config['auto_commit_enabled']:
                for file_path, change in self.pending_changes.items():
                    await self.commit_generated_output(
                        change.file_path,
                        change.content_after,
                        change.author,
                        change.message,
                        change.metadata
                    )
            
            logger.info("Git integration service closed")
            
        except Exception as e:
            logger.error("Error closing Git integration service", error=str(e))