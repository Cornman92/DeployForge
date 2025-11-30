"""
Cloud Integration Module

Provides integration with cloud platforms for image storage and deployment.

Features:
- Azure Blob Storage integration
- AWS S3 storage integration
- Azure VM image creation
- AWS EC2 AMI creation
- Automated cloud deployment
"""

import logging
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class AzureConfig:
    """Azure configuration."""

    subscription_id: str
    resource_group: str
    storage_account: str
    container_name: str = "images"
    location: str = "eastus"


@dataclass
class AWSConfig:
    """AWS configuration."""

    region: str = "us-east-1"
    bucket_name: str = "deployforge-images"
    profile: Optional[str] = None


@dataclass
class CloudImage:
    """Cloud image metadata."""

    name: str
    size_mb: float
    upload_date: str
    cloud_url: str
    provider: str  # azure, aws
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class AzureIntegration:
    """Azure cloud integration."""

    def __init__(self, config: AzureConfig):
        """
        Initialize Azure integration.

        Args:
            config: Azure configuration
        """
        self.config = config
        self._check_azure_cli()

    def _check_azure_cli(self):
        """Check if Azure CLI is available."""
        try:
            subprocess.run(["az", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                "Azure CLI not found. Install with: https://aka.ms/installazurecliwindows"
            )

    def login(self):
        """Login to Azure."""
        logger.info("Logging in to Azure...")

        try:
            subprocess.run(["az", "login"], check=True)
            logger.info("Azure login successful")
        except subprocess.CalledProcessError as e:
            logger.error(f"Azure login failed: {e}")
            raise

    def upload_image(self, image_path: Path, blob_name: Optional[str] = None) -> str:
        """
        Upload image to Azure Blob Storage.

        Args:
            image_path: Path to image file
            blob_name: Blob name (defaults to filename)

        Returns:
            Blob URL
        """
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        if blob_name is None:
            blob_name = image_path.name

        logger.info(f"Uploading to Azure: {blob_name}")

        try:
            # Create storage account if doesn't exist
            self._ensure_storage_account()

            # Create container if doesn't exist
            self._ensure_container()

            # Upload blob
            result = subprocess.run(
                [
                    "az",
                    "storage",
                    "blob",
                    "upload",
                    "--account-name",
                    self.config.storage_account,
                    "--container-name",
                    self.config.container_name,
                    "--name",
                    blob_name,
                    "--file",
                    str(image_path),
                    "--overwrite",
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            # Get blob URL
            url = self.get_blob_url(blob_name)

            logger.info(f"Upload successful: {url}")

            return url

        except subprocess.CalledProcessError as e:
            logger.error(f"Upload failed: {e.stderr}")
            raise

    def download_image(self, blob_name: str, output_path: Path):
        """
        Download image from Azure Blob Storage.

        Args:
            blob_name: Blob name
            output_path: Local output path
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Downloading from Azure: {blob_name}")

        try:
            subprocess.run(
                [
                    "az",
                    "storage",
                    "blob",
                    "download",
                    "--account-name",
                    self.config.storage_account,
                    "--container-name",
                    self.config.container_name,
                    "--name",
                    blob_name,
                    "--file",
                    str(output_path),
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            logger.info(f"Download successful: {output_path}")

        except subprocess.CalledProcessError as e:
            logger.error(f"Download failed: {e.stderr}")
            raise

    def list_images(self) -> List[CloudImage]:
        """
        List images in Azure storage.

        Returns:
            List of cloud images
        """
        try:
            result = subprocess.run(
                [
                    "az",
                    "storage",
                    "blob",
                    "list",
                    "--account-name",
                    self.config.storage_account,
                    "--container-name",
                    self.config.container_name,
                    "--output",
                    "json",
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            blobs = json.loads(result.stdout)

            images = []
            for blob in blobs:
                images.append(
                    CloudImage(
                        name=blob["name"],
                        size_mb=round(blob["properties"]["contentLength"] / 1024 / 1024, 2),
                        upload_date=blob["properties"]["creationTime"],
                        cloud_url=self.get_blob_url(blob["name"]),
                        provider="azure",
                        metadata=blob.get("metadata", {}),
                    )
                )

            return images

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to list images: {e.stderr}")
            return []

    def create_vm_image(self, vhd_blob_name: str, image_name: str) -> str:
        """
        Create Azure VM image from VHD.

        Args:
            vhd_blob_name: VHD blob name
            image_name: Image name

        Returns:
            Image ID
        """
        logger.info(f"Creating Azure VM image: {image_name}")

        try:
            vhd_url = self.get_blob_url(vhd_blob_name)

            result = subprocess.run(
                [
                    "az",
                    "image",
                    "create",
                    "--resource-group",
                    self.config.resource_group,
                    "--name",
                    image_name,
                    "--source",
                    vhd_url,
                    "--os-type",
                    "Windows",
                    "--location",
                    self.config.location,
                    "--output",
                    "json",
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            image_data = json.loads(result.stdout)
            image_id = image_data["id"]

            logger.info(f"VM image created: {image_id}")

            return image_id

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create VM image: {e.stderr}")
            raise

    def get_blob_url(self, blob_name: str) -> str:
        """
        Get blob URL.

        Args:
            blob_name: Blob name

        Returns:
            Blob URL
        """
        return f"https://{self.config.storage_account}.blob.core.windows.net/{self.config.container_name}/{blob_name}"

    def _ensure_storage_account(self):
        """Ensure storage account exists."""
        try:
            subprocess.run(
                [
                    "az",
                    "storage",
                    "account",
                    "show",
                    "--name",
                    self.config.storage_account,
                    "--resource-group",
                    self.config.resource_group,
                ],
                capture_output=True,
                check=True,
            )
        except subprocess.CalledProcessError:
            # Create storage account
            logger.info(f"Creating storage account: {self.config.storage_account}")
            subprocess.run(
                [
                    "az",
                    "storage",
                    "account",
                    "create",
                    "--name",
                    self.config.storage_account,
                    "--resource-group",
                    self.config.resource_group,
                    "--location",
                    self.config.location,
                    "--sku",
                    "Standard_LRS",
                ],
                check=True,
                capture_output=True,
            )

    def _ensure_container(self):
        """Ensure container exists."""
        try:
            subprocess.run(
                [
                    "az",
                    "storage",
                    "container",
                    "show",
                    "--account-name",
                    self.config.storage_account,
                    "--name",
                    self.config.container_name,
                ],
                capture_output=True,
                check=True,
            )
        except subprocess.CalledProcessError:
            # Create container
            logger.info(f"Creating container: {self.config.container_name}")
            subprocess.run(
                [
                    "az",
                    "storage",
                    "container",
                    "create",
                    "--account-name",
                    self.config.storage_account,
                    "--name",
                    self.config.container_name,
                ],
                check=True,
                capture_output=True,
            )


class AWSIntegration:
    """AWS cloud integration."""

    def __init__(self, config: AWSConfig):
        """
        Initialize AWS integration.

        Args:
            config: AWS configuration
        """
        self.config = config
        self._check_aws_cli()

    def _check_aws_cli(self):
        """Check if AWS CLI is available."""
        try:
            subprocess.run(["aws", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError("AWS CLI not found. Install with: https://aws.amazon.com/cli/")

    def upload_image(self, image_path: Path, key: Optional[str] = None) -> str:
        """
        Upload image to S3.

        Args:
            image_path: Path to image file
            key: S3 key (defaults to filename)

        Returns:
            S3 URL
        """
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        if key is None:
            key = image_path.name

        logger.info(f"Uploading to S3: {key}")

        try:
            # Create bucket if doesn't exist
            self._ensure_bucket()

            # Build command
            cmd = [
                "aws",
                "s3",
                "cp",
                str(image_path),
                f"s3://{self.config.bucket_name}/{key}",
                "--region",
                self.config.region,
            ]

            if self.config.profile:
                cmd.extend(["--profile", self.config.profile])

            subprocess.run(cmd, check=True, capture_output=True)

            # Get URL
            url = f"https://{self.config.bucket_name}.s3.{self.config.region}.amazonaws.com/{key}"

            logger.info(f"Upload successful: {url}")

            return url

        except subprocess.CalledProcessError as e:
            logger.error(f"Upload failed: {e.stderr.decode()}")
            raise

    def download_image(self, key: str, output_path: Path):
        """
        Download image from S3.

        Args:
            key: S3 key
            output_path: Local output path
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Downloading from S3: {key}")

        try:
            cmd = [
                "aws",
                "s3",
                "cp",
                f"s3://{self.config.bucket_name}/{key}",
                str(output_path),
                "--region",
                self.config.region,
            ]

            if self.config.profile:
                cmd.extend(["--profile", self.config.profile])

            subprocess.run(cmd, check=True, capture_output=True)

            logger.info(f"Download successful: {output_path}")

        except subprocess.CalledProcessError as e:
            logger.error(f"Download failed: {e.stderr.decode()}")
            raise

    def list_images(self) -> List[CloudImage]:
        """
        List images in S3 bucket.

        Returns:
            List of cloud images
        """
        try:
            cmd = [
                "aws",
                "s3api",
                "list-objects-v2",
                "--bucket",
                self.config.bucket_name,
                "--region",
                self.config.region,
                "--output",
                "json",
            ]

            if self.config.profile:
                cmd.extend(["--profile", self.config.profile])

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            data = json.loads(result.stdout)

            images = []
            for obj in data.get("Contents", []):
                images.append(
                    CloudImage(
                        name=obj["Key"],
                        size_mb=round(obj["Size"] / 1024 / 1024, 2),
                        upload_date=obj["LastModified"],
                        cloud_url=f"https://{self.config.bucket_name}.s3.{self.config.region}.amazonaws.com/{obj['Key']}",
                        provider="aws",
                    )
                )

            return images

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to list images: {e.stderr.decode()}")
            return []

    def create_ami(self, snapshot_id: str, ami_name: str, description: str = "") -> str:
        """
        Create EC2 AMI from snapshot.

        Args:
            snapshot_id: EBS snapshot ID
            ami_name: AMI name
            description: AMI description

        Returns:
            AMI ID
        """
        logger.info(f"Creating EC2 AMI: {ami_name}")

        try:
            cmd = [
                "aws",
                "ec2",
                "register-image",
                "--name",
                ami_name,
                "--description",
                description or f"DeployForge image: {ami_name}",
                "--architecture",
                "x86_64",
                "--root-device-name",
                "/dev/sda1",
                "--block-device-mappings",
                f"DeviceName=/dev/sda1,Ebs={{SnapshotId={snapshot_id}}}",
                "--virtualization-type",
                "hvm",
                "--region",
                self.config.region,
                "--output",
                "json",
            ]

            if self.config.profile:
                cmd.extend(["--profile", self.config.profile])

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            data = json.loads(result.stdout)
            ami_id = data["ImageId"]

            logger.info(f"AMI created: {ami_id}")

            return ami_id

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create AMI: {e.stderr.decode()}")
            raise

    def _ensure_bucket(self):
        """Ensure S3 bucket exists."""
        try:
            cmd = [
                "aws",
                "s3api",
                "head-bucket",
                "--bucket",
                self.config.bucket_name,
                "--region",
                self.config.region,
            ]

            if self.config.profile:
                cmd.extend(["--profile", self.config.profile])

            subprocess.run(cmd, capture_output=True, check=True)

        except subprocess.CalledProcessError:
            # Create bucket
            logger.info(f"Creating S3 bucket: {self.config.bucket_name}")

            cmd = [
                "aws",
                "s3api",
                "create-bucket",
                "--bucket",
                self.config.bucket_name,
                "--region",
                self.config.region,
            ]

            if self.config.region != "us-east-1":
                cmd.extend(
                    ["--create-bucket-configuration", f"LocationConstraint={self.config.region}"]
                )

            if self.config.profile:
                cmd.extend(["--profile", self.config.profile])

            subprocess.run(cmd, check=True, capture_output=True)


def upload_to_azure(image_path: Path, config: AzureConfig) -> str:
    """
    Quick upload to Azure.

    Args:
        image_path: Image path
        config: Azure configuration

    Returns:
        Blob URL
    """
    azure = AzureIntegration(config)
    url = azure.upload_image(image_path)

    logger.info(f"Uploaded to Azure: {url}")

    return url


def upload_to_aws(image_path: Path, config: AWSConfig) -> str:
    """
    Quick upload to AWS.

    Args:
        image_path: Image path
        config: AWS configuration

    Returns:
        S3 URL
    """
    aws = AWSIntegration(config)
    url = aws.upload_image(image_path)

    logger.info(f"Uploaded to AWS: {url}")

    return url
