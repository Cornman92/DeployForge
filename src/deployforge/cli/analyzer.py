"""
Image Analysis and Comparison Module

Provides detailed analysis of Windows images including:
- Image information and metadata
- Installed applications and features
- System configuration
- Size and performance metrics
- Comparison between images
"""

import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import json

logger = logging.getLogger(__name__)


@dataclass
class ImageInfo:
    """Image metadata and information."""

    path: str
    name: str
    description: str
    size_mb: float
    architecture: str
    version: str
    edition: str
    languages: List[str]
    build: str
    modified: str


@dataclass
class AnalysisReport:
    """Complete analysis report for an image."""

    image_info: ImageInfo
    features_count: int
    applications_count: int
    drivers_count: int
    updates_count: int
    features: List[str]
    applications: List[str]
    timestamp: str


class ImageAnalyzer:
    """Analyzes Windows images and generates reports."""

    def __init__(self, image_path: Path):
        """
        Initialize analyzer.

        Args:
            image_path: Path to image file
        """
        self.image_path = Path(image_path)

        if not self.image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

    def analyze(self, index: int = 1) -> Dict[str, Any]:
        """
        Perform complete analysis of the image.

        Args:
            index: Image index (for WIM files with multiple images)

        Returns:
            Analysis report dictionary
        """
        logger.info(f"Analyzing image: {self.image_path}")

        report = {
            "image_info": self._get_image_info(index),
            "features": self._get_features(index),
            "applications": self._get_applications(index),
            "drivers": self._get_drivers(index),
            "updates": self._get_updates(index),
            "size_analysis": self._analyze_size(),
            "timestamp": datetime.now().isoformat(),
        }

        return report

    def _get_image_info(self, index: int = 1) -> Dict[str, Any]:
        """Get basic image information using DISM."""
        try:
            result = subprocess.run(
                ["dism", "/Get-ImageInfo", f"/ImageFile:{self.image_path}", f"/Index:{index}"],
                capture_output=True,
                text=True,
                check=True,
            )

            output = result.stdout

            # Parse DISM output
            info = {
                "path": str(self.image_path),
                "name": self._extract_value(output, "Name"),
                "description": self._extract_value(output, "Description"),
                "size_mb": round(self.image_path.stat().st_size / 1024 / 1024, 2),
                "architecture": self._extract_value(output, "Architecture"),
                "version": self._extract_value(output, "Version"),
                "edition": self._extract_value(output, "Edition"),
                "build": self._extract_value(output, "Build"),
                "modified": self._extract_value(output, "Modified"),
                "languages": self._extract_value(output, "Languages").split(", ")
                if self._extract_value(output, "Languages")
                else [],
            }

            return info

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get image info: {e.stderr}")
            return {
                "path": str(self.image_path),
                "size_mb": round(self.image_path.stat().st_size / 1024 / 1024, 2),
                "error": "Failed to read image metadata",
            }

    def _get_features(self, index: int = 1) -> List[Dict[str, str]]:
        """Get installed Windows features."""
        mount_point = None

        try:
            # Mount image temporarily
            mount_point = Path(tempfile.mkdtemp(prefix="deployforge_analyze_"))

            subprocess.run(
                [
                    "dism",
                    "/Mount-Image",
                    f"/ImageFile:{self.image_path}",
                    f"/Index:{index}",
                    f"/MountDir:{mount_point}",
                    "/ReadOnly",
                ],
                capture_output=True,
                check=True,
            )

            # Get features
            result = subprocess.run(
                ["dism", "/Image:{}".format(mount_point), "/Get-Features"],
                capture_output=True,
                text=True,
                check=True,
            )

            features = []
            for line in result.stdout.split("\n"):
                if line.startswith("Feature Name :"):
                    name = line.split(":", 1)[1].strip()
                    features.append({"name": name, "state": "Enabled"})

            return features

        except Exception as e:
            logger.warning(f"Failed to get features: {e}")
            return []

        finally:
            if mount_point and mount_point.exists():
                try:
                    subprocess.run(
                        ["dism", "/Unmount-Image", f"/MountDir:{mount_point}", "/Discard"],
                        capture_output=True,
                        timeout=60,
                    )
                except Exception as e:
                    logger.warning(f"Failed to unmount: {e}")

    def _get_applications(self, index: int = 1) -> List[Dict[str, str]]:
        """Get provisioned applications."""
        mount_point = None

        try:
            mount_point = Path(tempfile.mkdtemp(prefix="deployforge_analyze_"))

            subprocess.run(
                [
                    "dism",
                    "/Mount-Image",
                    f"/ImageFile:{self.image_path}",
                    f"/Index:{index}",
                    f"/MountDir:{mount_point}",
                    "/ReadOnly",
                ],
                capture_output=True,
                check=True,
            )

            result = subprocess.run(
                ["dism", "/Image:{}".format(mount_point), "/Get-ProvisionedAppxPackages"],
                capture_output=True,
                text=True,
                check=True,
            )

            apps = []
            current_app = {}

            for line in result.stdout.split("\n"):
                if line.startswith("DisplayName :"):
                    if current_app:
                        apps.append(current_app)
                    current_app = {"name": line.split(":", 1)[1].strip()}
                elif line.startswith("Version :") and current_app:
                    current_app["version"] = line.split(":", 1)[1].strip()

            if current_app:
                apps.append(current_app)

            return apps

        except Exception as e:
            logger.warning(f"Failed to get applications: {e}")
            return []

        finally:
            if mount_point and mount_point.exists():
                try:
                    subprocess.run(
                        ["dism", "/Unmount-Image", f"/MountDir:{mount_point}", "/Discard"],
                        capture_output=True,
                        timeout=60,
                    )
                except Exception as e:
                    logger.warning(f"Failed to unmount: {e}")

    def _get_drivers(self, index: int = 1) -> List[Dict[str, str]]:
        """Get installed drivers."""
        mount_point = None

        try:
            mount_point = Path(tempfile.mkdtemp(prefix="deployforge_analyze_"))

            subprocess.run(
                [
                    "dism",
                    "/Mount-Image",
                    f"/ImageFile:{self.image_path}",
                    f"/Index:{index}",
                    f"/MountDir:{mount_point}",
                    "/ReadOnly",
                ],
                capture_output=True,
                check=True,
            )

            result = subprocess.run(
                ["dism", "/Image:{}".format(mount_point), "/Get-Drivers"],
                capture_output=True,
                text=True,
                check=True,
            )

            drivers = []
            for line in result.stdout.split("\n"):
                if "Published Name" in line:
                    driver_name = line.split(":", 1)[1].strip()
                    drivers.append({"name": driver_name})

            return drivers

        except Exception as e:
            logger.warning(f"Failed to get drivers: {e}")
            return []

        finally:
            if mount_point and mount_point.exists():
                try:
                    subprocess.run(
                        ["dism", "/Unmount-Image", f"/MountDir:{mount_point}", "/Discard"],
                        capture_output=True,
                        timeout=60,
                    )
                except Exception as e:
                    logger.warning(f"Failed to unmount: {e}")

    def _get_updates(self, index: int = 1) -> List[Dict[str, str]]:
        """Get installed updates."""
        mount_point = None

        try:
            mount_point = Path(tempfile.mkdtemp(prefix="deployforge_analyze_"))

            subprocess.run(
                [
                    "dism",
                    "/Mount-Image",
                    f"/ImageFile:{self.image_path}",
                    f"/Index:{index}",
                    f"/MountDir:{mount_point}",
                    "/ReadOnly",
                ],
                capture_output=True,
                check=True,
            )

            result = subprocess.run(
                ["dism", "/Image:{}".format(mount_point), "/Get-Packages"],
                capture_output=True,
                text=True,
                check=True,
            )

            updates = []
            for line in result.stdout.split("\n"):
                if "Package Identity" in line:
                    update_name = line.split(":", 1)[1].strip()
                    updates.append({"name": update_name})

            return updates

        except Exception as e:
            logger.warning(f"Failed to get updates: {e}")
            return []

        finally:
            if mount_point and mount_point.exists():
                try:
                    subprocess.run(
                        ["dism", "/Unmount-Image", f"/MountDir:{mount_point}", "/Discard"],
                        capture_output=True,
                        timeout=60,
                    )
                except Exception as e:
                    logger.warning(f"Failed to unmount: {e}")

    def _analyze_size(self) -> Dict[str, float]:
        """Analyze image size."""
        size_bytes = self.image_path.stat().st_size

        return {
            "bytes": size_bytes,
            "kb": round(size_bytes / 1024, 2),
            "mb": round(size_bytes / 1024 / 1024, 2),
            "gb": round(size_bytes / 1024 / 1024 / 1024, 2),
        }

    def _extract_value(self, text: str, key: str) -> str:
        """Extract value from DISM output."""
        for line in text.split("\n"):
            if key in line and ":" in line:
                return line.split(":", 1)[1].strip()
        return ""

    def format_text_report(self, report: Dict[str, Any]) -> str:
        """
        Format report as text.

        Args:
            report: Analysis report

        Returns:
            Formatted text report
        """
        output = []
        output.append("=" * 80)
        output.append("IMAGE ANALYSIS REPORT")
        output.append("=" * 80)
        output.append("")

        # Image info
        info = report["image_info"]
        output.append("IMAGE INFORMATION:")
        output.append(f"  Name: {info.get('name', 'N/A')}")
        output.append(f"  Description: {info.get('description', 'N/A')}")
        output.append(f"  Edition: {info.get('edition', 'N/A')}")
        output.append(f"  Version: {info.get('version', 'N/A')}")
        output.append(f"  Build: {info.get('build', 'N/A')}")
        output.append(f"  Architecture: {info.get('architecture', 'N/A')}")
        output.append(f"  Size: {info.get('size_mb', 0)} MB")
        output.append("")

        # Features
        features = report.get("features", [])
        output.append(f"WINDOWS FEATURES: {len(features)}")
        for feature in features[:10]:
            output.append(f"  - {feature['name']}")
        if len(features) > 10:
            output.append(f"  ... and {len(features) - 10} more")
        output.append("")

        # Applications
        apps = report.get("applications", [])
        output.append(f"PROVISIONED APPLICATIONS: {len(apps)}")
        for app in apps[:10]:
            output.append(f"  - {app['name']}")
        if len(apps) > 10:
            output.append(f"  ... and {len(apps) - 10} more")
        output.append("")

        # Drivers
        drivers = report.get("drivers", [])
        output.append(f"DRIVERS: {len(drivers)}")
        output.append("")

        # Updates
        updates = report.get("updates", [])
        output.append(f"INSTALLED UPDATES: {len(updates)}")
        output.append("")

        output.append("=" * 80)

        return "\n".join(output)

    def generate_html_report(self, report: Dict[str, Any]) -> str:
        """
        Generate HTML report.

        Args:
            report: Analysis report

        Returns:
            HTML report
        """
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>DeployForge Image Analysis</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #007acc; padding-bottom: 10px; }}
        h2 {{ color: #007acc; margin-top: 30px; }}
        .info-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin: 20px 0; }}
        .info-item {{ padding: 10px; background: #f9f9f9; border-left: 3px solid #007acc; }}
        .info-label {{ font-weight: bold; color: #666; }}
        .info-value {{ color: #333; }}
        .stats {{ display: flex; gap: 20px; margin: 20px 0; }}
        .stat-box {{ flex: 1; padding: 20px; background: #007acc; color: white; border-radius: 4px; text-align: center; }}
        .stat-number {{ font-size: 32px; font-weight: bold; }}
        .stat-label {{ font-size: 14px; margin-top: 5px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #007acc; color: white; }}
        tr:hover {{ background: #f5f5f5; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>DeployForge Image Analysis Report</h1>
        <p><strong>Generated:</strong> {timestamp}</p>

        <h2>Image Information</h2>
        <div class="info-grid">
            <div class="info-item">
                <div class="info-label">Name</div>
                <div class="info-value">{name}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Edition</div>
                <div class="info-value">{edition}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Version</div>
                <div class="info-value">{version}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Architecture</div>
                <div class="info-value">{architecture}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Build</div>
                <div class="info-value">{build}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Size</div>
                <div class="info-value">{size_mb} MB</div>
            </div>
        </div>

        <h2>Statistics</h2>
        <div class="stats">
            <div class="stat-box">
                <div class="stat-number">{features_count}</div>
                <div class="stat-label">Features</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{apps_count}</div>
                <div class="stat-label">Applications</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{drivers_count}</div>
                <div class="stat-label">Drivers</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{updates_count}</div>
                <div class="stat-label">Updates</div>
            </div>
        </div>

        <h2>Windows Features</h2>
        <table>
            <tr><th>Feature Name</th><th>State</th></tr>
            {features_rows}
        </table>

        <h2>Provisioned Applications</h2>
        <table>
            <tr><th>Application Name</th><th>Version</th></tr>
            {apps_rows}
        </table>
    </div>
</body>
</html>
"""

        info = report["image_info"]
        features = report.get("features", [])
        apps = report.get("applications", [])
        drivers = report.get("drivers", [])
        updates = report.get("updates", [])

        features_rows = "\n".join(
            [f"<tr><td>{f['name']}</td><td>{f['state']}</td></tr>" for f in features[:50]]
        )
        apps_rows = "\n".join(
            [f"<tr><td>{a['name']}</td><td>{a.get('version', 'N/A')}</td></tr>" for a in apps[:50]]
        )

        return html.format(
            timestamp=report["timestamp"],
            name=info.get("name", "N/A"),
            edition=info.get("edition", "N/A"),
            version=info.get("version", "N/A"),
            architecture=info.get("architecture", "N/A"),
            build=info.get("build", "N/A"),
            size_mb=info.get("size_mb", 0),
            features_count=len(features),
            apps_count=len(apps),
            drivers_count=len(drivers),
            updates_count=len(updates),
            features_rows=features_rows,
            apps_rows=apps_rows,
        )


def compare_images(image1_path: Path, image2_path: Path) -> Dict[str, Any]:
    """
    Compare two images and return differences.

    Args:
        image1_path: First image path
        image2_path: Second image path

    Returns:
        Dictionary with differences
    """
    logger.info(f"Comparing images...")
    logger.info(f"  Image 1: {image1_path}")
    logger.info(f"  Image 2: {image2_path}")

    analyzer1 = ImageAnalyzer(image1_path)
    analyzer2 = ImageAnalyzer(image2_path)

    report1 = analyzer1.analyze()
    report2 = analyzer2.analyze()

    # Compare features
    features1 = set(f["name"] for f in report1.get("features", []))
    features2 = set(f["name"] for f in report2.get("features", []))

    # Compare applications
    apps1 = set(a["name"] for a in report1.get("applications", []))
    apps2 = set(a["name"] for a in report2.get("applications", []))

    differences = {
        "image1_info": report1["image_info"],
        "image2_info": report2["image_info"],
        "size_difference_mb": abs(
            report1["image_info"]["size_mb"] - report2["image_info"]["size_mb"]
        ),
        "features_only_in_image1": list(features1 - features2),
        "features_only_in_image2": list(features2 - features1),
        "features_common": list(features1 & features2),
        "apps_only_in_image1": list(apps1 - apps2),
        "apps_only_in_image2": list(apps2 - apps1),
        "apps_common": list(apps1 & apps2),
    }

    return differences
