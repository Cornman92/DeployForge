namespace DeployForge.App.Models;

public record ImageInfo
{
    public string Path { get; init; } = string.Empty;
    public string Name { get; init; } = string.Empty;
    public string Format { get; init; } = string.Empty;
    public long Size { get; init; }
    public DateTime ModifiedDate { get; init; }
    public int ImageCount { get; init; } = 1;
    public List<ImageIndex> Indexes { get; init; } = new();
    public bool IsMounted { get; init; }
    public string? MountPoint { get; init; }
}

public record ImageIndex
{
    public int Index { get; init; }
    public string Name { get; init; } = string.Empty;
    public string Description { get; init; } = string.Empty;
    public long Size { get; init; }
    public string Architecture { get; init; } = "x64";
    public string Version { get; init; } = string.Empty;
    public string Build { get; init; } = string.Empty;
    public string Edition { get; init; } = string.Empty;
    public string Language { get; init; } = "en-US";
}

public record MountedImage
{
    public string ImagePath { get; init; } = string.Empty;
    public string MountPoint { get; init; } = string.Empty;
    public int Index { get; init; }
    public MountStatus Status { get; init; }
    public DateTime MountedAt { get; init; }
}

public enum MountStatus
{
    NotMounted,
    Mounting,
    Mounted,
    Dismounting,
    Error
}

public enum ImageFormat
{
    WIM,
    ESD,
    ISO,
    VHD,
    VHDX,
    PPKG,
    Unknown
}
