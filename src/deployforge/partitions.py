"""
UEFI/GPT Partition Management for DeployForge

This module provides functionality for managing UEFI/GPT partitions on Windows images.
Supports creating, modifying, and configuring GPT partition tables and EFI system partitions.

Features:
- GPT partition table creation and modification
- EFI System Partition (ESP) management
- Partition resizing and alignment
- UEFI boot configuration
- Multi-boot setup support

Platform Support:
- Windows: diskpart, bcdedit, bcdboot
- Linux: parted, sgdisk, efibootmgr
- macOS: diskutil, gdisk
"""

import json
import logging
import platform
import struct
import subprocess
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class PartitionType(Enum):
    """GPT Partition Type GUIDs"""

    # Microsoft partition types
    EFI_SYSTEM = "C12A7328-F81F-11D2-BA4B-00A0C93EC93B"
    MICROSOFT_RESERVED = "E3C9E316-0B5C-4DB8-817D-F92DF00215AE"
    BASIC_DATA = "EBD0A0A2-B9E5-4433-87C0-68B6B72699C7"
    WINDOWS_RECOVERY = "DE94BBA4-06D1-4D40-A16A-BFD50179D6AC"

    # Linux partition types
    LINUX_FILESYSTEM = "0FC63DAF-8483-4772-8E79-3D69D8477DE4"
    LINUX_SWAP = "0657FD6D-A4AB-43C4-84E5-0933C84B4F4F"
    LINUX_LVM = "E6D6D379-F507-44C2-A23C-238F2A3DF928"

    # Other
    BIOS_BOOT = "21686148-6449-6E6F-744E-656564454649"


class FileSystem(Enum):
    """Supported filesystems"""

    FAT32 = "FAT32"
    NTFS = "NTFS"
    REFS = "ReFS"
    EXT4 = "ext4"
    BTRFS = "btrfs"
    EXFAT = "exFAT"


@dataclass
class Partition:
    """Represents a GPT partition"""

    number: int
    name: str
    type_guid: str
    partition_guid: str
    start_sector: int
    end_sector: int
    size_bytes: int
    filesystem: Optional[str] = None
    label: Optional[str] = None
    attributes: int = 0

    @property
    def size_mb(self) -> int:
        """Get size in megabytes"""
        return self.size_bytes // (1024 * 1024)

    @property
    def size_gb(self) -> float:
        """Get size in gigabytes"""
        return self.size_bytes / (1024 * 1024 * 1024)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "number": self.number,
            "name": self.name,
            "type": self.type_guid,
            "guid": self.partition_guid,
            "start": self.start_sector,
            "end": self.end_sector,
            "size_bytes": self.size_bytes,
            "size_mb": self.size_mb,
            "size_gb": round(self.size_gb, 2),
            "filesystem": self.filesystem,
            "label": self.label,
            "attributes": self.attributes,
        }


@dataclass
class DiskLayout:
    """Represents a complete disk layout"""

    sector_size: int = 512
    alignment: int = 1048576  # 1MB alignment
    partitions: List[Partition] = field(default_factory=list)
    disk_guid: Optional[str] = None

    def add_partition(self, partition: Partition):
        """Add a partition to the layout"""
        self.partitions.append(partition)

    def get_partition(self, number: int) -> Optional[Partition]:
        """Get partition by number"""
        for part in self.partitions:
            if part.number == number:
                return part
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "disk_guid": self.disk_guid,
            "sector_size": self.sector_size,
            "alignment": self.alignment,
            "partitions": [p.to_dict() for p in self.partitions],
        }


class PartitionManager:
    """Manages GPT partitions on disk images"""

    def __init__(self, image_path: Path):
        """
        Initialize partition manager

        Args:
            image_path: Path to disk image (VHD, VHDX, or raw)
        """
        self.image_path = image_path
        self.platform = platform.system()
        self.layout: Optional[DiskLayout] = None

    def read_partition_table(self) -> DiskLayout:
        """
        Read GPT partition table from image

        Returns:
            DiskLayout object with current partitions
        """
        logger.info(f"Reading partition table from {self.image_path}")

        if self.platform == "Windows":
            return self._read_partitions_windows()
        elif self.platform == "Linux":
            return self._read_partitions_linux()
        else:
            return self._read_partitions_macos()

    def _read_partitions_windows(self) -> DiskLayout:
        """Read partitions using diskpart on Windows"""
        layout = DiskLayout()

        # Create diskpart script
        script = f"""select vdisk file="{self.image_path}"
attach vdisk readonly
list partition
detach vdisk
"""

        try:
            result = subprocess.run(
                ["diskpart"], input=script, capture_output=True, text=True, timeout=30
            )

            # Parse diskpart output
            lines = result.stdout.split("\n")
            partition_num = 1

            for line in lines:
                if "Partition" in line and line.strip().startswith("Partition"):
                    parts = line.split()
                    if len(parts) >= 4:
                        try:
                            size_str = parts[3]
                            size_mb = int(size_str.replace("MB", "").replace("GB", ""))
                            if "GB" in size_str:
                                size_mb *= 1024

                            partition = Partition(
                                number=partition_num,
                                name=f"Partition {partition_num}",
                                type_guid=PartitionType.BASIC_DATA.value,
                                partition_guid=str(uuid.uuid4()),
                                start_sector=0,  # Would need detailed parsing
                                end_sector=0,
                                size_bytes=size_mb * 1024 * 1024,
                            )
                            layout.add_partition(partition)
                            partition_num += 1
                        except (ValueError, IndexError):
                            continue

        except Exception as e:
            logger.error(f"Failed to read partitions: {e}")

        self.layout = layout
        return layout

    def _read_partitions_linux(self) -> DiskLayout:
        """Read partitions using parted on Linux"""
        layout = DiskLayout()

        try:
            # Use parted to list partitions
            result = subprocess.run(
                ["parted", "-s", "-m", str(self.image_path), "unit", "B", "print"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            lines = result.stdout.strip().split("\n")
            for line in lines[2:]:  # Skip header lines
                if line.strip():
                    fields = line.split(":")
                    if len(fields) >= 6:
                        try:
                            num = int(fields[0])
                            start = int(fields[1].rstrip("B"))
                            end = int(fields[2].rstrip("B"))
                            size = int(fields[3].rstrip("B"))
                            fs = fields[4] if fields[4] else None
                            name = fields[5] if len(fields) > 5 else f"Partition {num}"

                            partition = Partition(
                                number=num,
                                name=name,
                                type_guid=PartitionType.BASIC_DATA.value,
                                partition_guid=str(uuid.uuid4()),
                                start_sector=start // 512,
                                end_sector=end // 512,
                                size_bytes=size,
                                filesystem=fs,
                            )
                            layout.add_partition(partition)
                        except (ValueError, IndexError) as e:
                            logger.debug(f"Skipping line: {line}, error: {e}")
                            continue

        except FileNotFoundError:
            logger.warning("parted not found, partition reading limited")
        except Exception as e:
            logger.error(f"Failed to read partitions: {e}")

        self.layout = layout
        return layout

    def _read_partitions_macos(self) -> DiskLayout:
        """Read partitions using diskutil on macOS"""
        layout = DiskLayout()

        # macOS implementation would use diskutil
        logger.warning("macOS partition reading not fully implemented")

        self.layout = layout
        return layout

    def create_gpt_table(self, disk_size_gb: int) -> DiskLayout:
        """
        Create a new GPT partition table

        Args:
            disk_size_gb: Size of disk in GB

        Returns:
            New DiskLayout
        """
        logger.info(f"Creating GPT table for {disk_size_gb}GB disk")

        layout = DiskLayout()
        layout.disk_guid = str(uuid.uuid4())

        self.layout = layout
        return layout

    def create_uefi_boot_partition(self, size_mb: int = 100, label: str = "System") -> Partition:
        """
        Create EFI System Partition (ESP)

        Args:
            size_mb: Size in MB (default 100MB)
            label: Partition label

        Returns:
            Created Partition object
        """
        if not self.layout:
            self.layout = DiskLayout()

        # Calculate partition boundaries
        start_sector = 2048  # Standard 1MB alignment
        size_sectors = (size_mb * 1024 * 1024) // self.layout.sector_size
        end_sector = start_sector + size_sectors - 1

        partition = Partition(
            number=len(self.layout.partitions) + 1,
            name=label,
            type_guid=PartitionType.EFI_SYSTEM.value,
            partition_guid=str(uuid.uuid4()),
            start_sector=start_sector,
            end_sector=end_sector,
            size_bytes=size_mb * 1024 * 1024,
            filesystem=FileSystem.FAT32.value,
            label=label,
            attributes=0x0000000000000001,  # System partition
        )

        self.layout.add_partition(partition)
        logger.info(f"Created EFI System Partition: {size_mb}MB")

        return partition

    def create_msr_partition(self, size_mb: int = 16) -> Partition:
        """
        Create Microsoft Reserved Partition (MSR)

        Args:
            size_mb: Size in MB (default 16MB)

        Returns:
            Created Partition object
        """
        if not self.layout:
            raise ValueError("No partition layout initialized")

        # Get last partition end
        if self.layout.partitions:
            last_part = self.layout.partitions[-1]
            start_sector = last_part.end_sector + 1
        else:
            start_sector = 2048

        # Align to 1MB
        alignment_sectors = self.layout.alignment // self.layout.sector_size
        start_sector = (
            (start_sector + alignment_sectors - 1) // alignment_sectors
        ) * alignment_sectors

        size_sectors = (size_mb * 1024 * 1024) // self.layout.sector_size
        end_sector = start_sector + size_sectors - 1

        partition = Partition(
            number=len(self.layout.partitions) + 1,
            name="Microsoft reserved partition",
            type_guid=PartitionType.MICROSOFT_RESERVED.value,
            partition_guid=str(uuid.uuid4()),
            start_sector=start_sector,
            end_sector=end_sector,
            size_bytes=size_mb * 1024 * 1024,
            attributes=0x8000000000000001,  # Required partition
        )

        self.layout.add_partition(partition)
        logger.info(f"Created MSR partition: {size_mb}MB")

        return partition

    def create_windows_partition(
        self, size_gb: int, label: str = "Windows", filesystem: FileSystem = FileSystem.NTFS
    ) -> Partition:
        """
        Create Windows system partition

        Args:
            size_gb: Size in GB
            label: Partition label
            filesystem: Filesystem type

        Returns:
            Created Partition object
        """
        if not self.layout:
            raise ValueError("No partition layout initialized")

        # Get last partition end
        if self.layout.partitions:
            last_part = self.layout.partitions[-1]
            start_sector = last_part.end_sector + 1
        else:
            start_sector = 2048

        # Align to 1MB
        alignment_sectors = self.layout.alignment // self.layout.sector_size
        start_sector = (
            (start_sector + alignment_sectors - 1) // alignment_sectors
        ) * alignment_sectors

        size_sectors = (size_gb * 1024 * 1024 * 1024) // self.layout.sector_size
        end_sector = start_sector + size_sectors - 1

        partition = Partition(
            number=len(self.layout.partitions) + 1,
            name=label,
            type_guid=PartitionType.BASIC_DATA.value,
            partition_guid=str(uuid.uuid4()),
            start_sector=start_sector,
            end_sector=end_sector,
            size_bytes=size_gb * 1024 * 1024 * 1024,
            filesystem=filesystem.value,
            label=label,
        )

        self.layout.add_partition(partition)
        logger.info(f"Created Windows partition: {size_gb}GB, {filesystem.value}")

        return partition

    def create_recovery_partition(self, size_mb: int = 500, label: str = "Recovery") -> Partition:
        """
        Create Windows Recovery Environment partition

        Args:
            size_mb: Size in MB (default 500MB)
            label: Partition label

        Returns:
            Created Partition object
        """
        if not self.layout:
            raise ValueError("No partition layout initialized")

        # Get last partition end
        if self.layout.partitions:
            last_part = self.layout.partitions[-1]
            start_sector = last_part.end_sector + 1
        else:
            start_sector = 2048

        # Align to 1MB
        alignment_sectors = self.layout.alignment // self.layout.sector_size
        start_sector = (
            (start_sector + alignment_sectors - 1) // alignment_sectors
        ) * alignment_sectors

        size_sectors = (size_mb * 1024 * 1024) // self.layout.sector_size
        end_sector = start_sector + size_sectors - 1

        partition = Partition(
            number=len(self.layout.partitions) + 1,
            name=label,
            type_guid=PartitionType.WINDOWS_RECOVERY.value,
            partition_guid=str(uuid.uuid4()),
            start_sector=start_sector,
            end_sector=end_sector,
            size_bytes=size_mb * 1024 * 1024,
            filesystem=FileSystem.NTFS.value,
            label=label,
            attributes=0x8000000000000001,  # Required partition, hidden
        )

        self.layout.add_partition(partition)
        logger.info(f"Created Recovery partition: {size_mb}MB")

        return partition

    def apply_layout(self, target_disk: Optional[str] = None):
        """
        Apply partition layout to disk

        Args:
            target_disk: Target disk (if None, applies to image_path)
        """
        if not self.layout:
            raise ValueError("No partition layout to apply")

        target = target_disk or str(self.image_path)
        logger.info(f"Applying partition layout to {target}")

        if self.platform == "Windows":
            self._apply_layout_windows(target)
        elif self.platform == "Linux":
            self._apply_layout_linux(target)
        else:
            self._apply_layout_macos(target)

    def _apply_layout_windows(self, target: str):
        """Apply layout using diskpart on Windows"""
        # Build diskpart script
        script_lines = [
            f'select vdisk file="{target}"',
            "attach vdisk",
            "convert gpt",
        ]

        for part in self.layout.partitions:
            if part.type_guid == PartitionType.EFI_SYSTEM.value:
                script_lines.extend(
                    [
                        f"create partition efi size={part.size_mb}",
                        'format quick fs=fat32 label="System"',
                    ]
                )
            elif part.type_guid == PartitionType.MICROSOFT_RESERVED.value:
                script_lines.append(f"create partition msr size={part.size_mb}")
            elif part.type_guid == PartitionType.WINDOWS_RECOVERY.value:
                script_lines.extend(
                    [
                        f"create partition primary size={part.size_mb}",
                        f'format quick fs=ntfs label="{part.label}"',
                        'set id="de94bba4-06d1-4d40-a16a-bfd50179d6ac"',
                        "gpt attributes=0x8000000000000001",
                    ]
                )
            else:
                script_lines.extend(
                    [
                        f"create partition primary size={part.size_mb}",
                        f'format quick fs=ntfs label="{part.label or part.name}"',
                    ]
                )

        script_lines.append("detach vdisk")
        script = "\n".join(script_lines)

        logger.debug(f"Diskpart script:\n{script}")

        try:
            result = subprocess.run(
                ["diskpart"], input=script, capture_output=True, text=True, timeout=120
            )

            if result.returncode == 0:
                logger.info("Partition layout applied successfully")
            else:
                logger.error(f"Diskpart failed: {result.stderr}")
                raise RuntimeError(f"Failed to apply partition layout: {result.stderr}")

        except Exception as e:
            logger.error(f"Failed to apply layout: {e}")
            raise

    def _apply_layout_linux(self, target: str):
        """Apply layout using parted/sgdisk on Linux"""
        try:
            # Create GPT table
            subprocess.run(["parted", "-s", target, "mklabel", "gpt"], check=True, timeout=30)

            # Create partitions
            for part in self.layout.partitions:
                start_mb = (part.start_sector * self.layout.sector_size) // (1024 * 1024)
                end_mb = (part.end_sector * self.layout.sector_size) // (1024 * 1024)

                # Determine partition type name for parted
                if part.type_guid == PartitionType.EFI_SYSTEM.value:
                    subprocess.run(
                        [
                            "parted",
                            "-s",
                            target,
                            "mkpart",
                            part.name,
                            "fat32",
                            f"{start_mb}MB",
                            f"{end_mb}MB",
                        ],
                        check=True,
                        timeout=30,
                    )
                    subprocess.run(
                        ["parted", "-s", target, "set", str(part.number), "esp", "on"],
                        check=True,
                        timeout=30,
                    )
                else:
                    fs_type = "ext4" if "linux" in part.name.lower() else "ntfs"
                    subprocess.run(
                        [
                            "parted",
                            "-s",
                            target,
                            "mkpart",
                            part.name,
                            fs_type,
                            f"{start_mb}MB",
                            f"{end_mb}MB",
                        ],
                        check=True,
                        timeout=30,
                    )

            logger.info("Partition layout applied successfully (Linux)")

        except Exception as e:
            logger.error(f"Failed to apply layout on Linux: {e}")
            raise

    def _apply_layout_macos(self, target: str):
        """Apply layout using diskutil on macOS"""
        logger.warning("macOS partition layout application not fully implemented")
        raise NotImplementedError("macOS partition management requires diskutil implementation")

    def export_layout(self, output_path: Path):
        """
        Export partition layout to JSON

        Args:
            output_path: Output file path
        """
        if not self.layout:
            raise ValueError("No partition layout to export")

        layout_dict = self.layout.to_dict()

        with open(output_path, "w") as f:
            json.dump(layout_dict, f, indent=2)

        logger.info(f"Exported partition layout to {output_path}")

    def import_layout(self, layout_path: Path) -> DiskLayout:
        """
        Import partition layout from JSON

        Args:
            layout_path: Path to layout JSON file

        Returns:
            Imported DiskLayout
        """
        with open(layout_path, "r") as f:
            layout_dict = json.load(f)

        layout = DiskLayout(
            sector_size=layout_dict.get("sector_size", 512),
            alignment=layout_dict.get("alignment", 1048576),
            disk_guid=layout_dict.get("disk_guid"),
        )

        for part_dict in layout_dict.get("partitions", []):
            partition = Partition(
                number=part_dict["number"],
                name=part_dict["name"],
                type_guid=part_dict["type"],
                partition_guid=part_dict["guid"],
                start_sector=part_dict["start"],
                end_sector=part_dict["end"],
                size_bytes=part_dict["size_bytes"],
                filesystem=part_dict.get("filesystem"),
                label=part_dict.get("label"),
                attributes=part_dict.get("attributes", 0),
            )
            layout.add_partition(partition)

        self.layout = layout
        logger.info(f"Imported partition layout from {layout_path}")

        return layout

    def create_standard_windows_layout(
        self, disk_size_gb: int, include_recovery: bool = True
    ) -> DiskLayout:
        """
        Create standard Windows UEFI partition layout

        Creates:
        - 100MB EFI System Partition (FAT32)
        - 16MB Microsoft Reserved Partition
        - Remaining space for Windows (NTFS)
        - Optional 500MB Recovery partition

        Args:
            disk_size_gb: Total disk size in GB
            include_recovery: Include recovery partition

        Returns:
            Created DiskLayout
        """
        logger.info(f"Creating standard Windows layout for {disk_size_gb}GB disk")

        # Create empty layout
        self.create_gpt_table(disk_size_gb)

        # EFI System Partition (100MB)
        self.create_uefi_boot_partition(size_mb=100)

        # Microsoft Reserved Partition (16MB)
        self.create_msr_partition(size_mb=16)

        # Windows partition (remaining space minus recovery if needed)
        windows_size_gb = disk_size_gb - 1  # Reserve 1GB for overhead
        if include_recovery:
            windows_size_gb -= 1  # Reserve for recovery partition

        self.create_windows_partition(size_gb=int(windows_size_gb), label="Windows")

        # Recovery partition (500MB)
        if include_recovery:
            self.create_recovery_partition(size_mb=500)

        logger.info(
            f"Created standard Windows layout with {len(self.layout.partitions)} partitions"
        )

        return self.layout


def create_uefi_bootable_image(
    image_path: Path, disk_size_gb: int = 50, include_recovery: bool = True
) -> PartitionManager:
    """
    Create a UEFI bootable disk image with standard Windows partitioning

    Args:
        image_path: Path for the new disk image
        disk_size_gb: Size of disk in GB
        include_recovery: Include recovery partition

    Returns:
        PartitionManager with applied layout
    """
    pm = PartitionManager(image_path)
    pm.create_standard_windows_layout(disk_size_gb, include_recovery)

    return pm
