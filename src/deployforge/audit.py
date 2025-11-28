"""Audit logging system for DeployForge."""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import getpass
import platform

logger = logging.getLogger(__name__)


@dataclass
class AuditEvent:
    """Represents an audit event."""

    timestamp: str
    event_type: str
    action: str
    user: str
    host: str
    image_path: Optional[str] = None
    details: Dict[str, Any] = None
    success: bool = True
    error: Optional[str] = None


class AuditLogger:
    """Audit logging for compliance and security."""

    def __init__(self, audit_log_path: Path):
        """
        Initialize audit logger.

        Args:
            audit_log_path: Path to audit log file
        """
        self.audit_log_path = Path(audit_log_path)
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)

        self.user = getpass.getuser()
        self.host = platform.node()

    def log_event(
        self,
        event_type: str,
        action: str,
        image_path: Optional[Path] = None,
        details: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error: Optional[str] = None,
    ) -> None:
        """
        Log an audit event.

        Args:
            event_type: Type of event (mount, unmount, modify, etc.)
            action: Specific action taken
            image_path: Path to image affected
            details: Additional details
            success: Whether the operation succeeded
            error: Error message if failed
        """
        event = AuditEvent(
            timestamp=datetime.utcnow().isoformat() + "Z",
            event_type=event_type,
            action=action,
            user=self.user,
            host=self.host,
            image_path=str(image_path) if image_path else None,
            details=details or {},
            success=success,
            error=error,
        )

        # Write to audit log (append mode, JSONL format)
        try:
            with open(self.audit_log_path, "a") as f:
                f.write(json.dumps(asdict(event)) + "\n")

            logger.debug(f"Audit event logged: {event_type} - {action}")

        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")

    def get_events(
        self,
        event_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> list:
        """
        Retrieve audit events.

        Args:
            event_type: Filter by event type
            start_time: Filter by start time
            end_time: Filter by end time

        Returns:
            List of audit events
        """
        events = []

        if not self.audit_log_path.exists():
            return events

        try:
            with open(self.audit_log_path, "r") as f:
                for line in f:
                    event_data = json.loads(line.strip())

                    # Apply filters
                    if event_type and event_data.get("event_type") != event_type:
                        continue

                    event_time = datetime.fromisoformat(
                        event_data["timestamp"].replace("Z", "+00:00")
                    )

                    if start_time and event_time < start_time:
                        continue

                    if end_time and event_time > end_time:
                        continue

                    events.append(event_data)

        except Exception as e:
            logger.error(f"Error reading audit log: {e}")

        return events

    def generate_report(self, output_path: Path) -> None:
        """
        Generate an audit report.

        Args:
            output_path: Path to output report
        """
        events = self.get_events()

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            f.write("=" * 80 + "\n")
            f.write("DEPLOYFORGE AUDIT REPORT\n")
            f.write("=" * 80 + "\n\n")

            f.write(f"Total Events: {len(events)}\n\n")

            # Event type summary
            event_types = {}
            for event in events:
                et = event.get("event_type", "unknown")
                event_types[et] = event_types.get(et, 0) + 1

            f.write("Event Types:\n")
            for et, count in sorted(event_types.items()):
                f.write(f"  {et}: {count}\n")

            f.write("\n" + "-" * 80 + "\n\n")

            # Event details
            f.write("Event Log:\n\n")
            for event in events:
                f.write(f"[{event['timestamp']}] ")
                f.write(f"{event['event_type']} - {event['action']}\n")
                f.write(f"  User: {event['user']}@{event['host']}\n")

                if event.get("image_path"):
                    f.write(f"  Image: {event['image_path']}\n")

                if not event.get("success"):
                    f.write(f"  ERROR: {event.get('error')}\n")

                f.write("\n")

        logger.info(f"Audit report generated: {output_path}")
