namespace DeployForge.Common.Models;

/// <summary>
/// Represents Windows Update information
/// </summary>
public class UpdateInfo
{
    /// <summary>
    /// Update KB number
    /// </summary>
    public string KBNumber { get; set; } = string.Empty;

    /// <summary>
    /// Update title/description
    /// </summary>
    public string Title { get; set; } = string.Empty;

    /// <summary>
    /// Type of update
    /// </summary>
    public UpdateType Type { get; set; }

    /// <summary>
    /// Update version
    /// </summary>
    public string Version { get; set; } = string.Empty;

    /// <summary>
    /// Release date
    /// </summary>
    public DateTime? ReleaseDate { get; set; }

    /// <summary>
    /// Update size in bytes
    /// </summary>
    public long SizeBytes { get; set; }

    /// <summary>
    /// Installation state
    /// </summary>
    public UpdateState State { get; set; }

    /// <summary>
    /// Whether this update is installed
    /// </summary>
    public bool IsInstalled { get; set; }

    /// <summary>
    /// Restart required after installation
    /// </summary>
    public bool RestartRequired { get; set; }

    /// <summary>
    /// Superseded updates (this update replaces these)
    /// </summary>
    public List<string> SupersededUpdates { get; set; } = new();

    /// <summary>
    /// Prerequisites (updates required before this one)
    /// </summary>
    public List<string> Prerequisites { get; set; } = new();
}

/// <summary>
/// Types of Windows updates
/// </summary>
public enum UpdateType
{
    /// <summary>
    /// Security update
    /// </summary>
    SecurityUpdate,

    /// <summary>
    /// Cumulative update
    /// </summary>
    CumulativeUpdate,

    /// <summary>
    /// Feature update (new Windows version)
    /// </summary>
    FeatureUpdate,

    /// <summary>
    /// Service pack
    /// </summary>
    ServicePack,

    /// <summary>
    /// Critical update
    /// </summary>
    CriticalUpdate,

    /// <summary>
    /// Definition update (Windows Defender, etc.)
    /// </summary>
    DefinitionUpdate,

    /// <summary>
    /// Driver update
    /// </summary>
    DriverUpdate,

    /// <summary>
    /// Other/Unknown
    /// </summary>
    Other
}

/// <summary>
/// Update installation states
/// </summary>
public enum UpdateState
{
    /// <summary>
    /// Not installed
    /// </summary>
    NotInstalled,

    /// <summary>
    /// Installed
    /// </summary>
    Installed,

    /// <summary>
    /// Installation pending
    /// </summary>
    InstallPending,

    /// <summary>
    /// Superseded by newer update
    /// </summary>
    Superseded,

    /// <summary>
    /// Failed to install
    /// </summary>
    Failed
}
