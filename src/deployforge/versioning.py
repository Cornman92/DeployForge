"""
Version Control for Images Module

Provides Git-like version control for Windows images.

Features:
- Image versioning system
- Commit/checkout workflow
- Version history tracking
- Tag support
- Branch support for variants
- Diff between versions
- Rollback capability
- Change log generation
"""

import logging
import json
import shutil
import hashlib
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
import subprocess

logger = logging.getLogger(__name__)


@dataclass
class ImageCommit:
    """Represents a versioned image commit"""

    commit_id: str
    version: str
    message: str
    image_path: Path
    image_hash: str
    parent_commit: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "commit_id": self.commit_id,
            "version": self.version,
            "message": self.message,
            "image_path": str(self.image_path),
            "image_hash": self.image_hash,
            "parent_commit": self.parent_commit,
            "tags": self.tags,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }


@dataclass
class ImageBranch:
    """Represents an image variant branch"""

    name: str
    head_commit: str
    description: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "head_commit": self.head_commit,
            "description": self.description,
            "created_at": self.created_at,
        }


class ImageRepository:
    """
    Git-like version control repository for Windows images.

    Example:
        repo = ImageRepository(Path('/images/repo'))
        repo.init()

        # Commit image
        repo.commit(
            image=Path('windows11.wim'),
            version='1.0.0',
            message='Initial build',
            tags=['production']
        )

        # Checkout specific version
        repo.checkout('windows11.wim', version='1.0.0')

        # View differences
        diff = repo.diff('1.0.0', '1.1.0')
    """

    def __init__(self, repo_path: Path):
        """
        Initialize image repository.

        Args:
            repo_path: Repository root path
        """
        self.repo_path = repo_path
        self.objects_dir = repo_path / ".deployforge" / "objects"
        self.refs_dir = repo_path / ".deployforge" / "refs"
        self.commits_file = repo_path / ".deployforge" / "commits.json"
        self.branches_file = repo_path / ".deployforge" / "branches.json"
        self.head_file = repo_path / ".deployforge" / "HEAD"

        self.commits: Dict[str, ImageCommit] = {}
        self.branches: Dict[str, ImageBranch] = {}
        self.current_branch = "main"

    def init(self):
        """Initialize new repository"""
        if self.repo_path.exists() and (self.repo_path / ".deployforge").exists():
            logger.warning("Repository already initialized")
            return

        logger.info(f"Initializing repository: {self.repo_path}")

        # Create directory structure
        self.repo_path.mkdir(parents=True, exist_ok=True)
        self.objects_dir.mkdir(parents=True, exist_ok=True)
        self.refs_dir.mkdir(parents=True, exist_ok=True)

        # Create initial branch
        main_branch = ImageBranch(name="main", head_commit="", description="Main production branch")
        self.branches["main"] = main_branch

        # Save state
        self._save_branches()
        self._save_commits()
        self._save_head("main")

        logger.info("Repository initialized")

    def commit(
        self,
        image: Path,
        version: str,
        message: str,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Commit image version.

        Args:
            image: Path to image file
            version: Version identifier
            message: Commit message
            tags: Optional tags
            metadata: Optional metadata

        Returns:
            Commit ID
        """
        if not image.exists():
            raise FileNotFoundError(f"Image not found: {image}")

        logger.info(f"Committing version {version}: {message}")

        # Calculate image hash
        image_hash = self._calculate_hash(image)

        # Generate commit ID
        commit_data = f"{version}_{image_hash}_{datetime.now().isoformat()}"
        commit_id = hashlib.sha256(commit_data.encode()).hexdigest()[:12]

        # Get parent commit
        current_branch = self.branches.get(self.current_branch)
        parent_commit = (
            current_branch.head_commit if current_branch and current_branch.head_commit else None
        )

        # Store image in objects directory
        object_path = self.objects_dir / f"{commit_id}.wim"
        shutil.copy2(image, object_path)

        # Create commit
        commit = ImageCommit(
            commit_id=commit_id,
            version=version,
            message=message,
            image_path=object_path,
            image_hash=image_hash,
            parent_commit=parent_commit,
            tags=tags or [],
            metadata=metadata or {},
        )

        # Store commit
        self.commits[commit_id] = commit

        # Update branch head
        if self.current_branch in self.branches:
            self.branches[self.current_branch].head_commit = commit_id

        # Save state
        self._save_commits()
        self._save_branches()

        logger.info(f"Committed version {version} as {commit_id}")

        return commit_id

    def checkout(
        self,
        output_path: Path,
        version: Optional[str] = None,
        commit_id: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> bool:
        """
        Checkout specific version.

        Args:
            output_path: Output path for checked out image
            version: Version to checkout
            commit_id: Commit ID to checkout
            tag: Tag to checkout

        Returns:
            True if successful
        """
        # Load commits
        self._load_commits()

        # Find commit
        target_commit = None

        if commit_id:
            target_commit = self.commits.get(commit_id)
        elif version:
            # Find by version
            for commit in self.commits.values():
                if commit.version == version:
                    target_commit = commit
                    break
        elif tag:
            # Find by tag
            for commit in self.commits.values():
                if tag in commit.tags:
                    target_commit = commit
                    break

        if not target_commit:
            logger.error(f"Version not found: {version or commit_id or tag}")
            return False

        logger.info(f"Checking out version {target_commit.version} ({target_commit.commit_id})")

        # Copy image to output
        shutil.copy2(target_commit.image_path, output_path)

        logger.info(f"Checked out to {output_path}")

        return True

    def tag(self, commit_id: str, tag_name: str):
        """
        Add tag to commit.

        Args:
            commit_id: Commit to tag
            tag_name: Tag name
        """
        self._load_commits()

        if commit_id not in self.commits:
            raise ValueError(f"Commit not found: {commit_id}")

        commit = self.commits[commit_id]

        if tag_name not in commit.tags:
            commit.tags.append(tag_name)
            self._save_commits()

            logger.info(f"Tagged {commit_id} as '{tag_name}'")

    def branch(
        self, name: str, from_commit: Optional[str] = None, description: str = ""
    ) -> ImageBranch:
        """
        Create new branch.

        Args:
            name: Branch name
            from_commit: Starting commit (default: current HEAD)
            description: Branch description

        Returns:
            New branch
        """
        self._load_branches()

        if name in self.branches:
            raise ValueError(f"Branch already exists: {name}")

        # Get starting commit
        if from_commit is None:
            current_branch = self.branches.get(self.current_branch)
            from_commit = current_branch.head_commit if current_branch else ""

        branch = ImageBranch(name=name, head_commit=from_commit, description=description)

        self.branches[name] = branch
        self._save_branches()

        logger.info(f"Created branch '{name}'")

        return branch

    def switch_branch(self, branch_name: str):
        """
        Switch to different branch.

        Args:
            branch_name: Branch to switch to
        """
        self._load_branches()

        if branch_name not in self.branches:
            raise ValueError(f"Branch not found: {branch_name}")

        self.current_branch = branch_name
        self._save_head(branch_name)

        logger.info(f"Switched to branch '{branch_name}'")

    def log(self, limit: int = 10, branch: Optional[str] = None) -> List[ImageCommit]:
        """
        Get commit history.

        Args:
            limit: Maximum commits to return
            branch: Branch to show log for (default: current)

        Returns:
            List of commits
        """
        self._load_commits()
        self._load_branches()

        if branch is None:
            branch = self.current_branch

        target_branch = self.branches.get(branch)
        if not target_branch or not target_branch.head_commit:
            return []

        # Walk commit history
        history = []
        current_id = target_branch.head_commit

        while current_id and len(history) < limit:
            commit = self.commits.get(current_id)
            if not commit:
                break

            history.append(commit)
            current_id = commit.parent_commit

        return history

    def diff(self, version1: str, version2: str) -> Dict[str, Any]:
        """
        Compare two versions.

        Args:
            version1: First version
            version2: Second version

        Returns:
            Difference information
        """
        self._load_commits()

        # Find commits
        commit1 = None
        commit2 = None

        for commit in self.commits.values():
            if commit.version == version1:
                commit1 = commit
            if commit.version == version2:
                commit2 = commit

        if not commit1 or not commit2:
            raise ValueError("Version not found")

        logger.info(f"Comparing {version1} to {version2}")

        # Calculate size difference
        size1 = commit1.image_path.stat().st_size
        size2 = commit2.image_path.stat().st_size
        size_diff = size2 - size1

        diff_info = {
            "version1": version1,
            "version2": version2,
            "commit1": commit1.commit_id,
            "commit2": commit2.commit_id,
            "size1_bytes": size1,
            "size2_bytes": size2,
            "size_diff_bytes": size_diff,
            "size_diff_mb": size_diff / (1024**2),
            "hash1": commit1.image_hash,
            "hash2": commit2.image_hash,
            "changed": commit1.image_hash != commit2.image_hash,
        }

        return diff_info

    def generate_changelog(
        self, from_version: str, to_version: str, output_path: Optional[Path] = None
    ) -> str:
        """
        Generate changelog between versions.

        Args:
            from_version: Starting version
            to_version: Ending version
            output_path: Optional path to save changelog

        Returns:
            Changelog text
        """
        self._load_commits()

        # Get all commits
        all_commits = sorted(self.commits.values(), key=lambda c: c.timestamp)

        # Find version range
        start_idx = None
        end_idx = None

        for i, commit in enumerate(all_commits):
            if commit.version == from_version:
                start_idx = i
            if commit.version == to_version:
                end_idx = i

        if start_idx is None or end_idx is None:
            raise ValueError("Version not found")

        # Generate changelog
        changelog_lines = [
            f"# Changelog: {from_version} to {to_version}",
            "",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Changes",
            "",
        ]

        for commit in all_commits[start_idx + 1 : end_idx + 1]:
            changelog_lines.append(f"### Version {commit.version} ({commit.timestamp[:10]})")
            changelog_lines.append(f"- {commit.message}")

            if commit.tags:
                changelog_lines.append(f"- Tags: {', '.join(commit.tags)}")

            changelog_lines.append("")

        changelog = "\n".join(changelog_lines)

        if output_path:
            with open(output_path, "w") as f:
                f.write(changelog)

            logger.info(f"Changelog saved to {output_path}")

        return changelog

    def list_tags(self) -> Dict[str, List[str]]:
        """
        List all tags.

        Returns:
            Dictionary of tag -> commit IDs
        """
        self._load_commits()

        tags = {}
        for commit in self.commits.values():
            for tag in commit.tags:
                if tag not in tags:
                    tags[tag] = []
                tags[tag].append(commit.commit_id)

        return tags

    def list_branches(self) -> List[ImageBranch]:
        """
        List all branches.

        Returns:
            List of branches
        """
        self._load_branches()
        return list(self.branches.values())

    def _calculate_hash(self, file_path: Path, algorithm: str = "sha256") -> str:
        """Calculate file hash"""
        hash_obj = hashlib.new(algorithm)

        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                hash_obj.update(chunk)

        return hash_obj.hexdigest()

    def _save_commits(self):
        """Save commits to file"""
        commits_data = {cid: commit.to_dict() for cid, commit in self.commits.items()}

        with open(self.commits_file, "w") as f:
            json.dump(commits_data, f, indent=2)

    def _load_commits(self):
        """Load commits from file"""
        if not self.commits_file.exists():
            return

        with open(self.commits_file, "r") as f:
            commits_data = json.load(f)

        for cid, data in commits_data.items():
            data["image_path"] = Path(data["image_path"])
            self.commits[cid] = ImageCommit(**data)

    def _save_branches(self):
        """Save branches to file"""
        branches_data = {name: branch.to_dict() for name, branch in self.branches.items()}

        with open(self.branches_file, "w") as f:
            json.dump(branches_data, f, indent=2)

    def _load_branches(self):
        """Load branches from file"""
        if not self.branches_file.exists():
            return

        with open(self.branches_file, "r") as f:
            branches_data = json.load(f)

        for name, data in branches_data.items():
            self.branches[name] = ImageBranch(**data)

    def _save_head(self, branch: str):
        """Save HEAD reference"""
        with open(self.head_file, "w") as f:
            f.write(branch)

    def _load_head(self) -> str:
        """Load HEAD reference"""
        if not self.head_file.exists():
            return "main"

        with open(self.head_file, "r") as f:
            return f.read().strip()


def create_versioned_build(
    repo_path: Path, image: Path, version: str, message: str, tags: Optional[List[str]] = None
) -> str:
    """
    Create versioned build in repository.

    Args:
        repo_path: Repository path
        image: Image to commit
        version: Version identifier
        message: Commit message
        tags: Optional tags

    Returns:
        Commit ID

    Example:
        commit_id = create_versioned_build(
            repo_path=Path('/images/repo'),
            image=Path('windows11.wim'),
            version='1.0.0',
            message='Initial production build',
            tags=['production', 'stable']
        )
    """
    repo = ImageRepository(repo_path)

    # Init if needed
    if not (repo_path / ".deployforge").exists():
        repo.init()
    else:
        repo._load_commits()
        repo._load_branches()

    # Commit
    commit_id = repo.commit(image=image, version=version, message=message, tags=tags)

    logger.info(f"Created versioned build: {version} ({commit_id})")

    return commit_id


def rollback_to_version(repo_path: Path, version: str, output_path: Path) -> bool:
    """
    Rollback to specific version.

    Args:
        repo_path: Repository path
        version: Version to rollback to
        output_path: Output path

    Returns:
        True if successful

    Example:
        success = rollback_to_version(
            repo_path=Path('/images/repo'),
            version='1.0.0',
            output_path=Path('rollback.wim')
        )
    """
    repo = ImageRepository(repo_path)
    repo._load_commits()

    success = repo.checkout(output_path=output_path, version=version)

    if success:
        logger.info(f"Rolled back to version {version}")
    else:
        logger.error("Rollback failed")

    return success
