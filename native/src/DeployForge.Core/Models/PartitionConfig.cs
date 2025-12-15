using DeployForge.Core.Enums;

namespace DeployForge.Core.Models;

/// <summary>
/// Configuration for disk partitioning.
/// </summary>
public class PartitionConfig
{
    /// <summary>
    /// Disk number to partition.
    /// </summary>
    public int DiskNumber { get; set; }
    
    /// <summary>
    /// Whether to use UEFI/GPT layout.
    /// </summary>
    public bool UseUefi { get; set; } = true;
    
    /// <summary>
    /// Partition layout.
    /// </summary>
    public List<PartitionInfo> Partitions { get; set; } = new();
    
    /// <summary>
    /// Creates a standard UEFI partition layout.
    /// </summary>
    public static PartitionConfig CreateUefiLayout(long windowsSizeMB = 0, bool includeRecovery = true)
    {
        var config = new PartitionConfig
        {
            UseUefi = true,
            Partitions = new List<PartitionInfo>
            {
                new()
                {
                    Type = PartitionType.EFI,
                    FileSystem = FileSystemType.FAT32,
                    Label = "System",
                    SizeMB = 260,
                    DriveLetter = null
                },
                new()
                {
                    Type = PartitionType.MSR,
                    FileSystem = FileSystemType.None,
                    Label = "MSR",
                    SizeMB = 16,
                    DriveLetter = null
                },
                new()
                {
                    Type = PartitionType.Primary,
                    FileSystem = FileSystemType.NTFS,
                    Label = "Windows",
                    SizeMB = windowsSizeMB,
                    DriveLetter = 'C'
                }
            }
        };
        
        if (includeRecovery)
        {
            config.Partitions.Add(new PartitionInfo
            {
                Type = PartitionType.Recovery,
                FileSystem = FileSystemType.NTFS,
                Label = "Recovery",
                SizeMB = 1024,
                DriveLetter = null,
                IsRecovery = true
            });
        }
        
        return config;
    }
    
    /// <summary>
    /// Creates a legacy BIOS partition layout.
    /// </summary>
    public static PartitionConfig CreateBiosLayout(long windowsSizeMB = 0, bool includeRecovery = true)
    {
        var config = new PartitionConfig
        {
            UseUefi = false,
            Partitions = new List<PartitionInfo>
            {
                new()
                {
                    Type = PartitionType.Primary,
                    FileSystem = FileSystemType.NTFS,
                    Label = "System Reserved",
                    SizeMB = 550,
                    IsActive = true
                },
                new()
                {
                    Type = PartitionType.Primary,
                    FileSystem = FileSystemType.NTFS,
                    Label = "Windows",
                    SizeMB = windowsSizeMB,
                    DriveLetter = 'C'
                }
            }
        };
        
        if (includeRecovery)
        {
            config.Partitions.Add(new PartitionInfo
            {
                Type = PartitionType.Primary,
                FileSystem = FileSystemType.NTFS,
                Label = "Recovery",
                SizeMB = 1024,
                IsRecovery = true
            });
        }
        
        return config;
    }
}

/// <summary>
/// Information about a disk partition.
/// </summary>
public class PartitionInfo
{
    /// <summary>
    /// Partition type.
    /// </summary>
    public PartitionType Type { get; set; }
    
    /// <summary>
    /// File system type.
    /// </summary>
    public FileSystemType FileSystem { get; set; }
    
    /// <summary>
    /// Partition label/name.
    /// </summary>
    public string Label { get; set; } = string.Empty;
    
    /// <summary>
    /// Size in megabytes (0 = use remaining space).
    /// </summary>
    public long SizeMB { get; set; }
    
    /// <summary>
    /// Drive letter to assign (null for no letter).
    /// </summary>
    public char? DriveLetter { get; set; }
    
    /// <summary>
    /// Whether this is the active boot partition.
    /// </summary>
    public bool IsActive { get; set; }
    
    /// <summary>
    /// Whether this is a recovery partition.
    /// </summary>
    public bool IsRecovery { get; set; }
    
    /// <summary>
    /// GPT type GUID (for advanced scenarios).
    /// </summary>
    public Guid? GptTypeGuid { get; set; }
    
    /// <summary>
    /// Gets the DiskPart size string.
    /// </summary>
    public string GetSizeString()
    {
        return SizeMB > 0 ? $"size={SizeMB}" : string.Empty;
    }
}

/// <summary>
/// Result of a partition operation.
/// </summary>
public class PartitionResult
{
    /// <summary>
    /// Whether the operation succeeded.
    /// </summary>
    public bool Success { get; set; }
    
    /// <summary>
    /// Disk number that was partitioned.
    /// </summary>
    public int DiskNumber { get; set; }
    
    /// <summary>
    /// Created partitions.
    /// </summary>
    public List<CreatedPartition> Partitions { get; set; } = new();
    
    /// <summary>
    /// Error message if failed.
    /// </summary>
    public string? Error { get; set; }
}

/// <summary>
/// Information about a created partition.
/// </summary>
public class CreatedPartition
{
    /// <summary>
    /// Partition number.
    /// </summary>
    public int Number { get; set; }
    
    /// <summary>
    /// Partition type.
    /// </summary>
    public PartitionType Type { get; set; }
    
    /// <summary>
    /// Partition label.
    /// </summary>
    public string Label { get; set; } = string.Empty;
    
    /// <summary>
    /// Assigned drive letter.
    /// </summary>
    public char? DriveLetter { get; set; }
    
    /// <summary>
    /// Actual size in bytes.
    /// </summary>
    public long SizeBytes { get; set; }
}
