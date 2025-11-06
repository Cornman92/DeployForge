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


console = Console()
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version=__version__)
@click.option('-v', '--verbose', is_flag=True, help='Enable verbose logging')
@click.option('--log-file', type=click.Path(), help='Log file path')
@click.pass_context
def main(ctx, verbose, log_file):
    """
    DeployForge - Windows Deployment Suite

    Customize, personalize and optimize Windows images and packages.

    Supports: ISO, WIM, ESD, and PPKG formats.
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


if __name__ == '__main__':
    main()
