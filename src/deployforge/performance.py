"""Performance monitoring and optimization utilities."""

import time
import psutil
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, asdict
from functools import wraps
import json

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics for an operation."""

    operation: str
    duration_seconds: float
    memory_used_mb: float
    cpu_percent: float
    disk_read_mb: float
    disk_write_mb: float
    timestamp: str


class PerformanceMonitor:
    """Monitor and profile performance of operations."""

    def __init__(self):
        """Initialize performance monitor."""
        self.metrics: list[PerformanceMetrics] = []
        self.process = psutil.Process()

    def measure(self, operation_name: str):
        """
        Decorator to measure performance of a function.

        Args:
            operation_name: Name of the operation being measured
        """

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Start measurements
                start_time = time.time()
                start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
                start_io = psutil.disk_io_counters()

                # Execute function
                try:
                    result = func(*args, **kwargs)
                finally:
                    # End measurements
                    end_time = time.time()
                    end_memory = self.process.memory_info().rss / 1024 / 1024
                    end_io = psutil.disk_io_counters()

                    # Calculate metrics
                    duration = end_time - start_time
                    memory_used = end_memory - start_memory
                    cpu_percent = self.process.cpu_percent()
                    disk_read = (end_io.read_bytes - start_io.read_bytes) / 1024 / 1024
                    disk_write = (end_io.write_bytes - start_io.write_bytes) / 1024 / 1024

                    # Store metrics
                    metrics = PerformanceMetrics(
                        operation=operation_name,
                        duration_seconds=duration,
                        memory_used_mb=memory_used,
                        cpu_percent=cpu_percent,
                        disk_read_mb=disk_read,
                        disk_write_mb=disk_write,
                        timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                    )

                    self.metrics.append(metrics)

                    logger.info(
                        f"Performance: {operation_name} - "
                        f"{duration:.2f}s, {memory_used:.2f}MB, {cpu_percent:.1f}% CPU"
                    )

                return result

            return wrapper

        return decorator

    def get_metrics(self) -> list[PerformanceMetrics]:
        """Get all collected metrics."""
        return self.metrics

    def export_metrics(self, output_path: Path) -> None:
        """
        Export metrics to JSON file.

        Args:
            output_path: Path to output file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        data = [asdict(m) for m in self.metrics]

        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Exported {len(self.metrics)} metrics to {output_path}")

    def print_summary(self) -> None:
        """Print a summary of performance metrics."""
        if not self.metrics:
            print("No metrics collected")
            return

        print("\n" + "=" * 80)
        print("PERFORMANCE SUMMARY")
        print("=" * 80)

        for metric in self.metrics:
            print(f"\n{metric.operation}:")
            print(f"  Duration: {metric.duration_seconds:.2f}s")
            print(f"  Memory: {metric.memory_used_mb:.2f}MB")
            print(f"  CPU: {metric.cpu_percent:.1f}%")
            print(f"  Disk Read: {metric.disk_read_mb:.2f}MB")
            print(f"  Disk Write: {metric.disk_write_mb:.2f}MB")


class StreamingFileReader:
    """Memory-efficient streaming file reader for large files."""

    def __init__(self, file_path: Path, chunk_size: int = 8192):
        """
        Initialize streaming reader.

        Args:
            file_path: Path to file
            chunk_size: Size of chunks to read (bytes)
        """
        self.file_path = Path(file_path)
        self.chunk_size = chunk_size

    def read_chunks(self):
        """
        Read file in chunks.

        Yields:
            Bytes chunks of the file
        """
        with open(self.file_path, "rb") as f:
            while True:
                chunk = f.read(self.chunk_size)
                if not chunk:
                    break
                yield chunk

    def copy_to(self, destination: Path, progress_callback: Optional[Callable] = None) -> None:
        """
        Copy file to destination using streaming.

        Args:
            destination: Destination file path
            progress_callback: Optional progress callback
        """
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)

        file_size = self.file_path.stat().st_size
        bytes_copied = 0

        with open(destination, "wb") as dest_file:
            for chunk in self.read_chunks():
                dest_file.write(chunk)
                bytes_copied += len(chunk)

                if progress_callback:
                    progress_callback(bytes_copied, file_size)

        logger.info(f"Streamed {bytes_copied:,} bytes from {self.file_path} to {destination}")


class MemoryOptimizer:
    """Memory optimization utilities."""

    @staticmethod
    def get_memory_usage() -> Dict[str, float]:
        """
        Get current memory usage.

        Returns:
            Dictionary with memory statistics
        """
        process = psutil.Process()
        mem_info = process.memory_info()

        return {
            "rss_mb": mem_info.rss / 1024 / 1024,
            "vms_mb": mem_info.vms / 1024 / 1024,
            "percent": process.memory_percent(),
            "available_mb": psutil.virtual_memory().available / 1024 / 1024,
        }

    @staticmethod
    def check_memory_threshold(threshold_mb: float) -> bool:
        """
        Check if memory usage exceeds threshold.

        Args:
            threshold_mb: Memory threshold in MB

        Returns:
            True if under threshold
        """
        usage = MemoryOptimizer.get_memory_usage()
        return usage["rss_mb"] < threshold_mb

    @staticmethod
    def optimize_for_large_files() -> None:
        """Apply optimizations for large file operations."""
        # Force garbage collection
        import gc

        gc.collect()

        logger.debug("Applied memory optimizations for large files")


# Global performance monitor instance
perf_monitor = PerformanceMonitor()
