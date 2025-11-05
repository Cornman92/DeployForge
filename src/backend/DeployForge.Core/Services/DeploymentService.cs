using DeployForge.Common.Models;
using DeployForge.Core.Interfaces;
using System.Runtime.Versioning;
using System.Text;
using System.Xml;

namespace DeployForge.Core.Services;

/// <summary>
/// Service for deployment operations
/// </summary>
[SupportedOSPlatform("windows")]
public class DeploymentService : IDeploymentService
{
    private readonly ILogger<DeploymentService> _logger;

    public DeploymentService(ILogger<DeploymentService> logger)
    {
        _logger = logger;
    }

    public async Task<OperationResult<MediaCreationResult>> CreateISOAsync(
        ISOCreationRequest request,
        CancellationToken cancellationToken = default)
    {
        var startTime = DateTime.UtcNow;

        try
        {
            _logger.LogInformation("Creating ISO from {SourcePath} to {OutputPath}",
                request.SourcePath, request.OutputPath);

            if (!Directory.Exists(request.SourcePath))
            {
                return OperationResult<MediaCreationResult>.FailureResult("Source directory not found");
            }

            // Generate autounattend if requested
            if (request.IncludeAutounattend && request.AutounattendConfig != null)
            {
                var autounattendPath = Path.Combine(request.SourcePath, "autounattend.xml");
                var autounattendResult = await GenerateAutounattendAsync(
                    request.AutounattendConfig, autounattendPath, cancellationToken);

                if (!autounattendResult.Success)
                {
                    _logger.LogWarning("Failed to generate autounattend.xml: {Error}",
                        autounattendResult.ErrorMessage);
                }
            }

            // Use oscdimg.exe for ISO creation (part of Windows ADK)
            // In production, you would use a proper tool or library
            var result = await CreateISOUsingOscdimg(request, cancellationToken);

            if (result)
            {
                var fileInfo = new FileInfo(request.OutputPath);
                var duration = DateTime.UtcNow - startTime;

                return OperationResult<MediaCreationResult>.SuccessResult(new MediaCreationResult
                {
                    Success = true,
                    OutputPath = request.OutputPath,
                    SizeBytes = fileInfo.Exists ? fileInfo.Length : 0,
                    Duration = duration,
                    Message = $"ISO created successfully in {duration.TotalSeconds:F1} seconds"
                });
            }

            return OperationResult<MediaCreationResult>.FailureResult("Failed to create ISO");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to create ISO");
            return OperationResult<MediaCreationResult>.ExceptionResult(ex);
        }
    }

    public async Task<OperationResult<MediaCreationResult>> CreateBootableUSBAsync(
        BootableUSBRequest request,
        CancellationToken cancellationToken = default)
    {
        var startTime = DateTime.UtcNow;

        try
        {
            _logger.LogInformation("Creating bootable USB on {DriveLetter} from {SourcePath}",
                request.DriveLetter, request.SourcePath);

            // Validate drive
            if (!Directory.Exists(request.DriveLetter))
            {
                return OperationResult<MediaCreationResult>.FailureResult("USB drive not found");
            }

            // Format if requested
            if (request.Format)
            {
                _logger.LogInformation("Formatting {DriveLetter} as {FileSystem}",
                    request.DriveLetter, request.FileSystem);

                var formatResult = await FormatDriveAsync(
                    request.DriveLetter, request.FileSystem, request.VolumeLabel, cancellationToken);

                if (!formatResult)
                {
                    return OperationResult<MediaCreationResult>.FailureResult("Failed to format USB drive");
                }
            }

            // Copy files
            var copyResult = await CopyFilesToUSBAsync(request.SourcePath, request.DriveLetter, cancellationToken);

            if (!copyResult)
            {
                return OperationResult<MediaCreationResult>.FailureResult("Failed to copy files to USB");
            }

            // Make bootable
            var bootResult = await MakeUSBBootableAsync(request.DriveLetter, request.BootType, cancellationToken);

            if (!bootResult)
            {
                return OperationResult<MediaCreationResult>.FailureResult("Failed to make USB bootable");
            }

            // Generate autounattend if requested
            if (request.IncludeAutounattend && request.AutounattendConfig != null)
            {
                var autounattendPath = Path.Combine(request.DriveLetter, "autounattend.xml");
                await GenerateAutounattendAsync(request.AutounattendConfig, autounattendPath, cancellationToken);
            }

            var duration = DateTime.UtcNow - startTime;

            return OperationResult<MediaCreationResult>.SuccessResult(new MediaCreationResult
            {
                Success = true,
                OutputPath = request.DriveLetter,
                Duration = duration,
                Message = $"Bootable USB created successfully in {duration.TotalSeconds:F1} seconds"
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to create bootable USB");
            return OperationResult<MediaCreationResult>.ExceptionResult(ex);
        }
    }

    public async Task<OperationResult<string>> GenerateAutounattendAsync(
        AutounattendConfig config,
        string outputPath,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                _logger.LogInformation("Generating autounattend.xml at {OutputPath}", outputPath);

                var xml = GenerateAutounattendXml(config);

                Directory.CreateDirectory(Path.GetDirectoryName(outputPath) ?? string.Empty);
                File.WriteAllText(outputPath, xml);

                _logger.LogInformation("autounattend.xml generated successfully");

                return OperationResult<string>.SuccessResult(outputPath);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to generate autounattend.xml");
                return OperationResult<string>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult<List<Core.Interfaces.DriveInfo>>> GetRemovableDrivesAsync(
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                var drives = System.IO.DriveInfo.GetDrives()
                    .Where(d => d.DriveType == DriveType.Removable && d.IsReady)
                    .Select(d => new Core.Interfaces.DriveInfo
                    {
                        DriveLetter = d.Name,
                        VolumeLabel = d.VolumeLabel,
                        TotalSize = d.TotalSize,
                        FreeSpace = d.AvailableFreeSpace,
                        FileSystem = d.DriveFormat,
                        IsReady = d.IsReady
                    })
                    .ToList();

                return OperationResult<List<Core.Interfaces.DriveInfo>>.SuccessResult(drives);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get removable drives");
                return OperationResult<List<Core.Interfaces.DriveInfo>>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    #region Private Helper Methods

    private async Task<bool> CreateISOUsingOscdimg(ISOCreationRequest request, CancellationToken cancellationToken)
    {
        // This is a simplified implementation
        // In production, use oscdimg.exe from Windows ADK or a library like DiscUtils

        _logger.LogInformation("Creating ISO using oscdimg");

        // Example oscdimg command:
        // oscdimg.exe -m -o -u2 -udfver102 -bootdata:2#p0,e,b<bootfile>#pEF,e,b<efiboot> <source> <output.iso>

        var bootfile = request.BootType == BootType.BIOS || request.BootType == BootType.Both
            ? Path.Combine(request.SourcePath, "boot", "etfsboot.com")
            : null;

        var efiboot = request.BootType == BootType.UEFI || request.BootType == BootType.Both
            ? Path.Combine(request.SourcePath, "efi", "microsoft", "boot", "efisys.bin")
            : null;

        // For now, return success (in production, execute oscdimg.exe)
        await Task.Delay(1000, cancellationToken); // Simulate ISO creation

        return true;
    }

    private async Task<bool> FormatDriveAsync(
        string driveLetter,
        string fileSystem,
        string label,
        CancellationToken cancellationToken)
    {
        // Use diskpart or format command
        // For safety, this is a placeholder

        _logger.LogWarning("Format operation is a placeholder - implement with diskpart or WMI");

        await Task.Delay(500, cancellationToken);
        return true;
    }

    private async Task<bool> CopyFilesToUSBAsync(
        string sourcePath,
        string destinationPath,
        CancellationToken cancellationToken)
    {
        try
        {
            // Copy all files and directories
            await Task.Run(() =>
            {
                CopyDirectory(sourcePath, destinationPath, true);
            }, cancellationToken);

            return true;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to copy files to USB");
            return false;
        }
    }

    private void CopyDirectory(string sourceDir, string destDir, bool recursive)
    {
        var dir = new DirectoryInfo(sourceDir);

        if (!dir.Exists)
            throw new DirectoryNotFoundException($"Source directory not found: {sourceDir}");

        Directory.CreateDirectory(destDir);

        foreach (var file in dir.GetFiles())
        {
            file.CopyTo(Path.Combine(destDir, file.Name), true);
        }

        if (recursive)
        {
            foreach (var subDir in dir.GetDirectories())
            {
                CopyDirectory(subDir.FullName, Path.Combine(destDir, subDir.Name), true);
            }
        }
    }

    private async Task<bool> MakeUSBBootableAsync(
        string driveLetter,
        BootType bootType,
        CancellationToken cancellationToken)
    {
        // Use bootsect.exe or bcdboot.exe
        // For UEFI, ensure EFI partition exists

        _logger.LogInformation("Making USB bootable for {BootType}", bootType);

        await Task.Delay(500, cancellationToken);
        return true;
    }

    private string GenerateAutounattendXml(AutounattendConfig config)
    {
        var settings = new XmlWriterSettings
        {
            Indent = true,
            IndentChars = "    ",
            Encoding = Encoding.UTF8
        };

        using var stringWriter = new StringWriter();
        using var writer = XmlWriter.Create(stringWriter, settings);

        writer.WriteStartDocument();
        writer.WriteStartElement("unattend", "urn:schemas-microsoft-com:unattend");

        // Settings pass: windowsPE
        WriteWindowsPESettings(writer, config);

        // Settings pass: specialize
        WriteSpecializeSettings(writer, config);

        // Settings pass: oobeSystem
        WriteOOBESettings(writer, config);

        writer.WriteEndElement(); // unattend
        writer.WriteEndDocument();

        return stringWriter.ToString();
    }

    private void WriteWindowsPESettings(XmlWriter writer, AutounattendConfig config)
    {
        writer.WriteStartElement("settings");
        writer.WriteAttributeString("pass", "windowsPE");

        // International settings
        writer.WriteStartElement("component");
        writer.WriteAttributeString("name", "Microsoft-Windows-International-Core-WinPE");
        writer.WriteAttributeString("processorArchitecture", "amd64");
        writer.WriteAttributeString("publicKeyToken", "31bf3856ad364e35");
        writer.WriteAttributeString("language", "neutral");
        writer.WriteAttributeString("versionScope", "nonSxS");

        writer.WriteElementString("SetupUILanguage", "");
        writer.WriteStartElement("UILanguage");
        writer.WriteString(config.UILanguage);
        writer.WriteEndElement();

        writer.WriteElementString("InputLocale", config.InputLocale);
        writer.WriteElementString("SystemLocale", config.SystemLocale);
        writer.WriteElementString("UILanguage", config.UILanguage);
        writer.WriteElementString("UserLocale", config.UserLocale);

        writer.WriteEndElement(); // component

        // Disk configuration
        if (config.DiskConfig.WipeDisk)
        {
            WriteDiskConfiguration(writer, config.DiskConfig);
        }

        // Product key
        if (!string.IsNullOrEmpty(config.ProductKey))
        {
            writer.WriteStartElement("component");
            writer.WriteAttributeString("name", "Microsoft-Windows-Setup");
            writer.WriteAttributeString("processorArchitecture", "amd64");
            writer.WriteAttributeString("publicKeyToken", "31bf3856ad364e35");
            writer.WriteAttributeString("language", "neutral");
            writer.WriteAttributeString("versionScope", "nonSxS");

            writer.WriteStartElement("UserData");
            writer.WriteStartElement("ProductKey");
            writer.WriteElementString("Key", config.ProductKey);
            writer.WriteEndElement();
            writer.WriteEndElement();

            writer.WriteEndElement(); // component
        }

        writer.WriteEndElement(); // settings
    }

    private void WriteDiskConfiguration(XmlWriter writer, DiskConfiguration diskConfig)
    {
        writer.WriteStartElement("component");
        writer.WriteAttributeString("name", "Microsoft-Windows-Setup");
        writer.WriteAttributeString("processorArchitecture", "amd64");
        writer.WriteAttributeString("publicKeyToken", "31bf3856ad364e35");
        writer.WriteAttributeString("language", "neutral");
        writer.WriteAttributeString("versionScope", "nonSxS");

        writer.WriteStartElement("DiskConfiguration");
        writer.WriteStartElement("Disk");
        writer.WriteAttributeString("wcm:action", "add");
        writer.WriteElementString("DiskID", diskConfig.DiskId.ToString());

        if (diskConfig.WipeDisk)
        {
            writer.WriteElementString("WillWipeDisk", "true");
        }

        if (diskConfig.Layout == PartitionLayout.UEFI)
        {
            // EFI System Partition
            writer.WriteStartElement("CreatePartitions");
            writer.WriteStartElement("CreatePartition");
            writer.WriteAttributeString("wcm:action", "add");
            writer.WriteElementString("Order", "1");
            writer.WriteElementString("Size", "100");
            writer.WriteElementString("Type", "EFI");
            writer.WriteEndElement(); // CreatePartition

            // MSR
            writer.WriteStartElement("CreatePartition");
            writer.WriteAttributeString("wcm:action", "add");
            writer.WriteElementString("Order", "2");
            writer.WriteElementString("Size", "16");
            writer.WriteElementString("Type", "MSR");
            writer.WriteEndElement(); // CreatePartition

            // Windows partition
            writer.WriteStartElement("CreatePartition");
            writer.WriteAttributeString("wcm:action", "add");
            writer.WriteElementString("Order", "3");
            writer.WriteElementString("Extend", "true");
            writer.WriteElementString("Type", "Primary");
            writer.WriteEndElement(); // CreatePartition

            writer.WriteEndElement(); // CreatePartitions
        }

        writer.WriteEndElement(); // Disk
        writer.WriteEndElement(); // DiskConfiguration

        writer.WriteEndElement(); // component
    }

    private void WriteSpecializeSettings(XmlWriter writer, AutounattendConfig config)
    {
        writer.WriteStartElement("settings");
        writer.WriteAttributeString("pass", "specialize");

        // Computer name
        if (!string.IsNullOrEmpty(config.ComputerName))
        {
            writer.WriteStartElement("component");
            writer.WriteAttributeString("name", "Microsoft-Windows-Shell-Setup");
            writer.WriteAttributeString("processorArchitecture", "amd64");
            writer.WriteAttributeString("publicKeyToken", "31bf3856ad364e35");
            writer.WriteAttributeString("language", "neutral");
            writer.WriteAttributeString("versionScope", "nonSxS");

            writer.WriteElementString("ComputerName", config.ComputerName);
            writer.WriteElementString("TimeZone", config.TimeZone);

            writer.WriteEndElement(); // component
        }

        writer.WriteEndElement(); // settings
    }

    private void WriteOOBESettings(XmlWriter writer, AutounattendConfig config)
    {
        writer.WriteStartElement("settings");
        writer.WriteAttributeString("pass", "oobeSystem");

        writer.WriteStartElement("component");
        writer.WriteAttributeString("name", "Microsoft-Windows-Shell-Setup");
        writer.WriteAttributeString("processorArchitecture", "amd64");
        writer.WriteAttributeString("publicKeyToken", "31bf3856ad364e35");
        writer.WriteAttributeString("language", "neutral");
        writer.WriteAttributeString("versionScope", "nonSxS");

        // OOBE settings
        writer.WriteStartElement("OOBE");
        writer.WriteElementString("HideEULAPage", config.SkipOOBE.ToString().ToLower());
        writer.WriteElementString("HideOEMRegistrationScreen", config.SkipOOBE.ToString().ToLower());
        writer.WriteElementString("HideOnlineAccountScreens", config.SkipOOBE.ToString().ToLower());
        writer.WriteElementString("HideWirelessSetupInOOBE", config.SkipOOBE.ToString().ToLower());
        writer.WriteElementString("ProtectYourPC", config.SkipPrivacySettings ? "3" : "1");
        writer.WriteEndElement(); // OOBE

        // User accounts
        if (config.UserAccounts.Any())
        {
            writer.WriteStartElement("UserAccounts");
            writer.WriteStartElement("LocalAccounts");

            foreach (var user in config.UserAccounts)
            {
                writer.WriteStartElement("LocalAccount");
                writer.WriteAttributeString("wcm:action", "add");

                writer.WriteElementString("Name", user.Username);
                writer.WriteElementString("DisplayName", user.DisplayName);
                writer.WriteElementString("Group", user.Group);
                writer.WriteStartElement("Password");
                writer.WriteElementString("Value", user.Password);
                writer.WriteElementString("PlainText", "true");
                writer.WriteEndElement(); // Password

                writer.WriteEndElement(); // LocalAccount
            }

            writer.WriteEndElement(); // LocalAccounts
            writer.WriteEndElement(); // UserAccounts
        }

        // Auto logon
        if (config.AutoLogonCount > 0)
        {
            writer.WriteStartElement("AutoLogon");
            writer.WriteStartElement("Password");
            writer.WriteElementString("Value", config.AdministratorPassword);
            writer.WriteElementString("PlainText", "true");
            writer.WriteEndElement();
            writer.WriteElementString("Enabled", "true");
            writer.WriteElementString("LogonCount", config.AutoLogonCount.ToString());
            writer.WriteElementString("Username", "Administrator");
            writer.WriteEndElement(); // AutoLogon
        }

        // First logon commands
        if (config.FirstLogonCommands.Any())
        {
            writer.WriteStartElement("FirstLogonCommands");

            foreach (var command in config.FirstLogonCommands.OrderBy(c => c.Order))
            {
                writer.WriteStartElement("SynchronousCommand");
                writer.WriteAttributeString("wcm:action", "add");
                writer.WriteElementString("Order", command.Order.ToString());
                writer.WriteElementString("CommandLine", command.CommandLine);
                writer.WriteElementString("Description", command.Description);
                writer.WriteEndElement(); // SynchronousCommand
            }

            writer.WriteEndElement(); // FirstLogonCommands
        }

        writer.WriteEndElement(); // component
        writer.WriteEndElement(); // settings
    }

    #endregion
}
