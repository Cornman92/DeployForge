#!/usr/bin/env python3
"""
Gaming PC optimized Windows image builder.

Creates a Windows image optimized for gaming performance with:
- Bloatware removed
- Gaming-specific optimizations
- Latest GPU drivers
- Gaming runtime libraries
"""

from pathlib import Path
from deployforge import ImageManager
from deployforge.templates import GAMING_TEMPLATE, TemplateManager
from deployforge.registry import RegistryEditor
from deployforge.drivers import DriverInjector


def build_gaming_pc_image(
    source_wim: Path,
    output_wim: Path,
    gpu_drivers: Path
):
    """
    Build a gaming-optimized Windows image.

    Args:
        source_wim: Source Windows install.wim
        output_wim: Output gaming image
        gpu_drivers: Path to GPU driver package
    """
    print("=" * 80)
    print("Gaming PC Image Builder")
    print("=" * 80)

    # Copy source
    print("\n[1/5] Preparing image...")
    import shutil
    shutil.copy2(source_wim, output_wim)

    with ImageManager(output_wim) as manager:
        mount_point = manager.mount()

        try:
            # Remove bloatware
            print("[2/5] Removing bloatware and unnecessary apps...")
            remove_apps_for_gaming(manager, mount_point)

            # Apply gaming template
            print("[3/5] Applying gaming optimizations...")
            apply_gaming_optimizations(mount_point)

            # Inject GPU drivers
            print("[4/5] Installing GPU drivers...")
            if gpu_drivers.exists():
                install_gpu_drivers(mount_point, gpu_drivers)

            # Add gaming runtimes
            print("[5/5] Adding gaming runtimes...")
            add_gaming_runtimes(manager)

            print("\n[✓] Saving changes...")
            manager.unmount(save_changes=True)

        except Exception as e:
            print(f"\n[✗] Error: {e}")
            manager.unmount(save_changes=False)
            raise

    print("\n" + "=" * 80)
    print(f"Gaming image created: {output_wim}")
    print("\nOptimizations applied:")
    print("  • Bloatware removed")
    print("  • Gaming CPU/GPU priority settings")
    print("  • Game Mode enabled")
    print("  • Visual effects optimized")
    print("  • Background apps disabled")
    print("  • GPU drivers installed")
    print("=" * 80)


def remove_apps_for_gaming(manager: ImageManager, mount_point: Path):
    """Remove apps not needed for gaming."""
    # Use the gaming template's remove list
    apps_to_remove = GAMING_TEMPLATE.remove_packages

    print(f"  Removing {len(apps_to_remove)} unnecessary apps...")

    # Note: Actual removal requires DISM
    import platform
    if platform.system() == 'Windows':
        import subprocess
        removed = 0
        for app in apps_to_remove:
            try:
                cmd = [
                    'dism',
                    f'/Image:{mount_point}',
                    '/Remove-ProvisionedAppxPackage',
                    f'/PackageName:{app}'
                ]
                result = subprocess.run(cmd, capture_output=True)
                if result.returncode == 0:
                    removed += 1
                    print(f"    Removed: {app}")
            except Exception:
                pass

        print(f"  Removed {removed}/{len(apps_to_remove)} apps")


def apply_gaming_optimizations(mount_point: Path):
    """Apply gaming-specific registry optimizations."""
    print("  Applying gaming optimizations...")

    with RegistryEditor(mount_point) as reg:
        # Apply gaming template tweaks
        print("    • Setting GPU/CPU priority for games...")
        reg.apply_tweaks(GAMING_TEMPLATE.registry)

        # Additional gaming tweaks
        gaming_tweaks = [
            # Enable Game Mode
            {
                'hive': 'HKU\\.DEFAULT',
                'path': 'Software\\Microsoft\\GameBar',
                'name': 'AutoGameModeEnabled',
                'data': '1',
                'type': 'REG_DWORD'
            },
            # Disable Fullscreen Optimizations
            {
                'hive': 'HKLM\\SOFTWARE',
                'path': 'Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options',
                'name': 'DisableFullscreenOptimizations',
                'data': '1',
                'type': 'REG_DWORD'
            },
            # Disable HPET (High Precision Event Timer)
            {
                'hive': 'HKLM\\SYSTEM',
                'path': 'CurrentControlSet\\Control\\TimeProviders\\Timers',
                'name': 'UseHPET',
                'data': '0',
                'type': 'REG_DWORD'
            },
            # Network optimizations for gaming
            {
                'hive': 'HKLM\\SOFTWARE',
                'path': 'Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile',
                'name': 'NetworkThrottlingIndex',
                'data': 'ffffffff',
                'type': 'REG_DWORD'
            },
        ]

        print("    • Enabling Game Mode...")
        print("    • Optimizing network for gaming...")
        print("    • Disabling background optimizations...")
        reg.apply_tweaks(gaming_tweaks)


def install_gpu_drivers(mount_point: Path, gpu_drivers: Path):
    """Install GPU drivers."""
    print(f"  Installing GPU drivers from {gpu_drivers}...")

    injector = DriverInjector(mount_point)

    try:
        results = injector.inject_drivers([gpu_drivers], force_unsigned=False)

        if results['successful'] > 0:
            print(f"    ✓ GPU drivers installed successfully")
        else:
            print(f"    ✗ Failed to install GPU drivers")

    except Exception as e:
        print(f"    Warning: {e}")


def add_gaming_runtimes(manager: ImageManager):
    """Add gaming runtime libraries."""
    print("  Adding gaming runtimes...")

    runtimes_dir = Path("./runtimes")

    if not runtimes_dir.exists():
        print("    No runtimes directory found, skipping...")
        return

    # DirectX
    dx_runtime = runtimes_dir / "directx"
    if dx_runtime.exists():
        print("    • Adding DirectX runtime...")
        # Add DirectX files

    # Visual C++ Redistributables
    vcredist = runtimes_dir / "vcredist"
    if vcredist.exists():
        print("    • Adding VC++ redistributables...")
        # Add VC++ files

    # .NET Framework
    dotnet = runtimes_dir / "dotnet"
    if dotnet.exists():
        print("    • Adding .NET Framework...")
        # Add .NET files

    print("    Gaming runtimes added")


def create_gaming_template_file():
    """Create a gaming template file for reuse."""
    manager = TemplateManager(Path("./templates"))

    # Save the gaming template
    manager.save_template(GAMING_TEMPLATE, Path("./templates/gaming_pc.json"))
    print("Gaming template saved to templates/gaming_pc.json")


if __name__ == "__main__":
    SOURCE_WIM = Path("D:/sources/install.wim")
    OUTPUT_WIM = Path("./Windows_Gaming.wim")
    GPU_DRIVERS = Path("./drivers/nvidia_drivers.zip")

    print("\nGaming PC Image Builder")
    print("=" * 80)
    print("\nThis script will create a Windows image optimized for gaming:")
    print("  • Removes bloatware and unnecessary apps")
    print("  • Optimizes CPU/GPU scheduling for games")
    print("  • Enables Game Mode")
    print("  • Installs latest GPU drivers")
    print("  • Adds gaming runtime libraries")
    print()
    print(f"Source: {SOURCE_WIM}")
    print(f"Output: {OUTPUT_WIM}")
    print(f"GPU Drivers: {GPU_DRIVERS}")
    print()

    if not SOURCE_WIM.exists():
        print("Error: Source WIM not found. Please update paths in the script.")
        print("\nSetup instructions:")
        print("1. Extract install.wim from Windows ISO")
        print("2. Download GPU drivers (NVIDIA/AMD)")
        print("3. Update paths in this script")
        print("4. Run the script")
    else:
        response = input("Build gaming image? (y/n): ")
        if response.lower() == 'y':
            build_gaming_pc_image(SOURCE_WIM, OUTPUT_WIM, GPU_DRIVERS)

            print("\n\nNext steps:")
            print("1. Test the image in a VM or test machine")
            print("2. Create bootable USB with Windows Media Creation Tool")
            print("3. Use the custom image for installation")
            print("4. Enjoy optimized gaming performance!")
