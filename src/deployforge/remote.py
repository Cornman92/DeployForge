"""Remote image repository support."""

import logging
from pathlib import Path
from typing import Optional, Dict, Any
from urllib.parse import urlparse
import requests

logger = logging.getLogger(__name__)


class RemoteRepository:
    """Base class for remote image repositories."""

    def __init__(self, repository_url: str):
        """
        Initialize remote repository.

        Args:
            repository_url: URL to the repository
        """
        self.repository_url = repository_url
        self.parsed_url = urlparse(repository_url)

    def download(self, remote_path: str, local_path: Path) -> None:
        """
        Download an image from the repository.

        Args:
            remote_path: Path to image in repository
            local_path: Local path to save to
        """
        raise NotImplementedError

    def upload(self, local_path: Path, remote_path: str) -> None:
        """
        Upload an image to the repository.

        Args:
            local_path: Local image path
            remote_path: Destination path in repository
        """
        raise NotImplementedError

    def list_images(self, prefix: str = "") -> list:
        """
        List images in the repository.

        Args:
            prefix: Optional prefix filter

        Returns:
            List of image paths
        """
        raise NotImplementedError


class HTTPRepository(RemoteRepository):
    """HTTP/HTTPS remote repository."""

    def download(self, remote_path: str, local_path: Path) -> None:
        """Download image via HTTP."""
        url = f"{self.repository_url}/{remote_path}"
        local_path = Path(local_path)
        local_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Downloading from {url}...")

        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))
            downloaded = 0

            with open(local_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            logger.debug(f"Download progress: {progress:.1f}%")

            logger.info(f"Downloaded {downloaded:,} bytes to {local_path}")

        except requests.RequestException as e:
            logger.error(f"HTTP download failed: {e}")
            raise

    def upload(self, local_path: Path, remote_path: str) -> None:
        """Upload image via HTTP POST."""
        url = f"{self.repository_url}/{remote_path}"
        local_path = Path(local_path)

        if not local_path.exists():
            raise FileNotFoundError(f"Local file not found: {local_path}")

        logger.info(f"Uploading to {url}...")

        try:
            with open(local_path, "rb") as f:
                response = requests.post(url, files={"file": f})
                response.raise_for_status()

            logger.info(f"Uploaded {local_path.name} successfully")

        except requests.RequestException as e:
            logger.error(f"HTTP upload failed: {e}")
            raise

    def list_images(self, prefix: str = "") -> list:
        """List images via HTTP API."""
        url = f"{self.repository_url}/list"
        params = {"prefix": prefix} if prefix else {}

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json().get("images", [])

        except requests.RequestException as e:
            logger.error(f"HTTP list failed: {e}")
            return []


class S3Repository(RemoteRepository):
    """Amazon S3 remote repository."""

    def __init__(
        self,
        repository_url: str,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
    ):
        """
        Initialize S3 repository.

        Args:
            repository_url: S3 URL (s3://bucket-name/)
            access_key: AWS access key
            secret_key: AWS secret key
        """
        super().__init__(repository_url)
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket = self.parsed_url.netloc

        # Try to import boto3
        try:
            import boto3

            self.s3_client = boto3.client(
                "s3", aws_access_key_id=access_key, aws_secret_access_key=secret_key
            )
            self.boto3_available = True
        except ImportError:
            logger.warning("boto3 not available. Install with: pip install boto3")
            self.boto3_available = False

    def download(self, remote_path: str, local_path: Path) -> None:
        """Download image from S3."""
        if not self.boto3_available:
            raise ImportError("boto3 is required for S3 support")

        local_path = Path(local_path)
        local_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Downloading s3://{self.bucket}/{remote_path}...")

        try:
            self.s3_client.download_file(self.bucket, remote_path, str(local_path))

            logger.info(f"Downloaded to {local_path}")

        except Exception as e:
            logger.error(f"S3 download failed: {e}")
            raise

    def upload(self, local_path: Path, remote_path: str) -> None:
        """Upload image to S3."""
        if not self.boto3_available:
            raise ImportError("boto3 is required for S3 support")

        local_path = Path(local_path)

        if not local_path.exists():
            raise FileNotFoundError(f"Local file not found: {local_path}")

        logger.info(f"Uploading to s3://{self.bucket}/{remote_path}...")

        try:
            self.s3_client.upload_file(str(local_path), self.bucket, remote_path)

            logger.info(f"Uploaded {local_path.name} successfully")

        except Exception as e:
            logger.error(f"S3 upload failed: {e}")
            raise

    def list_images(self, prefix: str = "") -> list:
        """List images in S3 bucket."""
        if not self.boto3_available:
            raise ImportError("boto3 is required for S3 support")

        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket, Prefix=prefix)

            return [obj["Key"] for obj in response.get("Contents", [])]

        except Exception as e:
            logger.error(f"S3 list failed: {e}")
            return []


class AzureBlobRepository(RemoteRepository):
    """Microsoft Azure Blob Storage repository."""

    def __init__(self, repository_url: str, connection_string: Optional[str] = None):
        """
        Initialize Azure Blob repository.

        Args:
            repository_url: Azure URL (https://account.blob.core.windows.net/container/)
            connection_string: Azure storage connection string
        """
        super().__init__(repository_url)
        self.connection_string = connection_string

        # Try to import azure
        try:
            from azure.storage.blob import BlobServiceClient

            self.blob_service = BlobServiceClient.from_connection_string(connection_string)
            self.azure_available = True
        except ImportError:
            logger.warning(
                "azure-storage-blob not available. Install with: pip install azure-storage-blob"
            )
            self.azure_available = False

    def download(self, remote_path: str, local_path: Path) -> None:
        """Download image from Azure Blob."""
        if not self.azure_available:
            raise ImportError("azure-storage-blob is required for Azure support")

        local_path = Path(local_path)
        local_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Downloading from Azure Blob: {remote_path}...")

        try:
            # Extract container and blob name
            parts = remote_path.split("/", 1)
            container_name = parts[0]
            blob_name = parts[1] if len(parts) > 1 else ""

            blob_client = self.blob_service.get_blob_client(
                container=container_name, blob=blob_name
            )

            with open(local_path, "wb") as f:
                blob_data = blob_client.download_blob()
                blob_data.readinto(f)

            logger.info(f"Downloaded to {local_path}")

        except Exception as e:
            logger.error(f"Azure Blob download failed: {e}")
            raise

    def upload(self, local_path: Path, remote_path: str) -> None:
        """Upload image to Azure Blob."""
        if not self.azure_available:
            raise ImportError("azure-storage-blob is required for Azure support")

        local_path = Path(local_path)

        if not local_path.exists():
            raise FileNotFoundError(f"Local file not found: {local_path}")

        logger.info(f"Uploading to Azure Blob: {remote_path}...")

        try:
            parts = remote_path.split("/", 1)
            container_name = parts[0]
            blob_name = parts[1] if len(parts) > 1 else local_path.name

            blob_client = self.blob_service.get_blob_client(
                container=container_name, blob=blob_name
            )

            with open(local_path, "rb") as f:
                blob_client.upload_blob(f, overwrite=True)

            logger.info(f"Uploaded {local_path.name} successfully")

        except Exception as e:
            logger.error(f"Azure Blob upload failed: {e}")
            raise

    def list_images(self, prefix: str = "") -> list:
        """List images in Azure Blob container."""
        if not self.azure_available:
            raise ImportError("azure-storage-blob is required for Azure support")

        try:
            # Assume first part is container
            parts = prefix.split("/", 1)
            container_name = parts[0] if parts else ""
            blob_prefix = parts[1] if len(parts) > 1 else ""

            if not container_name:
                return []

            container_client = self.blob_service.get_container_client(container_name)
            blobs = container_client.list_blobs(name_starts_with=blob_prefix)

            return [blob.name for blob in blobs]

        except Exception as e:
            logger.error(f"Azure Blob list failed: {e}")
            return []


def get_repository(url: str, **kwargs) -> RemoteRepository:
    """
    Get appropriate repository based on URL scheme.

    Args:
        url: Repository URL
        **kwargs: Additional arguments for specific repository types

    Returns:
        RemoteRepository instance
    """
    parsed = urlparse(url)

    if parsed.scheme in ["http", "https"]:
        return HTTPRepository(url)
    elif parsed.scheme == "s3":
        return S3Repository(url, **kwargs)
    elif parsed.scheme in ["azure", "https"] and "blob.core.windows.net" in url:
        return AzureBlobRepository(url, **kwargs)
    else:
        raise ValueError(f"Unsupported repository scheme: {parsed.scheme}")
