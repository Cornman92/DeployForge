"""Image comparison functionality for DeployForge."""

import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Set, Any, Optional
from dataclasses import dataclass, field

from rich.console import Console
from rich.table import Table
from rich.tree import Tree

from deployforge.core.image_manager import ImageManager


logger = logging.getLogger(__name__)
console = Console()


@dataclass
class FileEntry:
    """Represents a file entry in an image."""
    path: str
    size: int
    is_dir: bool
    hash: Optional[str] = None


@dataclass
class ComparisonResult:
    """Result of comparing two images."""
    image1: str
    image2: str
    only_in_image1: List[str] = field(default_factory=list)
    only_in_image2: List[str] = field(default_factory=list)
    different_files: List[Dict[str, Any]] = field(default_factory=list)
    identical_files: List[str] = field(default_factory=list)
    total_files_image1: int = 0
    total_files_image2: int = 0

    def similarity_percentage(self) -> float:
        """Calculate similarity percentage between images."""
        total = self.total_files_image1 + self.total_files_image2
        if total == 0:
            return 100.0

        identical = len(self.identical_files)
        return (identical * 2 / total) * 100


class ImageComparator:
    """Compare two Windows deployment images."""

    def __init__(self, compute_hashes: bool = False):
        """
        Initialize the image comparator.

        Args:
            compute_hashes: Whether to compute file hashes for comparison
        """
        self.compute_hashes = compute_hashes

    def compare(
        self,
        image1_path: Path,
        image2_path: Path,
        path: str = "/"
    ) -> ComparisonResult:
        """
        Compare two images.

        Args:
            image1_path: Path to first image
            image2_path: Path to second image
            path: Path within images to compare

        Returns:
            ComparisonResult object
        """
        logger.info(f"Comparing {image1_path.name} with {image2_path.name}")

        result = ComparisonResult(
            image1=str(image1_path),
            image2=str(image2_path)
        )

        # Get file listings from both images
        with ImageManager(image1_path) as manager1:
            manager1.mount()
            try:
                files1 = self._get_all_files(manager1, path)
            finally:
                manager1.unmount()

        with ImageManager(image2_path) as manager2:
            manager2.mount()
            try:
                files2 = self._get_all_files(manager2, path)
            finally:
                manager2.unmount()

        result.total_files_image1 = len(files1)
        result.total_files_image2 = len(files2)

        # Get file paths
        paths1 = {f.path for f in files1}
        paths2 = {f.path for f in files2}

        # Files only in image1
        result.only_in_image1 = sorted(list(paths1 - paths2))

        # Files only in image2
        result.only_in_image2 = sorted(list(paths2 - paths1))

        # Files in both images
        common_paths = paths1 & paths2

        # Compare common files
        files1_dict = {f.path: f for f in files1}
        files2_dict = {f.path: f for f in files2}

        for file_path in common_paths:
            file1 = files1_dict[file_path]
            file2 = files2_dict[file_path]

            if self._files_different(file1, file2):
                result.different_files.append({
                    'path': file_path,
                    'size1': file1.size,
                    'size2': file2.size,
                    'hash1': file1.hash,
                    'hash2': file2.hash,
                })
            else:
                result.identical_files.append(file_path)

        return result

    def _get_all_files(
        self,
        manager: ImageManager,
        path: str = "/",
        recursive: bool = True
    ) -> List[FileEntry]:
        """
        Get all files from an image recursively.

        Args:
            manager: ImageManager instance
            path: Starting path
            recursive: Whether to recurse into subdirectories

        Returns:
            List of FileEntry objects
        """
        files = []
        mount_point = manager.mount_point

        if not mount_point:
            return files

        try:
            target_path = mount_point / path.lstrip('/')

            if not target_path.exists():
                return files

            for item in target_path.rglob('*') if recursive else target_path.iterdir():
                relative_path = str(item.relative_to(mount_point))

                entry = FileEntry(
                    path=relative_path,
                    size=item.stat().st_size if item.is_file() else 0,
                    is_dir=item.is_dir()
                )

                # Compute hash if requested and it's a file
                if self.compute_hashes and item.is_file():
                    entry.hash = self._compute_hash(item)

                files.append(entry)

        except Exception as e:
            logger.error(f"Error getting files from {path}: {e}")

        return files

    def _compute_hash(self, file_path: Path, algorithm: str = 'sha256') -> str:
        """
        Compute hash of a file.

        Args:
            file_path: Path to file
            algorithm: Hash algorithm to use

        Returns:
            Hex digest of file hash
        """
        hasher = hashlib.new(algorithm)

        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            logger.error(f"Error computing hash for {file_path}: {e}")
            return ""

    def _files_different(self, file1: FileEntry, file2: FileEntry) -> bool:
        """
        Check if two files are different.

        Args:
            file1: First file entry
            file2: Second file entry

        Returns:
            True if files are different
        """
        # Check size first (quick check)
        if file1.size != file2.size:
            return True

        # If hashes are computed, compare them
        if self.compute_hashes and file1.hash and file2.hash:
            return file1.hash != file2.hash

        # If no hash, assume different (conservative)
        return False

    def print_comparison(self, result: ComparisonResult, detailed: bool = False) -> None:
        """
        Print comparison results.

        Args:
            result: ComparisonResult object
            detailed: Whether to show detailed output
        """
        # Summary table
        table = Table(title="Image Comparison Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Image 1", style="green")
        table.add_column("Image 2", style="blue")

        table.add_row("Image Path", Path(result.image1).name, Path(result.image2).name)
        table.add_row("Total Files", str(result.total_files_image1), str(result.total_files_image2))
        table.add_row("Unique Files", str(len(result.only_in_image1)), str(len(result.only_in_image2)))
        table.add_row("Identical Files", str(len(result.identical_files)), str(len(result.identical_files)))
        table.add_row("Different Files", str(len(result.different_files)), str(len(result.different_files)))
        table.add_row("Similarity", f"{result.similarity_percentage():.2f}%", f"{result.similarity_percentage():.2f}%")

        console.print(table)

        if detailed:
            # Files only in image 1
            if result.only_in_image1:
                console.print(f"\n[bold cyan]Files only in {Path(result.image1).name}:[/bold cyan]")
                for file_path in result.only_in_image1[:20]:  # Limit to first 20
                    console.print(f"  • {file_path}")
                if len(result.only_in_image1) > 20:
                    console.print(f"  ... and {len(result.only_in_image1) - 20} more")

            # Files only in image 2
            if result.only_in_image2:
                console.print(f"\n[bold blue]Files only in {Path(result.image2).name}:[/bold blue]")
                for file_path in result.only_in_image2[:20]:
                    console.print(f"  • {file_path}")
                if len(result.only_in_image2) > 20:
                    console.print(f"  ... and {len(result.only_in_image2) - 20} more")

            # Different files
            if result.different_files:
                console.print("\n[bold yellow]Files with differences:[/bold yellow]")
                for diff in result.different_files[:20]:
                    console.print(f"  • {diff['path']}")
                    console.print(f"    Size: {diff['size1']} vs {diff['size2']}")
                if len(result.different_files) > 20:
                    console.print(f"  ... and {len(result.different_files) - 20} more")

    def generate_report(self, result: ComparisonResult, output_path: Path) -> None:
        """
        Generate a detailed comparison report.

        Args:
            result: ComparisonResult object
            output_path: Path to output report file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("IMAGE COMPARISON REPORT\n")
            f.write("=" * 80 + "\n\n")

            f.write(f"Image 1: {result.image1}\n")
            f.write(f"Image 2: {result.image2}\n\n")

            f.write("SUMMARY\n")
            f.write("-" * 80 + "\n")
            f.write(f"Total files in Image 1: {result.total_files_image1}\n")
            f.write(f"Total files in Image 2: {result.total_files_image2}\n")
            f.write(f"Identical files: {len(result.identical_files)}\n")
            f.write(f"Different files: {len(result.different_files)}\n")
            f.write(f"Files only in Image 1: {len(result.only_in_image1)}\n")
            f.write(f"Files only in Image 2: {len(result.only_in_image2)}\n")
            f.write(f"Similarity: {result.similarity_percentage():.2f}%\n\n")

            if result.only_in_image1:
                f.write("FILES ONLY IN IMAGE 1\n")
                f.write("-" * 80 + "\n")
                for file_path in result.only_in_image1:
                    f.write(f"{file_path}\n")
                f.write("\n")

            if result.only_in_image2:
                f.write("FILES ONLY IN IMAGE 2\n")
                f.write("-" * 80 + "\n")
                for file_path in result.only_in_image2:
                    f.write(f"{file_path}\n")
                f.write("\n")

            if result.different_files:
                f.write("DIFFERENT FILES\n")
                f.write("-" * 80 + "\n")
                for diff in result.different_files:
                    f.write(f"{diff['path']}\n")
                    f.write(f"  Size: {diff['size1']} vs {diff['size2']}\n")
                    if diff.get('hash1') and diff.get('hash2'):
                        f.write(f"  Hash1: {diff['hash1']}\n")
                        f.write(f"  Hash2: {diff['hash2']}\n")
                f.write("\n")

        logger.info(f"Comparison report saved to {output_path}")
