# DeployForge Troubleshooting Guide

**Version**: 1.7.0
**Last Updated**: 2025-11-17

---

## Table of Contents

1. [Quick Diagnostics](#quick-diagnostics)
2. [Installation Issues](#installation-issues)
3. [Image Mounting Problems](#image-mounting-problems)
4. [GUI Issues](#gui-issues)
5. [Permission and Access Errors](#permission-and-access-errors)
6. [Driver Injection Failures](#driver-injection-failures)
7. [Windows Update Integration Issues](#windows-update-integration-issues)
8. [Registry Modification Errors](#registry-modification-errors)
9. [Performance Problems](#performance-problems)
10. [Network and Remote Storage Issues](#network-and-remote-storage-issues)
11. [VM Testing Failures](#vm-testing-failures)
12. [MDT/SCCM Integration Problems](#mdtsccm-integration-problems)
13. [Certificate Installation Errors](#certificate-installation-errors)
14. [GPO Deployment Issues](#gpo-deployment-issues)
15. [Batch Operation Failures](#batch-operation-failures)
16. [Platform-Specific Issues](#platform-specific-issues)
17. [Error Messages Reference](#error-messages-reference)
18. [Advanced Diagnostics](#advanced-diagnostics)
19. [Getting Help](#getting-help)

---

## Quick Diagnostics

### Running the Built-in Diagnostic Tool

```bash
# Run comprehensive diagnostics
deployforge diagnose

# Run specific category diagnostics
deployforge diagnose --category mounting
deployforge diagnose --category permissions
deployforge diagnose --category dependencies

# Generate diagnostic report
deployforge diagnose --output diagnostics_report.txt

# Run with verbose output
deployforge diagnose --verbose
```

### Common Quick Fixes

1. **Try running as Administrator/root** (90% of issues)
2. **Restart the DeployForge service**
3. **Clear temporary files**: `deployforge cache clear`
4. **Update to latest version**: `pip install --upgrade deployforge`
5. **Check system dependencies**: `deployforge check-deps`

---

## Installation Issues

### Issue: `pip install deployforge` fails

**Symptoms:**
```
ERROR: Could not find a version that satisfies the requirement deployforge
ERROR: No matching distribution found for deployforge
```

**Solutions:**

1. **Check Python version** (requires 3.9+):
   ```bash
   python --version  # Should be 3.9, 3.10, 3.11, or 3.12
   ```

2. **Upgrade pip**:
   ```bash
   python -m pip install --upgrade pip
   ```

3. **Install from source** if PyPI is unavailable:
   ```bash
   git clone https://github.com/Cornman92/DeployForge.git
   cd DeployForge
   pip install -e .
   ```

4. **Check network connectivity** to PyPI:
   ```bash
   ping pypi.org
   ```

### Issue: Missing system dependencies

**Symptoms:**
```
ImportError: No module named 'pycdlib'
ModuleNotFoundError: No module named 'PyQt6'
```

**Solutions:**

**Linux (Ubuntu/Debian):**
```bash
# Install system packages
sudo apt-get update
sudo apt-get install -y wimtools python3-pip python3-venv

# Install Python dependencies
pip install -r requirements.txt
```

**Linux (RHEL/CentOS/Fedora):**
```bash
# Install system packages
sudo dnf install -y wimlib-utils python3-pip

# Install Python dependencies
pip install -r requirements.txt
```

**macOS:**
```bash
# Install Homebrew if not present
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install wimlib
brew install wimlib

# Install Python dependencies
pip install -r requirements.txt
```

**Windows:**
```powershell
# No additional system dependencies required
# DISM is built into Windows

# Install Python dependencies
pip install -r requirements.txt
```

### Issue: Permission denied during installation

**Symptoms:**
```
ERROR: Could not install packages due to an EnvironmentError: [Errno 13] Permission denied
```

**Solutions:**

1. **Use virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install deployforge
   ```

2. **User install** (without admin/root):
   ```bash
   pip install --user deployforge
   ```

3. **Use sudo/admin** (not recommended):
   ```bash
   sudo pip install deployforge  # Linux/macOS
   # or run PowerShell as Administrator on Windows
   ```

---

## Image Mounting Problems

### Issue: Image fails to mount

**Symptoms:**
```
MountError: Failed to mount image: install.wim
Error: The specified image file is corrupt or not a valid WIM file
```

**Solutions:**

1. **Verify image integrity**:
   ```bash
   # Check file exists
   ls -lh install.wim

   # Verify WIM format (Linux)
   wiminfo install.wim

   # Verify WIM format (Windows)
   dism /Get-ImageInfo /ImageFile:install.wim
   ```

2. **Check if image is already mounted**:
   ```bash
   # List mounted images
   deployforge list-mounts

   # Unmount if already mounted
   deployforge unmount install.wim --force
   ```

3. **Verify sufficient disk space**:
   ```bash
   # Check available space
   df -h /mnt  # Linux
   # or
   Get-PSDrive C  # Windows PowerShell
   ```

4. **Check mount point permissions**:
   ```bash
   # Create mount point with proper permissions (Linux)
   sudo mkdir -p /mnt/deployforge
   sudo chmod 755 /mnt/deployforge

   # Windows: Ensure mount directory is not in use
   ```

5. **Repair corrupt WIM**:
   ```bash
   # Windows
   dism /Cleanup-Wim

   # Check and repair image
   dism /Check-ImageHealth /ImageFile:install.wim
   dism /Restore-ImageHealth /ImageFile:install.wim
   ```

### Issue: "Access Denied" when mounting

**Symptoms:**
```
MountError: Access denied to mount point
PermissionError: [Errno 13] Permission denied: '/mnt/wim'
```

**Solutions:**

1. **Run as Administrator/root**:
   ```bash
   # Linux
   sudo deployforge ...

   # Windows: Run PowerShell as Administrator
   ```

2. **Check mount point ownership** (Linux):
   ```bash
   # Check ownership
   ls -ld /mnt/wim

   # Fix ownership
   sudo chown $USER:$USER /mnt/wim
   ```

3. **Disable antivirus temporarily** (Windows):
   - Windows Defender may block mounting operations
   - Add DeployForge to exclusion list

### Issue: Mount succeeds but files not visible

**Symptoms:**
- Mount operation reports success
- But `ls` or file explorer shows no files

**Solutions:**

1. **Check correct mount point**:
   ```python
   from deployforge import ImageManager

   img = ImageManager('install.wim')
   mount_path = img.mount()
   print(f"Mounted at: {mount_path}")  # Use this path
   ```

2. **Verify image index**:
   ```bash
   # List all indexes
   deployforge info install.wim

   # Mount specific index
   deployforge mount install.wim --index 1
   ```

3. **Check if read-only mount**:
   ```bash
   # Remount with read-write
   deployforge unmount install.wim
   deployforge mount install.wim --read-write
   ```

---

## GUI Issues

### Issue: GUI won't start

**Symptoms:**
```
ImportError: No module named 'PyQt6'
QApplication: no such file or directory
```

**Solutions:**

1. **Install PyQt6**:
   ```bash
   pip install PyQt6
   ```

2. **Check display server** (Linux):
   ```bash
   echo $DISPLAY  # Should output something like :0

   # If empty, set DISPLAY
   export DISPLAY=:0
   ```

3. **Install X11 dependencies** (Linux):
   ```bash
   sudo apt-get install -y libxcb-xinerama0 libxcb-cursor0
   ```

4. **Run in compatibility mode** (Windows):
   - Right-click executable
   - Properties → Compatibility
   - Check "Run this program as an administrator"

### Issue: GUI is blank or black screen

**Symptoms:**
- GUI window opens but shows nothing
- Window is all black or white

**Solutions:**

1. **Update graphics drivers**:
   - Windows: Update from Device Manager
   - Linux: Update Mesa drivers
   ```bash
   sudo apt-get update
   sudo apt-get upgrade mesa-utils
   ```

2. **Disable hardware acceleration**:
   ```bash
   # Set environment variable before launching
   export QT_XCB_GL_INTEGRATION=none  # Linux
   deployforge gui
   ```

3. **Try software rendering**:
   ```bash
   export LIBGL_ALWAYS_SOFTWARE=1
   deployforge gui
   ```

4. **Reset GUI settings**:
   ```bash
   # Delete settings file
   rm ~/.config/DeployForge/ModernGUI.conf  # Linux
   # Windows: Delete C:\Users\<username>\AppData\Roaming\DeployForge\ModernGUI.conf
   ```

### Issue: GUI theme broken or ugly

**Symptoms:**
- Colors are wrong
- Text is unreadable
- Buttons don't show properly

**Solutions:**

1. **Reset theme to default**:
   - Open Settings page
   - Select "Light" theme
   - Restart GUI

2. **Clear Qt cache**:
   ```bash
   # Linux
   rm -rf ~/.cache/qt_cache

   # Windows
   # Delete C:\Users\<username>\AppData\Local\DeployForge\cache
   ```

3. **Force theme reload**:
   ```python
   from deployforge.gui_modern import ThemeManager

   theme_manager = ThemeManager()
   theme_manager.apply_theme('Dark')  # or 'Light'
   ```

### Issue: Drag-and-drop not working

**Symptoms:**
- Cannot drag WIM/ISO files to GUI
- Drop events not recognized

**Solutions:**

1. **Run as Administrator** (Windows):
   - UAC blocks drag-and-drop from normal to elevated apps
   - Either run GUI as normal user OR drag from elevated explorer

2. **Check file permissions**:
   ```bash
   # Ensure file is readable
   chmod 644 image.wim
   ```

3. **Use File → Open instead**:
   - Click "Select Image" button
   - Browse to file manually

### Issue: Progress bar stuck or frozen

**Symptoms:**
- Progress bar shows but never updates
- GUI appears frozen but process is running

**Solutions:**

1. **Check logs**:
   ```bash
   tail -f ~/.config/DeployForge/logs/deployforge.log  # Linux
   # Windows: C:\Users\<username>\AppData\Local\DeployForge\logs\deployforge.log
   ```

2. **Long operations are normal**:
   - Large images (>5GB) can take 10+ minutes
   - Driver injection can take 5-15 minutes
   - Wait for completion

3. **Force refresh** (if truly frozen):
   - Press F5 to refresh GUI
   - Or restart application

---

## Permission and Access Errors

### Issue: Permission denied errors

**Symptoms:**
```
PermissionError: [Errno 13] Permission denied: 'install.wim'
Access is denied.
```

**Solutions:**

1. **Run with elevated privileges**:
   ```bash
   # Linux
   sudo deployforge ...

   # Windows: Run as Administrator
   ```

2. **Check file permissions** (Linux):
   ```bash
   # View permissions
   ls -l install.wim

   # Make readable/writable
   chmod 644 install.wim  # Read-only
   chmod 666 install.wim  # Read-write
   ```

3. **Take ownership** (Windows):
   ```powershell
   # Take ownership of file
   takeown /F install.wim

   # Grant full control
   icacls install.wim /grant %USERNAME%:F
   ```

4. **Check if file is in use**:
   ```bash
   # Linux
   lsof install.wim

   # Windows
   handle.exe install.wim
   ```

5. **Disable User Account Control** temporarily (Windows):
   - Not recommended for production
   - Use only for testing

### Issue: "Operation requires elevation"

**Symptoms:**
```
Error: This operation requires administrator privileges
Win32Error: Requires elevation
```

**Solutions:**

**Windows:**
```powershell
# Run PowerShell as Administrator
# Then run DeployForge commands
```

**Linux:**
```bash
# Use sudo
sudo deployforge mount install.wim
```

**Permanent fix (Linux):**
```bash
# Add user to sudoers for DeployForge commands
sudo visudo

# Add line:
%deployforge ALL=(ALL) NOPASSWD: /usr/local/bin/deployforge

# Add user to group
sudo usermod -aG deployforge $USER
```

---

## Driver Injection Failures

### Issue: Driver injection fails

**Symptoms:**
```
DriverInjectionError: Failed to inject driver: network_driver.inf
Error: The driver package is not compatible with this image
```

**Solutions:**

1. **Verify driver architecture**:
   ```bash
   # Check image architecture
   deployforge info install.wim | grep Architecture

   # Ensure driver matches (x64 vs x86)
   ```

2. **Check driver signature** (Windows):
   ```bash
   # Disable signature verification temporarily
   dism /Image:C:\mount /Add-Driver /Driver:driver.inf /ForceUnsigned
   ```

3. **Extract driver from .exe installer**:
   ```bash
   # Many drivers come as .exe
   # Extract to folder first
   driver_installer.exe /extract /silent

   # Then inject .inf files
   ```

4. **Inject one driver at a time**:
   ```python
   from deployforge import ImageManager

   with ImageManager('install.wim') as img:
       img.mount()

       # Inject drivers individually
       for driver in ['driver1.inf', 'driver2.inf']:
           try:
               img.inject_driver(driver)
               print(f"✓ {driver}")
           except Exception as e:
               print(f"✗ {driver}: {e}")

       img.unmount(save_changes=True)
   ```

5. **Check driver compatibility**:
   - Windows 11 requires signed drivers
   - Use manufacturer's official drivers
   - Check driver supports target Windows version

### Issue: "Driver is not compatible"

**Symptoms:**
```
Error: The third-party INF does not contain digital signature information
```

**Solutions:**

1. **Use signed drivers**:
   - Download from manufacturer's website
   - Avoid generic/modified drivers

2. **Force unsigned driver** (not recommended):
   ```python
   img.inject_driver(driver_path, force_unsigned=True)
   ```

3. **Sign driver yourself** (advanced):
   ```bash
   # Create self-signed certificate
   makecert -r -pe -ss PrivateCertStore -n "CN=DriverTestCert" DriverTest.cer

   # Sign driver
   signtool sign /a /v /s PrivateCertStore /n DriverTestCert /t http://timestamp.digicert.com driver.inf

   # Import certificate to image
   # (See Certificate Management section)
   ```

---

## Windows Update Integration Issues

### Issue: Updates fail to download

**Symptoms:**
```
UpdateError: Failed to download update KB5031354
Network error: Connection timeout
```

**Solutions:**

1. **Check internet connectivity**:
   ```bash
   ping update.microsoft.com
   ```

2. **Configure proxy** (if behind corporate proxy):
   ```python
   from deployforge.updates import UpdateManager

   updater = UpdateManager(img)
   updater.configure_proxy(
       proxy_url='http://proxy.company.com:8080',
       username='domain\\user',
       password='password'
   )
   ```

3. **Use WSUS server** (enterprise):
   ```python
   updater.configure_wsus(
       server='wsus.company.local',
       port=8530,
       use_ssl=False
   )
   ```

4. **Download updates manually**:
   ```bash
   # Download from Microsoft Update Catalog
   # https://www.catalog.update.microsoft.com/

   # Then install from local files
   deployforge updates install --source /path/to/updates/
   ```

### Issue: Update installation fails

**Symptoms:**
```
Error: Update KB5031354 failed with exit code 0x800f0922
```

**Solutions:**

1. **Check disk space**:
   ```bash
   # Windows updates need 10-20GB free space
   df -h  # Linux
   Get-PSDrive C  # Windows
   ```

2. **Install servicing stack update first**:
   ```bash
   # SSU must be installed before cumulative updates
   deployforge updates install --source SSU_KB5014032.msu
   deployforge updates install --source CUMULATIVE_KB5031354.msu
   ```

3. **Clean up WinSxS**:
   ```bash
   dism /Image:C:\mount /Cleanup-Image /StartComponentCleanup
   dism /Image:C:\mount /Cleanup-Image /SPSuperseded
   ```

4. **Check update compatibility**:
   - Ensure update matches Windows version
   - Windows 11 22H2 vs 23H2 have different updates

---

## Registry Modification Errors

### Issue: Registry key not found

**Symptoms:**
```
RegistryError: Key not found: HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion
```

**Solutions:**

1. **Use correct hive**:
   ```python
   # Correct hives:
   # HKLM (HKEY_LOCAL_MACHINE)
   # HKU (HKEY_USERS)
   # NOT: HKCU, HKCR (these don't exist in offline image)
   ```

2. **Create parent keys first**:
   ```python
   from deployforge.registry import RegistryEditor

   reg = RegistryEditor(img)

   # Create parent key
   reg.create_key('HKLM\\SOFTWARE\\MyCompany')

   # Then create sub-key
   reg.create_key('HKLM\\SOFTWARE\\MyCompany\\Settings')
   ```

3. **Check key path format**:
   ```python
   # Correct:
   reg.set_value('HKLM\\SOFTWARE\\Test', 'Value', 'Data', 'REG_SZ')

   # Incorrect (forward slashes):
   # reg.set_value('HKLM/SOFTWARE/Test', ...)

   # Incorrect (missing root):
   # reg.set_value('SOFTWARE\\Test', ...)
   ```

### Issue: Registry modification fails with "Access Denied"

**Symptoms:**
```
RegistryError: Access denied to registry key
```

**Solutions:**

1. **Run as Administrator**:
   - Registry modifications require admin privileges

2. **Check if hive is loaded**:
   ```bash
   # Windows: Check loaded hives
   reg query HKU

   # Ensure DeployForge mounted hive correctly
   ```

3. **Use offline registry editor**:
   ```bash
   # Alternative: Use reg.exe directly
   reg load HKLM\TempHive C:\mount\Windows\System32\config\SOFTWARE
   reg add HKLM\TempHive\MyKey /v Value /t REG_SZ /d Data /f
   reg unload HKLM\TempHive
   ```

---

## Performance Problems

### Issue: Operations are very slow

**Symptoms:**
- Mounting takes >5 minutes
- Driver injection takes >30 minutes
- Operations seem to hang

**Solutions:**

1. **Check disk performance**:
   ```bash
   # Test disk speed
   dd if=/dev/zero of=testfile bs=1M count=1024  # Linux

   # Windows: Use CrystalDiskMark
   ```

2. **Use SSD instead of HDD**:
   - Operations are 5-10x faster on SSD
   - Move image files to SSD

3. **Increase system resources**:
   - RAM: Minimum 8GB, recommended 16GB+
   - CPU: Multi-core helps with batch operations
   - Disk: NVMe > SATA SSD > HDD

4. **Enable caching**:
   ```python
   from deployforge import ImageManager

   img = ImageManager('install.wim', enable_cache=True)
   ```

5. **Disable antivirus scanning** for work directory:
   - Add DeployForge directories to exclusion list
   - Windows Defender can slow operations by 50%+

### Issue: High memory usage

**Symptoms:**
```
MemoryError: Out of memory
System memory usage: 95%+
```

**Solutions:**

1. **Close other applications**:
   - Image operations can use 4-8GB RAM
   - Close browsers, IDEs, etc.

2. **Reduce concurrent operations**:
   ```python
   from deployforge.batch import BatchProcessor

   # Reduce workers
   batch = BatchProcessor(max_workers=2)  # Instead of 4+
   ```

3. **Process images sequentially**:
   ```bash
   # Instead of batch processing, process one at a time
   for image in *.wim; do
       deployforge process "$image"
   done
   ```

4. **Increase swap/pagefile**:
   ```bash
   # Linux: Increase swap
   sudo fallocate -l 16G /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile

   # Windows: Increase pagefile
   # System Properties → Advanced → Performance Settings → Virtual Memory
   ```

---

## Network and Remote Storage Issues

### Issue: S3 upload fails

**Symptoms:**
```
S3Error: Failed to upload to bucket: access-denied
ClientError: An error occurred (403) when calling the PutObject operation
```

**Solutions:**

1. **Check AWS credentials**:
   ```bash
   # Verify credentials
   aws s3 ls s3://your-bucket/

   # Configure credentials
   aws configure
   ```

2. **Check bucket permissions**:
   ```json
   {
       "Version": "2012-10-17",
       "Statement": [
           {
               "Effect": "Allow",
               "Action": [
                   "s3:PutObject",
                   "s3:GetObject",
                   "s3:ListBucket"
               ],
               "Resource": [
                   "arn:aws:s3:::your-bucket/*",
                   "arn:aws:s3:::your-bucket"
               ]
           }
       ]
   }
   ```

3. **Check bucket policy**:
   - Ensure bucket allows uploads
   - Check CORS policy if accessing from web

4. **Use multipart upload** for large files:
   ```python
   from deployforge.cloud import S3Storage

   s3 = S3Storage(bucket='your-bucket')
   s3.upload(
       local_path='large_image.wim',
       remote_path='images/large_image.wim',
       multipart=True,  # Enable multipart for files >100MB
       part_size_mb=50
   )
   ```

### Issue: Azure Blob upload fails

**Symptoms:**
```
AzureError: Authentication failed
```

**Solutions:**

1. **Check connection string**:
   ```python
   from deployforge.cloud import AzureBlobStorage

   # Use connection string
   azure = AzureBlobStorage(
       connection_string='DefaultEndpointsProtocol=https;AccountName=...;AccountKey=...;EndpointSuffix=core.windows.net'
   )
   ```

2. **Check storage account access**:
   - Ensure storage account allows public access (if needed)
   - Check firewall rules

3. **Use SAS token**:
   ```python
   azure = AzureBlobStorage(
       account_url='https://youraccount.blob.core.windows.net',
       sas_token='?sv=2021-06-08&ss=b&srt=sco&sp=rwdlac&se=...'
   )
   ```

---

## VM Testing Failures

### Issue: VM fails to boot

**Symptoms:**
```
TestError: VM boot test failed - timeout after 300 seconds
```

**Solutions:**

1. **Increase timeout**:
   ```python
   from deployforge.testing import VMTester

   tester = VMTester(image_path, hypervisor)
   result = tester.test_boot(timeout=600)  # 10 minutes instead of 5
   ```

2. **Check VM configuration**:
   ```python
   # Ensure adequate resources
   tester.configure(
       memory_mb=4096,  # Minimum 4GB
       cpu_cores=2,     # Minimum 2 cores
       disk_size_gb=60  # Minimum 60GB for Windows 11
   )
   ```

3. **Enable boot logging**:
   ```python
   tester.configure(
       capture_screenshots=True,
       screenshot_interval=30,
       capture_logs=True,
       verbose=True
   )

   result = tester.test_boot()

   # Review screenshots and logs
   for i, screenshot in enumerate(result.details['screenshots']):
       with open(f'screenshot_{i}.png', 'wb') as f:
           f.write(screenshot)
   ```

4. **Check hypervisor status**:
   ```bash
   # Hyper-V (Windows)
   Get-VM
   Get-VMHost

   # VirtualBox
   vboxmanage list vms

   # Check virtualization enabled in BIOS
   systeminfo | findstr /C:"Hyper-V"  # Windows
   ```

### Issue: Hyper-V not available

**Symptoms:**
```
HypervisorError: Hyper-V is not available on this system
```

**Solutions:**

1. **Enable Hyper-V** (Windows 10/11 Pro):
   ```powershell
   # Run as Administrator
   Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
   ```

2. **Check Windows edition**:
   - Hyper-V requires Windows 10/11 Pro, Enterprise, or Education
   - Home edition does not support Hyper-V
   - Use VirtualBox or VMware instead

3. **Enable virtualization in BIOS**:
   - Restart computer
   - Enter BIOS/UEFI settings
   - Enable Intel VT-x or AMD-V
   - Save and restart

---

## MDT/SCCM Integration Problems

### Issue: Cannot connect to MDT deployment share

**Symptoms:**
```
MDTError: Failed to connect to deployment share: \\server\DeploymentShare$
Access is denied
```

**Solutions:**

1. **Check network connectivity**:
   ```bash
   # Test connection
   ping mdt-server.domain.local

   # Test SMB access
   net use \\mdt-server\DeploymentShare$ /user:domain\username
   ```

2. **Check credentials**:
   ```python
   from deployforge.integration import MDTManager

   mdt = MDTManager(
       server='\\\\mdt-server\\DeploymentShare$',
       username='domain\\administrator',
       password='password'
   )
   ```

3. **Check firewall rules**:
   - Allow SMB (ports 445, 139)
   - Allow RPC (port 135)

4. **Verify share permissions**:
   - Ensure user has Read/Write access
   - Check NTFS and Share permissions

### Issue: Task sequence import fails

**Symptoms:**
```
MDTError: Failed to import task sequence
XML parse error: Invalid XML
```

**Solutions:**

1. **Validate XML**:
   ```bash
   # Check XML syntax
   xmllint tasksequence.xml
   ```

2. **Export from MDT properly**:
   - Use MDT Workbench to export
   - Don't manually edit XML

3. **Check MDT version compatibility**:
   - DeployForge supports MDT 2013 Update 2+
   - Update MDT if using older version

---

## Certificate Installation Errors

### Issue: Certificate installation fails

**Symptoms:**
```
CertificateError: Failed to install certificate
The certificate is not valid
```

**Solutions:**

1. **Validate certificate**:
   ```python
   from deployforge.certificates import CertificateValidator

   validator = CertificateValidator()
   result = validator.validate_certificate('cert.cer')

   if not result.is_valid:
       print(f"Invalid: {result.error}")
   ```

2. **Check certificate format**:
   ```bash
   # View certificate
   openssl x509 -in cert.cer -text -noout

   # Convert format if needed
   openssl x509 -in cert.pem -outform DER -out cert.cer
   ```

3. **Check certificate expiration**:
   ```bash
   # Check validity dates
   openssl x509 -in cert.cer -noout -dates
   ```

4. **Install in correct store**:
   ```python
   # Root certificates go to 'Root' store
   cert_manager.install_certificate('root_ca.cer', store='Root')

   # Intermediate certificates go to 'CA' store
   cert_manager.install_certificate('intermediate.cer', store='CA')

   # Code signing certificates go to 'TrustedPublisher' store
   cert_manager.install_certificate('codesign.cer', store='TrustedPublisher')
   ```

---

## GPO Deployment Issues

### Issue: GPO import fails

**Symptoms:**
```
GPOError: Failed to import policy
Invalid policy XML format
```

**Solutions:**

1. **Export GPO properly**:
   ```bash
   # Use Group Policy Management Console (GPMC)
   # Right-click GPO → Backup → Export

   # Or use PowerShell
   Backup-GPO -Name "PolicyName" -Path C:\GPO_Backup
   ```

2. **Validate XML**:
   ```bash
   xmllint policy.xml
   ```

3. **Check DeployForge version**:
   - Ensure using latest version
   - GPO support improved in v1.7.0+

---

## Batch Operation Failures

### Issue: Batch processing fails for some images

**Symptoms:**
```
BatchError: 3/10 images failed to process
```

**Solutions:**

1. **Check error details**:
   ```python
   from deployforge.batch import BatchProcessor

   batch = BatchProcessor()
   # ... add jobs ...
   results = batch.execute()

   # Review failures
   for result in results:
       if result.status == 'failed':
           print(f"{result.image_path}: {result.error}")
   ```

2. **Process failed images individually**:
   ```python
   # Re-run failed images with verbose logging
   for failed in failed_images:
       try:
           process_image(failed)
       except Exception as e:
           logger.error(f"Failed to process {failed}: {e}")
   ```

3. **Reduce concurrency**:
   ```python
   # Lower max_workers to reduce resource contention
   batch = BatchProcessor(max_workers=2)
   ```

---

## Platform-Specific Issues

### Windows-Specific Issues

#### Issue: DISM fails with error 0x800f081f

**Symptoms:**
```
Error: 0x800f081f
The source files could not be found
```

**Solutions:**

1. **Specify source directory**:
   ```bash
   dism /Image:C:\mount /Enable-Feature /FeatureName:NetFx3 /Source:D:\sources\sxs /LimitAccess
   ```

2. **Use Windows installation media**:
   - Mount Windows ISO
   - Point DISM to sources\sxs folder

#### Issue: Windows Firewall blocks operations

**Solution:**
```powershell
# Add firewall rule
New-NetFirewallRule -DisplayName "DeployForge" -Direction Inbound -Program "C:\Python39\Scripts\deployforge.exe" -Action Allow
```

### Linux-Specific Issues

#### Issue: wimlib-imagex not found

**Symptoms:**
```
CommandNotFoundError: wimlib-imagex command not found
```

**Solutions:**

1. **Install wimtools**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install wimtools

   # RHEL/CentOS/Fedora
   sudo dnf install wimlib-utils

   # Arch Linux
   sudo pacman -S wimlib
   ```

2. **Verify installation**:
   ```bash
   which wimlib-imagex
   wimlib-imagex --version
   ```

#### Issue: Permission denied on /mnt

**Solution:**
```bash
# Create user-owned mount point
mkdir -p ~/mnt/wim
deployforge mount install.wim --mount-point ~/mnt/wim

# Or use sudo
sudo deployforge mount install.wim
```

### macOS-Specific Issues

#### Issue: FUSE not available

**Symptoms:**
```
Error: FUSE is not installed
```

**Solutions:**

1. **Install macFUSE**:
   ```bash
   brew install macfuse
   ```

2. **Allow kernel extension**:
   - System Preferences → Security & Privacy
   - Allow "Benjaming Fleischer"
   - Restart

---

## Error Messages Reference

### Common Error Codes

| Error Code | Meaning | Solution |
|------------|---------|----------|
| 0x800f081f | Source files not found | Specify source directory |
| 0x800f0906 | Image already mounted | Unmount first |
| 0x80070003 | Path not found | Check file path |
| 0x80070005 | Access denied | Run as administrator |
| 0x8007007b | Invalid file name | Check filename syntax |
| 0x800f0922 | Update installation failed | Check disk space |

### DeployForge-Specific Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `ImageNotFoundError` | Image file doesn't exist | Check file path |
| `MountError` | Failed to mount image | Check permissions, run as admin |
| `UnsupportedFormatError` | Image format not supported | Use WIM/ESD/ISO/PPKG/VHD/VHDX |
| `DriverInjectionError` | Driver injection failed | Check driver signature |
| `RegistryError` | Registry operation failed | Check key path format |
| `DeployForgeError` | General error | Check logs for details |

---

## Advanced Diagnostics

### Enable Debug Logging

```python
import logging
from deployforge import ImageManager

# Set debug level
logging.basicConfig(level=logging.DEBUG)

# Or configure in code
logger = logging.getLogger('deployforge')
logger.setLevel(logging.DEBUG)

# Add file handler
handler = logging.FileHandler('deployforge_debug.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
```

### Collect Diagnostic Information

```bash
# Generate diagnostic report
deployforge diagnose --full --output diag_report.txt

# Report includes:
# - System information
# - Python version and packages
# - System dependencies
# - Mount status
# - Disk space
# - Recent logs
# - Error traces
```

### Check System Requirements

```bash
# Run system check
deployforge check-system

# Output:
# ✓ Python 3.11.0
# ✓ Administrator privileges
# ✓ Disk space: 250GB available
# ✓ Memory: 16GB
# ✓ DISM available
# ✗ wimlib-imagex not found
# ! Warning: Antivirus may slow operations
```

---

## Getting Help

### Before Asking for Help

1. **Check this troubleshooting guide**
2. **Run diagnostics**: `deployforge diagnose`
3. **Check logs**: `~/.config/DeployForge/logs/` (Linux) or `%LOCALAPPDATA%\DeployForge\logs\` (Windows)
4. **Search existing issues**: https://github.com/Cornman92/DeployForge/issues
5. **Try with latest version**: `pip install --upgrade deployforge`

### Reporting Issues

When reporting issues, include:

1. **DeployForge version**: `deployforge --version`
2. **Python version**: `python --version`
3. **Operating system**: `Windows 11`, `Ubuntu 22.04`, etc.
4. **Full error message** (including stack trace)
5. **Steps to reproduce**
6. **Diagnostic report**: `deployforge diagnose --output diag.txt`
7. **Relevant logs**

### Getting Support

- **GitHub Issues**: https://github.com/Cornman92/DeployForge/issues
- **Documentation**: https://deployforge.readthedocs.io
- **Email**: support@deployforge.com
- **Enterprise Support**: enterprise-support@deployforge.com

### Community Resources

- **Discord**: https://discord.gg/deployforge
- **Reddit**: r/DeployForge
- **Stack Overflow**: Tag with `deployforge`

---

## Appendix: Useful Commands

### Quick Reference

```bash
# Diagnostics
deployforge diagnose
deployforge check-system
deployforge --version

# Mounting
deployforge mount image.wim
deployforge unmount image.wim
deployforge list-mounts

# Information
deployforge info image.wim
deployforge list image.wim

# Cleanup
deployforge cache clear
deployforge cleanup-mounts

# Logging
deployforge logs --tail 50
deployforge logs --level ERROR
```

---

**Version**: 1.7.0
**Last Updated**: 2025-11-17

For additional help, see:
- **GUI_GUIDE.md** - GUI-specific troubleshooting
- **ENTERPRISE_GUIDE.md** - Enterprise feature troubleshooting
- **README.md** - General documentation
