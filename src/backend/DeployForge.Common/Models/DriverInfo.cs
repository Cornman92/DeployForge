namespace DeployForge.Common.Models;

/// <summary>
/// Represents driver information
/// </summary>
public class DriverInfo
{
    /// <summary>
    /// Published name of the driver
    /// </summary>
    public string PublishedName { get; set; } = string.Empty;

    /// <summary>
    /// Original file name
    /// </summary>
    public string OriginalFileName { get; set; } = string.Empty;

    /// <summary>
    /// Driver inbox status
    /// </summary>
    public bool InBox { get; set; }

    /// <summary>
    /// Provider name
    /// </summary>
    public string ProviderName { get; set; } = string.Empty;

    /// <summary>
    /// Driver class name
    /// </summary>
    public string ClassName { get; set; } = string.Empty;

    /// <summary>
    /// Class GUID
    /// </summary>
    public string ClassGuid { get; set; } = string.Empty;

    /// <summary>
    /// Driver class description
    /// </summary>
    public string ClassDescription { get; set; } = string.Empty;

    /// <summary>
    /// Whether the driver is boot critical
    /// </summary>
    public bool BootCritical { get; set; }

    /// <summary>
    /// Driver signature status
    /// </summary>
    public string DriverSignature { get; set; } = string.Empty;

    /// <summary>
    /// Driver version
    /// </summary>
    public string Version { get; set; } = string.Empty;

    /// <summary>
    /// Driver date
    /// </summary>
    public DateTime? Date { get; set; }

    /// <summary>
    /// Architecture (x86, x64, ARM64)
    /// </summary>
    public string Architecture { get; set; } = string.Empty;

    /// <summary>
    /// Manufacturer
    /// </summary>
    public string Manufacturer { get; set; } = string.Empty;

    /// <summary>
    /// Hardware IDs supported by this driver
    /// </summary>
    public List<string> HardwareIds { get; set; } = new();

    /// <summary>
    /// Compatible IDs
    /// </summary>
    public List<string> CompatibleIds { get; set; } = new();
}
