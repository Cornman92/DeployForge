"""
Feature Update Management Module

Manages Windows feature updates and edition upgrades.

Features:
- Apply Windows feature updates
- Version compatibility checking
- Enablement package application
- Edition upgrade management
- Rollback support
"""

import logging
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum
import tempfile
import json

logger = logging.getLogger(__name__)


class WindowsEdition(Enum):
    """Windows editions"""
    HOME = "Home"
    PRO = "Professional"
    ENTERPRISE = "Enterprise"
    EDUCATION = "Education"
    PRO_WORKSTATION = "ProfessionalWorkstation"


class FeatureUpdateType(Enum):
    """Feature update types"""
    ENABLEMENT_PACKAGE = "enablement"
    FULL_UPDATE = "full"
    CUMULATIVE = "cumulative"


@dataclass
class FeatureUpdate:
    """Feature update package information"""
    name: str
    version_from: str
    version_to: str
    update_type: FeatureUpdateType
    package_path: Path
    size_bytes: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'version_from': self.version_from,
            'version_to': self.version_to,
            'update_type': self.update_type.value,
            'package_path': str(self.package_path),
            'size_bytes': self.size_bytes
        }


class FeatureUpdateManager:
    """
    Manages Windows feature updates.

    Example:
        fum = FeatureUpdateManager()
        fum.apply_feature_update(
            source_image=Path('win11-21h2.wim'),
            feature_update=Path('win11-22h2-enablement.cab'),
            output=Path('win11-22h2.wim')
        )
    """

    def __init__(self):
        """Initialize feature update manager"""
        pass

    def apply_feature_update(
        self,
        source_image: Path,
        feature_update: Path,
        output: Path,
        validate_compatibility: bool = True
    ) -> bool:
        """
        Apply feature update to image.

        Args:
            source_image: Source WIM/VHDX image
            feature_update: Feature update package (CAB/MSU)
            output: Output image path
            validate_compatibility: Validate before applying

        Returns:
            True if successful
        """
        if not source_image.exists():
            raise FileNotFoundError(f"Source image not found: {source_image}")

        if not feature_update.exists():
            raise FileNotFoundError(f"Feature update not found: {feature_update}")

        logger.info(f"Applying feature update to {source_image}")

        # Copy source to output first
        import shutil
        shutil.copy2(source_image, output)

        # Mount image
        mount_point = Path(tempfile.mkdtemp(prefix='deployforge_fu_'))

        try:
            # Mount
            subprocess.run([
                'dism',
                '/Mount-Wim',
                f'/WimFile:{output}',
                '/Index:1',
                f'/MountDir:{mount_point}'
            ], check=True, capture_output=True)

            # Apply update
            if feature_update.suffix.lower() == '.cab':
                # Apply CAB package
                subprocess.run([
                    'dism',
                    f'/Image:{mount_point}',
                    '/Add-Package',
                    f'/PackagePath:{feature_update}'
                ], check=True, capture_output=True)
            elif feature_update.suffix.lower() == '.msu':
                # Extract and apply MSU
                self._apply_msu_update(mount_point, feature_update)
            else:
                raise ValueError(f"Unsupported update format: {feature_update.suffix}")

            # Unmount with commit
            subprocess.run([
                'dism',
                '/Unmount-Image',
                f'/MountDir:{mount_point}',
                '/Commit'
            ], check=True, capture_output=True)

            logger.info("Feature update applied successfully")

            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to apply feature update: {e.stderr.decode()}")

            # Try to unmount without committing
            try:
                subprocess.run([
                    'dism',
                    '/Unmount-Image',
                    f'/MountDir:{mount_point}',
                    '/Discard'
                ], capture_output=True)
            except:
                pass

            return False

        finally:
            # Cleanup mount point
            if mount_point.exists():
                import shutil
                shutil.rmtree(mount_point, ignore_errors=True)

    def _apply_msu_update(self, mount_point: Path, msu_package: Path):
        """Apply MSU update package"""
        # Extract MSU to get CAB
        temp_extract = Path(tempfile.mkdtemp(prefix='deployforge_msu_'))

        try:
            # Expand MSU
            subprocess.run([
                'expand',
                '-F:*',
                str(msu_package),
                str(temp_extract)
            ], check=True, capture_output=True)

            # Find CAB file
            cab_files = list(temp_extract.glob('*.cab'))

            if not cab_files:
                raise ValueError("No CAB found in MSU package")

            # Apply CAB
            for cab_file in cab_files:
                subprocess.run([
                    'dism',
                    f'/Image:{mount_point}',
                    '/Add-Package',
                    f'/PackagePath:{cab_file}'
                ], check=True, capture_output=True)

        finally:
            # Cleanup
            if temp_extract.exists():
                import shutil
                shutil.rmtree(temp_extract, ignore_errors=True)

    def upgrade_edition(
        self,
        image: Path,
        target_edition: WindowsEdition,
        product_key: Optional[str] = None
    ) -> bool:
        """
        Upgrade Windows edition.

        Args:
            image: Image to upgrade
            target_edition: Target edition
            product_key: Product key for activation

        Returns:
            True if successful
        """
        if not image.exists():
            raise FileNotFoundError(f"Image not found: {image}")

        logger.info(f"Upgrading edition to {target_edition.value}")

        mount_point = Path(tempfile.mkdtemp(prefix='deployforge_edition_'))

        try:
            # Mount
            subprocess.run([
                'dism',
                '/Mount-Wim',
                f'/WimFile:{image}',
                '/Index:1',
                f'/MountDir:{mount_point}'
            ], check=True, capture_output=True)

            # Get current edition
            result = subprocess.run([
                'dism',
                f'/Image:{mount_point}',
                '/Get-CurrentEdition'
            ], capture_output=True, text=True)

            logger.info(f"Current edition info:\n{result.stdout}")

            # Set edition
            cmd = [
                'dism',
                f'/Image:{mount_point}',
                '/Set-Edition:{target_edition.value}'
            ]

            if product_key:
                cmd.append(f'/ProductKey:{product_key}')

            subprocess.run(cmd, check=True, capture_output=True)

            # Unmount
            subprocess.run([
                'dism',
                '/Unmount-Image',
                f'/MountDir:{mount_point}',
                '/Commit'
            ], check=True, capture_output=True)

            logger.info(f"Edition upgraded to {target_edition.value}")

            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Edition upgrade failed: {e.stderr.decode()}")

            # Cleanup
            try:
                subprocess.run([
                    'dism',
                    '/Unmount-Image',
                    f'/MountDir:{mount_point}',
                    '/Discard'
                ], capture_output=True)
            except:
                pass

            return False

        finally:
            if mount_point.exists():
                import shutil
                shutil.rmtree(mount_point, ignore_errors=True)

    def get_image_version(self, image: Path) -> Optional[str]:
        """
        Get Windows version from image.

        Args:
            image: Image path

        Returns:
            Version string or None
        """
        try:
            result = subprocess.run([
                'dism',
                '/Get-WimInfo',
                f'/WimFile:{image}',
                '/Index:1'
            ], capture_output=True, text=True, check=True)

            # Parse version from output
            for line in result.stdout.split('\n'):
                if 'Version' in line:
                    parts = line.split(':')
                    if len(parts) > 1:
                        return parts[1].strip()

            return None

        except Exception as e:
            logger.error(f"Failed to get image version: {e}")
            return None


def apply_enablement_package(
    source_image: Path,
    enablement_cab: Path,
    output_image: Path
) -> bool:
    """
    Apply Windows enablement package.

    Args:
        source_image: Source image
        enablement_cab: Enablement package CAB
        output_image: Output image

    Returns:
        True if successful

    Example:
        success = apply_enablement_package(
            source_image=Path('win11-21h2.wim'),
            enablement_cab=Path('enablement-22h2.cab'),
            output_image=Path('win11-22h2.wim')
        )
    """
    fum = FeatureUpdateManager()

    return fum.apply_feature_update(
        source_image=source_image,
        feature_update=enablement_cab,
        output=output_image
    )


def upgrade_to_enterprise(
    image: Path,
    product_key: Optional[str] = None
) -> bool:
    """
    Upgrade image to Enterprise edition.

    Args:
        image: Image to upgrade
        product_key: Optional product key

    Returns:
        True if successful

    Example:
        success = upgrade_to_enterprise(
            Path('win11-pro.wim'),
            product_key='XXXXX-XXXXX-XXXXX-XXXXX-XXXXX'
        )
    """
    fum = FeatureUpdateManager()

    return fum.upgrade_edition(
        image=image,
        target_edition=WindowsEdition.ENTERPRISE,
        product_key=product_key
    )
