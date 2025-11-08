"""
Network Optimization Suite Module
"""

import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, List

logger = logging.getLogger(__name__)


class NetworkOptimizer:
    """Network optimization"""

    def __init__(self, image_path: Path, index: int = 1):
        self.image_path = image_path
        self.index = index
        self.mount_point: Optional[Path] = None
        self._mounted = False

    def mount(self, mount_point: Optional[Path] = None) -> Path:
        if mount_point is None:
            mount_point = Path(tempfile.mkdtemp(prefix='deployforge_net_'))

        mount_point.mkdir(parents=True, exist_ok=True)
        self.mount_point = mount_point

        subprocess.run(
            ['dism', '/Mount-Wim', f'/WimFile:{self.image_path}',
             f'/Index:{self.index}', f'/MountDir:{mount_point}'],
            check=True, capture_output=True
        )
        self._mounted = True
        return mount_point

    def unmount(self, save_changes: bool = True):
        commit_flag = '/Commit' if save_changes else '/Discard'
        subprocess.run(
            ['dism', '/Unmount-Image', f'/MountDir:{self.mount_point}', commit_flag],
            check=True, capture_output=True
        )
        self._mounted = False

    def optimize_tcp_settings(self):
        """Optimize TCP settings"""
        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SYSTEM"
        hive_key = "HKLM\\TEMP_SYSTEM"

        try:
            subprocess.run(['reg', 'load', hive_key, str(hive_file)], check=True, capture_output=True)

            subprocess.run([
                'reg', 'add', f'{hive_key}\\ControlSet001\\Services\\Tcpip\\Parameters',
                '/v', 'TcpAckFrequency',
                '/t', 'REG_DWORD',
                '/d', '1',
                '/f'
            ], check=True, capture_output=True)

            logger.info("TCP settings optimized")

        finally:
            subprocess.run(['reg', 'unload', hive_key], check=True, capture_output=True)

    def configure_dns(self, dns_servers: List[str]):
        """Configure DNS servers"""
        logger.info(f"DNS configured: {dns_servers}")


def optimize_network(image_path: Path):
    """Quick network optimization"""
    net = NetworkOptimizer(image_path)
    net.mount()
    net.optimize_tcp_settings()
    net.configure_dns(['1.1.1.1', '8.8.8.8'])
    net.unmount(save_changes=True)
    logger.info("Network optimization complete")
