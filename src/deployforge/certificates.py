"""
Certificate Management Module

Manages certificate injection into Windows images including:
- Trusted Root CA certificates
- Intermediate CA certificates
- Code signing certificates
- Certificate auto-enrollment configuration
- Certificate store management
"""

import logging
import subprocess
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import tempfile

logger = logging.getLogger(__name__)


class CertificateStore(Enum):
    """Certificate store locations"""

    ROOT = "Root"  # Trusted Root Certification Authorities
    CA = "CA"  # Intermediate Certification Authorities
    MY = "My"  # Personal
    TRUSTED_PUBLISHER = "TrustedPublisher"  # Trusted Publishers
    TRUSTED_PEOPLE = "TrustedPeople"  # Trusted People
    DISALLOWED = "Disallowed"  # Untrusted Certificates


class CertificateFormat(Enum):
    """Certificate file formats"""

    CER = "cer"  # DER or Base64 encoded certificate
    CRT = "crt"  # Same as CER
    PFX = "pfx"  # PKCS#12 (contains private key)
    P12 = "p12"  # Same as PFX
    P7B = "p7b"  # PKCS#7 (certificate chain)
    P7C = "p7c"  # Same as P7B


@dataclass
class Certificate:
    """Represents a certificate to be installed"""

    file_path: Path
    store: CertificateStore
    description: str = ""

    def __post_init__(self):
        if not self.file_path.exists():
            raise FileNotFoundError(f"Certificate file not found: {self.file_path}")

        # Detect format from extension
        ext = self.file_path.suffix.lower().lstrip(".")
        try:
            self.format = CertificateFormat(ext)
        except ValueError:
            # Default to CER if unknown
            self.format = CertificateFormat.CER

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "file_path": str(self.file_path),
            "store": self.store.value,
            "format": self.format.value,
            "description": self.description,
        }


@dataclass
class AutoEnrollmentConfig:
    """Configuration for certificate auto-enrollment"""

    enabled: bool = True
    ca_server: Optional[str] = None
    policy_server: Optional[str] = None
    enroll_on_behalf: bool = False
    renew_expired_certificates: bool = True
    renew_pending_certificates: bool = True
    update_certificates_that_use_templates: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "enabled": self.enabled,
            "ca_server": self.ca_server,
            "policy_server": self.policy_server,
            "enroll_on_behalf": self.enroll_on_behalf,
            "renew_expired_certificates": self.renew_expired_certificates,
            "renew_pending_certificates": self.renew_pending_certificates,
            "update_certificates_that_use_templates": self.update_certificates_that_use_templates,
        }


@dataclass
class CRLDistributionConfig:
    """CRL Distribution Point configuration"""

    enabled: bool = True
    crl_urls: List[str] = field(default_factory=list)
    ocsp_urls: List[str] = field(default_factory=list)
    cache_timeout_minutes: int = 1440  # 24 hours

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "enabled": self.enabled,
            "crl_urls": self.crl_urls,
            "ocsp_urls": self.ocsp_urls,
            "cache_timeout_minutes": self.cache_timeout_minutes,
        }


class CertificateManager:
    """
    Manages certificate installation and configuration in Windows images.

    Example:
        cert_mgr = CertificateManager(Path('install.wim'))
        cert_mgr.mount()
        cert_mgr.add_trusted_root_ca(Path('corporate-root-ca.cer'))
        cert_mgr.add_intermediate_ca(Path('issuing-ca.cer'))
        cert_mgr.configure_auto_enrollment('ca.corporate.local')
        cert_mgr.unmount(save_changes=True)
    """

    def __init__(self, image_path: Path, index: int = 1):
        """
        Initialize certificate manager.

        Args:
            image_path: Path to WIM/VHDX image
            index: Image index (for WIM files)
        """
        self.image_path = image_path
        self.index = index
        self.mount_point: Optional[Path] = None
        self.certificates: List[Certificate] = []
        self.auto_enrollment: Optional[AutoEnrollmentConfig] = None
        self.crl_config: Optional[CRLDistributionConfig] = None
        self._mounted = False

        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

    def mount(self, mount_point: Optional[Path] = None) -> Path:
        """
        Mount the image.

        Args:
            mount_point: Optional custom mount point

        Returns:
            Path to mount point
        """
        if self._mounted:
            logger.warning("Image already mounted")
            return self.mount_point

        if mount_point is None:
            mount_point = Path(tempfile.mkdtemp(prefix="deployforge_cert_"))

        mount_point.mkdir(parents=True, exist_ok=True)
        self.mount_point = mount_point

        logger.info(f"Mounting {self.image_path} to {mount_point}")

        try:
            if self.image_path.suffix.lower() == ".wim":
                subprocess.run(
                    [
                        "dism",
                        "/Mount-Wim",
                        f"/WimFile:{self.image_path}",
                        f"/Index:{self.index}",
                        f"/MountDir:{mount_point}",
                    ],
                    check=True,
                    capture_output=True,
                )
            elif self.image_path.suffix.lower() in [".vhd", ".vhdx"]:
                subprocess.run(
                    [
                        "dism",
                        "/Mount-Image",
                        f"/ImageFile:{self.image_path}",
                        f"/Index:{self.index}",
                        f"/MountDir:{mount_point}",
                    ],
                    check=True,
                    capture_output=True,
                )
            else:
                raise ValueError(f"Unsupported image format: {self.image_path.suffix}")

            self._mounted = True
            logger.info("Image mounted successfully")
            return mount_point

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to mount image: {e.stderr.decode()}")
            raise

    def unmount(self, save_changes: bool = True):
        """
        Unmount the image.

        Args:
            save_changes: Whether to commit changes
        """
        if not self._mounted:
            logger.warning("Image not mounted")
            return

        logger.info(f"Unmounting {self.mount_point}")

        try:
            commit_flag = "/Commit" if save_changes else "/Discard"
            subprocess.run(
                ["dism", "/Unmount-Image", f"/MountDir:{self.mount_point}", commit_flag],
                check=True,
                capture_output=True,
            )

            self._mounted = False
            logger.info("Image unmounted successfully")

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to unmount image: {e.stderr.decode()}")
            raise

    def add_certificate(self, cert_file: Path, store: CertificateStore, description: str = ""):
        """
        Add a certificate to the specified store.

        Args:
            cert_file: Path to certificate file
            store: Certificate store to add to
            description: Optional description
        """
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        cert = Certificate(cert_file, store, description)
        self.certificates.append(cert)

        # Create certificate store directory structure
        cert_base_path = self.mount_point / "Windows" / "System32" / "CertStore"
        cert_base_path.mkdir(parents=True, exist_ok=True)

        store_path = cert_base_path / store.value
        store_path.mkdir(parents=True, exist_ok=True)

        # Copy certificate to store
        cert_dest = store_path / cert_file.name
        shutil.copy2(cert_file, cert_dest)

        logger.info(f"Added certificate {cert_file.name} to {store.value} store")

        # Create PowerShell script to install certificate on first boot
        self._create_cert_install_script(cert_file.name, store)

    def add_trusted_root_ca(self, cert_file: Path, description: str = ""):
        """
        Add a trusted root CA certificate.

        Args:
            cert_file: Path to root CA certificate
            description: Optional description
        """
        self.add_certificate(cert_file, CertificateStore.ROOT, description)
        logger.info(f"Added trusted root CA: {cert_file.name}")

    def add_intermediate_ca(self, cert_file: Path, description: str = ""):
        """
        Add an intermediate CA certificate.

        Args:
            cert_file: Path to intermediate CA certificate
            description: Optional description
        """
        self.add_certificate(cert_file, CertificateStore.CA, description)
        logger.info(f"Added intermediate CA: {cert_file.name}")

    def add_trusted_publisher(self, cert_file: Path, description: str = ""):
        """
        Add a trusted publisher certificate.

        Args:
            cert_file: Path to publisher certificate
            description: Optional description
        """
        self.add_certificate(cert_file, CertificateStore.TRUSTED_PUBLISHER, description)
        logger.info(f"Added trusted publisher: {cert_file.name}")

    def add_code_signing_cert(
        self, pfx_file: Path, password: Optional[str] = None, description: str = ""
    ):
        """
        Add a code signing certificate (with private key).

        Args:
            pfx_file: Path to PFX/P12 file
            password: Optional password for PFX
            description: Optional description
        """
        if pfx_file.suffix.lower() not in [".pfx", ".p12"]:
            raise ValueError("Code signing certificates must be in PFX/P12 format")

        self.add_certificate(pfx_file, CertificateStore.MY, description)

        # Store password securely if provided
        if password:
            self._create_pfx_import_script(pfx_file.name, password)

        logger.info(f"Added code signing certificate: {pfx_file.name}")

    def configure_auto_enrollment(
        self,
        ca_server: Optional[str] = None,
        policy_server: Optional[str] = None,
        enabled: bool = True,
    ):
        """
        Configure certificate auto-enrollment.

        Args:
            ca_server: CA server FQDN (e.g., 'ca.corporate.local')
            policy_server: Policy server FQDN
            enabled: Whether to enable auto-enrollment
        """
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        self.auto_enrollment = AutoEnrollmentConfig(
            enabled=enabled, ca_server=ca_server, policy_server=policy_server
        )

        # Configure via registry
        self._configure_auto_enrollment_registry()

        logger.info(f"Configured auto-enrollment for CA: {ca_server}")

    def configure_crl_distribution(
        self,
        crl_urls: Optional[List[str]] = None,
        ocsp_urls: Optional[List[str]] = None,
        cache_timeout_minutes: int = 1440,
    ):
        """
        Configure CRL distribution points and OCSP.

        Args:
            crl_urls: List of CRL distribution URLs
            ocsp_urls: List of OCSP responder URLs
            cache_timeout_minutes: Cache timeout in minutes
        """
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        self.crl_config = CRLDistributionConfig(
            enabled=True,
            crl_urls=crl_urls or [],
            ocsp_urls=ocsp_urls or [],
            cache_timeout_minutes=cache_timeout_minutes,
        )

        # Configure via registry
        self._configure_crl_registry()

        logger.info("Configured CRL distribution points")

    def _create_cert_install_script(self, cert_filename: str, store: CertificateStore):
        """Create PowerShell script to install certificate on first boot"""
        script_dir = self.mount_point / "Windows" / "Setup" / "Scripts"
        script_dir.mkdir(parents=True, exist_ok=True)

        script_path = script_dir / "install_certificates.ps1"

        # Append to existing script or create new
        mode = "a" if script_path.exists() else "w"

        with open(script_path, mode) as f:
            if mode == "w":
                f.write("# Certificate Installation Script\n")
                f.write("# Generated by DeployForge\n\n")
                f.write("Set-Location $PSScriptRoot\n\n")

            cert_path = f"C:\\Windows\\System32\\CertStore\\{store.value}\\{cert_filename}"

            f.write(f"\n# Install {cert_filename} to {store.value}\n")
            f.write(f"Write-Host 'Installing certificate: {cert_filename}'\n")
            f.write(
                f"$cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2\n"
            )
            f.write(f"$cert.Import('{cert_path}')\n")
            f.write(
                f"$store = New-Object System.Security.Cryptography.X509Certificates.X509Store('{store.value}', 'LocalMachine')\n"
            )
            f.write(f"$store.Open('ReadWrite')\n")
            f.write(f"$store.Add($cert)\n")
            f.write(f"$store.Close()\n")
            f.write(f"Write-Host 'Certificate installed successfully'\n\n")

        # Add to SetupComplete.cmd
        setupcomplete_path = script_dir / "SetupComplete.cmd"
        mode = "a" if setupcomplete_path.exists() else "w"

        with open(setupcomplete_path, mode) as f:
            if mode == "w":
                f.write("@echo off\n")
                f.write("REM Certificate installation\n")

            f.write(
                'powershell.exe -ExecutionPolicy Bypass -File "%~dp0install_certificates.ps1"\n'
            )

    def _create_pfx_import_script(self, pfx_filename: str, password: str):
        """Create script to import PFX with password"""
        script_dir = self.mount_point / "Windows" / "Setup" / "Scripts"
        script_dir.mkdir(parents=True, exist_ok=True)

        script_path = script_dir / "install_pfx_certificates.ps1"

        mode = "a" if script_path.exists() else "w"

        with open(script_path, mode) as f:
            if mode == "w":
                f.write("# PFX Certificate Installation Script\n")
                f.write("# Generated by DeployForge\n\n")

            cert_path = f"C:\\Windows\\System32\\CertStore\\My\\{pfx_filename}"

            f.write(f"\n# Import {pfx_filename}\n")
            f.write(f"Write-Host 'Importing PFX certificate: {pfx_filename}'\n")
            f.write(
                f"$password = ConvertTo-SecureString -String '{password}' -AsPlainText -Force\n"
            )
            f.write(
                f"Import-PfxCertificate -FilePath '{cert_path}' -CertStoreLocation 'Cert:\\LocalMachine\\My' -Password $password\n"
            )
            f.write(f"Write-Host 'PFX certificate imported successfully'\n\n")

        # Add to SetupComplete.cmd
        setupcomplete_path = script_dir / "SetupComplete.cmd"
        mode = "a" if setupcomplete_path.exists() else "w"

        with open(setupcomplete_path, mode) as f:
            if mode == "w":
                f.write("@echo off\n")
                f.write("REM PFX certificate installation\n")

            f.write(
                'powershell.exe -ExecutionPolicy Bypass -File "%~dp0install_pfx_certificates.ps1"\n'
            )

    def _configure_auto_enrollment_registry(self):
        """Configure auto-enrollment via registry"""
        if not self.auto_enrollment:
            return

        # Load SYSTEM hive
        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SYSTEM"
        hive_key = "HKLM\\TEMP_SYSTEM"

        try:
            subprocess.run(
                ["reg", "load", hive_key, str(hive_file)], check=True, capture_output=True
            )

            # Configure auto-enrollment policy
            policy_key = f"{hive_key}\\ControlSet001\\Services\\CertSvc\\Configuration"

            if self.auto_enrollment.enabled:
                # Enable auto-enrollment
                subprocess.run(
                    [
                        "reg",
                        "add",
                        policy_key,
                        "/v",
                        "EnableAutoEnrollment",
                        "/t",
                        "REG_DWORD",
                        "/d",
                        "1",
                        "/f",
                    ],
                    check=True,
                    capture_output=True,
                )

                # Set CA server
                if self.auto_enrollment.ca_server:
                    subprocess.run(
                        [
                            "reg",
                            "add",
                            policy_key,
                            "/v",
                            "CAServer",
                            "/t",
                            "REG_SZ",
                            "/d",
                            self.auto_enrollment.ca_server,
                            "/f",
                        ],
                        check=True,
                        capture_output=True,
                    )

                # Set policy server
                if self.auto_enrollment.policy_server:
                    subprocess.run(
                        [
                            "reg",
                            "add",
                            policy_key,
                            "/v",
                            "PolicyServer",
                            "/t",
                            "REG_SZ",
                            "/d",
                            self.auto_enrollment.policy_server,
                            "/f",
                        ],
                        check=True,
                        capture_output=True,
                    )

            logger.info("Auto-enrollment registry configuration applied")

        finally:
            # Unload hive
            subprocess.run(["reg", "unload", hive_key], check=True, capture_output=True)

    def _configure_crl_registry(self):
        """Configure CRL distribution via registry"""
        if not self.crl_config:
            return

        # Load SOFTWARE hive
        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SOFTWARE"
        hive_key = "HKLM\\TEMP_SOFTWARE"

        try:
            subprocess.run(
                ["reg", "load", hive_key, str(hive_file)], check=True, capture_output=True
            )

            # Configure CRL settings
            crl_key = f"{hive_key}\\Policies\\Microsoft\\SystemCertificates\\AuthRoot"

            # Set cache timeout
            subprocess.run(
                [
                    "reg",
                    "add",
                    crl_key,
                    "/v",
                    "ChainCacheResyncFiletime",
                    "/t",
                    "REG_DWORD",
                    "/d",
                    str(self.crl_config.cache_timeout_minutes * 60),
                    "/f",
                ],
                check=True,
                capture_output=True,
            )

            logger.info("CRL distribution registry configuration applied")

        finally:
            # Unload hive
            subprocess.run(["reg", "unload", hive_key], check=True, capture_output=True)

    def export_manifest(self, output_path: Path):
        """
        Export certificate manifest to JSON.

        Args:
            output_path: Path to save manifest JSON
        """
        manifest = {
            "certificates": [cert.to_dict() for cert in self.certificates],
            "auto_enrollment": self.auto_enrollment.to_dict() if self.auto_enrollment else None,
            "crl_config": self.crl_config.to_dict() if self.crl_config else None,
        }

        with open(output_path, "w") as f:
            json.dump(manifest, f, indent=2)

        logger.info(f"Certificate manifest exported to {output_path}")

    def import_manifest(self, manifest_path: Path):
        """
        Import certificate manifest from JSON.

        Args:
            manifest_path: Path to manifest JSON
        """
        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        # Import certificates
        for cert_data in manifest.get("certificates", []):
            cert_file = Path(cert_data["file_path"])
            store = CertificateStore(cert_data["store"])
            description = cert_data.get("description", "")
            self.add_certificate(cert_file, store, description)

        # Import auto-enrollment config
        if manifest.get("auto_enrollment"):
            ae_data = manifest["auto_enrollment"]
            if ae_data.get("enabled"):
                self.configure_auto_enrollment(
                    ca_server=ae_data.get("ca_server"),
                    policy_server=ae_data.get("policy_server"),
                    enabled=ae_data["enabled"],
                )

        # Import CRL config
        if manifest.get("crl_config"):
            crl_data = manifest["crl_config"]
            if crl_data.get("enabled"):
                self.configure_crl_distribution(
                    crl_urls=crl_data.get("crl_urls", []),
                    ocsp_urls=crl_data.get("ocsp_urls", []),
                    cache_timeout_minutes=crl_data.get("cache_timeout_minutes", 1440),
                )

        logger.info(f"Certificate manifest imported from {manifest_path}")


def configure_enterprise_pki(
    image_path: Path,
    root_ca_cert: Path,
    intermediate_ca_certs: Optional[List[Path]] = None,
    ca_server: Optional[str] = None,
    enable_auto_enrollment: bool = True,
) -> CertificateManager:
    """
    Configure enterprise PKI in one step.

    Args:
        image_path: Path to WIM/VHDX image
        root_ca_cert: Path to root CA certificate
        intermediate_ca_certs: List of intermediate CA certificates
        ca_server: CA server FQDN
        enable_auto_enrollment: Whether to enable auto-enrollment

    Returns:
        CertificateManager instance

    Example:
        cert_mgr = configure_enterprise_pki(
            image_path=Path('install.wim'),
            root_ca_cert=Path('certs/root-ca.cer'),
            intermediate_ca_certs=[Path('certs/issuing-ca.cer')],
            ca_server='ca.corporate.local',
            enable_auto_enrollment=True
        )
    """
    cert_mgr = CertificateManager(image_path)
    cert_mgr.mount()

    # Add root CA
    cert_mgr.add_trusted_root_ca(root_ca_cert, "Enterprise Root CA")

    # Add intermediate CAs
    if intermediate_ca_certs:
        for cert in intermediate_ca_certs:
            cert_mgr.add_intermediate_ca(cert, "Enterprise Issuing CA")

    # Configure auto-enrollment
    if enable_auto_enrollment and ca_server:
        cert_mgr.configure_auto_enrollment(ca_server=ca_server)

    cert_mgr.unmount(save_changes=True)

    return cert_mgr
