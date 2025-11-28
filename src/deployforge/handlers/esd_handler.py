"""ESD (Electronic Software Download) handler."""

import logging
from pathlib import Path
from typing import Dict, Any

from deployforge.handlers.wim_handler import WIMHandler


logger = logging.getLogger(__name__)


class ESDHandler(WIMHandler):
    """
    Handler for ESD (Electronic Software Download) files.

    ESD files are highly compressed WIM files used by Microsoft for
    Windows updates and downloads. They can be handled using the same
    tools as WIM files (DISM on Windows, wimlib on Linux/Mac).

    This handler inherits from WIMHandler as ESD files use the same
    underlying format and tools.
    """

    def __init__(self, image_path: Path):
        """Initialize the ESD handler."""
        super().__init__(image_path)
        logger.info(f"Initialized ESD handler for {image_path}")

    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the ESD.

        Returns:
            Dictionary containing ESD metadata
        """
        info = super().get_info()
        # Override format to indicate ESD
        info["format"] = "ESD (Electronic Software Download)"
        info["note"] = "ESD files are highly compressed WIM files"
        return info

    def convert_to_wim(self, output_path: Path, compression: str = "maximum") -> None:
        """
        Convert ESD to WIM format.

        Args:
            output_path: Path for the output WIM file
            compression: Compression type ('none', 'fast', 'maximum', 'lzx', 'xpress')

        Raises:
            OperationError: If conversion fails
        """
        from deployforge.core.exceptions import OperationError
        import subprocess

        try:
            output_path = Path(output_path)

            if self.is_windows and self._check_dism():
                # Use DISM to export (convert) ESD to WIM
                cmd = [
                    "dism",
                    "/Export-Image",
                    f"/SourceImageFile:{self.image_path}",
                    f"/SourceIndex:{self.index}",
                    f"/DestinationImageFile:{output_path}",
                    f"/Compress:{compression}",
                ]
            elif self._check_wimlib():
                # Use wimlib to export
                cmd = [
                    "wimlib-imagex",
                    "export",
                    str(self.image_path),
                    str(self.index),
                    str(output_path),
                    f"--compress={compression}",
                ]
            else:
                raise OperationError(
                    "No WIM/ESD conversion tool available. "
                    "Install DISM (Windows) or wimlib-imagex (Linux/Mac)"
                )

            logger.info(f"Converting ESD to WIM: {output_path}")
            logger.debug(f"Running: {' '.join(cmd)}")

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                raise OperationError(f"Conversion failed: {result.stderr}")

            logger.info(f"Successfully converted ESD to WIM: {output_path}")

        except Exception as e:
            raise OperationError(f"Failed to convert ESD to WIM: {e}")

    def __repr__(self) -> str:
        """String representation."""
        return f"ESDHandler(image_path={self.image_path})"
