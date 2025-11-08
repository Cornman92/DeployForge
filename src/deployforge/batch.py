"""Batch operations for processing multiple images."""

import logging
from pathlib import Path
from typing import List, Dict, Any, Callable, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

from rich.console import Console
from rich.progress import Progress, TaskID
from rich.table import Table

from deployforge.core.image_manager import ImageManager
from deployforge.core.exceptions import DeployForgeError


logger = logging.getLogger(__name__)
console = Console()


class BatchOperation:
    """Handle batch operations on multiple images."""

    def __init__(self, max_workers: int = 4):
        """
        Initialize batch operation handler.

        Args:
            max_workers: Maximum number of parallel workers
        """
        self.max_workers = max_workers
        self.results: List[Dict[str, Any]] = []

    def process_images(
        self,
        image_paths: List[Path],
        operation: Callable,
        description: str = "Processing images",
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Process multiple images in parallel.

        Args:
            image_paths: List of image file paths
            operation: Operation function to apply to each image
            description: Description for progress bar
            **kwargs: Additional arguments to pass to operation

        Returns:
            List of results for each image
        """
        results = []

        with Progress() as progress:
            task = progress.add_task(description, total=len(image_paths))

            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {
                    executor.submit(self._process_single, img, operation, **kwargs): img
                    for img in image_paths
                }

                for future in as_completed(futures):
                    image_path = futures[future]
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        logger.error(f"Failed to process {image_path}: {e}")
                        results.append({
                            'image': str(image_path),
                            'status': 'failed',
                            'error': str(e)
                        })

                    progress.advance(task)

        self.results = results
        return results

    def _process_single(
        self,
        image_path: Path,
        operation: Callable,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Process a single image.

        Args:
            image_path: Path to image file
            operation: Operation to perform
            **kwargs: Additional arguments

        Returns:
            Result dictionary
        """
        try:
            logger.info(f"Processing {image_path}")
            with ImageManager(image_path) as manager:
                result = operation(manager, **kwargs)

            return {
                'image': str(image_path),
                'status': 'success',
                'result': result
            }

        except Exception as e:
            logger.error(f"Error processing {image_path}: {e}")
            raise

    def get_info_batch(self, image_paths: List[Path]) -> List[Dict[str, Any]]:
        """
        Get information for multiple images.

        Args:
            image_paths: List of image paths

        Returns:
            List of image information
        """
        def get_info(manager: ImageManager) -> Dict[str, Any]:
            return manager.get_info()

        return self.process_images(
            image_paths,
            get_info,
            description="Getting image information"
        )

    def list_files_batch(
        self,
        image_paths: List[Path],
        path: str = "/"
    ) -> List[Dict[str, Any]]:
        """
        List files in multiple images.

        Args:
            image_paths: List of image paths
            path: Path within images to list

        Returns:
            List of file listings
        """
        def list_files(manager: ImageManager, path: str) -> List:
            manager.mount()
            try:
                return manager.list_files(path)
            finally:
                manager.unmount()

        return self.process_images(
            image_paths,
            list_files,
            description="Listing files",
            path=path
        )

    def add_file_batch(
        self,
        image_paths: List[Path],
        source: Path,
        destination: str
    ) -> List[Dict[str, Any]]:
        """
        Add a file to multiple images.

        Args:
            image_paths: List of image paths
            source: Source file to add
            destination: Destination path in images

        Returns:
            List of operation results
        """
        def add_file(manager: ImageManager, source: Path, dest: str) -> bool:
            manager.mount()
            try:
                manager.add_file(source, dest)
                manager.unmount(save_changes=True)
                return True
            except Exception:
                manager.unmount(save_changes=False)
                raise

        return self.process_images(
            image_paths,
            add_file,
            description=f"Adding {source.name}",
            source=source,
            dest=destination
        )

    def remove_file_batch(
        self,
        image_paths: List[Path],
        file_path: str
    ) -> List[Dict[str, Any]]:
        """
        Remove a file from multiple images.

        Args:
            image_paths: List of image paths
            file_path: Path to file to remove

        Returns:
            List of operation results
        """
        def remove_file(manager: ImageManager, path: str) -> bool:
            manager.mount()
            try:
                manager.remove_file(path)
                manager.unmount(save_changes=True)
                return True
            except Exception:
                manager.unmount(save_changes=False)
                raise

        return self.process_images(
            image_paths,
            remove_file,
            description=f"Removing {file_path}",
            path=file_path
        )

    def extract_file_batch(
        self,
        image_paths: List[Path],
        source: str,
        destination_dir: Path
    ) -> List[Dict[str, Any]]:
        """
        Extract a file from multiple images.

        Args:
            image_paths: List of image paths
            source: Path within images to extract
            destination_dir: Destination directory

        Returns:
            List of operation results
        """
        destination_dir = Path(destination_dir)
        destination_dir.mkdir(parents=True, exist_ok=True)

        def extract_file(
            manager: ImageManager,
            src: str,
            dest_dir: Path
        ) -> Path:
            manager.mount()
            try:
                # Create unique destination based on image name
                image_name = Path(manager.image_path).stem
                dest_file = dest_dir / f"{image_name}_{Path(src).name}"
                manager.extract_file(src, dest_file)
                return dest_file
            finally:
                manager.unmount()

        return self.process_images(
            image_paths,
            extract_file,
            description=f"Extracting {source}",
            src=source,
            dest_dir=destination_dir
        )

    def export_results(self, output_path: Path, format: str = 'json') -> None:
        """
        Export batch operation results.

        Args:
            output_path: Path to export file
            format: Export format ('json', 'csv', 'text')
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format == 'json':
            with open(output_path, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)

        elif format == 'text':
            with open(output_path, 'w') as f:
                for result in self.results:
                    f.write(f"Image: {result.get('image')}\n")
                    f.write(f"Status: {result.get('status')}\n")
                    if 'error' in result:
                        f.write(f"Error: {result.get('error')}\n")
                    f.write("-" * 80 + "\n")

        logger.info(f"Exported results to {output_path}")

    def print_summary(self) -> None:
        """Print a summary of batch operation results."""
        if not self.results:
            console.print("[yellow]No results to display[/yellow]")
            return

        successful = sum(1 for r in self.results if r.get('status') == 'success')
        failed = sum(1 for r in self.results if r.get('status') == 'failed')

        table = Table(title="Batch Operation Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Total Images", str(len(self.results)))
        table.add_row("Successful", str(successful))
        table.add_row("Failed", str(failed))

        console.print(table)

        if failed > 0:
            console.print("\n[bold red]Failed Images:[/bold red]")
            for result in self.results:
                if result.get('status') == 'failed':
                    console.print(f"  • {result.get('image')}: {result.get('error')}")
