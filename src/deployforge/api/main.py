"""FastAPI REST API for DeployForge."""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from fastapi import FastAPI, HTTPException, BackgroundTasks, status
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field

from deployforge import __version__
from deployforge.core.image_manager import ImageManager
from deployforge.batch import BatchOperation
from deployforge.comparison import ImageComparator
from deployforge.audit import AuditLogger


logger = logging.getLogger(__name__)

app = FastAPI(
    title="DeployForge API",
    description="REST API for Windows deployment image management",
    version=__version__
)

# In-memory job store (use Redis/DB in production)
jobs: Dict[str, Dict[str, Any]] = {}

# Audit logger
audit_logger = AuditLogger(Path("./logs/audit.jsonl"))


class ImageInfoRequest(BaseModel):
    """Request model for getting image information."""
    image_path: str = Field(..., description="Path to the image file")


class BatchOperationRequest(BaseModel):
    """Request model for batch operations."""
    image_paths: List[str] = Field(..., description="List of image paths")
    operation: str = Field(..., description="Operation to perform")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Operation parameters")


class CompareRequest(BaseModel):
    """Request model for image comparison."""
    image1_path: str
    image2_path: str
    compute_hashes: bool = False


class JobResponse(BaseModel):
    """Response model for job status."""
    job_id: str
    status: str
    created_at: str
    completed_at: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@app.get("/", tags=["General"])
async def root():
    """API root endpoint."""
    return {
        "name": "DeployForge API",
        "version": __version__,
        "documentation": "/docs"
    }


@app.get("/health", tags=["General"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": __version__,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/images/info", tags=["Images"])
async def get_image_info(request: ImageInfoRequest):
    """
    Get information about an image.

    Returns metadata, format information, and file details.
    """
    try:
        image_path = Path(request.image_path)

        if not image_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Image not found: {image_path}"
            )

        with ImageManager(image_path) as manager:
            info = manager.get_info()

        audit_logger.log_event(
            event_type="image_info",
            action="get_info",
            image_path=image_path,
            success=True
        )

        return info

    except Exception as e:
        logger.error(f"Error getting image info: {e}")
        audit_logger.log_event(
            event_type="image_info",
            action="get_info",
            image_path=Path(request.image_path) if request.image_path else None,
            success=False,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/images/list", tags=["Images"])
async def list_image_files(image_path: str, path: str = "/"):
    """List files in an image."""
    try:
        img_path = Path(image_path)

        if not img_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Image not found: {img_path}"
            )

        with ImageManager(img_path) as manager:
            manager.mount()
            try:
                files = manager.list_files(path)
            finally:
                manager.unmount()

        return {"files": files}

    except Exception as e:
        logger.error(f"Error listing files: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/images/compare", tags=["Images"])
async def compare_images(request: CompareRequest):
    """Compare two images."""
    try:
        image1 = Path(request.image1_path)
        image2 = Path(request.image2_path)

        if not image1.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Image 1 not found: {image1}"
            )

        if not image2.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Image 2 not found: {image2}"
            )

        comparator = ImageComparator(compute_hashes=request.compute_hashes)
        result = comparator.compare(image1, image2)

        return {
            "image1": result.image1,
            "image2": result.image2,
            "similarity": f"{result.similarity_percentage():.2f}%",
            "only_in_image1": len(result.only_in_image1),
            "only_in_image2": len(result.only_in_image2),
            "different_files": len(result.different_files),
            "identical_files": len(result.identical_files)
        }

    except Exception as e:
        logger.error(f"Error comparing images: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/batch/operations", tags=["Batch"])
async def create_batch_operation(
    request: BatchOperationRequest,
    background_tasks: BackgroundTasks
):
    """
    Create a batch operation job.

    Operations:
    - get_info: Get information about multiple images
    - list_files: List files in multiple images
    - add_file: Add a file to multiple images
    - remove_file: Remove a file from multiple images
    """
    job_id = str(uuid.uuid4())

    job = {
        "job_id": job_id,
        "status": "queued",
        "operation": request.operation,
        "image_paths": request.image_paths,
        "parameters": request.parameters,
        "created_at": datetime.utcnow().isoformat(),
        "completed_at": None,
        "result": None,
        "error": None
    }

    jobs[job_id] = job

    # Schedule background task
    background_tasks.add_task(execute_batch_operation, job_id)

    return {"job_id": job_id, "status": "queued"}


async def execute_batch_operation(job_id: str):
    """Execute a batch operation in the background."""
    job = jobs.get(job_id)
    if not job:
        return

    try:
        job["status"] = "running"

        image_paths = [Path(p) for p in job["image_paths"]]
        batch_op = BatchOperation()

        operation = job["operation"]
        params = job["parameters"]

        if operation == "get_info":
            result = batch_op.get_info_batch(image_paths)
        elif operation == "list_files":
            path = params.get("path", "/")
            result = batch_op.list_files_batch(image_paths, path)
        elif operation == "add_file":
            source = Path(params.get("source"))
            destination = params.get("destination")
            result = batch_op.add_file_batch(image_paths, source, destination)
        elif operation == "remove_file":
            file_path = params.get("file_path")
            result = batch_op.remove_file_batch(image_paths, file_path)
        else:
            raise ValueError(f"Unknown operation: {operation}")

        job["status"] = "completed"
        job["result"] = result
        job["completed_at"] = datetime.utcnow().isoformat()

        audit_logger.log_event(
            event_type="batch_operation",
            action=operation,
            details={"job_id": job_id, "images_count": len(image_paths)},
            success=True
        )

    except Exception as e:
        logger.error(f"Error in batch operation {job_id}: {e}")
        job["status"] = "failed"
        job["error"] = str(e)
        job["completed_at"] = datetime.utcnow().isoformat()

        audit_logger.log_event(
            event_type="batch_operation",
            action=job.get("operation", "unknown"),
            details={"job_id": job_id},
            success=False,
            error=str(e)
        )


@app.get("/jobs/{job_id}", tags=["Jobs"])
async def get_job_status(job_id: str):
    """Get the status of a batch operation job."""
    job = jobs.get(job_id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job not found: {job_id}"
        )

    return job


@app.get("/jobs", tags=["Jobs"])
async def list_jobs():
    """List all jobs."""
    return {"jobs": list(jobs.values())}


@app.get("/formats", tags=["General"])
async def list_supported_formats():
    """List supported image formats."""
    formats = ImageManager.supported_formats()

    format_info = {
        '.iso': 'ISO 9660 - Optical disc image',
        '.wim': 'WIM - Windows Imaging Format',
        '.esd': 'ESD - Electronic Software Download',
        '.ppkg': 'PPKG - Provisioning Package',
        '.vhd': 'VHD - Virtual Hard Disk',
        '.vhdx': 'VHDX - Virtual Hard Disk (Extended)'
    }

    return {
        "formats": [
            {"extension": fmt, "description": format_info.get(fmt, "Unknown")}
            for fmt in formats
        ]
    }


@app.get("/audit/events", tags=["Audit"])
async def get_audit_events(event_type: Optional[str] = None):
    """Get audit events."""
    events = audit_logger.get_events(event_type=event_type)
    return {"events": events, "count": len(events)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
