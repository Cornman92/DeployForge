# Security Hardening Guide

This guide covers security best practices when using DeployForge and creating Windows deployment images.

## Table of Contents

1. [Security Principles](#security-principles)
2. [Image Hardening](#image-hardening)
3. [Driver Security](#driver-security)
4. [Update Management](#update-management)
5. [Audit and Compliance](#audit-and-compliance)
6. [Best Practices](#best-practices)

---

## Security Principles

### Defense in Depth

Apply multiple layers of security:

- Image validation and verification
- Secure storage and transmission
- Access control and authentication
- Audit logging and monitoring

### Least Privilege

- Run DeployForge with minimum necessary permissions
- Use read-only mode when possible
- Separate roles for image creation and deployment

### Secure by Default

- Enable security features by default
- Disable unnecessary services
- Apply latest security updates

---

## Image Hardening

### 1. Disable Unnecessary Services

```python
from deployforge import ImageManager
from deployforge.registry import RegistryEditor

with ImageManager("install.wim") as manager:
    manager.mount()

    with RegistryEditor(manager.mount_point) as reg:
        # Disable Telemetry
        reg.set_value(
            'HKLM\\SOFTWARE',
            'Policies\\Microsoft\\Windows\\DataCollection',
            'AllowTelemetry',
            '0',
            'REG_DWORD'
        )
```

### 2. Enable Security Features

```python
security_tweaks = [
    # Enable BitLocker
    {
        'hive': 'HKLM\\SOFTWARE',
        'path': 'Policies\\Microsoft\\FVE',
        'name': 'EnableBDEWithNoTPM',
        'data': '1',
        'type': 'REG_DWORD'
    },
    # Enable Windows Defender
    {
        'hive': 'HKLM\\SOFTWARE',
        'path': 'Policies\\Microsoft\\Windows Defender',
        'name': 'DisableAntiSpyware',
        'data': '0',
        'type': 'REG_DWORD'
    },
    # Disable SMBv1
    {
        'hive': 'HKLM\\SYSTEM',
        'path': 'CurrentControlSet\\Services\\LanmanServer\\Parameters',
        'name': 'SMB1',
        'data': '0',
        'type': 'REG_DWORD'
    },
]

with RegistryEditor(mount_point) as reg:
    reg.apply_tweaks(security_tweaks)
```

### 3. Remove Bloatware

Reduce attack surface by removing unnecessary applications:

```python
bloatware = [
    "Microsoft.BingWeather",
    "Microsoft.XboxApp",
    # ... more packages
]

# Remove using DISM
import subprocess
for package in bloatware:
    subprocess.run([
        'dism',
        f'/Image:{mount_point}',
        '/Remove-ProvisionedAppxPackage',
        f'/PackageName:{package}'
    ])
```

---

## Driver Security

### Validate Driver Packages

Always validate driver packages before injection:

```python
from deployforge.drivers import DriverInjector

injector = DriverInjector(mount_point)

# Validate first
is_valid = injector.validate_driver_package(driver_dir)

if is_valid:
    # Inject only signed drivers
    injector.inject_drivers(
        [driver_dir],
        force_unsigned=False  # Reject unsigned drivers
    )
```

### Scan for Malware

Before injecting drivers:

1. Scan with antivirus
2. Verify digital signatures
3. Check publisher certificates
4. Review driver contents

### Driver Source Control

- Download drivers only from official sources
- Verify checksums and signatures
- Maintain driver repository with version control
- Document driver provenance

---

## Update Management

### Apply Security Updates

```python
from deployforge.updates import UpdateIntegrator

integrator = UpdateIntegrator(mount_point)

# Apply critical security updates first
security_updates = [
    "KB5001234.msu",  # Security update
    "KB5001235.msu",  # Critical update
]

for update in security_updates:
    integrator.apply_update(Path(update))

# Cleanup superseded components
integrator.cleanup_superseded()
```

### Update Strategy

1. **Critical First**: Apply security updates before others
2. **Test Thoroughly**: Test updates in staging environment
3. **Rollback Plan**: Maintain ability to rollback
4. **Documentation**: Document all applied updates

---

## Audit and Compliance

### Enable Audit Logging

```python
from deployforge.audit import AuditLogger

audit = AuditLogger(Path("./audit.jsonl"))

# Log all operations
audit.log_event(
    event_type="image_modification",
    action="driver_injection",
    image_path=image_path,
    details={'driver': 'nvidia_driver.zip'},
    success=True
)
```

### Compliance Reporting

Generate audit reports for compliance:

```python
# Generate report
audit.generate_report(Path("./audit_report.txt"))

# Filter by event type
events = audit.get_events(event_type="image_modification")
```

### Track Changes

Maintain changelog for all image modifications:

```python
# Example changelog entry
{
    "timestamp": "2025-11-08T10:30:00Z",
    "user": "admin@company.com",
    "image": "install.wim",
    "changes": [
        "Applied security updates KB5001234, KB5001235",
        "Injected network drivers v1.2.3",
        "Disabled telemetry",
        "Enabled BitLocker"
    ],
    "approved_by": "security@company.com"
}
```

---

## Best Practices

### 1. Secure Storage

- **Encryption**: Encrypt images at rest
- **Access Control**: Restrict access to image repository
- **Backup**: Maintain secure backups
- **Versioning**: Version control for images

### 2. Secure Transmission

When using remote repositories:

```python
from deployforge.remote import S3Repository

# Use HTTPS/SSL
repo = S3Repository(
    "s3://secure-bucket/",
    access_key=os.environ['AWS_ACCESS_KEY'],  # From environment
    secret_key=os.environ['AWS_SECRET_KEY']
)

# Enable encryption in transit
repo.download("image.wim", "./local.wim")
```

### 3. Validation and Verification

Always verify images:

```python
import hashlib

def verify_image_hash(image_path, expected_hash):
    """Verify image integrity with SHA256."""
    sha256 = hashlib.sha256()

    with open(image_path, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)

    actual_hash = sha256.hexdigest()

    if actual_hash != expected_hash:
        raise ValueError("Image integrity check failed!")

    return True
```

### 4. Principle of Least Privilege

```bash
# Create dedicated user for image operations
useradd -m -s /bin/bash imagebuilder

# Grant only necessary permissions
chown imagebuilder:imagebuilder /images
chmod 750 /images

# Run DeployForge as this user
su - imagebuilder
deployforge mount image.wim
```

### 5. Secure Defaults

Create a security baseline template:

```python
from deployforge.templates import CustomizationTemplate, RegistryTweak

security_baseline = CustomizationTemplate(
    name="Security Baseline",
    description="Corporate security baseline"
)

# Add security tweaks
security_baseline.registry = [
    RegistryTweak(
        hive="HKLM\\SOFTWARE",
        path="Policies\\Microsoft\\Windows\\DataCollection",
        name="AllowTelemetry",
        data="0",
        type="REG_DWORD"
    ),
    # ... more security settings
]

# Save and reuse
manager.save_template(security_baseline, "security_baseline.json")
```

---

## Security Checklist

Before deploying an image:

- [ ] All security updates applied
- [ ] Unnecessary services disabled
- [ ] Bloatware removed
- [ ] Security features enabled (BitLocker, Defender, Firewall)
- [ ] Audit logging configured
- [ ] Default passwords changed
- [ ] SMBv1 disabled
- [ ] PowerShell logging enabled
- [ ] Remote Desktop hardened
- [ ] AutoRun disabled
- [ ] Driver signatures verified
- [ ] Image hash verified
- [ ] Deployment tested in staging
- [ ] Incident response plan ready
- [ ] Rollback procedure documented

---

## Reporting Security Issues

If you discover a security vulnerability in DeployForge:

1. **Do NOT** open a public issue
2. Email security@deployforge.io with details
3. Include steps to reproduce
4. Allow time for patch development
5. Coordinate disclosure timeline

---

## Resources

- [CIS Windows Benchmarks](https://www.cisecurity.org/benchmark/microsoft_windows_desktop)
- [Microsoft Security Baselines](https://docs.microsoft.com/en-us/windows/security/threat-protection/windows-security-baselines)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

---

**Remember**: Security is not a one-time task but an ongoing process. Regularly review and update your security practices.
