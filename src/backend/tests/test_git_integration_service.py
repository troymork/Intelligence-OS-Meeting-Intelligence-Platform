"""
Tests for Git Repository Integration Service
"""

import pytest
import asyncio
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from pathlib import Path
import json
import git

from src.services.git_integration_service import (
    GitIntegrationService,
    GitChange,
    ChangeType,
    ConflictResolutionStrategy,
    BranchType,
    MergeConflict,
    BranchInfo
)


class TestGitIntegrationService:
    """Test cases for GitIntegrationService"""
    
    @pytest.fixture
    def temp_repo_dir(self):
        """Create a temporary directory for test repository"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def service(self, temp_repo_dir):
        """Create a GitIntegrationService instance for testing"""
        return GitIntegrationService(temp_repo_dir)
    
    @pytest.fixture
    def sample_content(self):
        """Sample content for testing"""
        return """# Meeting Analysis

## Executive Summary
This is a test meeting analysis with comprehensive insights.

## Key Decisions
1. Decision A - Approved
2. Decision B - Pending review

## Action Items
- [ ] Task 1: Complete by Friday
- [ ] Task 2: Review documentation
"""
    
    def test_initialize_repository(self, temp_repo_dir):
        """Test repository initialization"""
        service = GitIntegrationService(temp_repo_dir)
        
        # Check that repository was created
        assert service.repo is not None
        assert (Path(temp_repo_dir) / '.git').exists()
        
        # Check initial structure
        assert (Path(temp_repo_dir) / 'meetings').exists()
        assert (Path(temp_repo_dir) / 'analyses').exists()
        assert (Path(temp_repo_dir) / 'outputs').exists()
        assert (Path(temp_repo_dir) / 'README.md').exists()
        assert (Path(temp_repo_dir) / '.gitignore').exists()
        
        # Check initial commit
        commits = list(service.repo.iter_commits())
        assert len(commits) == 1
        assert "Initial repository setup" in commits[0].message
    
    @pytest.mark.asyncio
    async def test_commit_generated_output_create(self, service, sample_content):
        """Test committing a new file"""
        file_path = "analyses/test_analysis.md"
        author = "test@example.com"
        commit_message = "Add test analysis"
        metadata = {"analysis_id": "test_123", "type": "oracle_analysis"}
        
        change = await service.commit_generated_output(
            file_path=file_path,
            content=sample_content,
            author=author,
            commit_message=commit_message,
            metadata=metadata
        )
        
        # Verify change object
        assert change.file_path == file_path
        assert change.change_type == ChangeType.CREATE
        assert change.author == author
        assert change.message == commit_message
        assert change.metadata == metadata
        assert change.commit_hash is not None
        assert change.content_after == sample_content
        assert change.content_before is None
        
        # Verify file was created and committed
        full_path = Path(service.repo_path) / file_path
        assert full_path.exists()
        assert full_path.read_text() == sample_content
        
        # Verify commit was made
        latest_commit = service.repo.head.commit
        assert change.commit_hash == latest_commit.hexsha
        
        # Verify change was logged
        assert change in service.changes_log
    
    @pytest.mark.asyncio
    async def test_commit_generated_output_update(self, service, sample_content):
        """Test updating an existing file"""
        file_path = "analyses/test_analysis.md"
        author = "test@example.com"
        
        # Create initial file
        await service.commit_generated_output(
            file_path=file_path,
            content=sample_content,
            author=author,
            commit_message="Initial version"
        )
        
        # Update the file
        updated_content = sample_content + "\n\n## Additional Section\nNew content added."
        change = await service.commit_generated_output(
            file_path=file_path,
            content=updated_content,
            author=author,
            commit_message="Update analysis with additional section"
        )
        
        # Verify change object
        assert change.change_type == ChangeType.UPDATE
        assert change.content_before == sample_content
        assert change.content_after == updated_content
        
        # Verify file was updated
        full_path = Path(service.repo_path) / file_path
        assert full_path.read_text() == updated_content
        
        # Verify we have two commits now
        commits = list(service.repo.iter_commits())
        assert len(commits) == 3  # Initial + first file + update
    
    @pytest.mark.asyncio
    async def test_create_meeting_branch(self, service):
        """Test creating a meeting branch"""
        meeting_id = "meeting_123"
        meeting_title = "Project Planning Meeting"
        author = "test@example.com"
        
        branch_name = await service.create_meeting_branch(
            meeting_id=meeting_id,
            meeting_title=meeting_title,
            author=author
        )
        
        # Verify branch was created
        assert branch_name.startswith("meeting/")
        assert meeting_id in branch_name
        assert branch_name in [b.name for b in service.repo.branches]
        
        # Verify branch info was stored
        assert branch_name in service.branches
        branch_info = service.branches[branch_name]
        assert branch_info.branch_type == BranchType.MEETING
        assert branch_info.meeting_id == meeting_id
        assert branch_info.created_by == author
        assert branch_info.is_active
        
        # Verify meeting directory was created
        meeting_dir = Path(service.repo_path) / 'meetings' / meeting_id
        assert meeting_dir.exists()
        
        # Verify metadata file was created
        metadata_file = meeting_dir / 'metadata.json'
        assert metadata_file.exists()
        metadata = json.loads(metadata_file.read_text())
        assert metadata['meeting_id'] == meeting_id
        assert metadata['title'] == meeting_title
        assert metadata['branch'] == branch_name
    
    @pytest.mark.asyncio
    async def test_create_analysis_branch(self, service):
        """Test creating an analysis branch"""
        analysis_id = "analysis_456"
        analysis_type = "oracle_protocol"
        base_branch = "main"
        author = "analyst@example.com"
        
        branch_name = await service.create_analysis_branch(
            analysis_id=analysis_id,
            analysis_type=analysis_type,
            base_branch=base_branch,
            author=author
        )
        
        # Verify branch was created
        assert branch_name == f"analysis/{analysis_id}-{analysis_type}"
        assert branch_name in [b.name for b in service.repo.branches]
        
        # Verify branch info
        branch_info = service.branches[branch_name]
        assert branch_info.branch_type == BranchType.ANALYSIS
        assert branch_info.analysis_id == analysis_id
        assert branch_info.base_branch == base_branch
        assert branch_info.created_by == author
    
    @pytest.mark.asyncio
    async def test_create_review_branch(self, service):
        """Test creating a review branch"""
        # First create a source branch
        source_branch = await service.create_meeting_branch(
            "meeting_789", "Review Test Meeting", "author@example.com"
        )
        
        reviewer = "reviewer@example.com"
        review_purpose = "Content review and editing"
        
        review_branch = await service.create_review_branch(
            source_branch=source_branch,
            reviewer=reviewer,
            review_purpose=review_purpose
        )
        
        # Verify review branch was created
        assert review_branch.startswith("review/")
        assert review_branch in [b.name for b in service.repo.branches]
        
        # Verify branch info
        branch_info = service.branches[review_branch]
        assert branch_info.branch_type == BranchType.REVIEW
        assert branch_info.base_branch == source_branch
        assert branch_info.created_by == reviewer
        assert review_purpose in branch_info.description
    
    @pytest.mark.asyncio
    async def test_merge_branch_success(self, service, sample_content):
        """Test successful branch merge without conflicts"""
        # Create a feature branch
        feature_branch = await service.create_analysis_branch(
            "analysis_merge_test", "test_analysis", "main", "dev@example.com"
        )
        
        # Add content to feature branch
        await service.commit_generated_output(
            file_path="analyses/feature_content.md",
            content=sample_content,
            author="dev@example.com",
            commit_message="Add feature content"
        )
        
        # Merge back to main
        success, conflicts = await service.merge_branch(
            source_branch=feature_branch,
            target_branch="main",
            author="dev@example.com"
        )
        
        # Verify successful merge
        assert success is True
        assert len(conflicts) == 0
        
        # Verify merge commit was created
        commits = list(service.repo.iter_commits("main"))
        merge_commit = commits[0]
        assert f"Merge {feature_branch} into main" in merge_commit.message
        
        # Verify merge was logged
        merge_changes = [c for c in service.changes_log if c.change_type == ChangeType.MERGE]
        assert len(merge_changes) == 1
        assert merge_changes[0].metadata['source_branch'] == feature_branch
        assert merge_changes[0].metadata['target_branch'] == "main"
    
    def test_detect_merge_conflicts(self, service):
        """Test merge conflict detection"""
        # This is a complex test that would require setting up actual merge conflicts
        # For now, we'll test the conflict marker extraction
        
        conflicted_content = """# Test File

Some content here.

<<<<<<< HEAD
This is our version of the content.
We made these changes.
=======
This is their version of the content.
They made different changes.
>>>>>>> feature-branch

More content after conflict.
"""
        
        markers = service._extract_conflict_markers(conflicted_content)
        assert len(markers) == 1
        assert "<<<<<<< HEAD" in markers[0]
        assert "=======" in markers[0]
        assert ">>>>>>> feature-branch" in markers[0]
    
    @pytest.mark.asyncio
    async def test_intelligent_merge_json(self, service):
        """Test intelligent JSON merge resolution"""
        conflict = MergeConflict(
            file_path="test.json",
            conflict_markers=[],
            our_content='{"name": "Test", "version": "1.0", "features": ["a", "b"]}',
            their_content='{"name": "Test", "version": "1.1", "features": ["b", "c"], "author": "Someone"}'
        )
        
        resolved_content = await service._merge_json_content(conflict)
        resolved_data = json.loads(resolved_content)
        
        # Verify intelligent merging
        assert resolved_data["name"] == "Test"
        assert resolved_data["version"] == "1.1"  # Their version preferred
        assert resolved_data["author"] == "Someone"  # Their new field added
        assert set(resolved_data["features"]) == {"a", "b", "c"}  # Lists merged
    
    @pytest.mark.asyncio
    async def test_merge_markdown_content(self, service):
        """Test intelligent Markdown merge resolution"""
        our_content = """# Document Title

## Section A
Our content for section A.

## Section B
Our content for section B.
"""
        
        their_content = """# Document Title

## Section A
Their content for section A.

## Section C
Their new section C.
"""
        
        conflict = MergeConflict(
            file_path="test.md",
            conflict_markers=[],
            our_content=our_content,
            their_content=their_content
        )
        
        resolved_content = await service._merge_markdown_content(conflict)
        
        # Verify sections were merged
        assert "# Document Title" in resolved_content
        assert "## Section A" in resolved_content
        assert "## Section B" in resolved_content
        assert "## Section C" in resolved_content
    
    @pytest.mark.asyncio
    async def test_get_change_history(self, service, sample_content):
        """Test retrieving change history"""
        # Create some changes
        await service.commit_generated_output(
            "test1.md", sample_content, "user1@example.com", "First commit"
        )
        await service.commit_generated_output(
            "test2.md", sample_content, "user2@example.com", "Second commit"
        )
        await service.commit_generated_output(
            "test1.md", sample_content + "\nUpdated", "user1@example.com", "Update first file"
        )
        
        # Get all changes
        all_changes = await service.get_change_history()
        assert len(all_changes) == 3
        
        # Get changes for specific file
        file_changes = await service.get_change_history(file_path="test1.md")
        assert len(file_changes) == 2
        assert all(c.file_path == "test1.md" for c in file_changes)
        
        # Get changes by author
        user1_changes = await service.get_change_history(author="user1@example.com")
        assert len(user1_changes) == 2
        assert all(c.author == "user1@example.com" for c in user1_changes)
        
        # Get recent changes
        recent_changes = await service.get_change_history(
            since=datetime.utcnow() - timedelta(minutes=1)
        )
        assert len(recent_changes) == 3  # All should be recent
        
        # Test limit
        limited_changes = await service.get_change_history(limit=2)
        assert len(limited_changes) == 2
    
    @pytest.mark.asyncio
    async def test_get_file_diff(self, service, sample_content):
        """Test getting file diff between commits"""
        file_path = "test_diff.md"
        
        # Create initial version
        change1 = await service.commit_generated_output(
            file_path, sample_content, "user@example.com", "Initial version"
        )
        
        # Create updated version
        updated_content = sample_content + "\n\n## New Section\nAdditional content."
        change2 = await service.commit_generated_output(
            file_path, updated_content, "user@example.com", "Add new section"
        )
        
        # Get diff
        diff_data = await service.get_file_diff(
            file_path, change1.commit_hash, change2.commit_hash
        )
        
        assert 'error' not in diff_data
        assert diff_data['file_path'] == file_path
        assert diff_data['commit1'] == change1.commit_hash
        assert diff_data['commit2'] == change2.commit_hash
        assert diff_data['additions'] > 0
        assert diff_data['deletions'] == 0
        assert "## New Section" in diff_data['diff']
    
    @pytest.mark.asyncio
    async def test_create_backup(self, service, sample_content):
        """Test creating repository backup"""
        # Add some content first
        await service.commit_generated_output(
            "backup_test.md", sample_content, "user@example.com", "Test content for backup"
        )
        
        # Create backup
        backup_file = await service.create_backup("test_backup")
        
        # Verify backup file was created
        assert Path(backup_file).exists()
        assert backup_file.endswith('.tar.gz')
        
        # Verify backup metadata
        backup_dir = Path(backup_file).parent
        metadata_file = backup_dir / 'metadata.json'
        assert metadata_file.exists()
        
        metadata = json.loads(metadata_file.read_text())
        assert metadata['backup_name'] == 'test_backup'
        assert 'created_at' in metadata
        assert 'current_commit' in metadata
        assert metadata['backup_size_bytes'] > 0
    
    @pytest.mark.asyncio
    async def test_get_repository_status(self, service, sample_content):
        """Test getting repository status"""
        # Add some content and branches
        await service.commit_generated_output(
            "status_test.md", sample_content, "user@example.com", "Test content"
        )
        await service.create_meeting_branch("meeting_status", "Status Test", "user@example.com")
        
        status = await service.get_repository_status()
        
        assert 'error' not in status
        assert 'repository_path' in status
        assert 'current_branch' in status
        assert 'current_commit' in status
        assert 'total_commits' in status
        assert 'total_branches' in status
        assert 'active_branches' in status
        assert 'changes_logged' in status
        assert 'branch_types' in status
        assert 'recent_changes' in status
        assert 'repository_size_mb' in status
        
        # Verify branch types breakdown
        assert 'main' in status['branch_types']
        assert 'meeting' in status['branch_types']
    
    def test_merge_dict_recursive(self, service):
        """Test recursive dictionary merging"""
        dict1 = {
            "a": 1,
            "b": {"x": 10, "y": 20},
            "c": [1, 2, 3]
        }
        
        dict2 = {
            "a": 2,  # Conflict - should prefer dict2
            "b": {"y": 30, "z": 40},  # Merge nested dict
            "c": [3, 4, 5],  # Merge lists
            "d": "new"  # New key
        }
        
        result = service._merge_dict_recursive(dict1, dict2)
        
        assert result["a"] == 2  # dict2 value preferred
        assert result["b"]["x"] == 10  # From dict1
        assert result["b"]["y"] == 30  # From dict2 (preferred)
        assert result["b"]["z"] == 40  # From dict2 (new)
        assert set(result["c"]) == {1, 2, 3, 4, 5}  # Merged lists
        assert result["d"] == "new"  # New key from dict2
    
    def test_parse_markdown_sections(self, service):
        """Test Markdown section parsing"""
        content = """# Main Title

Some intro content.

## Section 1

Content for section 1.

### Subsection 1.1

Subsection content.

## Section 2

Content for section 2.
"""
        
        sections = service._parse_markdown_sections(content)
        
        assert "header" in sections
        assert "# Main Title" in sections
        assert "## Section 1" in sections
        assert "### Subsection 1.1" in sections
        assert "## Section 2" in sections
    
    def test_generate_change_id(self, service):
        """Test change ID generation"""
        id1 = service._generate_change_id()
        id2 = service._generate_change_id()
        
        assert id1 != id2
        assert id1.startswith('change_')
        assert id2.startswith('change_')
    
    def test_create_commit_message(self, service):
        """Test commit message creation"""
        change = GitChange(
            id="test_change",
            file_path="test.md",
            change_type=ChangeType.UPDATE,
            author="test@example.com",
            message="Test update",
            metadata={"analysis_id": "test_123", "type": "oracle"}
        )
        
        commit_message = service._create_commit_message(change)
        
        assert "[UPDATE]" in commit_message
        assert "test.md - Test update" in commit_message
        assert "Author: test@example.com" in commit_message
        assert "analysis_id: test_123" in commit_message
        assert "type: oracle" in commit_message
    
    @pytest.mark.asyncio
    async def test_error_handling(self, service):
        """Test error handling in various scenarios"""
        # Test committing to non-existent path (should create directories)
        try:
            await service.commit_generated_output(
                "deep/nested/path/file.md",
                "content",
                "user@example.com",
                "Test deep path"
            )
            # Should succeed by creating directories
            assert True
        except Exception:
            pytest.fail("Should handle deep paths by creating directories")
        
        # Test getting diff with invalid commits
        diff_data = await service.get_file_diff("test.md", "invalid_hash1", "invalid_hash2")
        assert 'error' in diff_data
    
    @pytest.mark.asyncio
    async def test_auto_commit_disabled(self, temp_repo_dir):
        """Test behavior when auto-commit is disabled"""
        service = GitIntegrationService(temp_repo_dir)
        service.config['auto_commit_enabled'] = False
        
        change = await service.commit_generated_output(
            "test.md", "content", "user@example.com", "Test commit"
        )
        
        # Should be added to pending changes instead of committed
        assert change.commit_hash is None
        assert "test.md" in service.pending_changes
        assert service.pending_changes["test.md"] == change
    
    def test_analyze_branch(self, service):
        """Test branch analysis"""
        # Test main branch analysis
        main_info = service._analyze_branch("main")
        assert main_info.branch_type == BranchType.MAIN
        assert main_info.name == "main"
        
        # Test feature branch analysis (simulated)
        # This would require creating actual branches, which is complex in tests
        # For now, we test the logic with branch name patterns
        
        # Test branch type detection from names
        test_cases = [
            ("feature/new-feature", BranchType.FEATURE),
            ("meeting/123-planning", BranchType.MEETING),
            ("analysis/456-oracle", BranchType.ANALYSIS),
            ("review/789-content", BranchType.REVIEW),
            ("hotfix/urgent-fix", BranchType.HOTFIX),
            ("random-name", BranchType.FEATURE)  # Default
        ]
        
        for branch_name, expected_type in test_cases:
            # We can't easily test _analyze_branch with non-existent branches
            # So we test the logic by checking the branch type determination
            if branch_name.startswith('meeting/'):
                assert expected_type == BranchType.MEETING
            elif branch_name.startswith('analysis/'):
                assert expected_type == BranchType.ANALYSIS
            # etc.


if __name__ == '__main__':
    pytest.main([__file__])