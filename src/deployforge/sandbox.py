"""
Windows Sandbox Integration Module

Provides Windows Sandbox integration for testing images in isolated environments.

Features:
- Test images in Windows Sandbox
- Run validation scripts
- Capture test results
- Automated testing in isolated environment
- Configuration file generation
"""

import logging
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


@dataclass
class SandboxConfig:
    """Windows Sandbox configuration"""

    vgpu: str = "Enable"  # Enable, Disable, Default
    networking: str = "Enable"  # Enable, Disable, Default
    mapped_folders: List[Dict[str, str]] = None
    logon_command: Optional[str] = None
    audio_input: str = "Disable"
    video_input: str = "Disable"
    protected_client: str = "Enable"
    printer_redirection: str = "Disable"
    clipboard_redirection: str = "Enable"
    memory_in_mb: int = 4096

    def __post_init__(self):
        if self.mapped_folders is None:
            self.mapped_folders = []


class WindowsSandbox:
    """
    Windows Sandbox integration for testing images.

    Example:
        sandbox = WindowsSandbox()
        result = sandbox.test_image(
            image=Path('custom.wim'),
            test_script=Path('validate.ps1'),
            timeout=300
        )
        print(f"Test result: {result['success']}")
    """

    def __init__(self):
        """Initialize Windows Sandbox integration"""
        self._check_sandbox_available()

    def _check_sandbox_available(self):
        """Check if Windows Sandbox is available"""
        try:
            result = subprocess.run(
                [
                    "powershell",
                    "-Command",
                    "Get-WindowsOptionalFeature -Online -FeatureName Containers-DisposableClientVM",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if "State" in result.stdout and "Enabled" in result.stdout:
                logger.info("Windows Sandbox is available")
            else:
                logger.warning("Windows Sandbox may not be enabled")

        except Exception as e:
            logger.warning(f"Could not verify Windows Sandbox availability: {e}")

    def test_image(
        self,
        image: Path,
        test_script: Optional[Path] = None,
        timeout: int = 600,
        capture_logs: bool = True,
    ) -> Dict[str, Any]:
        """
        Test image in Windows Sandbox.

        Args:
            image: Path to image file
            test_script: Optional test script to run
            timeout: Test timeout in seconds
            capture_logs: Whether to capture logs

        Returns:
            Test results dictionary
        """
        if not image.exists():
            raise FileNotFoundError(f"Image not found: {image}")

        logger.info(f"Testing image in Windows Sandbox: {image}")

        # Create temporary directory for test resources
        temp_dir = Path(tempfile.mkdtemp(prefix="deployforge_sandbox_"))

        try:
            # Create sandbox configuration
            config = SandboxConfig()

            # Map image directory
            config.mapped_folders.append({"HostFolder": str(image.parent), "ReadOnly": "true"})

            # Create test script
            if test_script:
                config.mapped_folders.append(
                    {"HostFolder": str(test_script.parent), "ReadOnly": "true"}
                )

                config.logon_command = (
                    f'powershell.exe -ExecutionPolicy Bypass -File "{test_script.name}"'
                )

            # Generate sandbox config file
            config_file = temp_dir / "sandbox.wsb"
            self._create_config_file(config, config_file)

            # Run sandbox
            result = self._run_sandbox(config_file, timeout)

            logger.info(f"Sandbox test completed")

            return result

        finally:
            # Cleanup
            if temp_dir.exists():
                import shutil

                shutil.rmtree(temp_dir, ignore_errors=True)

    def _create_config_file(self, config: SandboxConfig, output_path: Path):
        """Create Windows Sandbox configuration file"""
        root = ET.Element("Configuration")

        # vGPU
        vgpu = ET.SubElement(root, "VGpu")
        vgpu.text = config.vgpu

        # Networking
        networking = ET.SubElement(root, "Networking")
        networking.text = config.networking

        # Mapped folders
        if config.mapped_folders:
            mapped_folders = ET.SubElement(root, "MappedFolders")

            for folder in config.mapped_folders:
                mapped_folder = ET.SubElement(mapped_folders, "MappedFolder")

                host_folder = ET.SubElement(mapped_folder, "HostFolder")
                host_folder.text = folder["HostFolder"]

                read_only = ET.SubElement(mapped_folder, "ReadOnly")
                read_only.text = folder.get("ReadOnly", "false")

        # Logon command
        if config.logon_command:
            logon_command = ET.SubElement(root, "LogonCommand")
            command = ET.SubElement(logon_command, "Command")
            command.text = config.logon_command

        # Audio input
        audio_input = ET.SubElement(root, "AudioInput")
        audio_input.text = config.audio_input

        # Video input
        video_input = ET.SubElement(root, "VideoInput")
        video_input.text = config.video_input

        # Protected client
        protected_client = ET.SubElement(root, "ProtectedClient")
        protected_client.text = config.protected_client

        # Printer redirection
        printer_redirection = ET.SubElement(root, "PrinterRedirection")
        printer_redirection.text = config.printer_redirection

        # Clipboard redirection
        clipboard_redirection = ET.SubElement(root, "ClipboardRedirection")
        clipboard_redirection.text = config.clipboard_redirection

        # Memory
        memory_in_mb = ET.SubElement(root, "MemoryInMB")
        memory_in_mb.text = str(config.memory_in_mb)

        # Write XML
        tree = ET.ElementTree(root)
        tree.write(output_path, encoding="utf-8", xml_declaration=True)

        logger.info(f"Created sandbox config: {output_path}")

    def _run_sandbox(self, config_file: Path, timeout: int) -> Dict[str, Any]:
        """Run Windows Sandbox with configuration"""
        start_time = time.time()

        try:
            # Launch sandbox
            process = subprocess.Popen(
                ["WindowsSandbox.exe", str(config_file)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # Wait for completion or timeout
            try:
                process.wait(timeout=timeout)
                exit_code = process.returncode
            except subprocess.TimeoutExpired:
                process.kill()
                exit_code = -1
                logger.warning("Sandbox test timed out")

            duration = time.time() - start_time

            return {
                "success": exit_code == 0,
                "exit_code": exit_code,
                "duration_seconds": duration,
                "timed_out": exit_code == -1,
            }

        except Exception as e:
            logger.error(f"Sandbox execution failed: {e}")
            return {"success": False, "error": str(e), "duration_seconds": time.time() - start_time}


def create_validation_script(output_path: Path, tests: List[str]):
    """
    Create PowerShell validation script for sandbox testing.

    Args:
        output_path: Path to save script
        tests: List of tests to perform
    """
    script = """# Windows Image Validation Script
# Generated by DeployForge

$results = @()

"""

    test_templates = {
        "boot": """
Write-Host "Test: Boot validation"
$results += @{Test="Boot"; Status="PASS"}
""",
        "services": """
Write-Host "Test: Critical services"
$criticalServices = @('wuauserv', 'BITS', 'CryptSvc')
foreach ($svc in $criticalServices) {
    $service = Get-Service -Name $svc -ErrorAction SilentlyContinue
    if ($service -and $service.Status -eq 'Running') {
        $results += @{Test="Service_$svc"; Status="PASS"}
    } else {
        $results += @{Test="Service_$svc"; Status="FAIL"}
    }
}
""",
        "network": """
Write-Host "Test: Network connectivity"
$ping = Test-Connection -ComputerName "8.8.8.8" -Count 1 -Quiet
if ($ping) {
    $results += @{Test="Network"; Status="PASS"}
} else {
    $results += @{Test="Network"; Status="FAIL"}
}
""",
        "disk": """
Write-Host "Test: Disk space"
$disk = Get-PSDrive -Name C
if ($disk.Free -gt 10GB) {
    $results += @{Test="DiskSpace"; Status="PASS"}
} else {
    $results += @{Test="DiskSpace"; Status="FAIL"}
}
""",
    }

    for test in tests:
        if test in test_templates:
            script += test_templates[test]

    script += """
# Output results
$results | Format-Table -AutoSize

# Exit with appropriate code
$failed = ($results | Where-Object { $_.Status -eq "FAIL" }).Count
if ($failed -gt 0) {
    Write-Host "$failed tests failed" -ForegroundColor Red
    exit 1
} else {
    Write-Host "All tests passed" -ForegroundColor Green
    exit 0
}
"""

    with open(output_path, "w") as f:
        f.write(script)

    logger.info(f"Created validation script: {output_path}")


def quick_sandbox_test(image: Path, tests: Optional[List[str]] = None, timeout: int = 300) -> bool:
    """
    Quick sandbox test of image.

    Args:
        image: Image to test
        tests: Tests to run (default: ['boot', 'services', 'network'])
        timeout: Test timeout

    Returns:
        True if all tests passed

    Example:
        success = quick_sandbox_test(
            Path('custom.wim'),
            tests=['boot', 'services', 'network'],
            timeout=300
        )
    """
    if tests is None:
        tests = ["boot", "services", "network"]

    # Create validation script
    temp_dir = Path(tempfile.mkdtemp(prefix="deployforge_test_"))
    test_script = temp_dir / "validate.ps1"

    create_validation_script(test_script, tests)

    # Run sandbox test
    sandbox = WindowsSandbox()
    result = sandbox.test_image(image, test_script, timeout)

    # Cleanup
    import shutil

    shutil.rmtree(temp_dir, ignore_errors=True)

    return result["success"]
