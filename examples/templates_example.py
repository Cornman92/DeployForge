#!/usr/bin/env python3
"""
Example of using the template system in DeployForge.
"""

from pathlib import Path
from deployforge.templates import (
    TemplateManager,
    CustomizationTemplate,
    FileOperation,
    RegistryTweak,
    DriverPackage,
    GAMING_TEMPLATE
)


def create_custom_template():
    """Create a custom template programmatically."""
    template = CustomizationTemplate(
        name="Development Workstation",
        version="1.0",
        description="Optimized for software development",
        author="Your Name",
        tags=["development", "programming"]
    )

    # Add file operations
    template.files.append(FileOperation(
        action="add",
        source="./configs/bashrc",
        destination="/Users/Default/.bashrc"
    ))

    # Add registry tweaks
    template.registry.append(RegistryTweak(
        hive="HKLM\\SOFTWARE",
        path="Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
        name="HideFileExt",
        data="0",
        type="REG_DWORD",
        action="set"
    ))

    # Add drivers
    template.drivers.append(DriverPackage(
        name="USB 3.0 Drivers",
        path="./drivers/usb3.zip"
    ))

    # Windows features
    template.features = {
        "NetFx3": True,
        "WSL": True,
        "Containers": True
    }

    # Packages to remove
    template.remove_packages = [
        "Microsoft.BingWeather",
        "Microsoft.XboxApp"
    ]

    return template


def save_template_example():
    """Example of saving a template."""
    template = create_custom_template()

    manager = TemplateManager(templates_dir=Path("./templates"))

    # Save as JSON
    manager.save_template(template, Path("./templates/dev-workstation.json"))

    # Save as YAML
    manager.save_template(template, Path("./templates/dev-workstation.yaml"))

    print("Template saved!")


def load_and_apply_template():
    """Example of loading and using a template."""
    manager = TemplateManager(templates_dir=Path("./templates"))

    # Load template
    template = manager.load_template(Path("./templates/dev-workstation.json"))

    print(f"Loaded template: {template.name}")
    print(f"Description: {template.description}")
    print(f"Features: {template.features}")
    print(f"File operations: {len(template.files)}")
    print(f"Registry tweaks: {len(template.registry)}")
    print(f"Drivers: {len(template.drivers)}")

    # In a real scenario, you would apply this template to an image
    # For now, just validate it
    is_valid = manager.validate_template(template)
    print(f"Template valid: {is_valid}")


def use_predefined_template():
    """Example of using the pre-defined gaming template."""
    print("Gaming Template:")
    print(f"  Name: {GAMING_TEMPLATE.name}")
    print(f"  Description: {GAMING_TEMPLATE.description}")
    print(f"  Features to enable: {GAMING_TEMPLATE.features}")
    print(f"  Packages to remove: {len(GAMING_TEMPLATE.remove_packages)}")
    print(f"  Registry tweaks: {len(GAMING_TEMPLATE.registry)}")


def list_available_templates():
    """List all available templates."""
    manager = TemplateManager(templates_dir=Path("./templates"))

    templates = manager.list_templates()

    print(f"\nFound {len(templates)} templates:")
    for template in templates:
        print(f"\n  • {template.name} (v{template.version})")
        print(f"    {template.description}")
        print(f"    Tags: {', '.join(template.tags)}")


if __name__ == "__main__":
    print("DeployForge Template Examples")
    print("=" * 60)

    print("\n1. Creating a custom template...")
    template = create_custom_template()
    print(f"Created: {template.name}")

    print("\n2. Using pre-defined gaming template...")
    use_predefined_template()

    print("\n3. Saving template...")
    save_template_example()

    print("\n4. Loading and validating template...")
    load_and_apply_template()

    print("\n5. Listing available templates...")
    list_available_templates()

    print("\n" + "=" * 60)
    print("Template examples completed!")
