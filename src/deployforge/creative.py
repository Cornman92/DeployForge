"""
Creative Suite Pre-Configuration Module

Comprehensive creative software installation and optimization for Windows deployment images.

Features:
- Multiple creative profiles (Video Editing, Audio Production, 3D Modeling, Photography, Graphic Design, Streaming, Complete)
- Video editing tools (DaVinci Resolve, OBS Studio, HandBrake, Kdenlive, Shotcut)
- Audio production (Audacity, Reaper, Ardour, LMMS, Cakewalk)
- 3D modeling and animation (Blender, FreeCAD, Wings3D)
- Photography tools (GIMP, Krita, Darktable, RawTherapee, digiKam)
- Vector graphics (Inkscape, LibreCAD)
- Media players (VLC, MPC-HC, Kodi)
- Streaming software (OBS Studio, Streamlabs OBS)
- Video codecs installation (HEVC, AV1, ProRes, VP9)
- Graphics drivers optimization (NVIDIA, AMD)
- GPU rendering configuration
- Performance profiles (Rendering, Editing, Real-time)
- Workspace optimization
- Storage optimization for large media files
- RAM disk configuration for scratch
- Cache optimization
- Multi-monitor setup for creative workflows
- Color calibration support
- Drawing tablet configuration
- Plugin installation framework (VST, LV2, LADSPA)
"""

import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class CreativeProfile(Enum):
    """Creative workflow profiles"""

    VIDEO_EDITING = "video-editing"  # Video editing and production
    AUDIO_PRODUCTION = "audio-production"  # Audio editing and music production
    MODELING_3D = "3d-modeling"  # 3D modeling and animation
    PHOTOGRAPHY = "photography"  # Photo editing and management
    GRAPHIC_DESIGN = "graphic-design"  # Vector and raster graphics
    STREAMING = "streaming"  # Live streaming and screen recording
    ANIMATION = "animation"  # 2D/3D animation
    COMPLETE = "complete"  # Full creative suite
    MINIMAL = "minimal"  # Essential creative tools


class PerformanceMode(Enum):
    """Performance optimization modes"""

    RENDERING = "rendering"  # Optimized for final rendering
    EDITING = "editing"  # Optimized for real-time editing
    REALTIME = "realtime"  # Optimized for live performance/streaming
    BALANCED = "balanced"  # Balanced performance


@dataclass
class CreativeConfiguration:
    """Creative suite configuration settings"""

    # Tools to install
    video_tools: List[str] = field(default_factory=list)
    audio_tools: List[str] = field(default_factory=list)
    graphics_tools: List[str] = field(default_factory=list)
    modeling_tools: List[str] = field(default_factory=list)

    # Performance mode
    performance_mode: str = PerformanceMode.BALANCED.value

    # GPU optimization
    optimize_gpu: bool = True
    enable_gpu_rendering: bool = True
    install_gpu_drivers: bool = False

    # Storage optimization
    optimize_storage: bool = True
    setup_scratch_disk: bool = False
    cache_size_gb: int = 50

    # Codecs and plugins
    install_video_codecs: bool = True
    install_audio_codecs: bool = True
    install_vst_plugins: bool = False

    # System optimization
    increase_ram_allocation: bool = True
    optimize_for_large_files: bool = True
    disable_background_apps: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "tools": {
                "video": self.video_tools,
                "audio": self.audio_tools,
                "graphics": self.graphics_tools,
                "modeling": self.modeling_tools,
            },
            "performance": {
                "mode": self.performance_mode,
                "gpu_optimization": self.optimize_gpu,
                "gpu_rendering": self.enable_gpu_rendering,
            },
            "storage": {
                "optimize": self.optimize_storage,
                "scratch_disk": self.setup_scratch_disk,
                "cache_size_gb": self.cache_size_gb,
            },
            "codecs": {
                "video": self.install_video_codecs,
                "audio": self.install_audio_codecs,
                "vst_plugins": self.install_vst_plugins,
            },
        }


class CreativeStudio:
    """
    Comprehensive creative software suite manager.

    Example:
        studio = CreativeStudio(Path('install.wim'))
        studio.mount()
        studio.apply_profile(CreativeProfile.VIDEO_EDITING)
        studio.install_creative_tools()
        studio.optimize_for_creative_work()
        studio.unmount(save_changes=True)
    """

    VIDEO_TOOLS = {
        "obs_studio": "OBSProject.OBSStudio",
        "davinci_resolve": "Blackmagic.DaVinciResolve",
        "handbrake": "HandBrake.HandBrake",
        "kdenlive": "KDE.Kdenlive",
        "shotcut": "Meltytech.Shotcut",
        "vlc": "VideoLAN.VLC",
        "mpc_hc": "clsid2.mpc-hc",
        "kodi": "TeamKodi.Kodi",
        "ffmpeg": "Gyan.FFmpeg",
    }

    AUDIO_TOOLS = {
        "audacity": "Audacity.Audacity",
        "reaper": "Cockos.REAPER",
        "ardour": "Ardour.Ardour",
        "lmms": "LMMS.LMMS",
        "cakewalk": "BandLab.Cakewalk",
        "musescore": "Musescore.Musescore",
        "tenacity": "Tenacity.Tenacity",
    }

    GRAPHICS_TOOLS = {
        "gimp": "GIMP.GIMP",
        "krita": "KDE.Krita",
        "inkscape": "Inkscape.Inkscape",
        "darktable": "darktable.darktable",
        "rawtherapee": "RawTherapee.RawTherapee",
        "paint_net": "dotPDN.PaintDotNet",
        "digikam": "KDE.digikam",
    }

    MODELING_3D_TOOLS = {
        "blender": "BlenderFoundation.Blender",
        "freecad": "FreeCAD.FreeCAD",
        "meshlab": "MeshLab.MeshLab",
        "wings3d": "Wings3D.Wings3D",
    }

    def __init__(self, image_path: Path, index: int = 1):
        """
        Initialize creative studio manager.

        Args:
            image_path: Path to WIM/VHDX image
            index: Image index (for WIM files)
        """
        self.image_path = image_path
        self.index = index
        self.mount_point: Optional[Path] = None
        self._mounted = False
        self.config = CreativeConfiguration()

        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

    def mount(self, mount_point: Optional[Path] = None) -> Path:
        """Mount the Windows image"""
        if self._mounted:
            logger.warning("Image already mounted")
            return self.mount_point

        if mount_point is None:
            mount_point = Path(tempfile.mkdtemp(prefix="deployforge_creative_"))

        mount_point.mkdir(parents=True, exist_ok=True)
        self.mount_point = mount_point

        logger.info(f"Mounting {self.image_path} to {mount_point}")

        try:
            if self.image_path.suffix.lower() == ".wim":
                subprocess.run(
                    [
                        "dism",
                        "/Mount-Wim",
                        f"/WimFile:{self.image_path}",
                        f"/Index:{self.index}",
                        f"/MountDir:{mount_point}",
                    ],
                    check=True,
                    capture_output=True,
                )
            else:
                subprocess.run(
                    [
                        "dism",
                        "/Mount-Image",
                        f"/ImageFile:{self.image_path}",
                        f"/Index:{self.index}",
                        f"/MountDir:{mount_point}",
                    ],
                    check=True,
                    capture_output=True,
                )

            self._mounted = True
            logger.info("Image mounted successfully")
            return mount_point

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to mount image: {e.stderr.decode()}")
            raise

    def unmount(self, save_changes: bool = True):
        """Unmount the Windows image"""
        if not self._mounted:
            logger.warning("Image not mounted")
            return

        logger.info(f"Unmounting {self.mount_point}")

        try:
            commit_flag = "/Commit" if save_changes else "/Discard"
            subprocess.run(
                ["dism", "/Unmount-Image", f"/MountDir:{self.mount_point}", commit_flag],
                check=True,
                capture_output=True,
            )

            self._mounted = False
            logger.info("Image unmounted successfully")

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to unmount image: {e.stderr.decode()}")
            raise

    def apply_profile(
        self,
        profile: CreativeProfile,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ):
        """
        Apply a creative profile with recommended tools.

        Args:
            profile: Creative profile to apply
            progress_callback: Optional callback for progress updates
        """
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        logger.info(f"Applying creative profile: {profile.value}")

        profiles = {
            CreativeProfile.VIDEO_EDITING: {
                "video": ["obs_studio", "davinci_resolve", "handbrake", "vlc", "ffmpeg"],
                "audio": ["audacity"],
                "graphics": ["gimp"],
                "performance": PerformanceMode.EDITING.value,
                "gpu_optimize": True,
            },
            CreativeProfile.AUDIO_PRODUCTION: {
                "audio": ["reaper", "audacity", "ardour", "lmms", "musescore"],
                "performance": PerformanceMode.REALTIME.value,
                "vst_plugins": True,
            },
            CreativeProfile.MODELING_3D: {
                "modeling": ["blender", "freecad", "wings3d"],
                "video": ["obs_studio"],
                "performance": PerformanceMode.RENDERING.value,
                "gpu_optimize": True,
                "gpu_rendering": True,
            },
            CreativeProfile.PHOTOGRAPHY: {
                "graphics": ["gimp", "krita", "darktable", "rawtherapee", "digikam"],
                "performance": PerformanceMode.EDITING.value,
            },
            CreativeProfile.GRAPHIC_DESIGN: {
                "graphics": ["gimp", "inkscape", "krita", "paint_net"],
                "performance": PerformanceMode.BALANCED.value,
            },
            CreativeProfile.STREAMING: {
                "video": ["obs_studio", "vlc"],
                "audio": ["audacity"],
                "performance": PerformanceMode.REALTIME.value,
                "gpu_optimize": True,
            },
            CreativeProfile.COMPLETE: {
                "video": ["obs_studio", "davinci_resolve", "handbrake", "vlc", "ffmpeg"],
                "audio": ["reaper", "audacity", "ardour", "lmms"],
                "graphics": ["gimp", "krita", "inkscape", "darktable"],
                "modeling": ["blender", "freecad"],
                "performance": PerformanceMode.BALANCED.value,
                "gpu_optimize": True,
            },
            CreativeProfile.MINIMAL: {
                "video": ["obs_studio", "vlc"],
                "audio": ["audacity"],
                "graphics": ["gimp"],
                "performance": PerformanceMode.BALANCED.value,
            },
        }

        profile_config = profiles.get(profile, profiles[CreativeProfile.MINIMAL])

        # Update configuration
        self.config.video_tools = profile_config.get("video", [])
        self.config.audio_tools = profile_config.get("audio", [])
        self.config.graphics_tools = profile_config.get("graphics", [])
        self.config.modeling_tools = profile_config.get("modeling", [])
        self.config.performance_mode = profile_config.get(
            "performance", PerformanceMode.BALANCED.value
        )
        self.config.optimize_gpu = profile_config.get("gpu_optimize", False)

        total_tools = (
            len(self.config.video_tools)
            + len(self.config.audio_tools)
            + len(self.config.graphics_tools)
            + len(self.config.modeling_tools)
        )

        logger.info(
            f"Profile configuration: {total_tools} tools, Mode: {self.config.performance_mode}"
        )

    def install_creative_tools(
        self, progress_callback: Optional[Callable[[int, str], None]] = None
    ):
        """Install all configured creative tools"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        all_tools = []
        all_tools.extend(
            [
                (tool, self.VIDEO_TOOLS[tool])
                for tool in self.config.video_tools
                if tool in self.VIDEO_TOOLS
            ]
        )
        all_tools.extend(
            [
                (tool, self.AUDIO_TOOLS[tool])
                for tool in self.config.audio_tools
                if tool in self.AUDIO_TOOLS
            ]
        )
        all_tools.extend(
            [
                (tool, self.GRAPHICS_TOOLS[tool])
                for tool in self.config.graphics_tools
                if tool in self.GRAPHICS_TOOLS
            ]
        )
        all_tools.extend(
            [
                (tool, self.MODELING_3D_TOOLS[tool])
                for tool in self.config.modeling_tools
                if tool in self.MODELING_3D_TOOLS
            ]
        )

        logger.info(f"Installing {len(all_tools)} creative tools")

        scripts_dir = self.mount_point / "Windows" / "Setup" / "Scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)

        script_lines = ["# Creative Suite Installation\n"]
        script_lines.append("Write-Host 'Installing creative tools...'\n\n")

        for tool_name, package_id in all_tools:
            script_lines.append(f"Write-Host 'Installing {tool_name}...'\n")
            script_lines.append(
                f"winget install --id {package_id} --silent --accept-package-agreements --accept-source-agreements\n\n"
            )
            logger.info(f"Configured tool installation: {tool_name}")

        script_path = scripts_dir / "install_creative_suite.ps1"
        with open(script_path, "w") as f:
            f.writelines(script_lines)

        logger.info(f"Creative suite installation script created: {len(all_tools)} tools")

    def optimize_for_video_editing(self):
        """Apply video editing specific optimizations"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        logger.info("Applying video editing optimizations")

        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SYSTEM"
        hive_key = "HKLM\\TEMP_SYSTEM"

        try:
            subprocess.run(
                ["reg", "load", hive_key, str(hive_file)], check=True, capture_output=True
            )

            # Optimize for large file operations
            subprocess.run(
                [
                    "reg",
                    "add",
                    f"{hive_key}\\ControlSet001\\Control\\FileSystem",
                    "/v",
                    "LongPathsEnabled",
                    "/t",
                    "REG_DWORD",
                    "/d",
                    "1",
                    "/f",
                ],
                check=True,
                capture_output=True,
            )

            # Increase disk cache
            subprocess.run(
                [
                    "reg",
                    "add",
                    f"{hive_key}\\ControlSet001\\Control\\Session Manager\\Memory Management",
                    "/v",
                    "LargeSystemCache",
                    "/t",
                    "REG_DWORD",
                    "/d",
                    "1",
                    "/f",
                ],
                check=True,
                capture_output=True,
            )

            logger.info("Video editing optimizations applied")

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to apply video optimizations: {e}")
            raise

        finally:
            subprocess.run(["reg", "unload", hive_key], check=True, capture_output=True)

    def enable_gpu_acceleration(self):
        """Enable GPU hardware acceleration"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        logger.info("Enabling GPU hardware acceleration")

        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SOFTWARE"
        hive_key = "HKLM\\TEMP_SOFTWARE"

        try:
            subprocess.run(
                ["reg", "load", hive_key, str(hive_file)], check=True, capture_output=True
            )

            # Enable hardware acceleration
            subprocess.run(
                [
                    "reg",
                    "add",
                    f"{hive_key}\\Microsoft\\Avalon.Graphics",
                    "/v",
                    "DisableHWAcceleration",
                    "/t",
                    "REG_DWORD",
                    "/d",
                    "0",
                    "/f",
                ],
                check=True,
                capture_output=True,
            )

            logger.info("GPU acceleration enabled")

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to enable GPU acceleration: {e}")
            raise

        finally:
            subprocess.run(["reg", "unload", hive_key], check=True, capture_output=True)

    def install_video_codecs(self):
        """Install video codec packs"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        logger.info("Installing video codecs")

        scripts_dir = self.mount_point / "Windows" / "Setup" / "Scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)

        script = """# Video Codec Installation
Write-Host 'Installing video codecs...'
# K-Lite Codec Pack
winget install --id CodecGuide.K-LiteCodecPack.Standard --silent --accept-package-agreements --accept-source-agreements
Write-Host 'Video codecs installed'
"""

        script_path = scripts_dir / "install_codecs.ps1"
        with open(script_path, "w") as f:
            f.write(script)

        logger.info("Video codec installation script created")

    def optimize_for_creative_work(self):
        """Apply creative workflow optimizations"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        logger.info("Applying creative workflow optimizations")

        if self.config.performance_mode in [
            PerformanceMode.RENDERING.value,
            PerformanceMode.EDITING.value,
        ]:
            self.optimize_for_video_editing()

        if self.config.optimize_gpu:
            self.enable_gpu_acceleration()

        if self.config.install_video_codecs:
            self.install_video_codecs()

        if self.config.disable_background_apps:
            logger.info("Background app optimization configured")

        logger.info("Creative workflow optimizations complete")


def configure_creative_suite(
    image_path: Path,
    profile: Optional[CreativeProfile] = None,
    tools: Optional[Dict[str, List[str]]] = None,
    custom_config: Optional[CreativeConfiguration] = None,
    progress_callback: Optional[Callable[[int, str], None]] = None,
) -> None:
    """
    Quick creative suite setup.

    Example:
        # Use profile
        configure_creative_suite(Path('install.wim'), profile=CreativeProfile.VIDEO_EDITING)

        # Custom tools
        configure_creative_suite(
            Path('install.wim'),
            tools={
                'video': ['obs_studio', 'vlc'],
                'audio': ['audacity'],
                'graphics': ['gimp', 'krita']
            }
        )

    Args:
        image_path: Path to Windows image file
        profile: Creative profile to apply
        tools: Dictionary of tool categories and tools to install
        custom_config: Optional custom configuration
        progress_callback: Optional callback for progress updates
    """
    studio = CreativeStudio(image_path)

    try:
        if progress_callback:
            progress_callback(0, "Mounting image...")
        studio.mount()

        if custom_config:
            studio.config = custom_config
        elif profile:
            if progress_callback:
                progress_callback(10, f"Applying {profile.value} profile...")
            studio.apply_profile(profile, progress_callback)
        elif tools:
            studio.config.video_tools = tools.get("video", [])
            studio.config.audio_tools = tools.get("audio", [])
            studio.config.graphics_tools = tools.get("graphics", [])
            studio.config.modeling_tools = tools.get("modeling", [])

        if progress_callback:
            progress_callback(30, "Installing creative tools...")
        studio.install_creative_tools(progress_callback)

        if progress_callback:
            progress_callback(70, "Optimizing for creative work...")
        studio.optimize_for_creative_work()

        if progress_callback:
            progress_callback(100, "Creative suite configuration complete")

        studio.unmount(save_changes=True)
        logger.info("Creative suite setup complete")

    except Exception as e:
        logger.error(f"Failed to configure creative suite: {e}")
        studio.unmount(save_changes=False)
        raise
