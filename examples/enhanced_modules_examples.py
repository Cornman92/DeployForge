"""
DeployForge Enhanced Modules Examples

Demonstrates usage of all 9 world-class enhanced modules:
- devenv.py (Module 1)
- browsers.py (Module 2)
- creative.py (Module 3)
- privacy_hardening.py (Module 4)
- launchers.py (Module 5)
- ui_customization.py (Module 6)
- backup.py (Module 7)
- wizard.py (Module 8)
- portable.py (Module 9)
"""

from pathlib import Path

# =============================================================================
# Module 6: UI Customization Examples
# =============================================================================

def example_ui_customization_gaming():
    """Example: Apply gaming-focused UI customization"""
    from deployforge.ui_customization import UICustomizer, UIProfile

    # Quick profile-based approach
    from deployforge.ui_customization import customize_ui
    customize_ui(Path("install.wim"), UIProfile.GAMING)

    print("✅ Gaming UI applied: Dark theme, performance-focused, minimal UI")


def example_ui_customization_custom():
    """Example: Custom UI configuration"""
    from deployforge.ui_customization import UICustomizer, ThemeMode, TaskbarAlignment

    ui = UICustomizer(Path("install.wim"))
    ui.mount()

    # Custom configuration
    ui.config.theme_mode = ThemeMode.DARK
    ui.config.taskbar_alignment = TaskbarAlignment.LEFT
    ui.config.show_file_extensions = True
    ui.config.show_hidden_files = True
    ui.config.windows10_context_menu = True
    ui.config.disable_animations = True

    # Apply individual settings
    ui.restore_windows10_context_menu()
    ui.configure_taskbar()
    ui.customize_file_explorer()
    ui.configure_theme()
    ui.optimize_visual_effects()

    ui.unmount(save_changes=True)
    print("✅ Custom UI configuration applied")


def example_ui_all_profiles():
    """Example: List all available UI profiles"""
    from deployforge.ui_customization import UIProfile

    print("Available UI Profiles:")
    for profile in UIProfile:
        print(f"  - {profile.value}: {profile.name}")


# =============================================================================
# Module 7: Backup Configuration Examples
# =============================================================================

def example_backup_aggressive():
    """Example: Maximum protection backup setup"""
    from deployforge.backup import BackupIntegrator, BackupProfile

    # Quick aggressive backup
    from deployforge.backup import configure_backup
    configure_backup(Path("install.wim"), BackupProfile.AGGRESSIVE)

    print("✅ Aggressive backup: System Restore, VSS, File History, Recovery enabled")


def example_backup_custom():
    """Example: Custom backup configuration"""
    from deployforge.backup import BackupIntegrator, BackupType

    backup = BackupIntegrator(Path("install.wim"))
    backup.mount()

    # Configure specific backup features
    backup.config.enable_system_restore = True
    backup.config.system_restore_disk_usage = 10
    backup.config.create_restore_point_on_boot = True
    backup.config.enable_vss = True
    backup.config.enable_file_history = True
    backup.config.enable_recovery_environment = True

    # Apply configurations
    backup.configure_system_restore()
    backup.configure_vss()
    backup.create_restore_point_on_boot()
    backup.configure_recovery_environment()

    # Create scheduled backup
    backup.create_backup_schedule(BackupType.SYSTEM_RESTORE, schedule="weekly")

    # Enable compression
    backup.enable_backup_compression()

    # Create verification script
    backup.create_backup_verification_script()

    backup.unmount(save_changes=True)
    print("✅ Custom backup configuration applied")


def example_backup_enterprise():
    """Example: Enterprise-grade backup"""
    from deployforge.backup import BackupIntegrator, BackupProfile

    backup = BackupIntegrator(Path("install.wim"))
    backup.mount()

    # Apply enterprise profile
    backup.apply_profile(BackupProfile.ENTERPRISE)

    # Export configuration
    config_dict = backup.config.to_dict()
    print(f"Enterprise backup enabled: {config_dict}")

    backup.unmount(save_changes=True)


# =============================================================================
# Module 8: Setup Wizard Examples
# =============================================================================

def example_wizard_gaming():
    """Example: Create gaming setup wizard"""
    from deployforge.wizard import SetupWizard, SetupPreset

    wizard = SetupWizard()

    # Create guided setup for gaming
    wizard.create_guided_setup(
        presets=['gaming'],
        output_path=Path("gaming_setup.json")
    )

    # Generate installation script
    wizard.generate_installation_script(
        SetupPreset.GAMING,
        Path("gaming_install.ps1")
    )

    print("✅ Gaming wizard created: setup.json and install.ps1")


def example_wizard_developer():
    """Example: Developer workstation setup"""
    from deployforge.wizard import SetupWizard, SetupPreset

    wizard = SetupWizard()

    # Get developer preset details
    dev_config = wizard.get_preset(SetupPreset.DEVELOPER)

    print(f"Developer Setup: {dev_config.preset_name}")
    print(f"Description: {dev_config.description}")
    print(f"Essential Apps: {', '.join(dev_config.essential_apps)}")
    print(f"Recommended Apps: {', '.join(dev_config.recommended_apps)}")
    print(f"Hardware: {dev_config.min_ram_gb}-{dev_config.recommended_ram_gb}GB RAM")


def example_wizard_multi_preset():
    """Example: Create multi-preset wizard"""
    from deployforge.wizard import SetupWizard, SetupPreset

    wizard = SetupWizard()

    # Create wizard with multiple presets
    presets = [
        SetupPreset.GAMING,
        SetupPreset.DEVELOPER,
        SetupPreset.CONTENT_CREATOR,
        SetupPreset.STUDENT
    ]

    wizard.create_multi_preset_wizard(
        output_path=Path("multi_setup_wizard.json"),
        selected_presets=presets
    )

    print("✅ Multi-preset wizard created with 4 options")


def example_wizard_recommendation():
    """Example: Get preset recommendation"""
    from deployforge.wizard import SetupWizard

    wizard = SetupWizard()

    # Get recommendations
    use_cases = [
        "I'm a gamer who plays competitive esports",
        "I'm a software developer working with Python",
        "I'm a video editor and content creator",
        "I'm a student taking online classes"
    ]

    for use_case in use_cases:
        preset = wizard.recommend_preset(use_case, has_gpu=True, ram_gb=16)
        print(f"'{use_case}' → {preset.value}")


# =============================================================================
# Module 9: Portable Apps Examples
# =============================================================================

def example_portable_development():
    """Example: Install portable development tools"""
    from deployforge.portable import PortableAppManager, PortableProfile

    # Quick development profile
    from deployforge.portable import install_portable_apps
    install_portable_apps(Path("install.wim"), PortableProfile.DEVELOPMENT)

    print("✅ Development portable apps: VS Code, Git, Python, Notepad++, 7-Zip")


def example_portable_custom():
    """Example: Custom portable app selection"""
    from deployforge.portable import PortableAppManager

    manager = PortableAppManager(Path("install.wim"))
    manager.mount()

    # Select specific apps
    manager.config.selected_apps = [
        'vscode_portable',
        'git_portable',
        'python_portable',
        'notepadpp_portable',
        '7zip_portable',
        'firefox_portable',
        'vlc_portable'
    ]

    # Install selected apps
    manager.install_selected_apps()

    # Create launcher script
    manager.create_launcher_script()

    # Install PortableApps.com Platform
    manager.install_portableapps_platform()

    # Create auto-update script
    manager.create_auto_update_script()

    # Export app list
    manager.export_app_list(Path("installed_apps.json"))

    manager.unmount(save_changes=True)
    print("✅ Custom portable apps installed")


def example_portable_list_apps():
    """Example: List all available portable apps"""
    from deployforge.portable import PortableAppManager, PortableCategory

    manager = PortableAppManager(Path("install.wim"))

    # List apps by category
    apps_by_category = manager.list_available_apps()

    print("Available Portable Apps by Category:")
    for category, apps in apps_by_category.items():
        if apps:
            print(f"\n{category.upper()}:")
            for app in apps:
                print(f"  - {app}")


def example_portable_office():
    """Example: Office productivity portable apps"""
    from deployforge.portable import PortableAppManager, PortableProfile

    manager = PortableAppManager(Path("install.wim"))
    manager.mount()

    # Apply office profile
    manager.apply_profile(PortableProfile.OFFICE)

    print(f"Office apps to install: {', '.join(manager.config.selected_apps)}")

    manager.unmount(save_changes=True)


# =============================================================================
# Combined Workflow Examples
# =============================================================================

def example_complete_gaming_setup():
    """Example: Complete gaming Windows setup"""
    from deployforge.ui_customization import customize_ui, UIProfile
    from deployforge.backup import configure_backup, BackupProfile
    from deployforge.wizard import SetupWizard, SetupPreset
    from deployforge.portable import install_portable_apps, PortableProfile

    image_path = Path("install.wim")

    print("Creating complete gaming setup...")

    # 1. UI Optimization
    print("1/4 Applying gaming UI...")
    customize_ui(image_path, UIProfile.GAMING)

    # 2. Backup Configuration
    print("2/4 Configuring backups...")
    configure_backup(image_path, BackupProfile.MODERATE)

    # 3. Setup Wizard
    print("3/4 Creating setup wizard...")
    wizard = SetupWizard()
    wizard.create_guided_setup(['gaming'], Path("gaming_setup.json"))
    wizard.generate_installation_script(SetupPreset.GAMING, Path("install.ps1"))

    # 4. Portable Apps
    print("4/4 Installing portable apps...")
    # Gaming profile includes browsers and utilities
    # We'd use launchers.py from Module 5 for actual game platform installation

    print("✅ Complete gaming setup created!")


def example_complete_developer_setup():
    """Example: Complete developer workstation"""
    from deployforge.ui_customization import UICustomizer, UIProfile
    from deployforge.backup import BackupIntegrator, BackupProfile
    from deployforge.wizard import SetupWizard, SetupPreset
    from deployforge.portable import PortableAppManager, PortableProfile

    image_path = Path("install.wim")

    print("Creating complete developer workstation...")

    # 1. UI for developers (dark theme, file extensions, etc.)
    print("1/4 Applying developer UI...")
    ui = UICustomizer(image_path)
    ui.mount()
    ui.apply_profile(UIProfile.DEVELOPER)
    ui.unmount(save_changes=True)

    # 2. Backup (important for code!)
    print("2/4 Configuring backups...")
    backup = BackupIntegrator(image_path)
    backup.mount()
    backup.apply_profile(BackupProfile.AGGRESSIVE)
    backup.unmount(save_changes=True)

    # 3. Developer wizard
    print("3/4 Creating developer wizard...")
    wizard = SetupWizard()
    wizard.create_guided_setup(['developer'], Path("dev_setup.json"))

    # 4. Portable dev tools
    print("4/4 Installing portable development tools...")
    portable = PortableAppManager(image_path)
    portable.mount()
    portable.apply_profile(PortableProfile.DEVELOPMENT)
    portable.unmount(save_changes=True)

    print("✅ Complete developer workstation created!")


# =============================================================================
# Quick Reference
# =============================================================================

def print_quick_reference():
    """Print quick reference for all modules"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║         DeployForge Enhanced Modules - Quick Reference (v1.7.0)             ║
╚══════════════════════════════════════════════════════════════════════════════╝

MODULE 6: UI Customization (ui_customization.py)
  Profiles: Modern, Classic, Minimal, Gaming, Productivity, Developer
  Features: Taskbar, Start Menu, File Explorer, Themes, Visual Effects
  Example: customize_ui(Path("image.wim"), UIProfile.GAMING)

MODULE 7: Backup Configuration (backup.py)
  Profiles: Aggressive, Moderate, Minimal, Cloud-Only, Enterprise
  Features: System Restore, VSS, File History, Recovery Environment
  Example: configure_backup(Path("image.wim"), BackupProfile.AGGRESSIVE)

MODULE 8: Setup Wizard (wizard.py)
  Presets: Gaming, Developer, Content Creator, Student, Office, and more
  Features: Hardware detection, Installation scripts, Multi-preset wizards
  Example: wizard.create_guided_setup(['gaming'], Path("setup.json"))

MODULE 9: Portable Apps (portable.py)
  Profiles: Development, Office, Security, Media, Utilities, Complete
  Catalog: 20+ apps (Firefox, VS Code, Git, VLC, GIMP, 7-Zip, etc.)
  Example: install_portable_apps(Path("image.wim"), PortableProfile.DEVELOPMENT)

All modules support:
  ✅ Profile-based configuration (quick setup)
  ✅ Custom configuration (granular control)
  ✅ Progress callbacks (GUI integration)
  ✅ Error handling and logging
  ✅ JSON export (to_dict())

See examples above for detailed usage!
    """)


if __name__ == "__main__":
    print("DeployForge Enhanced Modules Examples")
    print("=" * 80)
    print("\nTo run these examples, uncomment the function calls below:")
    print()

    # Uncomment to run examples:
    # example_ui_customization_gaming()
    # example_backup_aggressive()
    # example_wizard_gaming()
    # example_portable_development()
    # example_complete_gaming_setup()

    # Print quick reference
    print_quick_reference()
