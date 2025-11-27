# DeployForge PowerShell Scripts

Native Windows automation scripts for DeployForge using DISM, PowerShell cmdlets, and native Windows tools.

## Overview

This directory contains PowerShell scripts that provide Windows-native alternatives to the Python-based DeployForge toolkit. All scripts use native Windows tools (DISM, reg.exe, PowerShell cmdlets) and require no external dependencies beyond Windows itself.

## Requirements

- **Windows Version**: Windows 10/11 or Windows Server 2016+
- **PowerShell**: Version 5.1 or higher
- **Privileges**: Administrator rights required
- **DISM**: Built-in Windows Deployment Image Servicing and Management tool
- **Windows ADK**: Optional, for advanced WinPE customization

## Script Inventory

### Utility Module

#### DeployForge-Utilities.psm1

Core PowerShell module providing reusable functions for all scripts.

**Functions:**
- `Mount-WindowsDeploymentImage` - Mount WIM/ESD images
- `Dismount-WindowsDeploymentImage` - Unmount and save/discard changes
- `Get-WindowsImageInfo` - Get image metadata
- `Mount-RegistryHive` - Load offline registry hives
- `Dismount-RegistryHive` - Unload registry hives
- `Set-OfflineRegistryValue` - Modify offline registry
- `Add-WindowsImagePackage` - Install packages
- `Remove-WindowsImagePackage` - Remove packages
- `Add-WindowsImageDriver` - Inject drivers
- `Remove-WindowsImageDriver` - Remove drivers
- `Enable-WindowsImageFeature` - Enable Windows features
- `Disable-WindowsImageFeature` - Disable features
- `Add-WindowsImageCapability` - Add capabilities
- `Remove-WindowsImageCapability` - Remove capabilities

**Usage:**
```powershell
Import-Module .\DeployForge-Utilities.psm1

# Mount image
Mount-WindowsDeploymentImage -ImagePath "C:\Images\install.wim" -Index 1 -MountPath "C:\Mount"

# Modify registry
Mount-RegistryHive -Hive SOFTWARE -KeyName "HKLM\TEMP_SOFTWARE"
Set-OfflineRegistryValue -Path "HKLM\TEMP_SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -Name "EnableLUA" -Value 0 -Type DWord
Dismount-RegistryHive -KeyName "HKLM\TEMP_SOFTWARE"

# Dismount and save
Dismount-WindowsDeploymentImage -MountPath "C:\Mount" -Save
```

### Build Scripts

#### Build-GamingImage.ps1

Create gaming-optimized Windows deployment images.

**Features:**
- 4 gaming profiles: Competitive, Balanced, Quality, Streaming
- Game Mode and GPU Hardware Scheduling
- Network optimizations (TCP tuning)
- Disable unnecessary services (SysMain, WSearch, DiagTrack)
- Remove bloatware and Xbox apps
- Performance-focused power plans

**Usage:**
```powershell
.\Build-GamingImage.ps1 -ImagePath "C:\Images\install.wim" -OutputPath "C:\Images\gaming.wim" -Profile Competitive
```

**Profiles:**
- **Competitive**: Maximum performance, minimum latency
- **Balanced**: Performance with quality balance
- **Quality**: Visual quality prioritized
- **Streaming**: Optimized for game streaming

**Size Reduction**: ~1-2 GB (bloatware removal)

---

#### Build-EnterpriseImage.ps1

Create enterprise-hardened Windows images with security focus.

**Features:**
- CIS Benchmark security settings
- BitLocker preparation
- Disable Cortana and telemetry
- Disable consumer features
- Enable Windows Defender
- Firewall configuration
- Disable SMBv1, LLMNR
- UAC and security policies

**Usage:**
```powershell
.\Build-EnterpriseImage.ps1 -ImagePath "C:\Images\install.wim" -OutputPath "C:\Images\enterprise.wim" -ApplyCISBenchmark -EnableBitLocker
```

**Parameters:**
- `-ApplyCISBenchmark`: Apply CIS security hardening
- `-EnableBitLocker`: Enable BitLocker preparation

**Compliance**: CIS Microsoft Windows 10/11 Benchmark Level 1

---

#### Build-DeveloperImage.ps1

Create developer workstation images with development tools and optimizations.

**Features:**
- 5 developer profiles: FullStack, Backend, Frontend, DataScience, DevOps
- Enable Developer Mode
- Install WSL, Hyper-V, Containers
- IIS and .NET Framework
- Long path support (260+ character paths)
- PowerShell ExecutionPolicy = RemoteSigned
- File Explorer optimizations (show hidden files, extensions)
- Git integration preparation
- OpenSSH client

**Usage:**
```powershell
.\Build-DeveloperImage.ps1 -ImagePath "C:\Images\install.wim" -OutputPath "C:\Images\developer.wim" -DevProfile FullStack
```

**Profiles:**
- **FullStack**: Web development (IIS, Node.js, containers)
- **Backend**: Server-side development (containers, Hyper-V)
- **Frontend**: UI/UX development
- **DataScience**: Data analysis (Hyper-V, VMs)
- **DevOps**: CI/CD and automation (containers, Hyper-V, virtualization)

**Post-Deployment Recommendations:**
1. Install Visual Studio / VS Code
2. Install Git and configure credentials
3. Install Node.js, Python, or other runtimes
4. Configure WSL2 and Docker Desktop
5. Install package managers (Chocolatey, Scoop, winget)

---

### Automation Scripts

#### Update-ImageDrivers.ps1

Automated driver injection into Windows images.

**Features:**
- Batch driver injection
- Recursive driver scanning
- Automatic backup creation
- Driver validation
- Unsigned driver support (optional)
- Comprehensive reporting

**Usage:**
```powershell
# Inject network drivers
.\Update-ImageDrivers.ps1 -ImagePath "C:\Images\install.wim" -DriverPath "C:\Drivers\Network" -Recurse

# Inject all drivers including unsigned
.\Update-ImageDrivers.ps1 -ImagePath "C:\Images\boot.wim" -DriverPath "C:\Drivers" -Index 2 -Recurse -ForceUnsigned
```

**Best Practices:**
- Always test injected drivers
- Use manufacturer-provided drivers
- Inject only necessary drivers
- Keep drivers up to date
- Use `-Recurse` for organized driver folders

**Automatic Backup**: Creates timestamped backup before injection

---

#### Export-ImageReport.ps1

Generate comprehensive Windows image analysis reports.

**Features:**
- 3 report formats: HTML, JSON, Text
- Image metadata and statistics
- Provisioned packages inventory
- Driver catalog
- Windows features status
- Installed capabilities
- File system statistics
- Interactive HTML reports with styling

**Usage:**
```powershell
# Generate HTML report
.\Export-ImageReport.ps1 -ImagePath "C:\Images\install.wim" -Format HTML

# Generate JSON report for automation
.\Export-ImageReport.ps1 -ImagePath "C:\Images\custom.wim" -Index 2 -OutputPath "C:\Reports\image.json" -Format JSON
```

**Report Formats:**
- **HTML**: Beautiful web-based report with charts and tables
- **JSON**: Machine-readable format for automation
- **Text**: Plain text for terminal viewing

**Report Contents:**
- Image name, edition, version, build, size
- Languages and architecture
- Provisioned packages (AppX)
- Installed drivers with versions
- Enabled Windows features
- Installed Windows capabilities
- File and folder counts

**Performance**: Read-only mount, no changes made to image

---

#### Build-DeploymentUSB.ps1

Create bootable Windows deployment USB drives.

**Features:**
- UEFI and Legacy BIOS support
- Automatic partitioning (GPT or MBR)
- Large file splitting (install.wim > 4GB for FAT32)
- Boot sector configuration
- Drive verification
- Safety confirmations

**Usage:**
```powershell
# Create UEFI bootable USB
.\Build-DeploymentUSB.ps1 -IsoPath "C:\ISOs\Windows11.iso" -DriveLetter "E:" -BootMode UEFI

# Create dual-boot USB (UEFI + Legacy)
.\Build-DeploymentUSB.ps1 -IsoPath "C:\ISOs\Windows10.iso" -DriveLetter "F:" -BootMode Both -Label "WIN10_PRO"
```

**Boot Modes:**
- **UEFI**: Modern systems (GPT, FAT32)
- **Legacy**: Older systems (MBR, NTFS)
- **Both**: Universal compatibility (splits large files)

**⚠️ WARNING**: This script erases all data on the target drive! Double-check drive letter before running.

**Requirements:**
- USB drive: 8GB minimum (16GB recommended)
- Windows ISO file
- Administrator privileges

**Time Required**: 10-20 minutes depending on USB speed

---

## Common Workflows

### Workflow 1: Gaming PC Build

```powershell
# 1. Create gaming image
.\Build-GamingImage.ps1 -ImagePath "C:\Images\Win11.wim" -OutputPath "C:\Images\Gaming.wim" -Profile Competitive

# 2. Inject GPU drivers
.\Update-ImageDrivers.ps1 -ImagePath "C:\Images\Gaming.wim" -DriverPath "C:\Drivers\NVIDIA" -Recurse

# 3. Generate report
.\Export-ImageReport.ps1 -ImagePath "C:\Images\Gaming.wim" -Format HTML

# 4. Create bootable USB
.\Build-DeploymentUSB.ps1 -IsoPath "C:\ISOs\Win11.iso" -DriveLetter "E:" -BootMode UEFI
```

### Workflow 2: Enterprise Deployment

```powershell
# 1. Create hardened enterprise image
.\Build-EnterpriseImage.ps1 -ImagePath "C:\Images\Win10.wim" -OutputPath "C:\Images\Enterprise.wim" -ApplyCISBenchmark -EnableBitLocker

# 2. Inject corporate drivers
.\Update-ImageDrivers.ps1 -ImagePath "C:\Images\Enterprise.wim" -DriverPath "\\FileServer\Drivers\Corporate" -Recurse

# 3. Generate compliance report
.\Export-ImageReport.ps1 -ImagePath "C:\Images\Enterprise.wim" -Format JSON -OutputPath "\\FileServer\Reports\enterprise.json"

# 4. Create deployment media
.\Build-DeploymentUSB.ps1 -IsoPath "C:\ISOs\Win10-Enterprise.iso" -DriveLetter "E:" -BootMode Both -Label "CORP_WIN10"
```

### Workflow 3: Developer Workstation

```powershell
# 1. Create developer image
.\Build-DeveloperImage.ps1 -ImagePath "C:\Images\Win11.wim" -OutputPath "C:\Images\DevWorkstation.wim" -DevProfile FullStack

# 2. Inject development drivers (Wi-Fi, Ethernet, etc.)
.\Update-ImageDrivers.ps1 -ImagePath "C:\Images\DevWorkstation.wim" -DriverPath "C:\Drivers\Dev" -Recurse

# 3. Generate image inventory
.\Export-ImageReport.ps1 -ImagePath "C:\Images\DevWorkstation.wim" -Format HTML

# 4. Deploy to USB for installation
.\Build-DeploymentUSB.ps1 -IsoPath "C:\ISOs\Win11-Pro.iso" -DriveLetter "F:" -BootMode UEFI -Label "DEV_SETUP"
```

## Advanced Usage

### Custom Registry Modifications

```powershell
Import-Module .\DeployForge-Utilities.psm1

Mount-WindowsDeploymentImage -ImagePath "C:\Images\install.wim" -Index 1 -MountPath "C:\Mount"

# Load SOFTWARE hive
Mount-RegistryHive -Hive SOFTWARE -KeyName "HKLM\TEMP_SOFTWARE"

# Custom modifications
Set-OfflineRegistryValue -Path "HKLM\TEMP_SOFTWARE\Policies\Microsoft\Edge" -Name "HideFirstRunExperience" -Value 1 -Type DWord
Set-OfflineRegistryValue -Path "HKLM\TEMP_SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer" -Name "NoAutorun" -Value 1 -Type DWord

# Unload hive
Dismount-RegistryHive -KeyName "HKLM\TEMP_SOFTWARE"

Dismount-WindowsDeploymentImage -MountPath "C:\Mount" -Save
```

### Batch Operations

```powershell
# Process multiple images
$images = @(
    @{Input = "C:\Images\Win10-Home.wim"; Output = "C:\Images\Gaming-Home.wim"; Profile = "Gaming"},
    @{Input = "C:\Images\Win10-Pro.wim"; Output = "C:\Images\Gaming-Pro.wim"; Profile = "Gaming"},
    @{Input = "C:\Images\Win11-Home.wim"; Output = "C:\Images\Gaming-W11.wim"; Profile = "Gaming"}
)

foreach ($img in $images) {
    Write-Host "Processing $($img.Input)..." -ForegroundColor Cyan
    .\Build-GamingImage.ps1 -ImagePath $img.Input -OutputPath $img.Output -Profile Competitive
    .\Export-ImageReport.ps1 -ImagePath $img.Output -Format HTML
}
```

## Troubleshooting

### Common Issues

#### 1. Access Denied Errors

**Problem**: "Access denied" when mounting images or modifying registry

**Solution**:
```powershell
# Run PowerShell as Administrator
Start-Process powershell -Verb RunAs

# Check execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 2. Image Already Mounted

**Problem**: "The image is already mounted" error

**Solution**:
```powershell
# List mounted images
Get-WindowsImage -Mounted

# Cleanup all mount points
DISM /Cleanup-Mountpoints

# Or use utility function
Dismount-WindowsDeploymentImage -MountPath "C:\Mount" -Discard
```

#### 3. Registry Hive Still Loaded

**Problem**: "The process cannot access the file because it is being used by another process"

**Solution**:
```powershell
# Manually unload registry hives
reg unload HKLM\TEMP_SOFTWARE
reg unload HKLM\TEMP_SYSTEM

# Restart explorer if needed
Stop-Process -Name explorer -Force
Start-Process explorer
```

#### 4. USB Creation Fails

**Problem**: USB drive not bootable after creation

**Solution**:
```powershell
# Verify UEFI boot files
Test-Path "E:\efi\boot\bootx64.efi"
Test-Path "E:\efi\microsoft\boot\bcd"

# Verify Legacy boot files
Test-Path "E:\bootmgr"
Test-Path "E:\boot\bcd"

# Re-run with -BootMode Both for maximum compatibility
.\Build-DeploymentUSB.ps1 -IsoPath "C:\ISOs\Windows.iso" -DriveLetter "E:" -BootMode Both
```

## Script Comparison

| Feature | Gaming | Enterprise | Developer | Driver Update | USB Creator | Report Generator |
|---------|--------|------------|-----------|---------------|-------------|------------------|
| **Purpose** | Performance | Security | Development | Driver Mgmt | Bootable Media | Analysis |
| **Profiles** | 4 | 2 | 5 | N/A | 3 boot modes | 3 formats |
| **Bloatware Removal** | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Registry Tweaks** | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Driver Injection** | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| **Time Required** | 10-15 min | 15-20 min | 15-20 min | 5-10 min | 10-20 min | 3-5 min |

## Best Practices

1. **Always backup original images** before modification
2. **Test images in VM** before production deployment (Hyper-V, VirtualBox)
3. **Document customizations** for compliance and troubleshooting
4. **Version control images** with meaningful names (Win11-Gaming-v1.0.wim)
5. **Keep drivers updated** regularly update driver repositories
6. **Validate images** use Export-ImageReport.ps1 to verify contents
7. **Use profiles** leverage built-in profiles for consistency
8. **Cleanup mount points** always use DISM /Cleanup-Mountpoints after errors

## Security Considerations

- **Run as Administrator**: Required for DISM and registry operations
- **Validate sources**: Only use trusted ISO files and drivers
- **Scan for malware**: Antivirus scan driver packages before injection
- **Network isolation**: Process images on isolated/offline systems
- **Audit trail**: Keep logs of all modifications for compliance
- **Signed drivers**: Prefer signed drivers, avoid `-ForceUnsigned` when possible
- **BitLocker**: Use `-EnableBitLocker` for enterprise deployments
- **CIS Benchmarks**: Apply `-ApplyCISBenchmark` for security hardening

## Compatibility

### Windows Versions Supported

- ✅ Windows 10 (all editions)
- ✅ Windows 11 (all editions)
- ✅ Windows Server 2016
- ✅ Windows Server 2019
- ✅ Windows Server 2022

### Image Formats Supported

- ✅ WIM (Windows Imaging Format)
- ✅ ESD (Electronic Software Download - compressed WIM)

### Architecture Support

- ✅ x64 (amd64)
- ✅ ARM64 (with compatible drivers)

## Contributing

To contribute improvements to these scripts:

1. Follow existing code style and structure
2. Add comprehensive error handling
3. Include parameter validation
4. Add detailed help comments
5. Test on multiple Windows versions
6. Document any new features in this README

## License

These scripts are part of the DeployForge project and are licensed under the MIT License.

## Support

For issues or questions:
- GitHub Issues: https://github.com/Cornman92/DeployForge/issues
- Documentation: https://github.com/Cornman92/DeployForge/tree/main/docs

## Version History

- **v0.3.0** (2025-11-15): Initial PowerShell script suite
  - DeployForge-Utilities.psm1 module
  - Build-GamingImage.ps1
  - Build-EnterpriseImage.ps1
  - Build-DeveloperImage.ps1
  - Update-ImageDrivers.ps1
  - Export-ImageReport.ps1
  - Build-DeploymentUSB.ps1

---

**DeployForge Team** | Windows Deployment Automation
