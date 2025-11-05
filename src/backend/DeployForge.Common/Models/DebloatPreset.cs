namespace DeployForge.Common.Models;

/// <summary>
/// Debloating preset configuration
/// </summary>
public class DebloatPreset
{
    /// <summary>
    /// Preset unique identifier
    /// </summary>
    public string Id { get; set; } = string.Empty;

    /// <summary>
    /// Preset name
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// Preset description
    /// </summary>
    public string Description { get; set; } = string.Empty;

    /// <summary>
    /// Severity level of debloating
    /// </summary>
    public DebloatLevel Level { get; set; }

    /// <summary>
    /// Target OS versions (empty = all versions)
    /// </summary>
    public List<string> TargetOSVersions { get; set; } = new();

    /// <summary>
    /// Components to remove
    /// </summary>
    public List<DebloatComponent> Components { get; set; } = new();

    /// <summary>
    /// Registry tweaks to apply
    /// </summary>
    public List<RegistryTweak> RegistryTweaks { get; set; } = new();

    /// <summary>
    /// Scheduled tasks to disable
    /// </summary>
    public List<string> ScheduledTasksToDisable { get; set; } = new();

    /// <summary>
    /// Services to disable
    /// </summary>
    public List<string> ServicesToDisable { get; set; } = new();

    /// <summary>
    /// Estimated space savings in MB
    /// </summary>
    public long EstimatedSpaceSavings { get; set; }
}

/// <summary>
/// Component to remove as part of debloating
/// </summary>
public class DebloatComponent
{
    /// <summary>
    /// Component identifier
    /// </summary>
    public string Id { get; set; } = string.Empty;

    /// <summary>
    /// Component name
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// Component type
    /// </summary>
    public ComponentType Type { get; set; }

    /// <summary>
    /// Reason for removal
    /// </summary>
    public string Reason { get; set; } = string.Empty;

    /// <summary>
    /// Whether removal is safe
    /// </summary>
    public bool SafeToRemove { get; set; } = true;

    /// <summary>
    /// Warning message if removal has risks
    /// </summary>
    public string? Warning { get; set; }
}

/// <summary>
/// Debloating severity levels
/// </summary>
public enum DebloatLevel
{
    /// <summary>
    /// Conservative - only obvious bloatware
    /// </summary>
    Conservative,

    /// <summary>
    /// Moderate - most unnecessary components
    /// </summary>
    Moderate,

    /// <summary>
    /// Aggressive - maximum debloating (may affect some features)
    /// </summary>
    Aggressive,

    /// <summary>
    /// Custom - user-defined selection
    /// </summary>
    Custom
}

/// <summary>
/// Request to apply debloat preset
/// </summary>
public class ApplyDebloatRequest
{
    /// <summary>
    /// Path to mounted image
    /// </summary>
    public string MountPath { get; set; } = string.Empty;

    /// <summary>
    /// Preset ID to apply
    /// </summary>
    public string PresetId { get; set; } = string.Empty;

    /// <summary>
    /// Custom preset (if PresetId is "custom")
    /// </summary>
    public DebloatPreset? CustomPreset { get; set; }

    /// <summary>
    /// Dry run (analyze only, don't make changes)
    /// </summary>
    public bool DryRun { get; set; }

    /// <summary>
    /// Create backup before applying
    /// </summary>
    public bool CreateBackup { get; set; } = true;
}

/// <summary>
/// Result of debloat operation
/// </summary>
public class DebloatResult
{
    /// <summary>
    /// Whether the operation succeeded
    /// </summary>
    public bool Success { get; set; }

    /// <summary>
    /// Components successfully removed
    /// </summary>
    public List<string> RemovedComponents { get; set; } = new();

    /// <summary>
    /// Components that failed to remove
    /// </summary>
    public List<DebloatError> FailedComponents { get; set; } = new();

    /// <summary>
    /// Registry tweaks applied
    /// </summary>
    public int RegistryTweaksApplied { get; set; }

    /// <summary>
    /// Services disabled
    /// </summary>
    public int ServicesDisabled { get; set; }

    /// <summary>
    /// Scheduled tasks disabled
    /// </summary>
    public int ScheduledTasksDisabled { get; set; }

    /// <summary>
    /// Actual space saved in bytes
    /// </summary>
    public long SpaceSaved { get; set; }

    /// <summary>
    /// Warnings generated
    /// </summary>
    public List<string> Warnings { get; set; } = new();

    /// <summary>
    /// Overall message
    /// </summary>
    public string Message { get; set; } = string.Empty;

    /// <summary>
    /// Dry run analysis (if applicable)
    /// </summary>
    public DebloatAnalysis? Analysis { get; set; }
}

/// <summary>
/// Error during debloat operation
/// </summary>
public class DebloatError
{
    /// <summary>
    /// Component identifier
    /// </summary>
    public string ComponentId { get; set; } = string.Empty;

    /// <summary>
    /// Error message
    /// </summary>
    public string ErrorMessage { get; set; } = string.Empty;

    /// <summary>
    /// Whether to continue despite this error
    /// </summary>
    public bool CanContinue { get; set; } = true;
}

/// <summary>
/// Analysis of debloat impact
/// </summary>
public class DebloatAnalysis
{
    /// <summary>
    /// Total components to remove
    /// </summary>
    public int TotalComponents { get; set; }

    /// <summary>
    /// Breakdown by component type
    /// </summary>
    public Dictionary<ComponentType, int> ComponentsByType { get; set; } = new();

    /// <summary>
    /// Estimated space savings
    /// </summary>
    public long EstimatedSpaceSavings { get; set; }

    /// <summary>
    /// Potential risks
    /// </summary>
    public List<string> Risks { get; set; } = new();

    /// <summary>
    /// Affected features
    /// </summary>
    public List<string> AffectedFeatures { get; set; } = new();

    /// <summary>
    /// Recommendations
    /// </summary>
    public List<string> Recommendations { get; set; } = new();
}
