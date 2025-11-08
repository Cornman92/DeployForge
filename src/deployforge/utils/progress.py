"""Progress tracking utilities for DeployForge."""

from typing import Optional, Callable
from pathlib import Path
import logging

from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeRemainingColumn,
    TimeElapsedColumn,
    FileSizeColumn,
    TransferSpeedColumn,
)


logger = logging.getLogger(__name__)


def create_progress() -> Progress:
    """
    Create a configured progress bar.

    Returns:
        Configured Progress instance
    """
    return Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
    )


def create_file_progress() -> Progress:
    """
    Create a progress bar for file operations.

    Returns:
        Configured Progress instance for file transfers
    """
    return Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        FileSizeColumn(),
        TransferSpeedColumn(),
        TimeRemainingColumn(),
    )


class ProgressCallback:
    """Callback handler for tracking operation progress."""

    def __init__(self, progress: Progress, task_id: int):
        """
        Initialize progress callback.

        Args:
            progress: Progress bar instance
            task_id: Task ID in the progress bar
        """
        self.progress = progress
        self.task_id = task_id
        self.current = 0
        self.total = 0

    def update(self, current: int, total: Optional[int] = None) -> None:
        """
        Update progress.

        Args:
            current: Current progress value
            total: Optional total value
        """
        if total is not None:
            self.total = total
            self.progress.update(self.task_id, total=total)

        self.current = current
        self.progress.update(self.task_id, completed=current)

    def advance(self, amount: int = 1) -> None:
        """
        Advance progress by amount.

        Args:
            amount: Amount to advance
        """
        self.current += amount
        self.progress.advance(self.task_id, amount)

    def complete(self) -> None:
        """Mark the task as complete."""
        if self.total > 0:
            self.progress.update(self.task_id, completed=self.total)


def track_file_operation(
    source: Path,
    destination: Path,
    operation: Callable,
    description: str,
    chunk_size: int = 1024 * 1024,  # 1MB chunks
) -> None:
    """
    Track a file operation with progress.

    Args:
        source: Source file path
        destination: Destination file path
        operation: Operation to perform (function that takes source, dest, callback)
        description: Description for progress bar
        chunk_size: Size of chunks for progress updates
    """
    source_size = source.stat().st_size if source.exists() else 0

    with create_file_progress() as progress:
        task = progress.add_task(description, total=source_size)
        callback = ProgressCallback(progress, task)
        operation(source, destination, callback)
