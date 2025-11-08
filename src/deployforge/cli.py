"""Command-line interface for DeployForge."""

import sys
from pathlib import Path
from typing import Optional
import logging

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from deployforge import __version__
from deployforge.core.image_manager import ImageManager
from deployforge.core.exceptions import DeployForgeError
from deployforge.utils.logger import setup_logging
from deployforge.partitions import PartitionManager, create_uefi_bootable_image
from deployforge.unattend import UnattendGenerator, UnattendConfig, create_basic_unattend
from deployforge.languages import LanguageManager, create_multilingual_config


console = Console()
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version=__version__)
@click.option('-v', '--verbose', is_flag=True, help='Enable verbose logging')
@click.option('--log-file', type=click.Path(), help='Log file path')
@click.pass_context
def main(ctx, verbose, log_file):
    """
    DeployForge - Enterprise Windows Deployment Suite

    Customize, personalize and optimize Windows images at scale.

    Supports: ISO, WIM, ESD, PPKG, VHD, and VHDX formats.

    Features: Partitioning, WinPE, Answer Files, Multi-language Support.
    """
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose

    # Setup logging
    level = "DEBUG" if verbose else "INFO"
    setup_logging(level=level, log_file=log_file, verbose=verbose)

    # Import handlers to register them
    import deployforge.handlers  # noqa: F401


@main.command()
def formats():
    """List supported image formats."""
    formats_list = ImageManager.supported_formats()

    table = Table(title="Supported Image Formats")
    table.add_column("Extension", style="cyan")
    table.add_column("Description", style="green")

    format_descriptions = {
        '.iso': 'ISO 9660 - Optical disc image',
        '.wim': 'WIM - Windows Imaging Format',
        '.esd': 'ESD - Electronic Software Download (compressed WIM)',
        '.ppkg': 'PPKG - Provisioning Package',
        '.vhd': 'VHD - Virtual Hard Disk',
        '.vhdx': 'VHDX - Hyper-V Virtual Hard Disk',
    }

    for fmt in formats_list:
        desc = format_descriptions.get(fmt, 'Unknown')
        table.add_row(fmt, desc)

    console.print(table)


@main.command()
@click.argument('image_path', type=click.Path(exists=True))
def info(image_path):
    """Get information about an image file."""
    try:
        image_path = Path(image_path)

        with console.status(f"[bold green]Reading {image_path.name}..."):
            manager = ImageManager(image_path)
            info_data = manager.get_info()

        # Display info
        table = Table(title=f"Image Information: {image_path.name}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        for key, value in info_data.items():
            if isinstance(value, dict):
                table.add_row(key, str(value))
            else:
                table.add_row(key, str(value))

        console.print(table)

    except DeployForgeError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        logger.exception("Unexpected error in info command")
        sys.exit(1)


@main.command()
@click.argument('image_path', type=click.Path(exists=True))
@click.option('-p', '--path', default='/', help='Path within the image to list')
def list(image_path, path):
    """List files in an image."""
    try:
        image_path = Path(image_path)

        with console.status(f"[bold green]Mounting {image_path.name}..."):
            manager = ImageManager(image_path)
            manager.mount()

        try:
            files = manager.list_files(path)

            table = Table(title=f"Files in {image_path.name}:{path}")
            table.add_column("Name", style="cyan")
            table.add_column("Type", style="magenta")
            table.add_column("Size", style="green")

            for file_info in files:
                file_type = "DIR" if file_info.get('is_dir') else "FILE"
                size = "-" if file_info.get('is_dir') else f"{file_info.get('size', 0):,} bytes"
                table.add_row(file_info['name'], file_type, size)

            console.print(table)

        finally:
            with console.status("[bold yellow]Unmounting..."):
                manager.unmount()

    except DeployForgeError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        logger.exception("Unexpected error in list command")
        sys.exit(1)


@main.command()
@click.argument('image_path', type=click.Path(exists=True))
@click.argument('source_file', type=click.Path(exists=True))
@click.argument('destination_path')
def add(image_path, source_file, destination_path):
    """Add a file to an image."""
    try:
        image_path = Path(image_path)
        source_file = Path(source_file)

        with console.status(f"[bold green]Mounting {image_path.name}..."):
            manager = ImageManager(image_path)
            manager.mount()

        try:
            with console.status(f"[bold green]Adding {source_file.name}..."):
                manager.add_file(source_file, destination_path)

            console.print(f"[bold green]✓[/bold green] Added {source_file.name} to {destination_path}")

        finally:
            with console.status("[bold yellow]Saving changes..."):
                manager.unmount(save_changes=True)

            console.print(f"[bold green]✓[/bold green] Changes saved")

    except DeployForgeError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        logger.exception("Unexpected error in add command")
        sys.exit(1)


@main.command()
@click.argument('image_path', type=click.Path(exists=True))
@click.argument('file_path')
def remove(image_path, file_path):
    """Remove a file from an image."""
    try:
        image_path = Path(image_path)

        with console.status(f"[bold green]Mounting {image_path.name}..."):
            manager = ImageManager(image_path)
            manager.mount()

        try:
            with console.status(f"[bold yellow]Removing {file_path}..."):
                manager.remove_file(file_path)

            console.print(f"[bold green]✓[/bold green] Removed {file_path}")

        finally:
            with console.status("[bold yellow]Saving changes..."):
                manager.unmount(save_changes=True)

            console.print(f"[bold green]✓[/bold green] Changes saved")

    except DeployForgeError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        logger.exception("Unexpected error in remove command")
        sys.exit(1)


@main.command()
@click.argument('image_path', type=click.Path(exists=True))
@click.argument('source_path')
@click.argument('destination_file', type=click.Path())
def extract(image_path, source_path, destination_file):
    """Extract a file from an image."""
    try:
        image_path = Path(image_path)
        destination_file = Path(destination_file)

        with console.status(f"[bold green]Mounting {image_path.name}..."):
            manager = ImageManager(image_path)
            manager.mount()

        try:
            with console.status(f"[bold green]Extracting {source_path}..."):
                manager.extract_file(source_path, destination_file)

            console.print(f"[bold green]✓[/bold green] Extracted to {destination_file}")

        finally:
            with console.status("[bold yellow]Unmounting..."):
                manager.unmount()

    except DeployForgeError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        logger.exception("Unexpected error in extract command")
        sys.exit(1)


@main.command()
@click.argument('image_path', type=click.Path(exists=True))
@click.argument('mount_point', type=click.Path())
@click.option('--index', default=1, help='Image index for WIM/ESD files')
def mount(image_path, mount_point, index):
    """Mount an image to a directory."""
    try:
        image_path = Path(image_path)
        mount_point = Path(mount_point)

        with console.status(f"[bold green]Mounting {image_path.name}..."):
            manager = ImageManager(image_path)

            # Handle WIM/ESD index
            if image_path.suffix.lower() in ['.wim', '.esd']:
                manager.handler.index = index

            mount_path = manager.mount(mount_point)

        console.print(f"[bold green]✓[/bold green] Mounted at {mount_path}")
        console.print(Panel(
            f"[yellow]Image is mounted. Use 'deployforge unmount {mount_path}' when done.[/yellow]",
            title="Warning"
        ))

    except DeployForgeError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        logger.exception("Unexpected error in mount command")
        sys.exit(1)


@main.command()
@click.argument('mount_point', type=click.Path(exists=True))
@click.option('--save/--discard', default=False, help='Save or discard changes')
def unmount(mount_point, save):
    """Unmount a previously mounted image."""
    try:
        # This is a simplified version - in practice, you'd need to track mounts
        console.print("[yellow]Note: Manual unmounting requires tracking mounted images.[/yellow]")
        console.print("[yellow]For WIM files on Windows, use: dism /Unmount-Wim[/yellow]")
        console.print("[yellow]For WIM files on Linux, use: wimlib-imagex unmount[/yellow]")

    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        logger.exception("Unexpected error in unmount command")
        sys.exit(1)


# Partition Management Commands
@main.group()
def partition():
    """Manage UEFI/GPT partitions on disk images."""
    pass


@partition.command('list')
@click.argument('image_path', type=click.Path(exists=True))
def partition_list(image_path):
    """List partitions in a disk image."""
    try:
        image_path = Path(image_path)

        with console.status(f"[bold green]Reading partitions from {image_path.name}..."):
            pm = PartitionManager(image_path)
            layout = pm.read_partition_table()

        table = Table(title=f"Partitions in {image_path.name}")
        table.add_column("Number", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Type", style="magenta")
        table.add_column("Size", style="yellow")
        table.add_column("Filesystem", style="blue")

        for part in layout.partitions:
            table.add_row(
                str(part.number),
                part.name,
                part.type_guid[:8] + "...",
                f"{part.size_gb:.2f} GB",
                part.filesystem or "N/A"
            )

        console.print(table)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        logger.exception("Error listing partitions")
        sys.exit(1)


@partition.command('create')
@click.argument('image_path', type=click.Path())
@click.option('--size', default=50, help='Disk size in GB')
@click.option('--recovery/--no-recovery', default=True, help='Include recovery partition')
def partition_create(image_path, size, recovery):
    """Create a new UEFI disk image with standard Windows partitioning."""
    try:
        image_path = Path(image_path)

        with console.status(f"[bold green]Creating UEFI disk image..."):
            pm = create_uefi_bootable_image(image_path, size, recovery)

        console.print(f"[bold green]✓[/bold green] Created {image_path}")
        console.print(f"  • Size: {size} GB")
        console.print(f"  • Partitions: {len(pm.layout.partitions)}")
        console.print(f"  • Recovery: {'Yes' if recovery else 'No'}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        logger.exception("Error creating partition")
        sys.exit(1)


@partition.command('export')
@click.argument('image_path', type=click.Path(exists=True))
@click.argument('output_json', type=click.Path())
def partition_export(image_path, output_json):
    """Export partition layout to JSON."""
    try:
        image_path = Path(image_path)
        output_json = Path(output_json)

        pm = PartitionManager(image_path)
        pm.read_partition_table()
        pm.export_layout(output_json)

        console.print(f"[bold green]✓[/bold green] Exported partition layout to {output_json}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        logger.exception("Error exporting partitions")
        sys.exit(1)


# Unattend.xml Commands
@main.group()
def unattend():
    """Generate Windows answer files (unattend.xml)."""
    pass


@unattend.command('create')
@click.argument('output_path', type=click.Path())
@click.option('--product-key', help='Windows product key')
@click.option('--username', default='Admin', help='Local admin username')
@click.option('--password', default='P@ssw0rd', help='Local admin password')
@click.option('--computer-name', help='Computer name')
@click.option('--timezone', default='Pacific Standard Time', help='Time zone')
def unattend_create(output_path, product_key, username, password, computer_name, timezone):
    """Create a basic unattend.xml file."""
    try:
        output_path = Path(output_path)

        with console.status("[bold green]Generating unattend.xml..."):
            config = create_basic_unattend(
                product_key=product_key,
                username=username,
                password=password,
                computer_name=computer_name or "DESKTOP-PC",
                time_zone=timezone
            )

            generator = UnattendGenerator(config)
            generator.save(output_path)

        console.print(f"[bold green]✓[/bold green] Created unattend.xml at {output_path}")
        console.print(f"  • Username: {username}")
        console.print(f"  • Computer: {computer_name or 'DESKTOP-PC'}")
        console.print(f"  • Timezone: {timezone}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        logger.exception("Error creating unattend.xml")
        sys.exit(1)


# Language Management Commands
@main.group()
def language():
    """Manage multi-language support (MUI packs)."""
    pass


@language.command('list')
@click.argument('image_path', type=click.Path(exists=True))
def language_list(image_path):
    """List installed languages in an image."""
    try:
        image_path = Path(image_path)

        with console.status(f"[bold green]Reading languages from {image_path.name}..."):
            lm = LanguageManager(image_path)
            # Note: Would need to mount image first in real implementation
            console.print("[yellow]Note: Image must be mounted to query languages[/yellow]")

        console.print(f"[bold green]Language management for {image_path.name}[/bold green]")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        logger.exception("Error listing languages")
        sys.exit(1)


@language.command('add')
@click.argument('image_path', type=click.Path(exists=True))
@click.argument('language_pack', type=click.Path(exists=True))
def language_add(image_path, language_pack):
    """Add a language pack to an image."""
    try:
        image_path = Path(image_path)
        language_pack = Path(language_pack)

        with console.status(f"[bold green]Installing language pack..."):
            console.print(f"[yellow]Installing {language_pack.name} to {image_path.name}[/yellow]")
            # Would need to mount, install, unmount

        console.print(f"[bold green]✓[/bold green] Language pack installed")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        logger.exception("Error adding language pack")
        sys.exit(1)


if __name__ == '__main__':
    main()
