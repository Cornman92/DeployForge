"""Windows Registry editing for offline images."""

import platform
import subprocess
import tempfile
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import json

from deployforge.core.exceptions import OperationError


logger = logging.getLogger(__name__)


class RegistryEditor:
    """
    Edit Windows registry hives in offline images.

    Supports editing registry hives from mounted WIM/VHD images.
    """

    HIVE_PATHS = {
        'HKLM\\SOFTWARE': 'Windows/System32/config/SOFTWARE',
        'HKLM\\SYSTEM': 'Windows/System32/config/SYSTEM',
        'HKLM\\SECURITY': 'Windows/System32/config/SECURITY',
        'HKLM\\SAM': 'Windows/System32/config/SAM',
        'HKU\\.DEFAULT': 'Windows/System32/config/DEFAULT',
    }

    def __init__(self, mount_point: Path):
        """
        Initialize registry editor.

        Args:
            mount_point: Path to mounted image
        """
        self.mount_point = Path(mount_point)
        self.is_windows = platform.system() == 'Windows'
        self.loaded_hives: Dict[str, str] = {}

    def load_hive(self, hive_key: str) -> None:
        """
        Load a registry hive for editing.

        Args:
            hive_key: Hive key (e.g., 'HKLM\\SOFTWARE')

        Raises:
            OperationError: If hive cannot be loaded
        """
        if hive_key in self.loaded_hives:
            logger.warning(f"{hive_key} already loaded")
            return

        hive_path = self.HIVE_PATHS.get(hive_key)
        if not hive_path:
            raise OperationError(f"Unknown hive: {hive_key}")

        full_path = self.mount_point / hive_path

        if not full_path.exists():
            raise OperationError(f"Hive file not found: {full_path}")

        if self.is_windows:
            self._load_hive_windows(hive_key, full_path)
        else:
            raise OperationError("Registry editing only supported on Windows")

    def _load_hive_windows(self, hive_key: str, hive_file: Path) -> None:
        """Load hive using Windows reg.exe."""
        # Create a unique mount point in the registry
        mount_key = f"HKLM\\DEPLOYFORGE_TEMP_{id(self)}"

        cmd = ['reg', 'load', mount_key, str(hive_file)]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise OperationError(f"Failed to load hive: {result.stderr}")

        self.loaded_hives[hive_key] = mount_key
        logger.info(f"Loaded {hive_key} to {mount_key}")

    def unload_hive(self, hive_key: str) -> None:
        """
        Unload a registry hive.

        Args:
            hive_key: Hive key to unload
        """
        if hive_key not in self.loaded_hives:
            logger.warning(f"{hive_key} not loaded")
            return

        mount_key = self.loaded_hives[hive_key]

        if self.is_windows:
            cmd = ['reg', 'unload', mount_key]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                logger.error(f"Failed to unload hive: {result.stderr}")
            else:
                logger.info(f"Unloaded {hive_key}")

        del self.loaded_hives[hive_key]

    def set_value(
        self,
        hive_key: str,
        sub_key: str,
        value_name: str,
        value_data: Any,
        value_type: str = 'REG_SZ'
    ) -> None:
        """
        Set a registry value.

        Args:
            hive_key: Hive key (e.g., 'HKLM\\SOFTWARE')
            sub_key: Subkey path
            value_name: Value name
            value_data: Value data
            value_type: Value type (REG_SZ, REG_DWORD, REG_BINARY, etc.)
        """
        if hive_key not in self.loaded_hives:
            self.load_hive(hive_key)

        mount_key = self.loaded_hives[hive_key]
        full_key = f"{mount_key}\\{sub_key}"

        if self.is_windows:
            cmd = ['reg', 'add', full_key, '/v', value_name, '/t', value_type, '/d', str(value_data), '/f']
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                raise OperationError(f"Failed to set value: {result.stderr}")

            logger.info(f"Set {full_key}\\{value_name} = {value_data}")

    def delete_value(self, hive_key: str, sub_key: str, value_name: str) -> None:
        """
        Delete a registry value.

        Args:
            hive_key: Hive key
            sub_key: Subkey path
            value_name: Value name to delete
        """
        if hive_key not in self.loaded_hives:
            self.load_hive(hive_key)

        mount_key = self.loaded_hives[hive_key]
        full_key = f"{mount_key}\\{sub_key}"

        if self.is_windows:
            cmd = ['reg', 'delete', full_key, '/v', value_name, '/f']
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                logger.warning(f"Failed to delete value: {result.stderr}")
            else:
                logger.info(f"Deleted {full_key}\\{value_name}")

    def delete_key(self, hive_key: str, sub_key: str) -> None:
        """
        Delete a registry key and all subkeys.

        Args:
            hive_key: Hive key
            sub_key: Subkey path to delete
        """
        if hive_key not in self.loaded_hives:
            self.load_hive(hive_key)

        mount_key = self.loaded_hives[hive_key]
        full_key = f"{mount_key}\\{sub_key}"

        if self.is_windows:
            cmd = ['reg', 'delete', full_key, '/f']
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                logger.warning(f"Failed to delete key: {result.stderr}")
            else:
                logger.info(f"Deleted {full_key}")

    def apply_tweaks(self, tweaks: List[Dict[str, Any]]) -> None:
        """
        Apply a list of registry tweaks.

        Args:
            tweaks: List of tweak dictionaries with keys:
                    - hive: Hive key
                    - path: Subkey path
                    - name: Value name
                    - data: Value data
                    - type: Value type (optional, default REG_SZ)
                    - action: 'set' or 'delete' (optional, default 'set')
        """
        for tweak in tweaks:
            try:
                action = tweak.get('action', 'set')

                if action == 'set':
                    self.set_value(
                        tweak['hive'],
                        tweak['path'],
                        tweak['name'],
                        tweak['data'],
                        tweak.get('type', 'REG_SZ')
                    )
                elif action == 'delete':
                    if 'name' in tweak:
                        self.delete_value(tweak['hive'], tweak['path'], tweak['name'])
                    else:
                        self.delete_key(tweak['hive'], tweak['path'])

            except Exception as e:
                logger.error(f"Failed to apply tweak {tweak}: {e}")

    def export_hive(self, hive_key: str, output_file: Path) -> None:
        """
        Export a hive to a .reg file.

        Args:
            hive_key: Hive key to export
            output_file: Output .reg file path
        """
        if hive_key not in self.loaded_hives:
            self.load_hive(hive_key)

        mount_key = self.loaded_hives[hive_key]

        if self.is_windows:
            cmd = ['reg', 'export', mount_key, str(output_file), '/y']
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                raise OperationError(f"Failed to export hive: {result.stderr}")

            logger.info(f"Exported {hive_key} to {output_file}")

    def cleanup(self) -> None:
        """Unload all loaded hives."""
        for hive_key in list(self.loaded_hives.keys()):
            try:
                self.unload_hive(hive_key)
            except Exception as e:
                logger.error(f"Error unloading {hive_key}: {e}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()
        return False


# Common registry tweaks
COMMON_TWEAKS = {
    'disable_telemetry': [
        {
            'hive': 'HKLM\\SOFTWARE',
            'path': 'Policies\\Microsoft\\Windows\\DataCollection',
            'name': 'AllowTelemetry',
            'data': '0',
            'type': 'REG_DWORD'
        }
    ],
    'disable_cortana': [
        {
            'hive': 'HKLM\\SOFTWARE',
            'path': 'Policies\\Microsoft\\Windows\\Windows Search',
            'name': 'AllowCortana',
            'data': '0',
            'type': 'REG_DWORD'
        }
    ],
    'disable_windows_update': [
        {
            'hive': 'HKLM\\SOFTWARE',
            'path': 'Policies\\Microsoft\\Windows\\WindowsUpdate\\AU',
            'name': 'NoAutoUpdate',
            'data': '1',
            'type': 'REG_DWORD'
        }
    ],
    'enable_dark_theme': [
        {
            'hive': 'HKU\\.DEFAULT',
            'path': 'Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize',
            'name': 'AppsUseLightTheme',
            'data': '0',
            'type': 'REG_DWORD'
        }
    ]
}
