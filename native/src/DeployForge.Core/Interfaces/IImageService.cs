using DeployForge.Core.Models;

namespace DeployForge.Core.Interfaces;

/// <summary>
/// Service for managing Windows deployment images.
/// </summary>
public interface IImageService
{
    /// <summary>
    /// Mounts a Windows image.
    /// </summary>
    /// <param name="imagePath">Path to the image file.</param>
    /// <param name="index">Image index (for WIM/ESD).</param>
    /// <param name="mountPath">Optional custom mount path.</param>
    /// <param name="readOnly">Mount as read-only.</param>
    /// <param name="progress">Progress reporter.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    Task<MountResult> MountAsync(
        string imagePath, 
        int index = 1, 
        string? mountPath = null, 
        bool readOnly = false,
        IProgress<ProgressInfo>? progress = null,
        CancellationToken cancellationToken = default);
    
    /// <summary>
    /// Unmounts a Windows image.
    /// </summary>
    /// <param name="mountPath">Mount path to unmount.</param>
    /// <param name="saveChanges">Save changes to the image.</param>
    /// <param name="progress">Progress reporter.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    Task<DismountResult> UnmountAsync(
        string mountPath, 
        bool saveChanges = false,
        IProgress<ProgressInfo>? progress = null,
        CancellationToken cancellationToken = default);
    
    /// <summary>
    /// Gets information about an image file.
    /// </summary>
    /// <param name="imagePath">Path to the image.</param>
    /// <param name="index">Optional specific index to get info for.</param>
    Task<ImageInfo> GetInfoAsync(string imagePath, int? index = null);
    
    /// <summary>
    /// Lists files in a mounted image.
    /// </summary>
    /// <param name="mountPath">Mount path.</param>
    /// <param name="path">Path within the image.</param>
    /// <param name="recurse">Include subdirectories.</param>
    Task<IEnumerable<ImageFileInfo>> ListFilesAsync(
        string mountPath, 
        string path = "", 
        bool recurse = false);
    
    /// <summary>
    /// Adds a file to a mounted image.
    /// </summary>
    /// <param name="mountPath">Mount path.</param>
    /// <param name="source">Source file path.</param>
    /// <param name="destination">Destination path in image.</param>
    Task AddFileAsync(string mountPath, string source, string destination);
    
    /// <summary>
    /// Removes a file from a mounted image.
    /// </summary>
    /// <param name="mountPath">Mount path.</param>
    /// <param name="path">Path to remove.</param>
    /// <param name="recurse">Remove recursively.</param>
    Task RemoveFileAsync(string mountPath, string path, bool recurse = false);
    
    /// <summary>
    /// Extracts a file from a mounted image.
    /// </summary>
    /// <param name="mountPath">Mount path.</param>
    /// <param name="source">Source path in image.</param>
    /// <param name="destination">Destination on host.</param>
    Task ExtractFileAsync(string mountPath, string source, string destination);
    
    /// <summary>
    /// Gets the current mount path if any image is mounted.
    /// </summary>
    string? GetCurrentMountPath();
    
    /// <summary>
    /// Checks if an image is currently mounted.
    /// </summary>
    bool IsMounted { get; }
}

/// <summary>
/// Service for executing PowerShell scripts.
/// </summary>
public interface IPowerShellExecutor
{
    /// <summary>
    /// Executes a PowerShell script.
    /// </summary>
    /// <param name="script">Script to execute.</param>
    /// <param name="parameters">Script parameters.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Execution result.</returns>
    Task<PowerShellResult> ExecuteAsync(
        string script, 
        Dictionary<string, object>? parameters = null,
        CancellationToken cancellationToken = default);
    
    /// <summary>
    /// Executes a PowerShell command.
    /// </summary>
    /// <param name="command">Command to execute.</param>
    /// <param name="parameters">Command parameters.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    Task<PowerShellResult> ExecuteCommandAsync(
        string command, 
        Dictionary<string, object>? parameters = null,
        CancellationToken cancellationToken = default);
    
    /// <summary>
    /// Imports the DeployForge PowerShell module.
    /// </summary>
    Task ImportModuleAsync();
    
    /// <summary>
    /// Whether the module is loaded.
    /// </summary>
    bool IsModuleLoaded { get; }
}

/// <summary>
/// Result of a PowerShell execution.
/// </summary>
public class PowerShellResult
{
    /// <summary>
    /// Whether the execution succeeded.
    /// </summary>
    public bool Success { get; set; }
    
    /// <summary>
    /// Output objects from the script.
    /// </summary>
    public List<object> Output { get; set; } = new();
    
    /// <summary>
    /// Error messages.
    /// </summary>
    public List<string> Errors { get; set; } = new();
    
    /// <summary>
    /// Warning messages.
    /// </summary>
    public List<string> Warnings { get; set; } = new();
    
    /// <summary>
    /// Verbose messages.
    /// </summary>
    public List<string> Verbose { get; set; } = new();
    
    /// <summary>
    /// Gets the first output object as type T.
    /// </summary>
    public T? GetOutput<T>() where T : class
    {
        return Output.FirstOrDefault() as T;
    }
}

/// <summary>
/// Progress information for long-running operations.
/// </summary>
public class ProgressInfo
{
    /// <summary>
    /// Progress percentage (0-100).
    /// </summary>
    public int Percentage { get; set; }
    
    /// <summary>
    /// Current operation description.
    /// </summary>
    public string Message { get; set; } = string.Empty;
    
    /// <summary>
    /// Current step number.
    /// </summary>
    public int CurrentStep { get; set; }
    
    /// <summary>
    /// Total number of steps.
    /// </summary>
    public int TotalSteps { get; set; }
    
    /// <summary>
    /// Whether the operation is indeterminate.
    /// </summary>
    public bool IsIndeterminate { get; set; }
}

/// <summary>
/// Service for feature operations (gaming, debloat, etc.).
/// </summary>
public interface IFeatureService
{
    /// <summary>
    /// Applies gaming optimizations.
    /// </summary>
    Task<GamingOptimizationResult> ApplyGamingOptimizationsAsync(
        string mountPath, 
        GamingConfig config,
        IProgress<ProgressInfo>? progress = null,
        CancellationToken cancellationToken = default);
    
    /// <summary>
    /// Removes bloatware.
    /// </summary>
    Task<DebloatResult> RemoveBloatwareAsync(
        string mountPath, 
        DebloatConfig config,
        IProgress<ProgressInfo>? progress = null,
        CancellationToken cancellationToken = default);
    
    /// <summary>
    /// Applies a complete build profile.
    /// </summary>
    Task<BuildResult> ApplyProfileAsync(
        string mountPath, 
        BuildProfile profile,
        IProgress<ProgressInfo>? progress = null,
        CancellationToken cancellationToken = default);
}

/// <summary>
/// Result of a build operation.
/// </summary>
public class BuildResult
{
    /// <summary>
    /// Whether the build succeeded.
    /// </summary>
    public bool Success { get; set; }
    
    /// <summary>
    /// Profile that was applied.
    /// </summary>
    public string ProfileName { get; set; } = string.Empty;
    
    /// <summary>
    /// All changes that were applied.
    /// </summary>
    public List<string> Changes { get; set; } = new();
    
    /// <summary>
    /// Any warnings during the build.
    /// </summary>
    public List<string> Warnings { get; set; } = new();
    
    /// <summary>
    /// Error message if failed.
    /// </summary>
    public string? Error { get; set; }
    
    /// <summary>
    /// Total build duration.
    /// </summary>
    public TimeSpan Duration { get; set; }
}

/// <summary>
/// Service for managing templates.
/// </summary>
public interface ITemplateService
{
    /// <summary>
    /// Gets all available build profiles.
    /// </summary>
    IEnumerable<BuildProfile> GetBuiltInProfiles();
    
    /// <summary>
    /// Gets all custom templates.
    /// </summary>
    Task<IEnumerable<BuildProfile>> GetCustomTemplatesAsync();
    
    /// <summary>
    /// Saves a custom template.
    /// </summary>
    Task SaveTemplateAsync(BuildProfile profile, string path);
    
    /// <summary>
    /// Loads a template from file.
    /// </summary>
    Task<BuildProfile> LoadTemplateAsync(string path);
    
    /// <summary>
    /// Deletes a custom template.
    /// </summary>
    Task DeleteTemplateAsync(string path);
}

/// <summary>
/// Service for application settings.
/// </summary>
public interface ISettingsService
{
    /// <summary>
    /// Gets a setting value.
    /// </summary>
    T? GetSetting<T>(string key, T? defaultValue = default);
    
    /// <summary>
    /// Sets a setting value.
    /// </summary>
    void SetSetting<T>(string key, T value);
    
    /// <summary>
    /// Gets the default mount path.
    /// </summary>
    string DefaultMountPath { get; set; }
    
    /// <summary>
    /// Gets the current theme.
    /// </summary>
    string Theme { get; set; }
    
    /// <summary>
    /// Whether to show advanced options.
    /// </summary>
    bool ShowAdvancedOptions { get; set; }
    
    /// <summary>
    /// Recent image paths.
    /// </summary>
    List<string> RecentImages { get; }
    
    /// <summary>
    /// Adds a recent image path.
    /// </summary>
    void AddRecentImage(string path);
    
    /// <summary>
    /// Saves all settings.
    /// </summary>
    Task SaveAsync();
    
    /// <summary>
    /// Loads settings from disk.
    /// </summary>
    Task LoadAsync();
}
