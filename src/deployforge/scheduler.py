"""
Scheduled Operations & Job Queue Module

Provides job scheduling and queue management for automated builds.

Features:
- Cron-based scheduling
- Job queue with priorities
- Background task execution
- Job status tracking
- Retry logic for failed jobs
- Notifications (email, webhook)
- Persistent job storage
"""

import logging
import json
import time
import threading
import queue
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
import hashlib
import pickle

logger = logging.getLogger(__name__)


class JobStatus(Enum):
    """Job execution status"""

    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRY = "retry"


class JobPriority(Enum):
    """Job priority levels"""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


class NotificationType(Enum):
    """Notification type"""

    EMAIL = "email"
    WEBHOOK = "webhook"
    LOG = "log"


@dataclass
class CronSchedule:
    """
    Cron-based schedule definition.

    Format: minute hour day month weekday
    Example: '0 2 * * *' = Every day at 2:00 AM
    """

    expression: str

    def __post_init__(self):
        """Validate cron expression"""
        parts = self.expression.split()
        if len(parts) != 5:
            raise ValueError(f"Invalid cron expression: {self.expression}")

    def next_run(self, from_time: Optional[datetime] = None) -> datetime:
        """
        Calculate next run time.

        Args:
            from_time: Calculate from this time (default: now)

        Returns:
            Next scheduled execution time
        """
        if from_time is None:
            from_time = datetime.now()

        # Simplified cron parser - in production would use croniter library
        minute, hour, day, month, weekday = self.expression.split()

        # For now, simple daily schedule
        if minute == "0" and hour != "*":
            next_run = from_time.replace(hour=int(hour), minute=0, second=0, microsecond=0)

            if next_run <= from_time:
                next_run += timedelta(days=1)

            return next_run

        # Default: run in 1 hour
        return from_time + timedelta(hours=1)


@dataclass
class Job:
    """
    Represents a scheduled or queued job.
    """

    id: str
    name: str
    task: str
    config: Dict[str, Any] = field(default_factory=dict)
    priority: JobPriority = JobPriority.NORMAL
    status: JobStatus = JobStatus.PENDING
    schedule: Optional[CronSchedule] = None
    max_retries: int = 3
    retry_count: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["priority"] = self.priority.value
        data["status"] = self.status.value
        if self.schedule:
            data["schedule"] = self.schedule.expression
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Job":
        """Create from dictionary"""
        data["priority"] = JobPriority(data.get("priority", 2))
        data["status"] = JobStatus(data.get("status", "pending"))
        if "schedule" in data and isinstance(data["schedule"], str):
            data["schedule"] = CronSchedule(data["schedule"])
        return cls(**data)


@dataclass
class NotificationConfig:
    """Notification configuration"""

    type: NotificationType
    recipients: List[str] = field(default_factory=list)
    webhook_url: Optional[str] = None
    on_success: bool = True
    on_failure: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "type": self.type.value,
            "recipients": self.recipients,
            "webhook_url": self.webhook_url,
            "on_success": self.on_success,
            "on_failure": self.on_failure,
        }


class JobQueue:
    """
    Job queue with priority support and persistence.

    Example:
        queue = JobQueue(backend='file')
        job_id = queue.enqueue('build-image', config={'image': 'windows11.wim'})
        status = queue.get_status(job_id)
    """

    def __init__(self, backend: str = "memory", storage_path: Optional[Path] = None):
        """
        Initialize job queue.

        Args:
            backend: Storage backend ('memory', 'file', 'redis')
            storage_path: Path for file-based storage
        """
        self.backend = backend
        self.storage_path = storage_path or Path(".deployforge/jobs")
        self.jobs: Dict[str, Job] = {}
        self.queue: queue.PriorityQueue = queue.PriorityQueue()
        self._lock = threading.Lock()

        if backend == "file":
            self.storage_path.mkdir(parents=True, exist_ok=True)
            self._load_jobs()

    def enqueue(
        self,
        task: str,
        config: Optional[Dict[str, Any]] = None,
        priority: JobPriority = JobPriority.NORMAL,
        name: Optional[str] = None,
    ) -> str:
        """
        Add job to queue.

        Args:
            task: Task type (e.g., 'build-image')
            config: Task configuration
            priority: Job priority
            name: Optional job name

        Returns:
            Job ID
        """
        job_id = self._generate_job_id(task, config or {})

        job = Job(
            id=job_id,
            name=name or f"{task}_{job_id[:8]}",
            task=task,
            config=config or {},
            priority=priority,
            status=JobStatus.QUEUED,
        )

        with self._lock:
            self.jobs[job_id] = job
            # Priority queue: (priority, timestamp, job)
            self.queue.put(
                (-priority.value, time.time(), job)  # Negative for higher priority first
            )

        self._save_job(job)

        logger.info(f"Enqueued job {job_id}: {task}")

        return job_id

    def dequeue(self, timeout: Optional[float] = None) -> Optional[Job]:
        """
        Get next job from queue.

        Args:
            timeout: Wait timeout in seconds

        Returns:
            Next job or None
        """
        try:
            _, _, job = self.queue.get(timeout=timeout)

            with self._lock:
                job.status = JobStatus.RUNNING
                job.started_at = datetime.now().isoformat()
                self._save_job(job)

            return job

        except queue.Empty:
            return None

    def complete_job(self, job_id: str, result: Optional[Dict[str, Any]] = None):
        """
        Mark job as completed.

        Args:
            job_id: Job ID
            result: Optional result data
        """
        with self._lock:
            if job_id in self.jobs:
                job = self.jobs[job_id]
                job.status = JobStatus.COMPLETED
                job.completed_at = datetime.now().isoformat()
                job.result = result
                self._save_job(job)

                logger.info(f"Job {job_id} completed successfully")

    def fail_job(self, job_id: str, error: str):
        """
        Mark job as failed.

        Args:
            job_id: Job ID
            error: Error message
        """
        with self._lock:
            if job_id in self.jobs:
                job = self.jobs[job_id]
                job.error_message = error

                # Check if we should retry
                if job.retry_count < job.max_retries:
                    job.retry_count += 1
                    job.status = JobStatus.RETRY
                    logger.warning(
                        f"Job {job_id} failed, retrying ({job.retry_count}/{job.max_retries})"
                    )

                    # Re-queue for retry
                    self.queue.put((-job.priority.value, time.time(), job))
                else:
                    job.status = JobStatus.FAILED
                    job.completed_at = datetime.now().isoformat()
                    logger.error(f"Job {job_id} failed permanently: {error}")

                self._save_job(job)

    def get_status(self, job_id: str) -> Optional[JobStatus]:
        """
        Get job status.

        Args:
            job_id: Job ID

        Returns:
            Job status or None
        """
        with self._lock:
            job = self.jobs.get(job_id)
            return job.status if job else None

    def get_job(self, job_id: str) -> Optional[Job]:
        """
        Get job details.

        Args:
            job_id: Job ID

        Returns:
            Job or None
        """
        with self._lock:
            return self.jobs.get(job_id)

    def list_jobs(self, status: Optional[JobStatus] = None, limit: int = 100) -> List[Job]:
        """
        List jobs.

        Args:
            status: Filter by status
            limit: Maximum number to return

        Returns:
            List of jobs
        """
        with self._lock:
            jobs = list(self.jobs.values())

            if status:
                jobs = [j for j in jobs if j.status == status]

            # Sort by created_at descending
            jobs.sort(key=lambda j: j.created_at, reverse=True)

            return jobs[:limit]

    def cancel_job(self, job_id: str):
        """
        Cancel a pending/queued job.

        Args:
            job_id: Job ID
        """
        with self._lock:
            if job_id in self.jobs:
                job = self.jobs[job_id]
                if job.status in [JobStatus.PENDING, JobStatus.QUEUED]:
                    job.status = JobStatus.CANCELLED
                    job.completed_at = datetime.now().isoformat()
                    self._save_job(job)
                    logger.info(f"Job {job_id} cancelled")

    def _generate_job_id(self, task: str, config: Dict[str, Any]) -> str:
        """Generate unique job ID"""
        data = f"{task}_{time.time()}_{json.dumps(config, sort_keys=True)}"
        return hashlib.sha256(data.encode()).hexdigest()

    def _save_job(self, job: Job):
        """Save job to persistent storage"""
        if self.backend == "file":
            job_file = self.storage_path / f"{job.id}.json"
            with open(job_file, "w") as f:
                json.dump(job.to_dict(), f, indent=2)

    def _load_jobs(self):
        """Load jobs from persistent storage"""
        if self.backend == "file":
            for job_file in self.storage_path.glob("*.json"):
                try:
                    with open(job_file, "r") as f:
                        data = json.load(f)
                        job = Job.from_dict(data)
                        self.jobs[job.id] = job

                        # Re-queue pending/retry jobs
                        if job.status in [JobStatus.QUEUED, JobStatus.RETRY]:
                            self.queue.put((-job.priority.value, time.time(), job))

                    logger.info(f"Loaded job {job.id}")

                except Exception as e:
                    logger.error(f"Failed to load job from {job_file}: {e}")


class JobScheduler:
    """
    Cron-based job scheduler.

    Example:
        scheduler = JobScheduler()
        scheduler.add_job(
            name='monthly-rebuild',
            schedule=CronSchedule('0 2 1 * *'),
            task='build-image',
            config={'deployment': 'production.yaml'}
        )
        scheduler.start()
    """

    def __init__(self, job_queue: Optional[JobQueue] = None):
        """
        Initialize scheduler.

        Args:
            job_queue: Job queue to use (creates new if not provided)
        """
        self.job_queue = job_queue or JobQueue()
        self.scheduled_jobs: Dict[str, Job] = {}
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    def add_job(
        self,
        name: str,
        schedule: CronSchedule,
        task: str,
        config: Optional[Dict[str, Any]] = None,
        priority: JobPriority = JobPriority.NORMAL,
    ) -> str:
        """
        Add scheduled job.

        Args:
            name: Job name
            schedule: Cron schedule
            task: Task type
            config: Task configuration
            priority: Job priority

        Returns:
            Job ID
        """
        job_id = hashlib.sha256(f"{name}_{task}".encode()).hexdigest()

        job = Job(
            id=job_id,
            name=name,
            task=task,
            config=config or {},
            priority=priority,
            schedule=schedule,
        )

        with self._lock:
            self.scheduled_jobs[job_id] = job

        logger.info(f"Added scheduled job {name}: {schedule.expression}")

        return job_id

    def remove_job(self, job_id: str):
        """
        Remove scheduled job.

        Args:
            job_id: Job ID
        """
        with self._lock:
            if job_id in self.scheduled_jobs:
                del self.scheduled_jobs[job_id]
                logger.info(f"Removed scheduled job {job_id}")

    def start(self):
        """Start scheduler"""
        if self._running:
            logger.warning("Scheduler already running")
            return

        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

        logger.info("Scheduler started")

    def stop(self):
        """Stop scheduler"""
        self._running = False
        if self._thread:
            self._thread.join()

        logger.info("Scheduler stopped")

    def _run(self):
        """Main scheduler loop"""
        while self._running:
            now = datetime.now()

            with self._lock:
                for job in self.scheduled_jobs.values():
                    if job.schedule:
                        next_run = job.schedule.next_run()

                        # Check if it's time to run
                        if now >= next_run:
                            # Queue the job
                            self.job_queue.enqueue(
                                task=job.task,
                                config=job.config,
                                priority=job.priority,
                                name=job.name,
                            )

                            logger.info(f"Scheduled job triggered: {job.name}")

            # Check every minute
            time.sleep(60)


class JobWorker:
    """
    Background worker that processes jobs from queue.

    Example:
        worker = JobWorker(job_queue, task_handlers={'build-image': build_handler})
        worker.start()
    """

    def __init__(
        self,
        job_queue: JobQueue,
        task_handlers: Dict[str, Callable],
        notification_config: Optional[NotificationConfig] = None,
    ):
        """
        Initialize worker.

        Args:
            job_queue: Job queue to process
            task_handlers: Map of task types to handler functions
            notification_config: Optional notification configuration
        """
        self.job_queue = job_queue
        self.task_handlers = task_handlers
        self.notification_config = notification_config
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self):
        """Start worker"""
        if self._running:
            logger.warning("Worker already running")
            return

        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

        logger.info("Worker started")

    def stop(self):
        """Stop worker"""
        self._running = False
        if self._thread:
            self._thread.join()

        logger.info("Worker stopped")

    def _run(self):
        """Main worker loop"""
        while self._running:
            job = self.job_queue.dequeue(timeout=1.0)

            if job:
                self._process_job(job)

    def _process_job(self, job: Job):
        """Process a single job"""
        logger.info(f"Processing job {job.id}: {job.task}")

        try:
            # Get handler for task type
            handler = self.task_handlers.get(job.task)

            if not handler:
                raise ValueError(f"No handler for task type: {job.task}")

            # Execute handler
            result = handler(job.config)

            # Mark as completed
            self.job_queue.complete_job(job.id, result)

            # Send success notification
            if self.notification_config and self.notification_config.on_success:
                self._send_notification(job, success=True)

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Job {job.id} failed: {error_msg}")

            # Mark as failed
            self.job_queue.fail_job(job.id, error_msg)

            # Send failure notification
            if self.notification_config and self.notification_config.on_failure:
                self._send_notification(job, success=False, error=error_msg)

    def _send_notification(self, job: Job, success: bool, error: Optional[str] = None):
        """Send job completion notification"""
        if not self.notification_config:
            return

        status = "succeeded" if success else "failed"
        message = f"Job {job.name} ({job.id}) {status}"

        if error:
            message += f": {error}"

        if self.notification_config.type == NotificationType.LOG:
            if success:
                logger.info(message)
            else:
                logger.error(message)

        elif self.notification_config.type == NotificationType.EMAIL:
            # Would send email notification
            logger.info(f"Would send email to {self.notification_config.recipients}: {message}")

        elif self.notification_config.type == NotificationType.WEBHOOK:
            # Would send webhook notification
            logger.info(f"Would send webhook to {self.notification_config.webhook_url}: {message}")


def create_scheduled_build(
    schedule: str, config_path: Path, priority: JobPriority = JobPriority.NORMAL
) -> tuple[JobScheduler, JobWorker]:
    """
    Create a scheduled build workflow.

    Args:
        schedule: Cron expression
        config_path: Path to deployment config
        priority: Job priority

    Returns:
        Tuple of (scheduler, worker)

    Example:
        scheduler, worker = create_scheduled_build(
            schedule='0 2 * * *',  # Daily at 2 AM
            config_path=Path('deployment.yaml')
        )
        scheduler.start()
        worker.start()
    """
    from deployforge.iac import build_from_config

    # Create job queue
    job_queue = JobQueue(backend="file")

    # Create scheduler
    scheduler = JobScheduler(job_queue)

    # Add scheduled build job
    scheduler.add_job(
        name="scheduled-build",
        schedule=CronSchedule(schedule),
        task="build-image",
        config={"config_path": str(config_path)},
        priority=priority,
    )

    # Create worker with build handler
    def build_handler(config: Dict[str, Any]) -> Dict[str, Any]:
        """Handle build task"""
        config_path = Path(config["config_path"])
        success = build_from_config(config_path)
        return {"success": success}

    worker = JobWorker(
        job_queue=job_queue,
        task_handlers={"build-image": build_handler},
        notification_config=NotificationConfig(
            type=NotificationType.LOG, on_success=True, on_failure=True
        ),
    )

    return scheduler, worker
