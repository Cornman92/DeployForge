"""
DeployForge Interactive CLI Tool

Provides interactive command-line interface with profile support.
"""

import click
import logging
from pathlib import Path
from typing import Optional
import json
import yaml

logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version='0.6.0')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def cli(verbose):
    """DeployForge - Enterprise Windows Deployment Suite"""
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)


@cli.command()
@click.argument('image', type=click.Path(exists=True))
@click.option('--profile', '-p', help='Profile to apply (gamer, developer, enterprise)')
@click.option('--interactive', '-i', is_flag=True, help='Interactive mode')
@click.option('--output', '-o', type=click.Path(), help='Output image path')
def build(image, profile, interactive, output):
    """Build customized Windows image"""

    if interactive:
        click.echo("🚀 DeployForge Interactive Image Builder")
        click.echo("=" * 50)

        # Get profile
        if not profile:
            profile = click.prompt(
                'Select profile',
                type=click.Choice(['gamer', 'developer', 'enterprise', 'student', 'creator', 'custom']),
                default='gamer'
            )

        # Get output path
        if not output:
            output = click.prompt('Output image path', default='custom.wim')

        # Confirm settings
        click.echo(f"\n📋 Configuration:")
        click.echo(f"  Source: {image}")
        click.echo(f"  Profile: {profile}")
        click.echo(f"  Output: {output}")

        if not click.confirm('\nProceed with build?'):
            click.echo("Build cancelled.")
            return

    click.echo(f"🔨 Building image with {profile} profile...")

    # Apply profile
    from deployforge.cli.profiles import apply_profile
    apply_profile(Path(image), profile, Path(output) if output else None)

    click.echo(f"✅ Build complete: {output}")


@cli.command()
@click.argument('profile_name')
@click.option('--config', '-c', type=click.Path(exists=True), help='Configuration file')
def apply_profile(profile_name, config):
    """Apply a profile to an image"""
    click.echo(f"Applying profile: {profile_name}")


@cli.command()
def list_profiles():
    """List available profiles"""
    click.echo("Available Profiles:")
    click.echo("  - gamer: Gaming optimization")
    click.echo("  - developer: Development tools")
    click.echo("  - enterprise: Enterprise features")
    click.echo("  - student: Student edition")
    click.echo("  - creator: Content creation")


@cli.command()
@click.argument('image', type=click.Path(exists=True))
@click.option('--format', '-f', type=click.Choice(['text', 'json', 'html']), default='text')
@click.option('--output', '-o', type=click.Path(), help='Output report file')
def analyze(image, format, output):
    """Analyze Windows image and generate report"""
    click.echo(f"🔍 Analyzing image: {image}")

    from deployforge.cli.analyzer import ImageAnalyzer

    analyzer = ImageAnalyzer(Path(image))
    report = analyzer.analyze()

    if format == 'json':
        output_data = json.dumps(report, indent=2)
    elif format == 'html':
        output_data = analyzer.generate_html_report(report)
    else:
        output_data = analyzer.format_text_report(report)

    if output:
        Path(output).write_text(output_data)
        click.echo(f"✅ Report saved: {output}")
    else:
        click.echo(output_data)


@cli.command()
@click.argument('image1', type=click.Path(exists=True))
@click.argument('image2', type=click.Path(exists=True))
def diff(image1, image2):
    """Compare two images and show differences"""
    click.echo(f"📊 Comparing images...")
    click.echo(f"  Image 1: {image1}")
    click.echo(f"  Image 2: {image2}")

    from deployforge.cli.analyzer import compare_images

    differences = compare_images(Path(image1), Path(image2))

    click.echo(f"\n🔍 Differences Found:")
    for key, value in differences.items():
        click.echo(f"  {key}: {value}")


@cli.command()
@click.argument('name')
@click.option('--base', '-b', help='Base profile to extend')
def create_preset(name, base):
    """Create a new preset configuration"""
    click.echo(f"Creating preset: {name}")

    from deployforge.cli.presets import PresetManager

    manager = PresetManager()
    manager.create_preset(name, base)

    click.echo(f"✅ Preset created: {name}")


@cli.command()
def list_presets():
    """List all available presets"""
    from deployforge.cli.presets import PresetManager

    manager = PresetManager()
    presets = manager.list_presets()

    click.echo("📦 Available Presets:")
    for preset in presets:
        click.echo(f"  - {preset['name']}: {preset['description']}")


@cli.command()
@click.argument('image', type=click.Path(exists=True))
def validate(image):
    """Validate image integrity and compatibility"""
    click.echo(f"✓ Validating image: {image}")

    from deployforge.testing import ImageValidator

    validator = ImageValidator(Path(image))
    results = validator.run_checks()

    summary = results.get_summary()

    click.echo(f"\n📊 Validation Results:")
    click.echo(f"  Total Tests: {summary['total']}")
    click.echo(f"  ✅ Passed: {summary['passed']}")
    click.echo(f"  ❌ Failed: {summary['failed']}")
    click.echo(f"  ⚠️  Warnings: {summary['warning']}")


@cli.group()
def preset():
    """Preset management commands"""
    pass


@preset.command('create')
@click.argument('name')
def preset_create(name):
    """Create a new preset"""
    click.echo(f"Creating preset: {name}")


@preset.command('apply')
@click.argument('name')
@click.argument('image')
def preset_apply(name, image):
    """Apply preset to image"""
    click.echo(f"Applying preset {name} to {image}")


if __name__ == '__main__':
    cli()
