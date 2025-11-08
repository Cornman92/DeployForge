#!/usr/bin/env python3
"""
Complete Windows 11 customization workflow.

This example demonstrates a full Windows 11 image customization process
including debloating, optimization, and custom configurations.
"""

from pathlib import Path
from deployforge import ImageManager
from deployforge.registry import RegistryEditor, COMMON_TWEAKS
from deployforge.drivers import DriverInjector
from deployforge.updates import UpdateIntegrator
from deployforge.templates import CustomizationTemplate, FileOperation, RegistryTweak


def create_windows11_custom_image(
    source_wim: Path,
    output_wim: Path,
    drivers_dir: Path,
    updates_dir: Path
):
    """
    Create a customized Windows 11 image.

    Args:
        source_wim: Source Windows 11 install.wim
        output_wim: Output customized image
        drivers_dir: Directory containing drivers
        updates_dir: Directory containing updates
    """
    print("=" * 80)
    print("Windows 11 Custom Image Builder")
    print("=" * 80)

    # Step 1: Copy source image
    print("\n[1/7] Copying source image...")
    import shutil
    shutil.copy2(source_wim, output_wim)

    # Step 2: Mount the image
    print("[2/7] Mounting image...")
    with ImageManager(output_wim) as manager:
        mount_point = manager.mount(index=1)

        try:
            # Step 3: Remove bloatware
            print("[3/7] Removing bloatware...")
            remove_bloatware(mount_point)

            # Step 4: Apply registry tweaks
            print("[4/7] Applying registry optimizations...")
            apply_registry_tweaks(mount_point)

            # Step 5: Inject drivers
            print("[5/7] Injecting drivers...")
            if drivers_dir.exists():
                inject_custom_drivers(mount_point, drivers_dir)

            # Step 6: Apply updates
            print("[6/7] Applying Windows updates...")
            if updates_dir.exists():
                apply_windows_updates(mount_point, updates_dir)

            # Step 7: Add custom files
            print("[7/7] Adding custom files...")
            add_custom_configurations(manager, mount_point)

            print("\n[✓] Saving changes...")
            manager.unmount(save_changes=True)

        except Exception as e:
            print(f"\n[✗] Error: {e}")
            manager.unmount(save_changes=False)
            raise

    print("\n" + "=" * 80)
    print(f"Custom image created: {output_wim}")
    print("=" * 80)


def remove_bloatware(mount_point: Path):
    """Remove Windows bloatware packages."""
    # List of packages to remove
    bloatware = [
        "Microsoft.549981C3F5F10",  # Cortana
        "Microsoft.BingNews",
        "Microsoft.BingWeather",
        "Microsoft.GetHelp",
        "Microsoft.Getstarted",
        "Microsoft.Messaging",
        "Microsoft.Microsoft3DViewer",
        "Microsoft.MicrosoftOfficeHub",
        "Microsoft.MicrosoftSolitaireCollection",
        "Microsoft.MicrosoftStickyNotes",
        "Microsoft.MixedReality.Portal",
        "Microsoft.Office.OneNote",
        "Microsoft.OneConnect",
        "Microsoft.People",
        "Microsoft.Print3D",
        "Microsoft.SkypeApp",
        "Microsoft.Wallet",
        "Microsoft.Windows.Photos",
        "Microsoft.WindowsAlarms",
        "Microsoft.WindowsCalculator",
        "Microsoft.WindowsCamera",
        "microsoft.windowscommunicationsapps",
        "Microsoft.WindowsFeedbackHub",
        "Microsoft.WindowsMaps",
        "Microsoft.WindowsSoundRecorder",
        "Microsoft.Xbox.TCUI",
        "Microsoft.XboxApp",
        "Microsoft.XboxGameOverlay",
        "Microsoft.XboxGamingOverlay",
        "Microsoft.XboxIdentityProvider",
        "Microsoft.XboxSpeechToTextOverlay",
        "Microsoft.YourPhone",
        "Microsoft.ZuneMusic",
        "Microsoft.ZuneVideo",
    ]

    print(f"  Removing {len(bloatware)} bloatware packages...")

    # Note: Actual removal requires DISM on Windows
    # This is a placeholder for the removal logic
    import platform
    if platform.system() == 'Windows':
        import subprocess
        for package in bloatware:
            try:
                cmd = [
                    'dism',
                    f'/Image:{mount_point}',
                    '/Remove-ProvisionedAppxPackage',
                    f'/PackageName:{package}'
                ]
                subprocess.run(cmd, capture_output=True, check=False)
                print(f"    Removed: {package}")
            except Exception:
                pass


def apply_registry_tweaks(mount_point: Path):
    """Apply performance and privacy registry tweaks."""
    print("  Applying registry tweaks...")

    with RegistryEditor(mount_point) as reg:
        # Disable telemetry
        print("    • Disabling telemetry...")
        reg.apply_tweaks(COMMON_TWEAKS['disable_telemetry'])

        # Disable Cortana
        print("    • Disabling Cortana...")
        reg.apply_tweaks(COMMON_TWEAKS['disable_cortana'])

        # Performance tweaks
        print("    • Applying performance tweaks...")
        performance_tweaks = [
            {
                'hive': 'HKLM\\SOFTWARE',
                'path': 'Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced',
                'name': 'DisablePreviewDesktop',
                'data': '1',
                'type': 'REG_DWORD'
            },
            {
                'hive': 'HKLM\\SOFTWARE',
                'path': 'Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects',
                'name': 'VisualFXSetting',
                'data': '3',  # Best performance
                'type': 'REG_DWORD'
            },
        ]
        reg.apply_tweaks(performance_tweaks)

        # Disable Windows Update (for deployment)
        print("    • Configuring Windows Update...")
        reg.apply_tweaks(COMMON_TWEAKS['disable_windows_update'])


def inject_custom_drivers(mount_point: Path, drivers_dir: Path):
    """Inject custom drivers."""
    print(f"  Injecting drivers from {drivers_dir}...")

    injector = DriverInjector(mount_point)

    driver_packages = list(drivers_dir.glob("*.zip"))
    driver_packages.extend(list(drivers_dir.glob("*.cab")))

    if driver_packages:
        results = injector.inject_drivers(driver_packages, force_unsigned=False)
        print(f"    Injected: {results['successful']}/{results['total']} driver packages")


def apply_windows_updates(mount_point: Path, updates_dir: Path):
    """Apply Windows updates."""
    print(f"  Applying updates from {updates_dir}...")

    integrator = UpdateIntegrator(mount_point)

    # Find all .msu and .cab files
    updates = []
    updates.extend(list(updates_dir.glob("*.msu")))
    updates.extend(list(updates_dir.glob("*.cab")))

    applied = 0
    for update in updates:
        try:
            integrator.apply_update(update)
            applied += 1
            print(f"    Applied: {update.name}")
        except Exception as e:
            print(f"    Failed: {update.name} - {e}")

    print(f"    Total: {applied}/{len(updates)} updates applied")

    # Cleanup
    if applied > 0:
        print("    Cleaning up superseded components...")
        integrator.cleanup_superseded()


def add_custom_configurations(manager: ImageManager, mount_point: Path):
    """Add custom configuration files."""
    print("  Adding custom configurations...")

    # Add custom wallpaper
    wallpaper_source = Path("./assets/wallpaper.jpg")
    if wallpaper_source.exists():
        manager.add_file(
            wallpaper_source,
            "/Windows/Web/Wallpaper/Windows/custom_wallpaper.jpg"
        )
        print("    • Added custom wallpaper")

    # Add custom scripts
    scripts_dir = Path("./scripts")
    if scripts_dir.exists():
        for script in scripts_dir.glob("*.ps1"):
            manager.add_file(
                script,
                f"/Windows/Setup/Scripts/{script.name}"
            )
            print(f"    • Added script: {script.name}")

    # Add custom answer file
    unattend_xml = Path("./configs/autounattend.xml")
    if unattend_xml.exists():
        manager.add_file(unattend_xml, "/autounattend.xml")
        print("    • Added autounattend.xml")


if __name__ == "__main__":
    # Example usage
    SOURCE_WIM = Path("D:/sources/install.wim")
    OUTPUT_WIM = Path("./Windows11_Custom.wim")
    DRIVERS_DIR = Path("./drivers")
    UPDATES_DIR = Path("./updates")

    print("\nWindows 11 Custom Image Builder")
    print("=" * 80)
    print(f"Source: {SOURCE_WIM}")
    print(f"Output: {OUTPUT_WIM}")
    print(f"Drivers: {DRIVERS_DIR}")
    print(f"Updates: {UPDATES_DIR}")
    print()

    if not SOURCE_WIM.exists():
        print("Error: Source WIM not found. Please update the SOURCE_WIM path.")
        print("\nTo use this script:")
        print("1. Extract install.wim from Windows 11 ISO")
        print("2. Update SOURCE_WIM path in this script")
        print("3. Place drivers in ./drivers directory")
        print("4. Place updates in ./updates directory")
        print("5. Run this script")
    else:
        response = input("Start customization? (y/n): ")
        if response.lower() == 'y':
            create_windows11_custom_image(
                SOURCE_WIM,
                OUTPUT_WIM,
                DRIVERS_DIR,
                UPDATES_DIR
            )
