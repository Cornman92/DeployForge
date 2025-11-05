namespace DeployForge.Common.Models;

/// <summary>
/// Request to convert an image from one format to another
/// </summary>
public class ConvertImageRequest
{
    /// <summary>
    /// Source image path
    /// </summary>
    public string SourcePath { get; set; } = string.Empty;

    /// <summary>
    /// Source image index (for WIM files)
    /// </summary>
    public int SourceIndex { get; set; } = 1;

    /// <summary>
    /// Destination image path
    /// </summary>
    public string DestinationPath { get; set; } = string.Empty;

    /// <summary>
    /// Target format
    /// </summary>
    public ImageFormat TargetFormat { get; set; }

    /// <summary>
    /// Compression level
    /// </summary>
    public ConversionCompressionLevel Compression { get; set; } = ConversionCompressionLevel.Maximum;

    /// <summary>
    /// Check integrity before and after conversion
    /// </summary>
    public bool CheckIntegrity { get; set; } = true;

    /// <summary>
    /// Verify the converted image
    /// </summary>
    public bool VerifyConversion { get; set; } = true;

    /// <summary>
    /// Delete source after successful conversion
    /// </summary>
    public bool DeleteSource { get; set; } = false;

    /// <summary>
    /// Maximum VHD/VHDX size in GB (for WIM to VHD/VHDX conversion)
    /// </summary>
    public int MaxVirtualDiskSizeGB { get; set; } = 127;

    /// <summary>
    /// Use dynamic expansion for VHD/VHDX (false = fixed size)
    /// </summary>
    public bool DynamicExpansion { get; set; } = true;
}

/// <summary>
/// Compression levels for image conversion
/// </summary>
public enum ConversionCompressionLevel
{
    /// <summary>
    /// No compression (fastest)
    /// </summary>
    None = 0,

    /// <summary>
    /// Fast compression (XPRESS)
    /// </summary>
    Fast = 1,

    /// <summary>
    /// Maximum compression (LZX)
    /// </summary>
    Maximum = 2,

    /// <summary>
    /// Recovery compression (for ESD files)
    /// </summary>
    Recovery = 3
}

/// <summary>
/// Result of an image conversion operation
/// </summary>
public class ImageConversionResult
{
    /// <summary>
    /// Whether conversion succeeded
    /// </summary>
    public bool Success { get; set; }

    /// <summary>
    /// Source image path
    /// </summary>
    public string SourcePath { get; set; } = string.Empty;

    /// <summary>
    /// Source format
    /// </summary>
    public ImageFormat SourceFormat { get; set; }

    /// <summary>
    /// Source size in bytes
    /// </summary>
    public long SourceSize { get; set; }

    /// <summary>
    /// Destination image path
    /// </summary>
    public string DestinationPath { get; set; } = string.Empty;

    /// <summary>
    /// Destination format
    /// </summary>
    public ImageFormat DestinationFormat { get; set; }

    /// <summary>
    /// Destination size in bytes
    /// </summary>
    public long DestinationSize { get; set; }

    /// <summary>
    /// Compression ratio (0-1)
    /// </summary>
    public double CompressionRatio { get; set; }

    /// <summary>
    /// Space saved in bytes (can be negative if destination is larger)
    /// </summary>
    public long SpaceSaved { get; set; }

    /// <summary>
    /// Conversion duration
    /// </summary>
    public TimeSpan Duration { get; set; }

    /// <summary>
    /// Result message
    /// </summary>
    public string Message { get; set; } = string.Empty;

    /// <summary>
    /// Error message (if conversion failed)
    /// </summary>
    public string? ErrorMessage { get; set; }

    /// <summary>
    /// Conversion stages completed
    /// </summary>
    public List<ConversionStage> CompletedStages { get; set; } = new();
}

/// <summary>
/// Stages in the conversion process
/// </summary>
public class ConversionStage
{
    /// <summary>
    /// Stage name
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// Stage status
    /// </summary>
    public StageStatus Status { get; set; }

    /// <summary>
    /// Stage duration
    /// </summary>
    public TimeSpan Duration { get; set; }

    /// <summary>
    /// Stage message
    /// </summary>
    public string Message { get; set; } = string.Empty;
}

/// <summary>
/// Conversion stage status
/// </summary>
public enum StageStatus
{
    /// <summary>
    /// Stage pending
    /// </summary>
    Pending,

    /// <summary>
    /// Stage in progress
    /// </summary>
    InProgress,

    /// <summary>
    /// Stage completed successfully
    /// </summary>
    Completed,

    /// <summary>
    /// Stage failed
    /// </summary>
    Failed,

    /// <summary>
    /// Stage skipped
    /// </summary>
    Skipped
}

/// <summary>
/// Request to extract ISO contents
/// </summary>
public class ExtractISORequest
{
    /// <summary>
    /// ISO file path
    /// </summary>
    public string ISOPath { get; set; } = string.Empty;

    /// <summary>
    /// Extraction directory
    /// </summary>
    public string DestinationPath { get; set; } = string.Empty;

    /// <summary>
    /// Overwrite existing files
    /// </summary>
    public bool Overwrite { get; set; } = false;

    /// <summary>
    /// Verify ISO integrity before extraction
    /// </summary>
    public bool VerifyIntegrity { get; set; } = true;
}

/// <summary>
/// Result of ISO extraction
/// </summary>
public class ISOExtractionResult
{
    /// <summary>
    /// Whether extraction succeeded
    /// </summary>
    public bool Success { get; set; }

    /// <summary>
    /// ISO path
    /// </summary>
    public string ISOPath { get; set; } = string.Empty;

    /// <summary>
    /// Destination path
    /// </summary>
    public string DestinationPath { get; set; } = string.Empty;

    /// <summary>
    /// Number of files extracted
    /// </summary>
    public int FilesExtracted { get; set; }

    /// <summary>
    /// Number of directories created
    /// </summary>
    public int DirectoriesCreated { get; set; }

    /// <summary>
    /// Total size extracted in bytes
    /// </summary>
    public long TotalSize { get; set; }

    /// <summary>
    /// Extraction duration
    /// </summary>
    public TimeSpan Duration { get; set; }

    /// <summary>
    /// Result message
    /// </summary>
    public string Message { get; set; } = string.Empty;

    /// <summary>
    /// Error message (if extraction failed)
    /// </summary>
    public string? ErrorMessage { get; set; }
}

/// <summary>
/// Supported conversion paths
/// </summary>
public static class ImageConversionSupport
{
    /// <summary>
    /// Check if conversion between formats is supported
    /// </summary>
    public static bool IsConversionSupported(ImageFormat source, ImageFormat target)
    {
        return (source, target) switch
        {
            // WIM conversions
            (ImageFormat.WIM, ImageFormat.ESD) => true,
            (ImageFormat.WIM, ImageFormat.VHD) => true,
            (ImageFormat.WIM, ImageFormat.VHDX) => true,

            // ESD conversions
            (ImageFormat.ESD, ImageFormat.WIM) => true,
            (ImageFormat.ESD, ImageFormat.VHD) => true,
            (ImageFormat.ESD, ImageFormat.VHDX) => true,

            // VHD conversions
            (ImageFormat.VHD, ImageFormat.VHDX) => true,
            (ImageFormat.VHD, ImageFormat.WIM) => true,

            // VHDX conversions
            (ImageFormat.VHDX, ImageFormat.VHD) => true,
            (ImageFormat.VHDX, ImageFormat.WIM) => true,

            // Same format (optimization)
            _ when source == target => true,

            _ => false
        };
    }

    /// <summary>
    /// Get conversion complexity
    /// </summary>
    public static ConversionComplexity GetConversionComplexity(ImageFormat source, ImageFormat target)
    {
        return (source, target) switch
        {
            // Simple conversions (DISM native)
            (ImageFormat.WIM, ImageFormat.ESD) => ConversionComplexity.Simple,
            (ImageFormat.ESD, ImageFormat.WIM) => ConversionComplexity.Simple,

            // Medium conversions (requires mounting)
            (ImageFormat.WIM, ImageFormat.VHD) => ConversionComplexity.Medium,
            (ImageFormat.WIM, ImageFormat.VHDX) => ConversionComplexity.Medium,
            (ImageFormat.ESD, ImageFormat.VHD) => ConversionComplexity.Medium,
            (ImageFormat.ESD, ImageFormat.VHDX) => ConversionComplexity.Medium,

            // Complex conversions (VHD manipulation)
            (ImageFormat.VHD, ImageFormat.VHDX) => ConversionComplexity.Complex,
            (ImageFormat.VHDX, ImageFormat.VHD) => ConversionComplexity.Complex,
            (ImageFormat.VHD, ImageFormat.WIM) => ConversionComplexity.Complex,
            (ImageFormat.VHDX, ImageFormat.WIM) => ConversionComplexity.Complex,

            // Same format (trivial)
            _ when source == target => ConversionComplexity.Trivial,

            _ => ConversionComplexity.Unsupported
        };
    }
}

/// <summary>
/// Conversion complexity levels
/// </summary>
public enum ConversionComplexity
{
    /// <summary>
    /// Trivial (same format)
    /// </summary>
    Trivial,

    /// <summary>
    /// Simple (native DISM support)
    /// </summary>
    Simple,

    /// <summary>
    /// Medium (requires mounting/temporary files)
    /// </summary>
    Medium,

    /// <summary>
    /// Complex (multiple steps, VHD manipulation)
    /// </summary>
    Complex,

    /// <summary>
    /// Not supported
    /// </summary>
    Unsupported
}
