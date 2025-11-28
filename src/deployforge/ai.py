"""
AI-Powered Features Module

Provides intelligent hardware detection, optimization suggestions,
and profile recommendations using ML and heuristics.

Features:
- Hardware detection and analysis
- Automatic profile recommendations
- Optimization suggestions based on system specs
- Predictive performance analysis
- Intelligent debloating recommendations
"""

import logging
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class SystemType(Enum):
    """System type classification."""

    GAMING = "gaming"
    WORKSTATION = "workstation"
    LAPTOP = "laptop"
    SERVER = "server"
    BASIC = "basic"
    HIGH_END = "high_end"


class UsageProfile(Enum):
    """Usage profile classification."""

    GAMER = "gamer"
    DEVELOPER = "developer"
    CREATOR = "creator"
    OFFICE = "office"
    STUDENT = "student"
    POWER_USER = "power_user"


@dataclass
class HardwareSpecs:
    """Hardware specification data."""

    cpu_cores: int = 0
    cpu_threads: int = 0
    cpu_brand: str = ""
    cpu_model: str = ""
    ram_gb: float = 0.0
    gpu_model: str = ""
    gpu_vram_gb: float = 0.0
    storage_type: str = ""  # SSD, HDD, NVMe
    storage_size_gb: float = 0.0
    has_tpm: bool = False
    has_secure_boot: bool = False
    is_laptop: bool = False


@dataclass
class OptimizationSuggestion:
    """AI-generated optimization suggestion."""

    category: str
    suggestion: str
    reason: str
    impact: str  # low, medium, high
    module: str  # deployforge module to use
    action: str  # specific action to take
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProfileRecommendation:
    """Profile recommendation with confidence score."""

    profile_name: str
    confidence: float
    reasons: List[str]
    suggested_tweaks: List[str]


class AIOptimizer:
    """AI-powered optimization engine."""

    def __init__(self):
        """Initialize AI optimizer."""
        self.hardware_specs: Optional[HardwareSpecs] = None
        self.system_type: Optional[SystemType] = None
        self.usage_profile: Optional[UsageProfile] = None

    def detect_hardware(self) -> HardwareSpecs:
        """
        Detect hardware specifications.

        Returns:
            Hardware specifications
        """
        logger.info("Detecting hardware specifications...")

        specs = HardwareSpecs()

        try:
            # Detect CPU
            cpu_info = self._get_cpu_info()
            specs.cpu_cores = cpu_info.get("cores", 0)
            specs.cpu_threads = cpu_info.get("threads", 0)
            specs.cpu_brand = cpu_info.get("brand", "")
            specs.cpu_model = cpu_info.get("model", "")

            # Detect RAM
            specs.ram_gb = self._get_ram_size()

            # Detect GPU
            gpu_info = self._get_gpu_info()
            specs.gpu_model = gpu_info.get("model", "")
            specs.gpu_vram_gb = gpu_info.get("vram_gb", 0.0)

            # Detect storage
            storage_info = self._get_storage_info()
            specs.storage_type = storage_info.get("type", "HDD")
            specs.storage_size_gb = storage_info.get("size_gb", 0.0)

            # Detect security features
            specs.has_tpm = self._check_tpm()
            specs.has_secure_boot = self._check_secure_boot()

            # Detect if laptop
            specs.is_laptop = self._is_laptop()

            self.hardware_specs = specs
            logger.info(
                f"Hardware detected: {specs.cpu_model}, {specs.ram_gb}GB RAM, {specs.gpu_model}"
            )

        except Exception as e:
            logger.warning(f"Hardware detection failed: {e}")

        return specs

    def recommend_profile(self, specs: Optional[HardwareSpecs] = None) -> ProfileRecommendation:
        """
        Recommend optimal profile based on hardware.

        Args:
            specs: Hardware specifications (auto-detect if None)

        Returns:
            Profile recommendation
        """
        if specs is None:
            specs = self.detect_hardware()

        # Classify system type
        system_type = self._classify_system(specs)

        # Analyze usage patterns
        usage_hints = self._analyze_usage_hints(specs)

        # Generate recommendation
        if system_type == SystemType.GAMING:
            return ProfileRecommendation(
                profile_name="gamer",
                confidence=0.9,
                reasons=[
                    f"High-end GPU detected: {specs.gpu_model}",
                    f"{specs.cpu_cores}+ CPU cores optimal for gaming",
                    f"{specs.ram_gb}GB RAM sufficient for gaming",
                ],
                suggested_tweaks=[
                    "Enable competitive gaming optimizations",
                    "Install gaming launchers (Steam, Epic)",
                    "Apply network latency tweaks",
                ],
            )

        elif "nvidia" in specs.gpu_model.lower() or "amd" in specs.gpu_model.lower():
            if specs.ram_gb >= 16:
                return ProfileRecommendation(
                    profile_name="creator",
                    confidence=0.8,
                    reasons=[
                        f"Dedicated GPU: {specs.gpu_model}",
                        f"{specs.ram_gb}GB RAM suitable for content creation",
                        "System capable of video editing and 3D work",
                    ],
                    suggested_tweaks=[
                        "Install creative tools (OBS, GIMP, Blender)",
                        "Optimize storage for media files",
                        "Enable GPU acceleration",
                    ],
                )

        if specs.cpu_threads >= 8 and specs.ram_gb >= 16:
            return ProfileRecommendation(
                profile_name="developer",
                confidence=0.85,
                reasons=[
                    f"{specs.cpu_threads} threads suitable for compilation",
                    f"{specs.ram_gb}GB RAM adequate for VMs and containers",
                    "System capable of running development tools",
                ],
                suggested_tweaks=[
                    "Enable WSL2 and Hyper-V",
                    "Install development tools",
                    "Configure Docker Desktop",
                ],
            )

        if specs.is_laptop:
            return ProfileRecommendation(
                profile_name="student",
                confidence=0.75,
                reasons=[
                    "Laptop detected",
                    "Balanced profile for mobility",
                    "Battery optimization included",
                ],
                suggested_tweaks=[
                    "Enable power management",
                    "Install productivity tools",
                    "Optimize for battery life",
                ],
            )

        # Default recommendation
        return ProfileRecommendation(
            profile_name="custom",
            confidence=0.5,
            reasons=[
                "System specs don't match predefined profiles",
                "Manual customization recommended",
            ],
            suggested_tweaks=[
                "Review hardware capabilities",
                "Select specific optimizations",
                "Create custom profile",
            ],
        )

    def generate_optimizations(
        self, specs: Optional[HardwareSpecs] = None
    ) -> List[OptimizationSuggestion]:
        """
        Generate optimization suggestions.

        Args:
            specs: Hardware specifications

        Returns:
            List of optimization suggestions
        """
        if specs is None:
            specs = self.detect_hardware()

        suggestions = []

        # CPU optimizations
        if specs.cpu_cores >= 6:
            suggestions.append(
                OptimizationSuggestion(
                    category="Performance",
                    suggestion="Enable multi-core optimization",
                    reason=f"System has {specs.cpu_cores} cores available",
                    impact="high",
                    module="optimizer",
                    action="optimize_boot_time",
                    parameters={},
                )
            )

        # RAM optimizations
        if specs.ram_gb >= 16:
            suggestions.append(
                OptimizationSuggestion(
                    category="Performance",
                    suggestion="Disable hibernation to save disk space",
                    reason=f"System has {specs.ram_gb}GB RAM, hibernation not critical",
                    impact="medium",
                    module="optimizer",
                    action="disable_hibernation",
                    parameters={},
                )
            )

        # Storage optimizations
        if specs.storage_type in ["SSD", "NVMe"]:
            suggestions.append(
                OptimizationSuggestion(
                    category="Storage",
                    suggestion="Disable disk defragmentation",
                    reason=f"{specs.storage_type} detected, defragmentation not needed",
                    impact="medium",
                    module="optimizer",
                    action="disable_defrag",
                    parameters={},
                )
            )

        # GPU optimizations
        if "nvidia" in specs.gpu_model.lower():
            suggestions.append(
                OptimizationSuggestion(
                    category="Gaming",
                    suggestion="Enable NVIDIA-specific optimizations",
                    reason="NVIDIA GPU detected",
                    impact="high",
                    module="gaming",
                    action="enable_gpu_scheduling",
                    parameters={"vendor": "nvidia"},
                )
            )

        # Security optimizations
        if specs.has_tpm and specs.has_secure_boot:
            suggestions.append(
                OptimizationSuggestion(
                    category="Security",
                    suggestion="Enable BitLocker encryption",
                    reason="TPM and Secure Boot available",
                    impact="high",
                    module="encryption",
                    action="configure_bitlocker",
                    parameters={"require_tpm": True},
                )
            )

        # Debloating recommendations
        if specs.is_laptop:
            suggestions.append(
                OptimizationSuggestion(
                    category="Performance",
                    suggestion="Moderate debloating recommended",
                    reason="Laptop detected, balance performance and features",
                    impact="medium",
                    module="debloat",
                    action="remove_bloatware",
                    parameters={"level": "moderate"},
                )
            )
        else:
            suggestions.append(
                OptimizationSuggestion(
                    category="Performance",
                    suggestion="Aggressive debloating available",
                    reason="Desktop system, can remove more bloatware",
                    impact="high",
                    module="debloat",
                    action="remove_bloatware",
                    parameters={"level": "aggressive"},
                )
            )

        # Network optimizations
        if system_type == SystemType.GAMING:
            suggestions.append(
                OptimizationSuggestion(
                    category="Network",
                    suggestion="Apply gaming network optimizations",
                    reason="Gaming system detected",
                    impact="high",
                    module="network",
                    action="optimize_for_gaming",
                    parameters={},
                )
            )

        return suggestions

    def predict_performance_impact(self, optimization: OptimizationSuggestion) -> Dict[str, Any]:
        """
        Predict performance impact of an optimization.

        Args:
            optimization: Optimization to analyze

        Returns:
            Performance prediction
        """
        impact_map = {
            "low": {"boot_time": 0.02, "responsiveness": 0.05, "disk_space": 0.01},
            "medium": {"boot_time": 0.05, "responsiveness": 0.10, "disk_space": 0.05},
            "high": {"boot_time": 0.10, "responsiveness": 0.20, "disk_space": 0.10},
        }

        base_impact = impact_map.get(optimization.impact, impact_map["low"])

        return {
            "boot_time_improvement": f"{int(base_impact['boot_time'] * 100)}%",
            "responsiveness_improvement": f"{int(base_impact['responsiveness'] * 100)}%",
            "disk_space_saved": f"{int(base_impact['disk_space'] * 100)}%",
            "estimated_benefit": optimization.impact,
            "recommendation": "Apply" if optimization.impact in ["medium", "high"] else "Optional",
        }

    def _get_cpu_info(self) -> Dict[str, Any]:
        """Get CPU information using WMIC."""
        try:
            result = subprocess.run(
                [
                    "wmic",
                    "cpu",
                    "get",
                    "Name,NumberOfCores,NumberOfLogicalProcessors",
                    "/format:list",
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            output = result.stdout
            info = {}

            for line in output.split("\n"):
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()

                    if key == "Name":
                        info["model"] = value
                        if "intel" in value.lower():
                            info["brand"] = "Intel"
                        elif "amd" in value.lower():
                            info["brand"] = "AMD"
                    elif key == "NumberOfCores":
                        info["cores"] = int(value) if value.isdigit() else 0
                    elif key == "NumberOfLogicalProcessors":
                        info["threads"] = int(value) if value.isdigit() else 0

            return info

        except Exception as e:
            logger.warning(f"Failed to get CPU info: {e}")
            return {}

    def _get_ram_size(self) -> float:
        """Get total RAM in GB."""
        try:
            result = subprocess.run(
                ["wmic", "ComputerSystem", "get", "TotalPhysicalMemory", "/format:list"],
                capture_output=True,
                text=True,
                check=True,
            )

            for line in result.stdout.split("\n"):
                if "=" in line:
                    key, value = line.split("=", 1)
                    if "TotalPhysicalMemory" in key:
                        bytes_ram = int(value.strip())
                        return round(bytes_ram / (1024**3), 2)

        except Exception as e:
            logger.warning(f"Failed to get RAM size: {e}")

        return 0.0

    def _get_gpu_info(self) -> Dict[str, Any]:
        """Get GPU information."""
        try:
            result = subprocess.run(
                ["wmic", "path", "win32_VideoController", "get", "Name,AdapterRAM", "/format:list"],
                capture_output=True,
                text=True,
                check=True,
            )

            info = {}
            for line in result.stdout.split("\n"):
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()

                    if key == "Name":
                        info["model"] = value
                    elif key == "AdapterRAM" and value.isdigit():
                        info["vram_gb"] = round(int(value) / (1024**3), 2)

            return info

        except Exception as e:
            logger.warning(f"Failed to get GPU info: {e}")
            return {}

    def _get_storage_info(self) -> Dict[str, Any]:
        """Get storage information."""
        try:
            result = subprocess.run(
                ["wmic", "diskdrive", "get", "Model,Size,MediaType", "/format:list"],
                capture_output=True,
                text=True,
                check=True,
            )

            info = {}
            for line in result.stdout.split("\n"):
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()

                    if key == "Size" and value.isdigit():
                        info["size_gb"] = round(int(value) / (1024**3), 2)
                    elif key == "MediaType":
                        if "SSD" in value or "Solid" in value:
                            info["type"] = "SSD"
                        elif "NVMe" in value:
                            info["type"] = "NVMe"
                        else:
                            info["type"] = "HDD"

            return info

        except Exception as e:
            logger.warning(f"Failed to get storage info: {e}")
            return {}

    def _check_tpm(self) -> bool:
        """Check if TPM is available."""
        try:
            result = subprocess.run(
                [
                    "wmic",
                    "/namespace:\\\\root\\cimv2\\security\\microsofttpm",
                    "path",
                    "win32_tpm",
                    "get",
                    "/format:list",
                ],
                capture_output=True,
                text=True,
            )
            return "IsActivated_InitialValue=TRUE" in result.stdout
        except:
            return False

    def _check_secure_boot(self) -> bool:
        """Check if Secure Boot is enabled."""
        try:
            result = subprocess.run(
                ["powershell", "Confirm-SecureBootUEFI"], capture_output=True, text=True
            )
            return "True" in result.stdout
        except:
            return False

    def _is_laptop(self) -> bool:
        """Detect if system is a laptop."""
        try:
            result = subprocess.run(
                ["wmic", "systemenclosure", "get", "chassistypes", "/format:list"],
                capture_output=True,
                text=True,
                check=True,
            )

            # Chassis types 8-14 are portable/laptop
            for line in result.stdout.split("\n"):
                if "ChassisTypes" in line:
                    value = line.split("=", 1)[1].strip()
                    if any(str(i) in value for i in range(8, 15)):
                        return True

        except Exception as e:
            logger.warning(f"Failed to detect laptop: {e}")

        return False

    def _classify_system(self, specs: HardwareSpecs) -> SystemType:
        """Classify system type based on specs."""
        # High-end gaming
        if specs.gpu_vram_gb >= 8 and specs.cpu_cores >= 8 and specs.ram_gb >= 16:
            return SystemType.GAMING

        # Workstation
        if specs.cpu_threads >= 16 and specs.ram_gb >= 32:
            return SystemType.WORKSTATION

        # Laptop
        if specs.is_laptop:
            return SystemType.LAPTOP

        # High-end
        if specs.cpu_cores >= 6 and specs.ram_gb >= 16:
            return SystemType.HIGH_END

        # Basic
        return SystemType.BASIC

    def _analyze_usage_hints(self, specs: HardwareSpecs) -> List[str]:
        """Analyze usage pattern hints."""
        hints = []

        if specs.gpu_vram_gb >= 6:
            hints.append("gaming")
            hints.append("content_creation")

        if specs.cpu_threads >= 12:
            hints.append("development")
            hints.append("virtualization")

        if specs.is_laptop:
            hints.append("mobility")

        return hints


def auto_optimize_image(image_path: Path) -> List[OptimizationSuggestion]:
    """
    Automatically detect hardware and generate optimizations.

    Args:
        image_path: Path to Windows image

    Returns:
        List of optimization suggestions
    """
    ai = AIOptimizer()
    specs = ai.detect_hardware()
    suggestions = ai.generate_optimizations(specs)

    logger.info(f"Generated {len(suggestions)} optimization suggestions")

    return suggestions
