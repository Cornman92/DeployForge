"""Tests for batch operations."""

import pytest
from pathlib import Path
from deployforge.batch import BatchOperation


def test_batch_operation_init():
    """Test BatchOperation initialization."""
    batch_op = BatchOperation(max_workers=4)
    assert batch_op.max_workers == 4
    assert batch_op.results == []


def test_process_images_empty_list():
    """Test processing empty image list."""
    batch_op = BatchOperation()

    def dummy_op(manager):
        return {"test": "data"}

    results = batch_op.process_images([], dummy_op)
    assert results == []


def test_export_results_json(temp_dir):
    """Test exporting results to JSON."""
    batch_op = BatchOperation()
    batch_op.results = [
        {"image": "test1.wim", "status": "success"},
        {"image": "test2.wim", "status": "failed", "error": "Test error"}
    ]

    output_path = temp_dir / "results.json"
    batch_op.export_results(output_path, format='json')

    assert output_path.exists()

    import json
    with open(output_path) as f:
        data = json.load(f)

    assert len(data) == 2
    assert data[0]["image"] == "test1.wim"


def test_export_results_text(temp_dir):
    """Test exporting results to text."""
    batch_op = BatchOperation()
    batch_op.results = [
        {"image": "test1.wim", "status": "success"},
        {"image": "test2.wim", "status": "failed", "error": "Test error"}
    ]

    output_path = temp_dir / "results.txt"
    batch_op.export_results(output_path, format='text')

    assert output_path.exists()
    content = output_path.read_text()
    assert "test1.wim" in content
    assert "success" in content
    assert "Test error" in content
