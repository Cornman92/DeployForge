using DeployForge.Core.Enums;

namespace DeployForge.Core.Models;

/// <summary>
/// Gaming optimization configuration.
/// </summary>
public class GamingConfig
{
    /// <summary>
    /// Gaming profile to apply.
    /// </summary>
    public GamingProfile Profile { get; set; } = GamingProfile.Competitive;
    
    /// <summary>
    /// Enable Windows Game Mode.
    /// </summary>
    public bool EnableGameMode { get; set; } = true;
    
    /// <summary>
    /// Disable fullscreen optimizations.
    /// </summary>
    public bool DisableFullscreenOptimizations { get; set; } = false;
    
    /// <summary>
    /// Optimize network for low latency.
    /// </summary>
    public bool OptimizeNetworkLatency { get; set; } = true;
    
    /// <summary>
    /// Disable Windows Game Bar.
    /// </summary>
    public bool DisableGameBar { get; set; } = false;
    
    /// <summary>
    /// Enable hardware-accelerated GPU scheduling.
    /// </summary>
    public bool EnableHardwareAcceleration { get; set; } = true;
    
    /// <summary>
    /// Disable background game recording.
    /// </summary>
    public bool DisableBackgroundRecording { get; set; } = true;
    
    /// <summary>
    /// Optimize mouse polling rate.
    /// </summary>
    public bool OptimizeMousePolling { get; set; } = true;
    
    /// <summary>
    /// Disable Nagle's algorithm for reduced latency.
    /// </summary>
    public bool DisableNagleAlgorithm { get; set; } = true;
    
    /// <summary>
    /// Process priority boost level.
    /// </summary>
    public string PriorityBoost { get; set; } = "High";
    
    /// <summary>
    /// Install gaming runtimes (DirectX, Visual C++).
    /// </summary>
    public bool InstallRuntimes { get; set; } = true;
    
    /// <summary>
    /// Optimize Windows services for gaming.
    /// </summary>
    public bool OptimizeServices { get; set; } = true;

    /// <summary>
    /// Creates a configuration from a predefined profile.
    /// </summary>
    public static GamingConfig FromProfile(GamingProfile profile)
    {
        return profile switch
        {
            GamingProfile.Competitive => new GamingConfig
            {
                Profile = GamingProfile.Competitive,
                EnableGameMode = true,
                DisableFullscreenOptimizations = true,
                OptimizeNetworkLatency = true,
                DisableGameBar = true,
                EnableHardwareAcceleration = true,
                DisableBackgroundRecording = true,
                OptimizeMousePolling = true,
                DisableNagleAlgorithm = true,
                PriorityBoost = "High",
                OptimizeServices = true
            },
            GamingProfile.Balanced => new GamingConfig
            {
                Profile = GamingProfile.Balanced,
                EnableGameMode = true,
                DisableFullscreenOptimizations = false,
                OptimizeNetworkLatency = true,
                DisableGameBar = false,
                EnableHardwareAcceleration = true,
                DisableBackgroundRecording = true,
                OptimizeMousePolling = false,
                DisableNagleAlgorithm = false,
                PriorityBoost = "Normal",
                OptimizeServices = false
            },
            GamingProfile.Quality => new GamingConfig
            {
                Profile = GamingProfile.Quality,
                EnableGameMode = true,
                DisableFullscreenOptimizations = false,
                OptimizeNetworkLatency = false,
                DisableGameBar = false,
                EnableHardwareAcceleration = true,
                DisableBackgroundRecording = false,
                OptimizeMousePolling = false,
                DisableNagleAlgorithm = false,
                PriorityBoost = "Normal",
                OptimizeServices = false
            },
            GamingProfile.Streaming => new GamingConfig
            {
                Profile = GamingProfile.Streaming,
                EnableGameMode = true,
                DisableFullscreenOptimizations = false,
                OptimizeNetworkLatency = true,
                DisableGameBar = false,
                EnableHardwareAcceleration = true,
                DisableBackgroundRecording = false,
                OptimizeMousePolling = false,
                DisableNagleAlgorithm = true,
                PriorityBoost = "High",
                OptimizeServices = false
            },
            _ => new GamingConfig()
        };
    }
}

/// <summary>
/// Result of a gaming optimization operation.
/// </summary>
public class GamingOptimizationResult
{
    /// <summary>
    /// Whether the operation succeeded.
    /// </summary>
    public bool Success { get; set; }
    
    /// <summary>
    /// Profile that was applied.
    /// </summary>
    public GamingProfile Profile { get; set; }
    
    /// <summary>
    /// List of changes applied.
    /// </summary>
    public List<string> Changes { get; set; } = new();
    
    /// <summary>
    /// Error message if failed.
    /// </summary>
    public string? Error { get; set; }
}
