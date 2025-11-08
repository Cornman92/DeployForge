"""Tests for audit logging."""

import pytest
from pathlib import Path
from datetime import datetime
from deployforge.audit import AuditLogger


def test_audit_logger_init(audit_log_path):
    """Test audit logger initialization."""
    logger = AuditLogger(audit_log_path)

    assert logger.audit_log_path == audit_log_path
    assert logger.user is not None
    assert logger.host is not None


def test_log_event(audit_log_path):
    """Test logging an audit event."""
    logger = AuditLogger(audit_log_path)

    logger.log_event(
        event_type="mount",
        action="mount_image",
        image_path=Path("/test/image.wim"),
        success=True
    )

    assert audit_log_path.exists()

    # Read and verify
    events = logger.get_events()
    assert len(events) == 1
    assert events[0]["event_type"] == "mount"
    assert events[0]["action"] == "mount_image"
    assert events[0]["success"] is True


def test_log_event_with_error(audit_log_path):
    """Test logging a failed event."""
    logger = AuditLogger(audit_log_path)

    logger.log_event(
        event_type="modify",
        action="add_file",
        image_path=Path("/test/image.wim"),
        success=False,
        error="File not found"
    )

    events = logger.get_events()
    assert len(events) == 1
    assert events[0]["success"] is False
    assert events[0]["error"] == "File not found"


def test_get_events_filter_by_type(audit_log_path):
    """Test filtering events by type."""
    logger = AuditLogger(audit_log_path)

    logger.log_event("mount", "mount_image", success=True)
    logger.log_event("unmount", "unmount_image", success=True)
    logger.log_event("mount", "mount_image", success=True)

    mount_events = logger.get_events(event_type="mount")
    assert len(mount_events) == 2

    unmount_events = logger.get_events(event_type="unmount")
    assert len(unmount_events) == 1


def test_generate_report(audit_log_path, temp_dir):
    """Test generating audit report."""
    logger = AuditLogger(audit_log_path)

    logger.log_event("mount", "mount_image", success=True)
    logger.log_event("modify", "add_file", success=False, error="Error")

    report_path = temp_dir / "audit_report.txt"
    logger.generate_report(report_path)

    assert report_path.exists()

    content = report_path.read_text()
    assert "DEPLOYFORGE AUDIT REPORT" in content
    assert "Total Events: 2" in content
    assert "mount" in content
