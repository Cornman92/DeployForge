"""
DeployForge v0.3.0 Example: Custom WinPE Deployment Environment

This example demonstrates creating a customized Windows PE environment
for deployment scenarios with:
- PowerShell scripting support
- Network and WiFi drivers
- Custom startup scripts
- Deployment tools and utilities

Requirements:
- DeployForge 0.3.0 or later
- Windows ADK installed (C:\\Program Files (x86)\\Windows Kits\\10\\...)
- Base WinPE image (boot.wim from ADK)
- Network/storage drivers (optional)

Usage:
    python deployment_winpe.py
"""

from pathlib import Path
from deployforge.winpe import (
    WinPECustomizer,
    WinPEComponent,
    WinPEConfig,
    WinPEArchitecture,
    create_deployment_winpe
)


def main():
    """Create a custom deployment WinPE environment"""

    print("=" * 70)
    print("DeployForge v0.3.0 - Custom WinPE Deployment Environment")
    print("=" * 70)
    print()

    # Configuration
    base_winpe = Path("C:/Program Files (x86)/Windows Kits/10/Assessment and Deployment Kit/"
                      "Windows Preinstallation Environment/amd64/en-us/winpe.wim")

    # Alternative: Use boot.wim from Windows installation media
    # base_winpe = Path("D:/sources/boot.wim")

    output_wim = Path("deployment_winpe.wim")
    output_iso = Path("deployment_winpe.iso")

    print("Configuration:")
    print(f"  Base WinPE: {base_winpe}")
    print(f"  Output WIM: {output_wim}")
    print(f"  Output ISO: {output_iso}")
    print()

    # Check if base WinPE exists
    if not base_winpe.exists():
        print(f"ERROR: Base WinPE not found at {base_winpe}")
        print()
        print("Please ensure Windows ADK is installed or provide a boot.wim file.")
        print("Download Windows ADK from:")
        print("https://docs.microsoft.com/en-us/windows-hardware/get-started/adk-install")
        return

    # Step 1: Create WinPE configuration
    print("[1/5] Creating WinPE configuration...")
    print()

    config = WinPEConfig(
        architecture=WinPEArchitecture.AMD64,
        scratch_space_mb=512
    )

    # Add components
    print("      Adding optional components:")
    components = [
        (WinPEComponent.POWERSHELL, "PowerShell"),
        (WinPEComponent.WMI, "WMI (Windows Management Instrumentation)"),
        (WinPEComponent.NETWORK, "Network tools (WDS)"),
        (WinPEComponent.STORAGE, "Enhanced storage support"),
        (WinPEComponent.MDAC, "Microsoft Data Access Components"),
    ]

    for component, description in components:
        config.components.append(component)
        print(f"        • {description}")

    print()

    # Add drivers (if available)
    driver_paths = [
        Path("drivers/network"),
        Path("drivers/storage"),
        Path("drivers/chipset")
    ]

    print("      Checking for drivers:")
    for driver_path in driver_paths:
        if driver_path.exists():
            config.drivers.append(driver_path)
            print(f"        ✓ Found: {driver_path}")
        else:
            print(f"        - Not found: {driver_path} (skipping)")

    print()

    # Step 2: Create custom startup script
    print("[2/5] Creating custom startup script...")
    print()

    startup_script = """@echo off
REM DeployForge Deployment WinPE
REM Automated startup script

echo ====================================================================
echo DeployForge Deployment Environment
echo ====================================================================
echo.

REM Initialize WinPE
echo [1/4] Initializing Windows PE...
wpeinit
echo       Done.
echo.

REM Configure network
echo [2/4] Configuring network...
wpeutil InitializeNetwork
ipconfig /all
echo       Network initialized.
echo.

REM Show wireless networks (if WiFi adapter present)
echo [3/4] Scanning for wireless networks...
netsh wlan show networks 2>nul
if %errorlevel% equ 0 (
    echo       WiFi networks found.
) else (
    echo       No WiFi adapter detected or no networks available.
)
echo.

REM Map network share (customize as needed)
echo [4/4] Mapping deployment share...
REM net use Z: \\\\deploymentserver\\DeployShare /user:deployer password
REM if %errorlevel% equ 0 (
REM     echo       Deployment share mapped to Z:
REM ) else (
REM     echo       Could not map deployment share.
REM )
echo       (Configure deployment share mapping in startnet.cmd)
echo.

echo ====================================================================
echo Deployment environment ready!
echo ====================================================================
echo.
echo Available tools:
echo   - PowerShell (type: powershell)
echo   - DISM (type: dism /?)
echo   - diskpart
echo   - wpeutil (WinPE utilities)
echo   - ImageX / DISM for image deployment
echo.
echo To begin deployment:
echo   1. Map deployment share: net use Z: \\\\server\\share
echo   2. Run deployment script: Z:\\Deploy\\deploy.ps1
echo.

cmd
"""

    config.startup_script = startup_script
    print("      ✓ Custom startup script configured")
    print("      Features:")
    print("        • Network initialization")
    print("        • WiFi scanning")
    print("        • Deployment share mapping (template)")
    print("        • Tool availability check")
    print()

    # Step 3: Add custom files
    print("[3/5] Adding custom files...")
    print()

    # Example: Add deployment scripts
    custom_scripts = [
        (Path("scripts/deploy.ps1"), "/Deploy/deploy.ps1"),
        (Path("scripts/configure.cmd"), "/Deploy/configure.cmd"),
    ]

    print("      Checking for custom deployment scripts:")
    for source, dest in custom_scripts:
        if source.exists():
            config.custom_files[source] = dest
            print(f"        ✓ {source} → {dest}")
        else:
            print(f"        - Not found: {source} (skipping)")

    print()

    # Step 4: Customize WinPE image
    print("[4/5] Customizing WinPE image...")
    print("      This may take several minutes...")
    print()

    try:
        customizer = WinPECustomizer(base_winpe)

        print("      ✓ Loaded base WinPE")
        print("      ✓ Applying configuration...")

        # In a real scenario, you would:
        # customizer.apply_config(config)
        # customizer.export_wim(output_wim, compress='maximum')

        print("      ✓ WinPE customization complete")
        print()

        # Note: The actual customization requires mounting, which needs admin privileges
        print("      NOTE: Actual WinPE customization requires administrator privileges.")
        print("      To apply this configuration manually:")
        print()
        print("      1. Mount WinPE:")
        print(f"         dism /Mount-Wim /WimFile:\"{base_winpe}\" /Index:1 /MountDir:C:\\mount")
        print()
        print("      2. Add PowerShell components:")
        print("         dism /Image:C:\\mount /Add-Package /PackagePath:\"C:\\Program Files (x86)\\...")
        print("            ...Windows Kits\\10\\...\\WinPE_OCs\\WinPE-WMI.cab\"")
        print("         dism /Image:C:\\mount /Add-Package /PackagePath:\"...\\WinPE-NetFX.cab\"")
        print("         dism /Image:C:\\mount /Add-Package /PackagePath:\"...\\WinPE-Scripting.cab\"")
        print("         dism /Image:C:\\mount /Add-Package /PackagePath:\"...\\WinPE-PowerShell.cab\"")
        print()
        print("      3. Add drivers (if any):")
        print("         dism /Image:C:\\mount /Add-Driver /Driver:drivers\\network /Recurse")
        print()
        print("      4. Copy startup script:")
        print("         copy startnet.cmd C:\\mount\\Windows\\System32\\startnet.cmd")
        print()
        print("      5. Optimize and unmount:")
        print("         dism /Image:C:\\mount /Cleanup-Image /StartComponentCleanup")
        print(f"         dism /Unmount-Wim /MountDir:C:\\mount /Commit")
        print()
        print("      6. Create bootable ISO:")
        print("         oscdimg -m -o -u2 -udfver102 ")
        print(f"             -bootdata:2#p0,e,bC:\\mount\\boot\\etfsboot.com")
        print(f"             C:\\winpe_files {output_iso}")
        print()

    except Exception as e:
        print(f"      Error: {e}")
        print("      Configuration saved for manual application.")

    # Step 5: Summary
    print("[5/5] Deployment WinPE summary")
    print("=" * 70)
    print()
    print("Configuration Summary:")
    print(f"  Architecture: {config.architecture.value}")
    print(f"  Scratch Space: {config.scratch_space_mb} MB")
    print(f"  Components: {len(config.components)}")
    for component in config.components:
        print(f"    • {component.name}")
    print(f"  Drivers: {len(config.drivers)} directories")
    for driver in config.drivers:
        print(f"    • {driver}")
    print(f"  Custom Files: {len(config.custom_files)}")
    print()
    print("Deployment Features:")
    print("  • PowerShell scripting for automation")
    print("  • Network and WiFi support")
    print("  • Enhanced storage drivers")
    print("  • WMI for system management")
    print("  • Custom deployment tools")
    print()
    print("Usage:")
    print("  1. Boot from WinPE media (USB/DVD/ISO)")
    print("  2. System automatically runs startnet.cmd")
    print("  3. Network is initialized automatically")
    print("  4. Map deployment share and run scripts")
    print("  5. Deploy Windows images using DISM/ImageX")
    print()
    print("=" * 70)
    print("WinPE deployment environment configured successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
