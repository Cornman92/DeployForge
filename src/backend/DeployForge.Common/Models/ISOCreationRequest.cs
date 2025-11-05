namespace DeployForge.Common.Models;

/// <summary>
/// Request to create an ISO image
/// </summary>
public class ISOCreationRequest
{
    /// <summary>
    /// Source directory containing Windows image files
    /// </summary>
    public string SourcePath { get; set; } = string.Empty;

    /// <summary>
    /// Output ISO file path
    /// </summary>
    public string OutputPath { get; set; } = string.Empty;

    /// <summary>
    /// Volume label
    /// </summary>
    public string VolumeLabel { get; set; } = "Windows";

    /// <summary>
    /// Boot type
    /// </summary>
    public BootType BootType { get; set; } = BootType.UEFI;

    /// <summary>
    /// Include autounattend.xml
    /// </summary>
    public bool IncludeAutounattend { get; set; }

    /// <summary>
    /// Autounattend configuration (if IncludeAutounattend is true)
    /// </summary>
    public AutounattendConfig? AutounattendConfig { get; set; }
}

/// <summary>
/// Boot types for ISO
/// </summary>
public enum BootType
{
    /// <summary>
    /// Legacy BIOS boot
    /// </summary>
    BIOS,

    /// <summary>
    /// UEFI boot
    /// </summary>
    UEFI,

    /// <summary>
    /// Both BIOS and UEFI (hybrid)
    /// </summary>
    Both
}

/// <summary>
/// Request to create bootable USB
/// </summary>
public class BootableUSBRequest
{
    /// <summary>
    /// Source directory or ISO path
    /// </summary>
    public string SourcePath { get; set; } = string.Empty;

    /// <summary>
    /// USB drive letter (e.g., "D:")
    /// </summary>
    public string DriveLetter { get; set; } = string.Empty;

    /// <summary>
    /// Volume label
    /// </summary>
    public string VolumeLabel { get; set; } = "Windows";

    /// <summary>
    /// Boot type
    /// </summary>
    public BootType BootType { get; set; } = BootType.UEFI;

    /// <summary>
    /// Format the USB drive before creating
    /// </summary>
    public bool Format { get; set; } = true;

    /// <summary>
    /// File system (FAT32 for UEFI, NTFS for BIOS)
    /// </summary>
    public string FileSystem { get; set; } = "FAT32";

    /// <summary>
    /// Include autounattend.xml
    /// </summary>
    public bool IncludeAutounattend { get; set; }

    /// <summary>
    /// Autounattend configuration
    /// </summary>
    public AutounattendConfig? AutounattendConfig { get; set; }
}

/// <summary>
/// Result of ISO/USB creation
/// </summary>
public class MediaCreationResult
{
    /// <summary>
    /// Whether creation succeeded
    /// </summary>
    public bool Success { get; set; }

    /// <summary>
    /// Output path (ISO file or USB drive)
    /// </summary>
    public string OutputPath { get; set; } = string.Empty;

    /// <summary>
    /// Size in bytes
    /// </summary>
    public long SizeBytes { get; set; }

    /// <summary>
    /// Creation duration
    /// </summary>
    public TimeSpan Duration { get; set; }

    /// <summary>
    /// Message
    /// </summary>
    public string Message { get; set; } = string.Empty;

    /// <summary>
    /// Warnings
    /// </summary>
    public List<string> Warnings { get; set; } = new();
}
