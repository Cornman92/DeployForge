"""
Rollback Mechanism

Provides transaction-like operations with automatic rollback on failure.

Features:
- Automatic backup before modifications
- Checkpoint system
- Transaction context manager
- Recovery from failures
- Cleanup of old backups
"""

import logging
import shutil
import tempfile
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from contextlib import contextmanager
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class Checkpoint:
    """Represents a checkpoint/backup of an image."""

    id: str
    image_path: str
    backup_path: str
    created_at: str
    description: str
    metadata: Dict[str, Any]
    size_mb: float
    checksum: str


@dataclass
class Transaction:
    """Represents a transaction with rollback capability."""

    id: str
    checkpoint: Checkpoint
    operations: List[str]
    status: str  # pending, committed, rolled_back
    started_at: str
    completed_at: Optional[str] = None


class RollbackManager:
    """Manages checkpoints and rollback operations."""

    def __init__(self, backup_dir: Optional[Path] = None):
        """
        Initialize rollback manager.

        Args:
            backup_dir: Directory for storing backups
        """
        self.backup_dir = backup_dir or Path.home() / ".deployforge" / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        self.checkpoints_file = self.backup_dir / "checkpoints.json"
        self.checkpoints: Dict[str, Checkpoint] = {}
        self.transactions: Dict[str, Transaction] = {}

        self._load_checkpoints()

    def create_checkpoint(self, image_path: Path, description: str = "") -> Checkpoint:
        """
        Create a checkpoint (backup) of an image.

        Args:
            image_path: Path to image to backup
            description: Optional description

        Returns:
            Checkpoint object
        """
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        logger.info(f"Creating checkpoint for: {image_path}")

        # Generate checkpoint ID
        checkpoint_id = self._generate_checkpoint_id(image_path)

        # Create backup
        backup_path = self.backup_dir / f"{checkpoint_id}{image_path.suffix}"

        try:
            # Copy image to backup
            logger.info(f"Backing up to: {backup_path}")
            shutil.copy2(image_path, backup_path)

            # Calculate checksum
            checksum = self._calculate_checksum(backup_path)

            # Get file size
            size_mb = round(backup_path.stat().st_size / 1024 / 1024, 2)

            # Create checkpoint object
            checkpoint = Checkpoint(
                id=checkpoint_id,
                image_path=str(image_path),
                backup_path=str(backup_path),
                created_at=datetime.now().isoformat(),
                description=description or f"Backup of {image_path.name}",
                metadata={
                    "original_name": image_path.name,
                    "original_size": image_path.stat().st_size,
                },
                size_mb=size_mb,
                checksum=checksum,
            )

            # Store checkpoint
            self.checkpoints[checkpoint_id] = checkpoint
            self._save_checkpoints()

            logger.info(f"Checkpoint created: {checkpoint_id}")

            return checkpoint

        except Exception as e:
            logger.error(f"Failed to create checkpoint: {e}")

            # Cleanup failed backup
            if backup_path.exists():
                backup_path.unlink()

            raise

    def restore_checkpoint(self, checkpoint_id: str) -> bool:
        """
        Restore image from checkpoint.

        Args:
            checkpoint_id: Checkpoint ID

        Returns:
            True if successful
        """
        if checkpoint_id not in self.checkpoints:
            raise ValueError(f"Checkpoint not found: {checkpoint_id}")

        checkpoint = self.checkpoints[checkpoint_id]

        logger.info(f"Restoring checkpoint: {checkpoint_id}")

        backup_path = Path(checkpoint.backup_path)
        image_path = Path(checkpoint.image_path)

        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")

        try:
            # Verify backup integrity
            if not self._verify_checkpoint(checkpoint):
                raise ValueError("Checkpoint verification failed - backup may be corrupted")

            # Restore image
            logger.info(f"Restoring: {backup_path} -> {image_path}")

            # Create parent directory if needed
            image_path.parent.mkdir(parents=True, exist_ok=True)

            # Copy backup to original location
            shutil.copy2(backup_path, image_path)

            logger.info(f"Checkpoint restored successfully")

            return True

        except Exception as e:
            logger.error(f"Failed to restore checkpoint: {e}")
            raise

    def delete_checkpoint(self, checkpoint_id: str):
        """
        Delete a checkpoint.

        Args:
            checkpoint_id: Checkpoint ID
        """
        if checkpoint_id not in self.checkpoints:
            raise ValueError(f"Checkpoint not found: {checkpoint_id}")

        checkpoint = self.checkpoints[checkpoint_id]

        logger.info(f"Deleting checkpoint: {checkpoint_id}")

        # Delete backup file
        backup_path = Path(checkpoint.backup_path)
        if backup_path.exists():
            backup_path.unlink()

        # Remove from checkpoints
        del self.checkpoints[checkpoint_id]
        self._save_checkpoints()

        logger.info(f"Checkpoint deleted")

    def list_checkpoints(self, image_path: Optional[Path] = None) -> List[Checkpoint]:
        """
        List all checkpoints.

        Args:
            image_path: Optional filter by image path

        Returns:
            List of checkpoints
        """
        checkpoints = list(self.checkpoints.values())

        if image_path:
            image_path = str(Path(image_path).absolute())
            checkpoints = [c for c in checkpoints if c.image_path == image_path]

        # Sort by creation date (newest first)
        checkpoints.sort(key=lambda c: c.created_at, reverse=True)

        return checkpoints

    def cleanup_old_checkpoints(self, older_than_days: int = 7):
        """
        Delete checkpoints older than specified days.

        Args:
            older_than_days: Delete checkpoints older than this many days
        """
        cutoff_date = datetime.now() - timedelta(days=older_than_days)

        logger.info(f"Cleaning up checkpoints older than {older_than_days} days")

        checkpoints_to_delete = []

        for checkpoint_id, checkpoint in self.checkpoints.items():
            created_at = datetime.fromisoformat(checkpoint.created_at)

            if created_at < cutoff_date:
                checkpoints_to_delete.append(checkpoint_id)

        for checkpoint_id in checkpoints_to_delete:
            try:
                self.delete_checkpoint(checkpoint_id)
                logger.info(f"Deleted old checkpoint: {checkpoint_id}")
            except Exception as e:
                logger.warning(f"Failed to delete checkpoint {checkpoint_id}: {e}")

        logger.info(f"Cleanup complete: {len(checkpoints_to_delete)} checkpoints deleted")

    def get_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """
        Get checkpoint by ID.

        Args:
            checkpoint_id: Checkpoint ID

        Returns:
            Checkpoint or None
        """
        return self.checkpoints.get(checkpoint_id)

    @contextmanager
    def transaction(self, image_path: Path, description: str = "", auto_cleanup: bool = True):
        """
        Transaction context manager with automatic rollback.

        Args:
            image_path: Path to image
            description: Operation description
            auto_cleanup: Delete checkpoint on success

        Yields:
            Transaction object

        Example:
            with manager.transaction(image_path, "Apply gaming profile") as tx:
                apply_profile(image_path, 'gamer')
                # Auto-rollback on error
        """
        image_path = Path(image_path)

        # Create checkpoint
        checkpoint = self.create_checkpoint(image_path, description)

        # Create transaction
        transaction_id = self._generate_transaction_id()
        transaction = Transaction(
            id=transaction_id,
            checkpoint=checkpoint,
            operations=[],
            status="pending",
            started_at=datetime.now().isoformat(),
        )

        self.transactions[transaction_id] = transaction

        try:
            # Yield transaction for operations
            yield transaction

            # Mark as committed
            transaction.status = "committed"
            transaction.completed_at = datetime.now().isoformat()

            logger.info(f"Transaction committed: {transaction_id}")

            # Auto-cleanup checkpoint if successful
            if auto_cleanup:
                self.delete_checkpoint(checkpoint.id)
                logger.info(f"Checkpoint auto-deleted: {checkpoint.id}")

        except Exception as e:
            # Rollback on error
            logger.error(f"Transaction failed, rolling back: {e}")

            transaction.status = "rolled_back"
            transaction.completed_at = datetime.now().isoformat()

            try:
                self.restore_checkpoint(checkpoint.id)
                logger.info(f"Rollback successful: {transaction_id}")
            except Exception as rollback_error:
                logger.error(f"Rollback failed: {rollback_error}")

            # Re-raise original exception
            raise

        finally:
            self._save_checkpoints()

    def _generate_checkpoint_id(self, image_path: Path) -> str:
        """Generate unique checkpoint ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = image_path.stem
        return f"checkpoint_{name}_{timestamp}"

    def _generate_transaction_id(self) -> str:
        """Generate unique transaction ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"tx_{timestamp}"

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of file."""
        sha256 = hashlib.sha256()

        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)

        return sha256.hexdigest()

    def _verify_checkpoint(self, checkpoint: Checkpoint) -> bool:
        """
        Verify checkpoint integrity.

        Args:
            checkpoint: Checkpoint to verify

        Returns:
            True if valid
        """
        backup_path = Path(checkpoint.backup_path)

        if not backup_path.exists():
            logger.warning(f"Backup file not found: {backup_path}")
            return False

        # Verify checksum
        current_checksum = self._calculate_checksum(backup_path)

        if current_checksum != checkpoint.checksum:
            logger.warning(f"Checksum mismatch for checkpoint {checkpoint.id}")
            return False

        return True

    def _load_checkpoints(self):
        """Load checkpoints from disk."""
        if self.checkpoints_file.exists():
            try:
                with open(self.checkpoints_file, "r") as f:
                    data = json.load(f)

                for checkpoint_data in data:
                    checkpoint = Checkpoint(**checkpoint_data)
                    self.checkpoints[checkpoint.id] = checkpoint

                logger.info(f"Loaded {len(self.checkpoints)} checkpoints")

            except Exception as e:
                logger.warning(f"Failed to load checkpoints: {e}")

    def _save_checkpoints(self):
        """Save checkpoints to disk."""
        try:
            data = [asdict(c) for c in self.checkpoints.values()]

            with open(self.checkpoints_file, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save checkpoints: {e}")


# Global instance
_default_manager: Optional[RollbackManager] = None


def get_rollback_manager() -> RollbackManager:
    """Get global rollback manager instance."""
    global _default_manager

    if _default_manager is None:
        _default_manager = RollbackManager()

    return _default_manager


# Convenience functions
def create_checkpoint(image_path: Path, description: str = "") -> Checkpoint:
    """Create checkpoint using global manager."""
    return get_rollback_manager().create_checkpoint(image_path, description)


def restore_checkpoint(checkpoint_id: str) -> bool:
    """Restore checkpoint using global manager."""
    return get_rollback_manager().restore_checkpoint(checkpoint_id)


@contextmanager
def safe_operation(image_path: Path, description: str = "", auto_cleanup: bool = True):
    """
    Safe operation context manager.

    Example:
        with safe_operation(image_path, "Apply profile"):
            apply_profile(image_path, 'gamer')
    """
    manager = get_rollback_manager()

    with manager.transaction(image_path, description, auto_cleanup):
        yield
