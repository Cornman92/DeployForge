"""
Tests for partition management
"""

import pytest
from pathlib import Path
from deployforge.partitions import (
    PartitionManager,
    DiskLayout,
    Partition,
    PartitionType,
    FileSystem,
    create_uefi_bootable_image
)


def test_disk_layout_creation():
    """Test creating a disk layout"""
    layout = DiskLayout()

    assert layout.sector_size == 512
    assert layout.alignment == 1048576
    assert len(layout.partitions) == 0


def test_add_partition_to_layout():
    """Test adding partition to layout"""
    layout = DiskLayout()

    partition = Partition(
        number=1,
        name="Test",
        type_guid=PartitionType.EFI_SYSTEM.value,
        partition_guid="test-guid",
        start_sector=2048,
        end_sector=206848,
        size_bytes=100 * 1024 * 1024
    )

    layout.add_partition(partition)

    assert len(layout.partitions) == 1
    assert layout.get_partition(1) == partition


def test_partition_size_calculations():
    """Test partition size calculations"""
    partition = Partition(
        number=1,
        name="Test",
        type_guid=PartitionType.BASIC_DATA.value,
        partition_guid="test-guid",
        start_sector=0,
        end_sector=0,
        size_bytes=10 * 1024 * 1024 * 1024  # 10GB
    )

    assert partition.size_mb == 10240
    assert partition.size_gb == 10.0


def test_standard_windows_layout_creation(tmp_path):
    """Test creating standard Windows layout"""
    image_path = tmp_path / "test.vhd"

    pm = PartitionManager(image_path)
    layout = pm.create_standard_windows_layout(50, include_recovery=True)

    # Should have 4 partitions: EFI, MSR, Windows, Recovery
    assert len(layout.partitions) == 4

    # Check partition types
    assert layout.partitions[0].type_guid == PartitionType.EFI_SYSTEM.value
    assert layout.partitions[1].type_guid == PartitionType.MICROSOFT_RESERVED.value
    assert layout.partitions[2].type_guid == PartitionType.BASIC_DATA.value
    assert layout.partitions[3].type_guid == PartitionType.WINDOWS_RECOVERY.value


def test_partition_export_import(tmp_path):
    """Test exporting and importing partition layouts"""
    image_path = tmp_path / "test.vhd"
    export_path = tmp_path / "layout.json"

    pm = PartitionManager(image_path)
    pm.create_standard_windows_layout(50)
    pm.export_layout(export_path)

    assert export_path.exists()

    # Import it back
    pm2 = PartitionManager(image_path)
    imported_layout = pm2.import_layout(export_path)

    assert len(imported_layout.partitions) == 4


def test_efi_partition_creation(tmp_path):
    """Test creating EFI system partition"""
    image_path = tmp_path / "test.vhd"

    pm = PartitionManager(image_path)
    pm.create_gpt_table(50)

    efi_part = pm.create_uefi_boot_partition(size_mb=100)

    assert efi_part.type_guid == PartitionType.EFI_SYSTEM.value
    assert efi_part.size_mb == 100
    assert efi_part.filesystem == FileSystem.FAT32.value


def test_msr_partition_creation(tmp_path):
    """Test creating Microsoft Reserved partition"""
    image_path = tmp_path / "test.vhd"

    pm = PartitionManager(image_path)
    pm.create_gpt_table(50)
    pm.create_uefi_boot_partition()

    msr_part = pm.create_msr_partition(size_mb=16)

    assert msr_part.type_guid == PartitionType.MICROSOFT_RESERVED.value
    assert msr_part.size_mb == 16


def test_windows_partition_creation(tmp_path):
    """Test creating Windows partition"""
    image_path = tmp_path / "test.vhd"

    pm = PartitionManager(image_path)
    pm.create_gpt_table(50)
    pm.create_uefi_boot_partition()
    pm.create_msr_partition()

    win_part = pm.create_windows_partition(size_gb=40, label="Windows")

    assert win_part.type_guid == PartitionType.BASIC_DATA.value
    assert win_part.size_gb == 40.0
    assert win_part.label == "Windows"
    assert win_part.filesystem == FileSystem.NTFS.value


def test_recovery_partition_creation(tmp_path):
    """Test creating recovery partition"""
    image_path = tmp_path / "test.vhd"

    pm = PartitionManager(image_path)
    pm.create_gpt_table(50)
    pm.create_uefi_boot_partition()
    pm.create_msr_partition()
    pm.create_windows_partition(40)

    recovery_part = pm.create_recovery_partition(size_mb=500)

    assert recovery_part.type_guid == PartitionType.WINDOWS_RECOVERY.value
    assert recovery_part.size_mb == 500
    assert recovery_part.label == "Recovery"


def test_partition_to_dict():
    """Test partition serialization"""
    partition = Partition(
        number=1,
        name="Test",
        type_guid=PartitionType.BASIC_DATA.value,
        partition_guid="test-guid",
        start_sector=2048,
        end_sector=206848,
        size_bytes=100 * 1024 * 1024,
        filesystem="NTFS",
        label="TestLabel"
    )

    data = partition.to_dict()

    assert data['number'] == 1
    assert data['name'] == "Test"
    assert data['size_mb'] == 100
    assert data['filesystem'] == "NTFS"
    assert data['label'] == "TestLabel"
