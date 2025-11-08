#!/usr/bin/env python3
"""
Basic usage examples for DeployForge.

This script demonstrates the core functionality of DeployForge.
"""

from pathlib import Path
from deployforge import ImageManager

def example_1_get_info():
    """Get information about an image."""
    print("=" * 60)
    print("Example 1: Get Image Information")
    print("=" * 60)

    image_path = Path("path/to/your/image.wim")

    if not image_path.exists():
        print(f"Image not found: {image_path}")
        print("Please update the path to point to a real image file")
        return

    with ImageManager(image_path) as manager:
        info = manager.get_info()

        print(f"\nImage: {info['path']}")
        print(f"Format: {info['format']}")
        print(f"Size: {info['size']:,} bytes")
        print(f"Mounted: {info['mounted']}")


def example_2_list_files():
    """List files in an image."""
    print("\n" + "=" * 60)
    print("Example 2: List Files in Image")
    print("=" * 60)

    image_path = Path("path/to/your/image.iso")

    if not image_path.exists():
        print(f"Image not found: {image_path}")
        return

    with ImageManager(image_path) as manager:
        manager.mount()

        try:
            files = manager.list_files("/")

            print(f"\nFiles in root directory:")
            for i, file_info in enumerate(files[:10], 1):  # Show first 10
                file_type = "DIR" if file_info['is_dir'] else "FILE"
                size = f"{file_info['size']:,}" if not file_info['is_dir'] else "-"
                print(f"  {i}. [{file_type}] {file_info['name']} ({size} bytes)")

            if len(files) > 10:
                print(f"  ... and {len(files) - 10} more files/directories")

        finally:
            manager.unmount()


def example_3_add_file():
    """Add a file to an image."""
    print("\n" + "=" * 60)
    print("Example 3: Add File to Image")
    print("=" * 60)

    image_path = Path("path/to/your/image.wim")
    source_file = Path("path/to/file/to/add.txt")
    destination = "/CustomFiles/added_file.txt"

    if not image_path.exists() or not source_file.exists():
        print("Please update paths to real files")
        return

    with ImageManager(image_path) as manager:
        manager.mount()

        try:
            print(f"\nAdding {source_file.name} to image...")
            manager.add_file(source_file, destination)
            print(f"Successfully added to {destination}")

            # Save changes
            manager.unmount(save_changes=True)
            print("Changes saved!")

        except Exception as e:
            print(f"Error: {e}")
            manager.unmount(save_changes=False)


def example_4_extract_file():
    """Extract a file from an image."""
    print("\n" + "=" * 60)
    print("Example 4: Extract File from Image")
    print("=" * 60)

    image_path = Path("path/to/your/image.wim")
    source_path = "/Windows/System32/config/SOFTWARE"
    dest_file = Path("./extracted_SOFTWARE.hive")

    if not image_path.exists():
        print("Please update path to real image")
        return

    with ImageManager(image_path) as manager:
        manager.mount()

        try:
            print(f"\nExtracting {source_path}...")
            manager.extract_file(source_path, dest_file)
            print(f"Successfully extracted to {dest_file}")

        finally:
            manager.unmount()


def example_5_batch_operations():
    """Perform batch operations on multiple images."""
    print("\n" + "=" * 60)
    print("Example 5: Batch Operations")
    print("=" * 60)

    from deployforge.batch import BatchOperation

    image_paths = [
        Path("path/to/image1.wim"),
        Path("path/to/image2.wim"),
        Path("path/to/image3.wim"),
    ]

    # Filter to only existing images
    existing_images = [p for p in image_paths if p.exists()]

    if not existing_images:
        print("No images found. Please update paths.")
        return

    batch_op = BatchOperation(max_workers=4)

    print(f"\nGetting information for {len(existing_images)} images...")
    results = batch_op.get_info_batch(existing_images)

    batch_op.print_summary()


def example_6_compare_images():
    """Compare two images."""
    print("\n" + "=" * 60)
    print("Example 6: Compare Images")
    print("=" * 60)

    from deployforge.comparison import ImageComparator

    image1 = Path("path/to/image1.wim")
    image2 = Path("path/to/image2.wim")

    if not image1.exists() or not image2.exists():
        print("Please update paths to real images")
        return

    comparator = ImageComparator(compute_hashes=False)

    print(f"\nComparing {image1.name} with {image2.name}...")
    result = comparator.compare(image1, image2)

    comparator.print_comparison(result, detailed=True)


def example_7_registry_editing():
    """Edit registry in an offline image."""
    print("\n" + "=" * 60)
    print("Example 7: Registry Editing")
    print("=" * 60)

    from deployforge.registry import RegistryEditor
    from deployforge import ImageManager

    image_path = Path("path/to/your/image.wim")

    if not image_path.exists():
        print("Please update path to real image")
        return

    with ImageManager(image_path) as manager:
        mount_point = manager.mount()

        try:
            with RegistryEditor(mount_point) as reg_editor:
                print("\nApplying registry tweaks...")

                # Disable telemetry
                reg_editor.set_value(
                    'HKLM\\SOFTWARE',
                    'Policies\\Microsoft\\Windows\\DataCollection',
                    'AllowTelemetry',
                    '0',
                    'REG_DWORD'
                )

                print("Telemetry disabled")

            manager.unmount(save_changes=True)
            print("Registry changes saved!")

        except Exception as e:
            print(f"Error: {e}")
            manager.unmount(save_changes=False)


if __name__ == "__main__":
    print("DeployForge Examples")
    print("=" * 60)
    print("\nNote: Update file paths before running examples")
    print()

    # Run examples (comment out ones you don't want to run)
    example_1_get_info()
    # example_2_list_files()
    # example_3_add_file()
    # example_4_extract_file()
    # example_5_batch_operations()
    # example_6_compare_images()
    # example_7_registry_editing()

    print("\n" + "=" * 60)
    print("Examples completed!")
