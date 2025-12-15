using DeployForge.Core.Enums;

namespace DeployForge.Core.Models;

/// <summary>
/// Information about a Windows deployment image.
/// </summary>
public class ImageInfo
{
    /// <summary>
    /// Full path to the image file.
    /// </summary>
    public string ImagePath { get; set; } = string.Empty;
    
    /// <summary>
    /// Image file name.
    /// </summary>
    public string FileName { get; set; } = string.Empty;
    
    /// <summary>
    /// Image format type.
    /// </summary>
    public ImageFormat Format { get; set; }
    
    /// <summary>
    /// File size in bytes.
    /// </summary>
    public long FileSizeBytes { get; set; }
    
    /// <summary>
    /// File size in gigabytes.
    /// </summary>
    public double FileSizeGB => Math.Round(FileSizeBytes / (1024.0 * 1024.0 * 1024.0), 2);
    
    /// <summary>
    /// Number of images/indexes in the file.
    /// </summary>
    public int ImageCount { get; set; }
    
    /// <summary>
    /// Last modified timestamp.
    /// </summary>
    public DateTime LastModified { get; set; }
    
    /// <summary>
    /// List of images/indexes in the file.
    /// </summary>
    public List<ImageIndexInfo> Images { get; set; } = new();
}

/// <summary>
/// Information about a specific image index within a WIM/ESD file.
/// </summary>
public class ImageIndexInfo
{
    /// <summary>
    /// Image index number.
    /// </summary>
    public int Index { get; set; }
    
    /// <summary>
    /// Image name (e.g., "Windows 11 Pro").
    /// </summary>
    public string Name { get; set; } = string.Empty;
    
    /// <summary>
    /// Image description.
    /// </summary>
    public string Description { get; set; } = string.Empty;
    
    /// <summary>
    /// Uncompressed image size in bytes.
    /// </summary>
    public long ImageSizeBytes { get; set; }
    
    /// <summary>
    /// Image size in gigabytes.
    /// </summary>
    public double ImageSizeGB => Math.Round(ImageSizeBytes / (1024.0 * 1024.0 * 1024.0), 2);
    
    /// <summary>
    /// Processor architecture (amd64, x86, arm64).
    /// </summary>
    public string Architecture { get; set; } = string.Empty;
    
    /// <summary>
    /// Windows version string.
    /// </summary>
    public string Version { get; set; } = string.Empty;
    
    /// <summary>
    /// Windows edition ID (e.g., "Professional").
    /// </summary>
    public string EditionId { get; set; } = string.Empty;
    
    /// <summary>
    /// Installation type (Client, Server).
    /// </summary>
    public string InstallationType { get; set; } = string.Empty;
    
    /// <summary>
    /// Installed languages.
    /// </summary>
    public List<string> Languages { get; set; } = new();
    
    /// <summary>
    /// Default language.
    /// </summary>
    public string DefaultLanguage { get; set; } = string.Empty;
    
    /// <summary>
    /// Product type.
    /// </summary>
    public string ProductType { get; set; } = string.Empty;
    
    /// <summary>
    /// System root path.
    /// </summary>
    public string SystemRoot { get; set; } = @"\Windows";
}

/// <summary>
/// Result of a mount operation.
/// </summary>
public class MountResult
{
    /// <summary>
    /// Whether the operation succeeded.
    /// </summary>
    public bool Success { get; set; }
    
    /// <summary>
    /// Path to the mounted image.
    /// </summary>
    public string ImagePath { get; set; } = string.Empty;
    
    /// <summary>
    /// Mount point path.
    /// </summary>
    public string MountPath { get; set; } = string.Empty;
    
    /// <summary>
    /// Image index that was mounted.
    /// </summary>
    public int Index { get; set; }
    
    /// <summary>
    /// Whether mounted read-only.
    /// </summary>
    public bool ReadOnly { get; set; }
    
    /// <summary>
    /// Duration of the mount operation.
    /// </summary>
    public TimeSpan Duration { get; set; }
    
    /// <summary>
    /// Result message.
    /// </summary>
    public string Message { get; set; } = string.Empty;
    
    /// <summary>
    /// Error message if failed.
    /// </summary>
    public string? Error { get; set; }
}

/// <summary>
/// Result of a dismount operation.
/// </summary>
public class DismountResult
{
    /// <summary>
    /// Whether the operation succeeded.
    /// </summary>
    public bool Success { get; set; }
    
    /// <summary>
    /// Mount path that was dismounted.
    /// </summary>
    public string MountPath { get; set; } = string.Empty;
    
    /// <summary>
    /// Whether changes were saved.
    /// </summary>
    public bool ChangesSaved { get; set; }
    
    /// <summary>
    /// Duration of the dismount operation.
    /// </summary>
    public TimeSpan Duration { get; set; }
    
    /// <summary>
    /// Result message.
    /// </summary>
    public string Message { get; set; } = string.Empty;
    
    /// <summary>
    /// Error message if failed.
    /// </summary>
    public string? Error { get; set; }
}

/// <summary>
/// Information about a file in a mounted image.
/// </summary>
public class ImageFileInfo
{
    /// <summary>
    /// File or directory name.
    /// </summary>
    public string Name { get; set; } = string.Empty;
    
    /// <summary>
    /// Full path within the image.
    /// </summary>
    public string Path { get; set; } = string.Empty;
    
    /// <summary>
    /// Whether this is a directory.
    /// </summary>
    public bool IsDirectory { get; set; }
    
    /// <summary>
    /// File size in bytes (0 for directories).
    /// </summary>
    public long Size { get; set; }
    
    /// <summary>
    /// Last modified timestamp.
    /// </summary>
    public DateTime LastModified { get; set; }
    
    /// <summary>
    /// File attributes.
    /// </summary>
    public FileAttributes Attributes { get; set; }
}
