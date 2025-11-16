# DeployForge REST API Reference

**Version**: 1.7.0 / 0.3.0
**Last Updated**: 2025-11-15
**Base Technology**: FastAPI + Uvicorn
**Documentation**: Auto-generated OpenAPI/Swagger at `/docs`

Complete REST API reference for DeployForge Windows deployment automation.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Authentication](#authentication)
3. [API Endpoints](#api-endpoints)
4. [Request/Response Models](#requestresponse-models)
5. [Error Handling](#error-handling)
6. [Rate Limiting](#rate-limiting)
7. [Examples](#examples)
8. [SDKs & Client Libraries](#sdks--client-libraries)

---

## Getting Started

### Starting the API Server

#### Method 1: Using deployforge CLI
```bash
deployforge api --host 0.0.0.0 --port 8000
```

#### Method 2: Using Python module
```bash
python -m deployforge.api.main
```

#### Method 3: Using Uvicorn directly
```bash
uvicorn deployforge.api.main:app --host 0.0.0.0 --port 8000
```

#### Method 4: Using Docker
```bash
docker run -p 8000:8000 -v /images:/images deployforge api
```

### Base URL

**Local Development**:
```
http://localhost:8000
```

**Production**:
```
https://api.deployforge.yourdomain.com
```

### Interactive Documentation

Once the server is running, access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## Authentication

### Current Status

**v0.3.0**: No authentication (development mode)

### Future Versions

**v1.0.0+** will include:
- API Key authentication
- OAuth 2.0 support
- JWT tokens
- Role-based access control (RBAC)

### Planned Header Format
```http
Authorization: Bearer <api_key>
```

---

## API Endpoints

### General

#### GET / - Root Endpoint

Get API information.

**Request**: None

**Response**:
```json
{
  "name": "DeployForge API",
  "version": "0.3.0",
  "documentation": "/docs"
}
```

**Example**:
```bash
curl http://localhost:8000/
```

---

#### GET /health - Health Check

Check API server health status.

**Request**: None

**Response**:
```json
{
  "status": "healthy",
  "version": "0.3.0",
  "timestamp": "2025-11-15T10:30:00.000Z"
}
```

**Example**:
```bash
curl http://localhost:8000/health
```

---

### Image Operations

#### POST /images/info - Get Image Information

Retrieve metadata and information about a Windows deployment image.

**Request Body**:
```json
{
  "image_path": "/path/to/install.wim"
}
```

**Response**:
```json
{
  "format": "WIM",
  "size": 4294967296,
  "created": "2025-11-15T10:00:00",
  "modified": "2025-11-15T10:30:00",
  "images": [
    {
      "index": 1,
      "name": "Windows 11 Pro",
      "description": "Windows 11 Pro",
      "architecture": "x64",
      "size": 15000000000,
      "flags": "9"
    }
  ],
  "compression": "LZX",
  "boot_index": 1
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/images/info \
  -H "Content-Type: application/json" \
  -d '{"image_path": "/images/install.wim"}'
```

**Python Example**:
```python
import requests

response = requests.post(
    'http://localhost:8000/images/info',
    json={'image_path': '/images/install.wim'}
)
info = response.json()
print(f"Format: {info['format']}, Size: {info['size']:,} bytes")
```

**Errors**:
- `404 Not Found` - Image file does not exist
- `500 Internal Server Error` - Image is corrupted or unsupported format

---

#### POST /images/list - List Files in Image

List files and directories within a mounted image.

**Request**:
```json
{
  "image_path": "/path/to/install.wim",
  "path": "/Windows/System32",
  "index": 1
}
```

**Response**:
```json
{
  "files": [
    {
      "name": "notepad.exe",
      "path": "/Windows/System32/notepad.exe",
      "size": 425984,
      "type": "file",
      "modified": "2025-10-15T08:00:00"
    },
    {
      "name": "drivers",
      "path": "/Windows/System32/drivers",
      "type": "directory"
    }
  ],
  "total_files": 2,
  "total_size": 425984
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/images/list \
  -H "Content-Type: application/json" \
  -d '{"image_path": "/images/install.wim", "path": "/Windows"}'
```

---

#### POST /images/add - Add File to Image

Add a file to a Windows image.

**Request**:
```json
{
  "image_path": "/path/to/install.wim",
  "source_path": "/local/driver.sys",
  "destination_path": "/Windows/System32/drivers/driver.sys",
  "index": 1
}
```

**Response**:
```json
{
  "success": true,
  "message": "File added successfully",
  "source": "/local/driver.sys",
  "destination": "/Windows/System32/drivers/driver.sys",
  "size": 524288
}
```

**Example**:
```python
import requests

response = requests.post(
    'http://localhost:8000/images/add',
    json={
        'image_path': '/images/install.wim',
        'source_path': '/drivers/nvidia.inf',
        'destination_path': '/Windows/INF/nvidia.inf'
    }
)
result = response.json()
```

---

#### POST /images/remove - Remove File from Image

Remove a file from a Windows image.

**Request**:
```json
{
  "image_path": "/path/to/install.wim",
  "file_path": "/Windows/bloatware.exe",
  "index": 1
}
```

**Response**:
```json
{
  "success": true,
  "message": "File removed successfully",
  "path": "/Windows/bloatware.exe"
}
```

---

#### POST /images/extract - Extract File from Image

Extract a file from an image to the local filesystem.

**Request**:
```json
{
  "image_path": "/path/to/install.wim",
  "source_path": "/Windows/System32/notepad.exe",
  "destination_path": "/local/notepad.exe",
  "index": 1
}
```

**Response**:
```json
{
  "success": true,
  "message": "File extracted successfully",
  "source": "/Windows/System32/notepad.exe",
  "destination": "/local/notepad.exe",
  "size": 425984
}
```

---

#### POST /images/mount - Mount Image

Mount a Windows image to a directory.

**Request**:
```json
{
  "image_path": "/path/to/install.wim",
  "mount_point": "/mnt/wim",
  "index": 1,
  "read_only": false
}
```

**Response**:
```json
{
  "success": true,
  "mount_point": "/mnt/wim",
  "image_path": "/path/to/install.wim",
  "index": 1,
  "status": "mounted"
}
```

---

#### POST /images/unmount - Unmount Image

Unmount a previously mounted image.

**Request**:
```json
{
  "mount_point": "/mnt/wim",
  "save_changes": true,
  "discard": false
}
```

**Response**:
```json
{
  "success": true,
  "mount_point": "/mnt/wim",
  "changes_saved": true,
  "status": "unmounted"
}
```

---

#### POST /images/compare - Compare Two Images

Compare two Windows images and generate a diff report.

**Request**:
```json
{
  "image1_path": "/path/to/image1.wim",
  "image2_path": "/path/to/image2.wim",
  "compute_hashes": true,
  "deep_scan": false
}
```

**Response**:
```json
{
  "similarity": 87.5,
  "total_files_image1": 50000,
  "total_files_image2": 48000,
  "only_in_image1": 3500,
  "only_in_image2": 1500,
  "different_files": 500,
  "identical_files": 44500,
  "size_difference": 2147483648,
  "differences": [
    {
      "path": "/Windows/bloatware.exe",
      "status": "only_in_image1",
      "size1": 1048576,
      "size2": null
    },
    {
      "path": "/Windows/System32/driver.sys",
      "status": "different",
      "size1": 524288,
      "size2": 524800,
      "hash1": "abc123...",
      "hash2": "def456..."
    }
  ]
}
```

**Example**:
```python
import requests

response = requests.post(
    'http://localhost:8000/images/compare',
    json={
        'image1_path': '/images/windows_base.wim',
        'image2_path': '/images/windows_custom.wim',
        'compute_hashes': True
    }
)
comparison = response.json()
print(f"Similarity: {comparison['similarity']:.2f}%")
```

---

### Registry Operations

#### POST /registry/set - Set Registry Value

Set a registry value in an offline Windows image.

**Request**:
```json
{
  "image_path": "/path/to/install.wim",
  "hive": "HKLM",
  "key_path": "SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection",
  "value_name": "AllowTelemetry",
  "value_data": "0",
  "value_type": "REG_DWORD",
  "index": 1
}
```

**Response**:
```json
{
  "success": true,
  "message": "Registry value set successfully",
  "hive": "HKLM",
  "key": "SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection",
  "value_name": "AllowTelemetry",
  "value_data": "0"
}
```

**Value Types**:
- `REG_SZ` - String value
- `REG_DWORD` - 32-bit number
- `REG_QWORD` - 64-bit number
- `REG_BINARY` - Binary data
- `REG_MULTI_SZ` - Multi-string value
- `REG_EXPAND_SZ` - Expandable string

---

#### POST /registry/get - Get Registry Value

Retrieve a registry value from an offline image.

**Request**:
```json
{
  "image_path": "/path/to/install.wim",
  "hive": "HKLM",
  "key_path": "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion",
  "value_name": "ProductName",
  "index": 1
}
```

**Response**:
```json
{
  "success": true,
  "hive": "HKLM",
  "key": "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion",
  "value_name": "ProductName",
  "value_data": "Windows 11 Pro",
  "value_type": "REG_SZ"
}
```

---

#### POST /registry/delete - Delete Registry Key

Delete a registry key from an offline image.

**Request**:
```json
{
  "image_path": "/path/to/install.wim",
  "hive": "HKLM",
  "key_path": "SOFTWARE\\UnwantedSoftware",
  "recursive": true,
  "index": 1
}
```

**Response**:
```json
{
  "success": true,
  "message": "Registry key deleted successfully",
  "key": "SOFTWARE\\UnwantedSoftware"
}
```

---

### Driver Operations

#### POST /drivers/inject - Inject Driver Package

Inject driver packages (.inf files) into a Windows image.

**Request**:
```json
{
  "image_path": "/path/to/install.wim",
  "driver_paths": [
    "/drivers/nvidia.inf",
    "/drivers/intel_chipset.inf"
  ],
  "force_unsigned": false,
  "recursive": true,
  "index": 1
}
```

**Response**:
```json
{
  "success": true,
  "message": "Drivers injected successfully",
  "total_drivers": 2,
  "successful": 2,
  "failed": 0,
  "details": [
    {
      "driver": "/drivers/nvidia.inf",
      "status": "success",
      "provider": "NVIDIA Corporation",
      "version": "531.68.0.0",
      "date": "2023-05-15"
    },
    {
      "driver": "/drivers/intel_chipset.inf",
      "status": "success",
      "provider": "Intel Corporation",
      "version": "10.1.18836.8283",
      "date": "2023-04-20"
    }
  ]
}
```

---

#### GET /drivers/list - List Installed Drivers

List all drivers installed in an image.

**Request**:
```
GET /drivers/list?image_path=/path/to/install.wim&index=1
```

**Response**:
```json
{
  "drivers": [
    {
      "provider": "Microsoft",
      "class": "System",
      "version": "10.0.22621.1",
      "date": "2022-09-20",
      "inbox": true
    },
    {
      "provider": "NVIDIA Corporation",
      "class": "Display",
      "version": "531.68.0.0",
      "date": "2023-05-15",
      "inbox": false
    }
  ],
  "total": 2
}
```

---

### Batch Operations

#### POST /batch/operations - Create Batch Job

Create a batch operation to process multiple images.

**Request**:
```json
{
  "image_paths": [
    "/images/install1.wim",
    "/images/install2.wim",
    "/images/install3.wim"
  ],
  "operation": "get_info",
  "parameters": {},
  "max_workers": 4,
  "priority": "normal"
}
```

**Response**:
```json
{
  "job_id": "batch-550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "created_at": "2025-11-15T10:30:00.000Z",
  "total_images": 3,
  "message": "Batch job created successfully"
}
```

**Supported Operations**:
- `get_info` - Get information for all images
- `add_file` - Add file to all images
- `remove_file` - Remove file from all images
- `inject_drivers` - Inject drivers to all images
- `apply_template` - Apply template to all images

---

#### GET /batch/status/{job_id} - Get Batch Job Status

Check the status of a running batch job.

**Request**:
```
GET /batch/status/batch-550e8400-e29b-41d4-a716-446655440000
```

**Response**:
```json
{
  "job_id": "batch-550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "created_at": "2025-11-15T10:30:00.000Z",
  "started_at": "2025-11-15T10:30:05.000Z",
  "total_images": 3,
  "processed": 2,
  "remaining": 1,
  "progress": 66.67,
  "errors": 0
}
```

**Status Values**:
- `queued` - Waiting to start
- `running` - Currently processing
- `completed` - Successfully finished
- `failed` - Failed with errors
- `cancelled` - Manually cancelled

---

#### GET /batch/results/{job_id} - Get Batch Job Results

Retrieve results from a completed batch job.

**Request**:
```
GET /batch/results/batch-550e8400-e29b-41d4-a716-446655440000
```

**Response**:
```json
{
  "job_id": "batch-550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "created_at": "2025-11-15T10:30:00.000Z",
  "completed_at": "2025-11-15T10:35:00.000Z",
  "duration_seconds": 300,
  "total_images": 3,
  "successful": 3,
  "failed": 0,
  "results": [
    {
      "image": "/images/install1.wim",
      "status": "success",
      "result": {...}
    },
    {
      "image": "/images/install2.wim",
      "status": "success",
      "result": {...}
    },
    {
      "image": "/images/install3.wim",
      "status": "success",
      "result": {...}
    }
  ]
}
```

---

#### DELETE /batch/cancel/{job_id} - Cancel Batch Job

Cancel a running or queued batch job.

**Request**:
```
DELETE /batch/cancel/batch-550e8400-e29b-41d4-a716-446655440000
```

**Response**:
```json
{
  "success": true,
  "job_id": "batch-550e8400-e29b-41d4-a716-446655440000",
  "status": "cancelled",
  "message": "Batch job cancelled successfully"
}
```

---

### Template Operations

#### POST /templates/apply - Apply Template

Apply a pre-defined or custom template to an image.

**Request**:
```json
{
  "image_path": "/path/to/install.wim",
  "template_name": "gaming",
  "index": 1,
  "variables": {
    "username": "Gamer",
    "computer_name": "GAMING-PC"
  }
}
```

**Response**:
```json
{
  "success": true,
  "message": "Template applied successfully",
  "template": "gaming",
  "changes": {
    "registry_tweaks": 15,
    "files_added": 3,
    "files_removed": 25,
    "drivers_injected": 2
  }
}
```

---

#### GET /templates/list - List Available Templates

List all available templates.

**Request**:
```
GET /templates/list
```

**Response**:
```json
{
  "templates": [
    {
      "name": "gaming",
      "description": "Optimized for gaming performance",
      "category": "Performance",
      "features": ["debloat", "gpu_drivers", "game_mode"]
    },
    {
      "name": "enterprise",
      "description": "Enterprise security and compliance",
      "category": "Enterprise",
      "features": ["security_hardening", "domain_join", "gpo"]
    },
    {
      "name": "developer",
      "description": "Development environment setup",
      "category": "Development",
      "features": ["dev_tools", "ides", "runtimes"]
    }
  ],
  "total": 3
}
```

---

#### GET /templates/get/{name} - Get Template Details

Get detailed information about a specific template.

**Request**:
```
GET /templates/get/gaming
```

**Response**:
```json
{
  "name": "gaming",
  "description": "Optimized for gaming performance",
  "version": "1.0.0",
  "category": "Performance",
  "features": {
    "debloat": {
      "remove_packages": ["Xbox", "Teams", "Skype"],
      "disable_services": ["DiagTrack", "SysMain"]
    },
    "registry": {
      "tweaks": [
        {
          "key": "HKLM\\SOFTWARE\\...",
          "value": "GameMode",
          "data": "1"
        }
      ]
    },
    "drivers": {
      "inject": ["nvidia_latest", "amd_latest"]
    }
  }
}
```

---

#### POST /templates/create - Create Custom Template

Create a new custom template.

**Request**:
```json
{
  "name": "custom_template",
  "description": "My custom configuration",
  "category": "Custom",
  "configuration": {
    "debloat": [...],
    "registry": [...],
    "drivers": [...]
  }
}
```

**Response**:
```json
{
  "success": true,
  "message": "Template created successfully",
  "template_name": "custom_template",
  "template_id": "tpl-550e8400-e29b-41d4-a716-446655440000"
}
```

---

### Update Operations

#### POST /updates/apply - Apply Windows Updates

Apply Windows updates (MSU/CAB files) to an offline image.

**Request**:
```json
{
  "image_path": "/path/to/install.wim",
  "update_paths": [
    "/updates/KB5031354.msu",
    "/updates/KB5031358.cab"
  ],
  "index": 1
}
```

**Response**:
```json
{
  "success": true,
  "message": "Updates applied successfully",
  "total_updates": 2,
  "successful": 2,
  "failed": 0,
  "details": [
    {
      "update": "KB5031354.msu",
      "status": "success",
      "size": 524288000
    },
    {
      "update": "KB5031358.cab",
      "status": "success",
      "size": 104857600
    }
  ]
}
```

---

## Request/Response Models

### Common Models

#### ErrorResponse
```json
{
  "detail": "Error message describing what went wrong",
  "status_code": 400,
  "timestamp": "2025-11-15T10:30:00.000Z"
}
```

#### SuccessResponse
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": { ... }
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created |
| 202 | Accepted | Request accepted (async) |
| 400 | Bad Request | Invalid request parameters |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource conflict |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Server overloaded |

### Error Response Format

```json
{
  "detail": "Image file not found: /path/to/missing.wim",
  "status_code": 404,
  "error_type": "ImageNotFoundError",
  "timestamp": "2025-11-15T10:30:00.000Z",
  "request_id": "req-550e8400-e29b-41d4-a716-446655440000"
}
```

### Common Errors

**404 Not Found**:
```json
{
  "detail": "Image file not found: /images/install.wim",
  "status_code": 404
}
```

**400 Bad Request**:
```json
{
  "detail": "Invalid image path: must be absolute path",
  "status_code": 400
}
```

**500 Internal Server Error**:
```json
{
  "detail": "Failed to mount image: insufficient permissions",
  "status_code": 500,
  "error_type": "MountError"
}
```

---

## Rate Limiting

### Current Status

**v0.3.0**: No rate limiting

### Planned (v1.0.0+)

- **Requests per minute**: 60
- **Concurrent requests**: 10
- **Batch job limit**: 5 active jobs

### Headers (Future)
```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1699876543
```

---

## Examples

### Complete Workflow: Custom Windows 11 Image

```python
import requests
from pathlib import Path

BASE_URL = 'http://localhost:8000'

# 1. Get image info
info_response = requests.post(
    f'{BASE_URL}/images/info',
    json={'image_path': '/images/Win11_22H2.wim'}
)
info = info_response.json()
print(f"Image: {info['images'][0]['name']}")

# 2. Apply gaming template
template_response = requests.post(
    f'{BASE_URL}/templates/apply',
    json={
        'image_path': '/images/Win11_22H2.wim',
        'template_name': 'gaming',
        'index': 1
    }
)
template_result = template_response.json()
print(f"Template applied: {template_result['changes']}")

# 3. Inject NVIDIA drivers
driver_response = requests.post(
    f'{BASE_URL}/drivers/inject',
    json={
        'image_path': '/images/Win11_22H2.wim',
        'driver_paths': ['/drivers/nvidia_531.68.inf'],
        'index': 1
    }
)
driver_result = driver_response.json()
print(f"Drivers injected: {driver_result['successful']}/{driver_result['total_drivers']}")

# 4. Apply Windows updates
update_response = requests.post(
    f'{BASE_URL}/updates/apply',
    json={
        'image_path': '/images/Win11_22H2.wim',
        'update_paths': ['/updates/KB5031354.msu'],
        'index': 1
    }
)
update_result = update_response.json()
print(f"Updates applied: {update_result['successful']}/{update_result['total_updates']}")

print("Custom Windows 11 gaming image created successfully!")
```

### Batch Processing Multiple Images

```python
import requests
import time

BASE_URL = 'http://localhost:8000'

# Create batch job
batch_response = requests.post(
    f'{BASE_URL}/batch/operations',
    json={
        'image_paths': [
            '/images/image1.wim',
            '/images/image2.wim',
            '/images/image3.wim'
        ],
        'operation': 'inject_drivers',
        'parameters': {
            'driver_paths': ['/drivers/nvidia.inf'],
            'force_unsigned': False
        },
        'max_workers': 4
    }
)
job = batch_response.json()
job_id = job['job_id']
print(f"Batch job created: {job_id}")

# Poll for status
while True:
    status_response = requests.get(f'{BASE_URL}/batch/status/{job_id}')
    status = status_response.json()

    print(f"Progress: {status['progress']:.1f}% ({status['processed']}/{status['total_images']})")

    if status['status'] == 'completed':
        break

    time.sleep(5)

# Get results
results_response = requests.get(f'{BASE_URL}/batch/results/{job_id}')
results = results_response.json()
print(f"Batch completed: {results['successful']}/{results['total_images']} successful")
```

---

## SDKs & Client Libraries

### Official Python SDK (Planned)

```python
from deployforge_sdk import DeployForgeClient

client = DeployForgeClient('http://localhost:8000')

# Get image info
info = client.images.get_info('/images/install.wim')

# Apply template
client.templates.apply('/images/install.wim', 'gaming')

# Inject drivers
client.drivers.inject('/images/install.wim', ['/drivers/nvidia.inf'])
```

### Community Libraries

- **JavaScript/TypeScript**: `deployforge-js` (community)
- **Go**: `go-deployforge` (community)
- **PowerShell**: `DeployForge-PS` (community)

---

## Webhooks (Future)

### Event Types (v1.0.0+)

- `image.mounted` - Image mounted
- `image.unmounted` - Image unmounted
- `batch.started` - Batch job started
- `batch.completed` - Batch job completed
- `batch.failed` - Batch job failed
- `driver.injected` - Driver injected
- `update.applied` - Update applied

### Webhook Payload Example
```json
{
  "event": "batch.completed",
  "timestamp": "2025-11-15T10:30:00.000Z",
  "data": {
    "job_id": "batch-550e8400-...",
    "status": "completed",
    "total_images": 3,
    "successful": 3
  }
}
```

---

## Performance Tips

1. **Use batch operations** for multiple images
2. **Enable caching** for repeated operations
3. **Use async/background jobs** for long operations
4. **Limit concurrent requests** to avoid overload
5. **Use compression** for large file transfers
6. **Monitor job status** with polling (5-second intervals)

---

## Support

- **Documentation**: http://localhost:8000/docs
- **Issues**: https://github.com/Cornman92/DeployForge/issues
- **Discussions**: https://github.com/Cornman92/DeployForge/discussions

---

**Last Updated**: 2025-11-15
**API Version**: 0.3.0
**Maintained By**: DeployForge Team
