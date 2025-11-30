"""
MDT/SCCM Integration Module

Provides integration with Microsoft Deployment Toolkit (MDT) and
System Center Configuration Manager (SCCM) for enterprise deployment.

Features:
- MDT deployment share management
- Task sequence creation and modification
- Application and driver import
- SCCM package creation
- OS image deployment
"""

import logging
import subprocess
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid

logger = logging.getLogger(__name__)


class TaskSequenceType(Enum):
    """MDT/SCCM task sequence types"""

    STANDARD_CLIENT = "Standard Client Task Sequence"
    CUSTOM = "Custom Task Sequence"
    REPLACE_COMPUTER = "Replace Computer"
    REFRESH_COMPUTER = "Refresh Computer"
    BARE_METAL = "Bare Metal Deployment"


class MDTApplicationType(Enum):
    """MDT application types"""

    APPLICATION = "Application"
    BUNDLE = "Bundle"


@dataclass
class MDTApplication:
    """MDT application definition"""

    name: str
    source_path: Path
    command_line: str
    working_directory: str = ""
    quiet_install: bool = True
    dependencies: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "source_path": str(self.source_path),
            "command_line": self.command_line,
            "working_directory": self.working_directory,
            "quiet_install": self.quiet_install,
            "dependencies": self.dependencies,
        }


@dataclass
class MDTDriver:
    """MDT driver definition"""

    name: str
    source_path: Path
    manufacturer: str = ""
    model: str = ""
    version: str = ""
    platform: str = "x64"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "source_path": str(self.source_path),
            "manufacturer": self.manufacturer,
            "model": self.model,
            "version": self.version,
            "platform": self.platform,
        }


@dataclass
class TaskSequenceStep:
    """Task sequence step definition"""

    name: str
    type: str
    command: Optional[str] = None
    condition: Optional[str] = None
    success_codes: List[int] = field(default_factory=lambda: [0])
    continue_on_error: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "type": self.type,
            "command": self.command,
            "condition": self.condition,
            "success_codes": self.success_codes,
            "continue_on_error": self.continue_on_error,
        }


class MDTIntegration:
    """
    MDT (Microsoft Deployment Toolkit) integration.

    Example:
        mdt = MDTIntegration(deployment_share=Path('\\\\server\\DeploymentShare$'))
        mdt.import_image(Path('custom.wim'), 'Windows 11 Custom')
        mdt.create_task_sequence(
            name='Deploy Windows 11',
            image='custom.wim',
            applications=['Office 365', 'Adobe Reader']
        )
    """

    def __init__(self, deployment_share: Path):
        """
        Initialize MDT integration.

        Args:
            deployment_share: Path to MDT deployment share
        """
        self.deployment_share = deployment_share
        self.operating_systems_path = deployment_share / "Operating Systems"
        self.applications_path = deployment_share / "Applications"
        self.drivers_path = deployment_share / "Out-of-Box Drivers"
        self.task_sequences_path = deployment_share / "Control"
        self.scripts_path = deployment_share / "Scripts"

        # Verify deployment share exists
        if not deployment_share.exists():
            raise FileNotFoundError(f"MDT deployment share not found: {deployment_share}")

    def import_image(
        self, image_path: Path, os_name: str, destination_folder: Optional[str] = None
    ) -> Path:
        """
        Import OS image into MDT.

        Args:
            image_path: Path to WIM file
            os_name: Name for the OS in MDT
            destination_folder: Optional subfolder in Operating Systems

        Returns:
            Path to imported OS folder
        """
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Create destination folder
        if destination_folder:
            os_dest = self.operating_systems_path / destination_folder / os_name
        else:
            os_dest = self.operating_systems_path / os_name

        os_dest.mkdir(parents=True, exist_ok=True)

        # Copy image
        dest_wim = os_dest / image_path.name
        shutil.copy2(image_path, dest_wim)

        logger.info(f"Imported OS image '{os_name}' to MDT")

        # Update MDT database (if using PowerShell MDT module)
        self._update_mdt_database()

        return os_dest

    def import_application(self, app: MDTApplication) -> Path:
        """
        Import application into MDT.

        Args:
            app: MDT application definition

        Returns:
            Path to imported application folder
        """
        # Create application folder
        app_dest = self.applications_path / app.name
        app_dest.mkdir(parents=True, exist_ok=True)

        # Copy source files
        if app.source_path.is_dir():
            for item in app.source_path.iterdir():
                if item.is_file():
                    shutil.copy2(item, app_dest / item.name)
        else:
            shutil.copy2(app.source_path, app_dest / app.source_path.name)

        # Create application XML
        self._create_application_xml(app, app_dest)

        logger.info(f"Imported application '{app.name}' to MDT")

        return app_dest

    def import_driver(self, driver: MDTDriver) -> Path:
        """
        Import driver into MDT.

        Args:
            driver: MDT driver definition

        Returns:
            Path to imported driver folder
        """
        # Create driver folder structure: Manufacturer/Model
        if driver.manufacturer and driver.model:
            driver_dest = self.drivers_path / driver.manufacturer / driver.model
        else:
            driver_dest = self.drivers_path / driver.name

        driver_dest.mkdir(parents=True, exist_ok=True)

        # Copy driver files
        if driver.source_path.is_dir():
            for item in driver.source_path.rglob("*"):
                if item.is_file():
                    rel_path = item.relative_to(driver.source_path)
                    dest_file = driver_dest / rel_path
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, dest_file)
        else:
            shutil.copy2(driver.source_path, driver_dest / driver.source_path.name)

        logger.info(f"Imported driver '{driver.name}' to MDT")

        return driver_dest

    def create_task_sequence(
        self,
        name: str,
        ts_id: Optional[str] = None,
        image: Optional[str] = None,
        applications: Optional[List[str]] = None,
        drivers: Optional[List[str]] = None,
        ts_type: TaskSequenceType = TaskSequenceType.STANDARD_CLIENT,
    ) -> Path:
        """
        Create MDT task sequence.

        Args:
            name: Task sequence name
            ts_id: Task sequence ID (auto-generated if not provided)
            image: OS image name
            applications: List of application names to install
            drivers: List of driver selections
            ts_type: Task sequence type

        Returns:
            Path to task sequence folder
        """
        if ts_id is None:
            ts_id = name.replace(" ", "_").upper()

        ts_folder = self.task_sequences_path / ts_id
        ts_folder.mkdir(parents=True, exist_ok=True)

        # Create ts.xml
        ts_xml_path = ts_folder / "ts.xml"
        self._create_task_sequence_xml(
            name=name,
            ts_id=ts_id,
            image=image,
            applications=applications or [],
            drivers=drivers or [],
            ts_type=ts_type,
            output_path=ts_xml_path,
        )

        logger.info(f"Created task sequence '{name}' (ID: {ts_id})")

        return ts_folder

    def add_task_sequence_step(
        self, ts_id: str, step: TaskSequenceStep, group: Optional[str] = None
    ):
        """
        Add step to existing task sequence.

        Args:
            ts_id: Task sequence ID
            step: Task sequence step
            group: Optional group name to add step to
        """
        ts_xml_path = self.task_sequences_path / ts_id / "ts.xml"

        if not ts_xml_path.exists():
            raise FileNotFoundError(f"Task sequence not found: {ts_id}")

        # Parse existing XML
        tree = ET.parse(ts_xml_path)
        root = tree.getroot()

        # Create step element
        step_elem = ET.SubElement(root.find(".//sequence"), "step")
        step_elem.set("name", step.name)
        step_elem.set("type", step.type)

        if step.command:
            step_elem.set("command", step.command)

        if step.condition:
            condition_elem = ET.SubElement(step_elem, "condition")
            condition_elem.text = step.condition

        # Save updated XML
        tree.write(ts_xml_path, encoding="utf-8", xml_declaration=True)

        logger.info(f"Added step '{step.name}' to task sequence '{ts_id}'")

    def create_selection_profile(
        self,
        name: str,
        include_os: Optional[List[str]] = None,
        include_apps: Optional[List[str]] = None,
        include_drivers: Optional[List[str]] = None,
    ) -> Path:
        """
        Create MDT selection profile.

        Args:
            name: Profile name
            include_os: OS names to include
            include_apps: Application names to include
            include_drivers: Driver names to include

        Returns:
            Path to selection profile
        """
        profiles_path = self.deployment_share / "Control" / "SelectionProfiles"
        profiles_path.mkdir(parents=True, exist_ok=True)

        profile_path = profiles_path / f"{name}.xml"

        # Create selection profile XML
        root = ET.Element("SelectionProfile")
        root.set("name", name)

        if include_os:
            os_elem = ET.SubElement(root, "OperatingSystems")
            for os in include_os:
                item = ET.SubElement(os_elem, "item")
                item.text = os

        if include_apps:
            apps_elem = ET.SubElement(root, "Applications")
            for app in include_apps:
                item = ET.SubElement(apps_elem, "item")
                item.text = app

        if include_drivers:
            drivers_elem = ET.SubElement(root, "Drivers")
            for driver in include_drivers:
                item = ET.SubElement(drivers_elem, "item")
                item.text = driver

        tree = ET.ElementTree(root)
        tree.write(profile_path, encoding="utf-8", xml_declaration=True)

        logger.info(f"Created selection profile '{name}'")

        return profile_path

    def update_bootstrap_ini(self, settings: Dict[str, Any]):
        """
        Update Bootstrap.ini with settings.

        Args:
            settings: Dictionary of settings to update
        """
        bootstrap_path = self.deployment_share / "Control" / "Bootstrap.ini"

        # Read existing content
        lines = []
        if bootstrap_path.exists():
            with open(bootstrap_path, "r") as f:
                lines = f.readlines()

        # Update settings
        updated = False
        for key, value in settings.items():
            found = False
            for i, line in enumerate(lines):
                if line.startswith(f"{key}="):
                    lines[i] = f"{key}={value}\n"
                    found = True
                    break

            if not found:
                lines.append(f"{key}={value}\n")

        # Write back
        with open(bootstrap_path, "w") as f:
            f.writelines(lines)

        logger.info("Updated Bootstrap.ini")

    def update_customsettings_ini(self, settings: Dict[str, Any]):
        """
        Update CustomSettings.ini with settings.

        Args:
            settings: Dictionary of settings to update
        """
        customsettings_path = self.deployment_share / "Control" / "CustomSettings.ini"

        # Read existing content
        lines = []
        if customsettings_path.exists():
            with open(customsettings_path, "r") as f:
                lines = f.readlines()

        # Update settings
        for key, value in settings.items():
            found = False
            for i, line in enumerate(lines):
                if line.startswith(f"{key}="):
                    lines[i] = f"{key}={value}\n"
                    found = True
                    break

            if not found:
                # Add to [Default] section
                for i, line in enumerate(lines):
                    if line.strip() == "[Default]":
                        lines.insert(i + 1, f"{key}={value}\n")
                        break

        # Write back
        with open(customsettings_path, "w") as f:
            f.writelines(lines)

        logger.info("Updated CustomSettings.ini")

    def _create_application_xml(self, app: MDTApplication, app_folder: Path):
        """Create MDT application XML"""
        xml_path = app_folder / "application.xml"

        root = ET.Element("Application")
        root.set("guid", str(uuid.uuid4()))

        name_elem = ET.SubElement(root, "Name")
        name_elem.text = app.name

        command_elem = ET.SubElement(root, "CommandLine")
        command_elem.text = app.command_line

        if app.working_directory:
            workdir_elem = ET.SubElement(root, "WorkingDirectory")
            workdir_elem.text = app.working_directory

        quiet_elem = ET.SubElement(root, "QuietInstall")
        quiet_elem.text = str(app.quiet_install).lower()

        if app.dependencies:
            deps_elem = ET.SubElement(root, "Dependencies")
            for dep in app.dependencies:
                dep_item = ET.SubElement(deps_elem, "Dependency")
                dep_item.text = dep

        tree = ET.ElementTree(root)
        tree.write(xml_path, encoding="utf-8", xml_declaration=True)

    def _create_task_sequence_xml(
        self,
        name: str,
        ts_id: str,
        image: Optional[str],
        applications: List[str],
        drivers: List[str],
        ts_type: TaskSequenceType,
        output_path: Path,
    ):
        """Create MDT task sequence XML"""
        root = ET.Element("sequence")
        root.set("version", "3.00")
        root.set("name", name)
        root.set("guid", str(uuid.uuid4()))

        # Add metadata
        metadata = ET.SubElement(root, "globalVarList")

        id_elem = ET.SubElement(metadata, "variable")
        id_elem.set("name", "TaskSequenceID")
        id_elem.set("property", "TaskSequenceID")
        id_elem.text = ts_id

        name_elem = ET.SubElement(metadata, "variable")
        name_elem.set("name", "TaskSequenceName")
        name_elem.set("property", "TaskSequenceName")
        name_elem.text = name

        # Create standard groups
        groups = [
            "Initialization",
            "Validation",
            "State Capture",
            "Preinstall",
            "Install",
            "Postinstall",
            "State Restore",
            "Applications",
            "Finalize",
        ]

        for group in groups:
            group_elem = ET.SubElement(root, "group")
            group_elem.set("name", group)
            group_elem.set("expand", "true")

            # Add steps based on group
            if group == "Install" and image:
                step = ET.SubElement(group_elem, "step")
                step.set("type", "BDD_InstallOS")
                step.set("name", "Install Operating System")

                var = ET.SubElement(step, "defaultVarList")
                os_var = ET.SubElement(var, "variable")
                os_var.set("name", "OSGUID")
                os_var.text = image

            elif group == "Applications" and applications:
                for app in applications:
                    step = ET.SubElement(group_elem, "step")
                    step.set("type", "BDD_InstallApplication")
                    step.set("name", f"Install {app}")

                    var = ET.SubElement(step, "defaultVarList")
                    app_var = ET.SubElement(var, "variable")
                    app_var.set("name", "ApplicationGUID")
                    app_var.text = app

        tree = ET.ElementTree(root)
        tree.write(output_path, encoding="utf-8", xml_declaration=True)

    def _update_mdt_database(self):
        """Update MDT database (requires PowerShell MDT module)"""
        try:
            # Try to update MDT database
            ps_script = f"""
            Import-Module 'C:\\Program Files\\Microsoft Deployment Toolkit\\bin\\MicrosoftDeploymentToolkit.psd1'
            New-PSDrive -Name "DS001" -PSProvider "MDTProvider" -Root "{self.deployment_share}"
            Update-MDTDeploymentShare -Path "DS001:"
            Remove-PSDrive -Name "DS001"
            """

            subprocess.run(["powershell", "-Command", ps_script], capture_output=True, timeout=60)

            logger.info("Updated MDT database")
        except Exception as e:
            logger.warning(f"Could not update MDT database: {e}")


class SCCMIntegration:
    """
    SCCM (System Center Configuration Manager) integration.

    Example:
        sccm = SCCMIntegration(server='sccm.corporate.local')
        sccm.create_os_image_package(Path('custom.wim'), 'Windows 11 Custom')
        sccm.create_task_sequence('Deploy Windows 11', 'Windows 11 Custom')
    """

    def __init__(self, server: str, site_code: Optional[str] = None, namespace: str = "root\\SMS"):
        """
        Initialize SCCM integration.

        Args:
            server: SCCM server name
            site_code: SCCM site code
            namespace: WMI namespace
        """
        self.server = server
        self.site_code = site_code
        self.namespace = namespace

    def create_os_image_package(
        self,
        image_path: Path,
        package_name: str,
        package_description: Optional[str] = None,
        source_path: Optional[Path] = None,
    ) -> str:
        """
        Create SCCM OS image package.

        Args:
            image_path: Path to WIM file
            package_name: Package name
            package_description: Optional description
            source_path: Optional source path for package

        Returns:
            Package ID
        """
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Create package using PowerShell SCCM cmdlets
        ps_script = f"""
        Import-Module ConfigurationManager

        $package = New-CMOperatingSystemImage `
            -Name "{package_name}" `
            -Path "{image_path}" `
            -Description "{package_description or package_name}"

        Write-Output $package.PackageID
        """

        try:
            result = subprocess.run(
                ["powershell", "-Command", ps_script], capture_output=True, text=True, check=True
            )

            package_id = result.stdout.strip()
            logger.info(f"Created SCCM OS image package '{package_name}' (ID: {package_id})")
            return package_id

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create SCCM package: {e.stderr}")
            raise

    def create_task_sequence(
        self, name: str, os_image_package_id: str, boot_image_package_id: Optional[str] = None
    ) -> str:
        """
        Create SCCM task sequence.

        Args:
            name: Task sequence name
            os_image_package_id: OS image package ID
            boot_image_package_id: Optional boot image package ID

        Returns:
            Task sequence ID
        """
        ps_script = f"""
        Import-Module ConfigurationManager

        $ts = New-CMTaskSequence `
            -Name "{name}" `
            -OperatingSystemImagePackageId "{os_image_package_id}"

        Write-Output $ts.PackageID
        """

        try:
            result = subprocess.run(
                ["powershell", "-Command", ps_script], capture_output=True, text=True, check=True
            )

            ts_id = result.stdout.strip()
            logger.info(f"Created SCCM task sequence '{name}' (ID: {ts_id})")
            return ts_id

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create SCCM task sequence: {e.stderr}")
            raise

    def distribute_package(self, package_id: str, distribution_points: List[str]):
        """
        Distribute package to distribution points.

        Args:
            package_id: Package ID
            distribution_points: List of distribution point names
        """
        for dp in distribution_points:
            ps_script = f"""
            Import-Module ConfigurationManager

            Start-CMContentDistribution `
                -PackageId "{package_id}" `
                -DistributionPointName "{dp}"
            """

            try:
                subprocess.run(
                    ["powershell", "-Command", ps_script], capture_output=True, check=True
                )

                logger.info(f"Distributed package {package_id} to {dp}")

            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to distribute to {dp}: {e.stderr}")


def create_mdt_deployment(
    deployment_share: Path,
    image_path: Path,
    os_name: str,
    task_sequence_name: str,
    applications: Optional[List[MDTApplication]] = None,
) -> MDTIntegration:
    """
    Create complete MDT deployment in one step.

    Args:
        deployment_share: Path to MDT deployment share
        image_path: Path to OS image WIM
        os_name: Name for OS in MDT
        task_sequence_name: Task sequence name
        applications: Optional list of applications to import

    Returns:
        MDTIntegration instance

    Example:
        mdt = create_mdt_deployment(
            deployment_share=Path('\\\\server\\DeploymentShare$'),
            image_path=Path('custom.wim'),
            os_name='Windows 11 Custom',
            task_sequence_name='Deploy Windows 11',
            applications=[
                MDTApplication(
                    name='Office 365',
                    source_path=Path('apps/office'),
                    command_line='setup.exe /configure config.xml'
                )
            ]
        )
    """
    mdt = MDTIntegration(deployment_share)

    # Import OS image
    mdt.import_image(image_path, os_name)

    # Import applications
    app_names = []
    if applications:
        for app in applications:
            mdt.import_application(app)
            app_names.append(app.name)

    # Create task sequence
    mdt.create_task_sequence(name=task_sequence_name, image=os_name, applications=app_names)

    logger.info(f"Created complete MDT deployment for '{os_name}'")

    return mdt
