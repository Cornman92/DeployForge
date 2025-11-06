namespace DeployForge.Common.Models;

/// <summary>
/// Image template definition
/// </summary>
public class ImageTemplate
{
    /// <summary>
    /// Template ID
    /// </summary>
    public string Id { get; set; } = Guid.NewGuid().ToString();

    /// <summary>
    /// Template name
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// Template description
    /// </summary>
    public string Description { get; set; } = string.Empty;

    /// <summary>
    /// Template author
    /// </summary>
    public string Author { get; set; } = string.Empty;

    /// <summary>
    /// Template version
    /// </summary>
    public string Version { get; set; } = "1.0.0";

    /// <summary>
    /// Created date
    /// </summary>
    public DateTime CreatedDate { get; set; } = DateTime.UtcNow;

    /// <summary>
    /// Last modified date
    /// </summary>
    public DateTime ModifiedDate { get; set; } = DateTime.UtcNow;

    /// <summary>
    /// Template tags for categorization
    /// </summary>
    public List<string> Tags { get; set; } = new();

    /// <summary>
    /// Target Windows versions (e.g., "Windows 11", "Windows 10")
    /// </summary>
    public List<string> TargetVersions { get; set; } = new();

    /// <summary>
    /// Debloat configuration
    /// </summary>
    public DebloatConfiguration? Debloat { get; set; }

    /// <summary>
    /// Component configuration
    /// </summary>
    public ComponentConfiguration? Components { get; set; }

    /// <summary>
    /// Driver configuration
    /// </summary>
    public DriverConfiguration? Drivers { get; set; }

    /// <summary>
    /// Update configuration
    /// </summary>
    public UpdateConfiguration? Updates { get; set; }

    /// <summary>
    /// Registry tweaks configuration
    /// </summary>
    public RegistryConfiguration? Registry { get; set; }

    /// <summary>
    /// Language configuration
    /// </summary>
    public LanguageConfiguration? Languages { get; set; }

    /// <summary>
    /// Workflow to execute
    /// </summary>
    public string? WorkflowId { get; set; }

    /// <summary>
    /// Custom metadata
    /// </summary>
    public Dictionary<string, string> Metadata { get; set; } = new();
}

/// <summary>
/// Debloat configuration for template
/// </summary>
public class DebloatConfiguration
{
    public string PresetId { get; set; } = string.Empty;
    public List<string> AdditionalComponentsToRemove { get; set; } = new();
    public List<string> ComponentsToKeep { get; set; } = new();
}

/// <summary>
/// Component configuration for template
/// </summary>
public class ComponentConfiguration
{
    public List<string> ComponentsToAdd { get; set; } = new();
    public List<string> ComponentsToRemove { get; set; } = new();
    public List<string> FeaturesToEnable { get; set; } = new();
    public List<string> FeaturesToDisable { get; set; } = new();
}

/// <summary>
/// Driver configuration for template
/// </summary>
public class DriverConfiguration
{
    public List<string> DriverPackPaths { get; set; } = new();
    public bool RecurseDriverPaths { get; set; } = true;
}

/// <summary>
/// Update configuration for template
/// </summary>
public class UpdateConfiguration
{
    public List<string> UpdatePaths { get; set; } = new();
    public bool CleanupSuperseded { get; set; } = true;
}

/// <summary>
/// Registry configuration for template
/// </summary>
public class RegistryConfiguration
{
    public List<string> TweakPresets { get; set; } = new();
    public List<RegistryTweak> CustomTweaks { get; set; } = new();
}

/// <summary>
/// Custom registry tweak
/// </summary>
public class RegistryTweak
{
    public string Path { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public string Value { get; set; } = string.Empty;
    public string Type { get; set; } = "String";
}

/// <summary>
/// Language configuration for template
/// </summary>
public class LanguageConfiguration
{
    public List<string> LanguagePacksToAdd { get; set; } = new();
    public List<string> LanguagePacksToRemove { get; set; } = new();
    public string? DefaultUILanguage { get; set; }
}

/// <summary>
/// Request to create template from current image state
/// </summary>
public class CreateTemplateRequest
{
    public string Name { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public string Author { get; set; } = string.Empty;
    public List<string> Tags { get; set; } = new();
    public string MountPath { get; set; } = string.Empty;
}

/// <summary>
/// Request to apply template to an image
/// </summary>
public class ApplyTemplateRequest
{
    public string TemplateId { get; set; } = string.Empty;
    public string ImagePath { get; set; } = string.Empty;
    public string MountPath { get; set; } = string.Empty;
    public int ImageIndex { get; set; } = 1;
    public bool DryRun { get; set; } = false;
    public Dictionary<string, string> Variables { get; set; } = new();
}

/// <summary>
/// Result of applying a template
/// </summary>
public class ApplyTemplateResult
{
    public bool Success { get; set; }
    public string Message { get; set; } = string.Empty;
    public List<string> AppliedSteps { get; set; } = new();
    public List<string> FailedSteps { get; set; } = new();
    public List<string> SkippedSteps { get; set; } = new();
    public TimeSpan Duration { get; set; }
}
