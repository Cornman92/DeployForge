using DeployForge.Core.Enums;

namespace DeployForge.Core.Models;

/// <summary>
/// Debloat and privacy configuration.
/// </summary>
public class DebloatConfig
{
    /// <summary>
    /// Debloat level.
    /// </summary>
    public DebloatLevel Level { get; set; } = DebloatLevel.Moderate;
    
    /// <summary>
    /// Disable Windows telemetry.
    /// </summary>
    public bool DisableTelemetry { get; set; } = true;
    
    /// <summary>
    /// Disable Cortana.
    /// </summary>
    public bool DisableCortana { get; set; } = true;
    
    /// <summary>
    /// Disable Windows Spotlight.
    /// </summary>
    public bool DisableSpotlight { get; set; } = true;
    
    /// <summary>
    /// Disable advertising ID.
    /// </summary>
    public bool DisableAdvertisingId { get; set; } = true;
    
    /// <summary>
    /// Disable app suggestions.
    /// </summary>
    public bool DisableAppSuggestions { get; set; } = true;
    
    /// <summary>
    /// Disable delivery optimization (P2P updates).
    /// </summary>
    public bool DisableDeliveryOptimization { get; set; } = true;
    
    /// <summary>
    /// Disable web search in Start menu.
    /// </summary>
    public bool DisableWebSearch { get; set; } = true;
    
    /// <summary>
    /// Disable Windows tips and suggestions.
    /// </summary>
    public bool DisableTips { get; set; } = true;
    
    /// <summary>
    /// Additional apps to remove (package names).
    /// </summary>
    public List<string> AdditionalAppsToRemove { get; set; } = new();
    
    /// <summary>
    /// Apps to preserve (won't be removed).
    /// </summary>
    public List<string> AppsToPreserve { get; set; } = new();

    /// <summary>
    /// Creates a default configuration.
    /// </summary>
    public static DebloatConfig Default => new()
    {
        Level = DebloatLevel.Moderate,
        DisableTelemetry = true,
        DisableCortana = true,
        DisableAdvertisingId = true,
        DisableAppSuggestions = true,
        AppsToPreserve = new List<string>
        {
            "Microsoft.Xbox*",
            "Microsoft.OneDrive*",
            "Microsoft.WindowsTerminal"
        }
    };
}

/// <summary>
/// Result of a debloat operation.
/// </summary>
public class DebloatResult
{
    /// <summary>
    /// Whether the operation succeeded.
    /// </summary>
    public bool Success { get; set; }
    
    /// <summary>
    /// Debloat level that was applied.
    /// </summary>
    public DebloatLevel Level { get; set; }
    
    /// <summary>
    /// Apps that were successfully removed.
    /// </summary>
    public List<string> RemovedApps { get; set; } = new();
    
    /// <summary>
    /// Apps that failed to remove.
    /// </summary>
    public List<string> FailedApps { get; set; } = new();
    
    /// <summary>
    /// Privacy changes that were applied.
    /// </summary>
    public List<string> PrivacyChanges { get; set; } = new();
    
    /// <summary>
    /// Total number of apps removed.
    /// </summary>
    public int TotalRemoved => RemovedApps.Count;
    
    /// <summary>
    /// Error message if failed.
    /// </summary>
    public string? Error { get; set; }
}

/// <summary>
/// Information about a bloatware app.
/// </summary>
public class BloatwareApp
{
    /// <summary>
    /// Package name.
    /// </summary>
    public string PackageName { get; set; } = string.Empty;
    
    /// <summary>
    /// Display name.
    /// </summary>
    public string DisplayName { get; set; } = string.Empty;
    
    /// <summary>
    /// Category (Minimal, Moderate, Aggressive).
    /// </summary>
    public DebloatLevel Category { get; set; }
    
    /// <summary>
    /// Whether this app is selected for removal.
    /// </summary>
    public bool Selected { get; set; }
}
