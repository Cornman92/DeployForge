namespace DeployForge.Common.Models;

/// <summary>
/// Information about a Windows image
/// </summary>
public class ImageInfo
{
    /// <summary>
    /// Image file path
    /// </summary>
    public string FilePath { get; set; } = string.Empty;

    /// <summary>
    /// Image format
    /// </summary>
    public ImageFormat Format { get; set; }

    /// <summary>
    /// Image architecture
    /// </summary>
    public string Architecture { get; set; } = string.Empty;

    /// <summary>
    /// Image version (e.g., 10.0.19041.1)
    /// </summary>
    public string Version { get; set; } = string.Empty;

    /// <summary>
    /// Image edition (e.g., Professional, Enterprise)
    /// </summary>
    public string Edition { get; set; } = string.Empty;

    /// <summary>
    /// Image name
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// Image description
    /// </summary>
    public string Description { get; set; } = string.Empty;

    /// <summary>
    /// Image index (for WIM files)
    /// </summary>
    public int Index { get; set; }

    /// <summary>
    /// Total number of images in the file
    /// </summary>
    public int ImageCount { get; set; }

    /// <summary>
    /// Image size in bytes
    /// </summary>
    public long SizeBytes { get; set; }

    /// <summary>
    /// Creation date
    /// </summary>
    public DateTime CreatedDate { get; set; }

    /// <summary>
    /// Modified date
    /// </summary>
    public DateTime ModifiedDate { get; set; }

    /// <summary>
    /// Image languages
    /// </summary>
    public List<string> Languages { get; set; } = new();

    /// <summary>
    /// Whether the image is mounted
    /// </summary>
    public bool IsMounted { get; set; }

    /// <summary>
    /// Mount path (if mounted)
    /// </summary>
    public string? MountPath { get; set; }

    /// <summary>
    /// Mount status
    /// </summary>
    public MountStatus MountStatus { get; set; }
}

/// <summary>
/// Image format types
/// </summary>
public enum ImageFormat
{
    /// <summary>
    /// Windows Imaging Format (.wim)
    /// </summary>
    WIM,

    /// <summary>
    /// Electronic Software Download (.esd)
    /// </summary>
    ESD,

    /// <summary>
    /// Virtual Hard Disk (.vhd)
    /// </summary>
    VHD,

    /// <summary>
    /// Virtual Hard Disk v2 (.vhdx)
    /// </summary>
    VHDX,

    /// <summary>
    /// ISO image (.iso)
    /// </summary>
    ISO,

    /// <summary>
    /// Raw disk image (.img)
    /// </summary>
    IMG,

    /// <summary>
    /// Provisioning package (.ppkg)
    /// </summary>
    PPKG
}

/// <summary>
/// Mount status
/// </summary>
public enum MountStatus
{
    /// <summary>
    /// Not mounted
    /// </summary>
    NotMounted,

    /// <summary>
    /// Successfully mounted
    /// </summary>
    Mounted,

    /// <summary>
    /// Mount in progress
    /// </summary>
    Mounting,

    /// <summary>
    /// Unmount in progress
    /// </summary>
    Unmounting,

    /// <summary>
    /// Needs remount (corrupted)
    /// </summary>
    NeedsRemount,

    /// <summary>
    /// Invalid mount
    /// </summary>
    Invalid
}

/// <summary>
/// Request to mount an image
/// </summary>
public class MountImageRequest
{
    /// <summary>
    /// Image file path
    /// </summary>
    public string ImagePath { get; set; } = string.Empty;

    /// <summary>
    /// Image index (for WIM files, 1-based)
    /// </summary>
    public int Index { get; set; } = 1;

    /// <summary>
    /// Mount path
    /// </summary>
    public string MountPath { get; set; } = string.Empty;

    /// <summary>
    /// Mount read-only
    /// </summary>
    public bool ReadOnly { get; set; }

    /// <summary>
    /// Verify integrity before mounting
    /// </summary>
    public bool CheckIntegrity { get; set; }
}

/// <summary>
/// Request to unmount an image
/// </summary>
public class UnmountImageRequest
{
    /// <summary>
    /// Mount path
    /// </summary>
    public string MountPath { get; set; } = string.Empty;

    /// <summary>
    /// Commit changes (true) or discard (false)
    /// </summary>
    public bool Commit { get; set; } = true;

    /// <summary>
    /// Force unmount even if in use
    /// </summary>
    public bool Force { get; set; }

    /// <summary>
    /// Check integrity after unmount
    /// </summary>
    public bool CheckIntegrity { get; set; }
}

/// <summary>
/// Mount/unmount operation result
/// </summary>
public class MountOperationResult
{
    /// <summary>
    /// Whether operation succeeded
    /// </summary>
    public bool Success { get; set; }

    /// <summary>
    /// Mount path
    /// </summary>
    public string MountPath { get; set; } = string.Empty;

    /// <summary>
    /// Image path
    /// </summary>
    public string ImagePath { get; set; } = string.Empty;

    /// <summary>
    /// Mount status
    /// </summary>
    public MountStatus Status { get; set; }

    /// <summary>
    /// Operation message
    /// </summary>
    public string Message { get; set; } = string.Empty;

    /// <summary>
    /// Operation duration
    /// </summary>
    public TimeSpan Duration { get; set; }
}

/// <summary>
/// Mounted image information
/// </summary>
public class MountedImageInfo
{
    /// <summary>
    /// Image path
    /// </summary>
    public string ImagePath { get; set; } = string.Empty;

    /// <summary>
    /// Mount path
    /// </summary>
    public string MountPath { get; set; } = string.Empty;

    /// <summary>
    /// Image index
    /// </summary>
    public int ImageIndex { get; set; }

    /// <summary>
    /// Mount status
    /// </summary>
    public MountStatus Status { get; set; }

    /// <summary>
    /// Is read-only
    /// </summary>
    public bool IsReadOnly { get; set; }

    /// <summary>
    /// Mount time
    /// </summary>
    public DateTime MountTime { get; set; }
}
