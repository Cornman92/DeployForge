using DeployForge.Core.Enums;
using DeployForge.Core.Exceptions;
using DeployForge.Core.Interfaces;
using DeployForge.Core.Models;

namespace DeployForge.Services;

/// <summary>
/// Service for applying feature customizations to Windows images.
/// </summary>
public class FeatureService : IFeatureService
{
    private readonly IPowerShellExecutor _executor;
    
    /// <summary>
    /// Creates a new FeatureService.
    /// </summary>
    public FeatureService(IPowerShellExecutor executor)
    {
        _executor = executor ?? throw new ArgumentNullException(nameof(executor));
    }
    
    /// <inheritdoc />
    public async Task<GamingOptimizationResult> ApplyGamingOptimizationsAsync(
        string mountPath, 
        GamingConfig config,
        IProgress<ProgressInfo>? progress = null,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(mountPath))
            throw new ArgumentException("Mount path is required", nameof(mountPath));
        
        var result = new GamingOptimizationResult { Success = true };
        var totalSteps = CountGamingSteps(config);
        var currentStep = 0;
        
        try
        {
            // Apply gaming profile
            ReportProgress(progress, "Applying gaming profile...", ++currentStep, totalSteps);
            
            var profileParams = new Dictionary<string, object>
            {
                ["MountPath"] = mountPath,
                ["Profile"] = config.Profile.ToString()
            };
            
            var profileResult = await _executor.ExecuteCommandAsync(
                "Set-GamingProfile", profileParams, cancellationToken);
            
            if (!profileResult.Success)
            {
                result.Warnings.AddRange(profileResult.Errors);
            }
            else
            {
                result.AppliedOptimizations.Add($"Applied {config.Profile} gaming profile");
            }
            
            // Enable Game Mode
            if (config.EnableGameMode)
            {
                ReportProgress(progress, "Enabling Game Mode...", ++currentStep, totalSteps);
                
                var gameModeResult = await _executor.ExecuteCommandAsync(
                    "Enable-GameMode",
                    new Dictionary<string, object> { ["MountPath"] = mountPath },
                    cancellationToken);
                
                if (gameModeResult.Success)
                {
                    result.AppliedOptimizations.Add("Enabled Windows Game Mode");
                }
            }
            
            // Disable Game Bar
            if (config.DisableGameBar)
            {
                ReportProgress(progress, "Disabling Game Bar...", ++currentStep, totalSteps);
                
                var gameBarResult = await _executor.ExecuteCommandAsync(
                    "Disable-GameBar",
                    new Dictionary<string, object> { ["MountPath"] = mountPath },
                    cancellationToken);
                
                if (gameBarResult.Success)
                {
                    result.AppliedOptimizations.Add("Disabled Xbox Game Bar");
                }
            }
            
            // Optimize network latency
            if (config.OptimizeNetwork)
            {
                ReportProgress(progress, "Optimizing network latency...", ++currentStep, totalSteps);
                
                var networkResult = await _executor.ExecuteCommandAsync(
                    "Optimize-NetworkLatency",
                    new Dictionary<string, object> { ["MountPath"] = mountPath },
                    cancellationToken);
                
                if (networkResult.Success)
                {
                    result.AppliedOptimizations.Add("Optimized network settings for low latency");
                }
            }
            
            // Install gaming runtimes
            if (config.InstallRuntimes)
            {
                ReportProgress(progress, "Preparing gaming runtime installers...", ++currentStep, totalSteps);
                
                var runtimeParams = new Dictionary<string, object>
                {
                    ["MountPath"] = mountPath,
                    ["DirectX"] = config.InstallDirectX,
                    ["VCRedist"] = config.InstallVCRedist,
                    ["DotNet"] = config.InstallDotNetRuntime
                };
                
                var runtimeResult = await _executor.ExecuteCommandAsync(
                    "Install-GamingRuntimes", runtimeParams, cancellationToken);
                
                if (runtimeResult.Success)
                {
                    var runtimes = new List<string>();
                    if (config.InstallDirectX) runtimes.Add("DirectX");
                    if (config.InstallVCRedist) runtimes.Add("VC++ Redistributables");
                    if (config.InstallDotNetRuntime) runtimes.Add(".NET Runtime");
                    
                    result.AppliedOptimizations.Add($"Prepared first-boot installers: {string.Join(", ", runtimes)}");
                }
            }
            
            // Optimize gaming services
            if (config.OptimizeServices)
            {
                ReportProgress(progress, "Optimizing gaming services...", ++currentStep, totalSteps);
                
                var serviceParams = new Dictionary<string, object>
                {
                    ["MountPath"] = mountPath,
                    ["DisableXboxServices"] = config.DisableXboxServices,
                    ["DisableGameDVR"] = config.DisableGameDVR
                };
                
                var serviceResult = await _executor.ExecuteCommandAsync(
                    "Optimize-GamingServices", serviceParams, cancellationToken);
                
                if (serviceResult.Success)
                {
                    result.AppliedOptimizations.Add("Optimized system services for gaming");
                }
            }
            
            ReportProgress(progress, "Gaming optimizations complete", totalSteps, totalSteps);
        }
        catch (Exception ex)
        {
            result.Success = false;
            result.Error = ex.Message;
        }
        
        return result;
    }
    
    /// <inheritdoc />
    public async Task<DebloatResult> RemoveBloatwareAsync(
        string mountPath, 
        DebloatConfig config,
        IProgress<ProgressInfo>? progress = null,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(mountPath))
            throw new ArgumentException("Mount path is required", nameof(mountPath));
        
        var result = new DebloatResult { Success = true };
        var totalSteps = CountDebloatSteps(config);
        var currentStep = 0;
        
        try
        {
            // Remove bloatware apps
            if (config.RemoveApps.Count > 0)
            {
                ReportProgress(progress, "Removing bloatware apps...", ++currentStep, totalSteps);
                
                var removeParams = new Dictionary<string, object>
                {
                    ["MountPath"] = mountPath,
                    ["Apps"] = config.RemoveApps.ToArray(),
                    ["Level"] = config.Level.ToString()
                };
                
                var removeResult = await _executor.ExecuteCommandAsync(
                    "Remove-Bloatware", removeParams, cancellationToken);
                
                if (removeResult.Success)
                {
                    result.RemovedApps.AddRange(config.RemoveApps);
                }
                else
                {
                    result.Warnings.AddRange(removeResult.Errors);
                }
            }
            
            // Disable telemetry
            if (config.DisableTelemetry)
            {
                ReportProgress(progress, "Disabling telemetry...", ++currentStep, totalSteps);
                
                var telemetryResult = await _executor.ExecuteCommandAsync(
                    "Disable-Telemetry",
                    new Dictionary<string, object> { ["MountPath"] = mountPath },
                    cancellationToken);
                
                if (telemetryResult.Success)
                {
                    result.AppliedSettings.Add("Disabled Windows Telemetry");
                }
            }
            
            // Disable Cortana
            if (config.DisableCortana)
            {
                ReportProgress(progress, "Disabling Cortana...", ++currentStep, totalSteps);
                
                var cortanaResult = await _executor.ExecuteCommandAsync(
                    "Disable-Cortana",
                    new Dictionary<string, object> { ["MountPath"] = mountPath },
                    cancellationToken);
                
                if (cortanaResult.Success)
                {
                    result.AppliedSettings.Add("Disabled Cortana");
                }
            }
            
            // Apply privacy settings
            if (config.ApplyPrivacySettings)
            {
                ReportProgress(progress, "Applying privacy settings...", ++currentStep, totalSteps);
                
                var privacyParams = new Dictionary<string, object>
                {
                    ["MountPath"] = mountPath,
                    ["Level"] = config.PrivacyLevel.ToString()
                };
                
                var privacyResult = await _executor.ExecuteCommandAsync(
                    "Set-PrivacySettings", privacyParams, cancellationToken);
                
                if (privacyResult.Success)
                {
                    result.AppliedSettings.Add($"Applied {config.PrivacyLevel} privacy level");
                }
            }
            
            // Disable Delivery Optimization
            if (config.DisableDeliveryOptimization)
            {
                ReportProgress(progress, "Disabling Delivery Optimization...", ++currentStep, totalSteps);
                
                var doResult = await _executor.ExecuteCommandAsync(
                    "Disable-DeliveryOptimization",
                    new Dictionary<string, object> { ["MountPath"] = mountPath },
                    cancellationToken);
                
                if (doResult.Success)
                {
                    result.AppliedSettings.Add("Disabled Windows Delivery Optimization");
                }
            }
            
            ReportProgress(progress, "Debloat complete", totalSteps, totalSteps);
        }
        catch (Exception ex)
        {
            result.Success = false;
            result.Error = ex.Message;
        }
        
        return result;
    }
    
    /// <inheritdoc />
    public async Task<BuildResult> ApplyProfileAsync(
        string mountPath, 
        BuildProfile profile,
        IProgress<ProgressInfo>? progress = null,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(mountPath))
            throw new ArgumentException("Mount path is required", nameof(mountPath));
        
        var startTime = DateTime.Now;
        var result = new BuildResult 
        { 
            Success = true,
            ProfileName = profile.Name
        };
        
        var totalSteps = CountProfileSteps(profile);
        var currentStep = 0;
        
        try
        {
            // Apply debloat if enabled
            if (profile.EnableDebloat && profile.Debloat != null)
            {
                ReportProgress(progress, "Applying debloat settings...", ++currentStep, totalSteps);
                
                var debloatResult = await RemoveBloatwareAsync(
                    mountPath, profile.Debloat, null, cancellationToken);
                
                result.Changes.AddRange(debloatResult.RemovedApps.Select(a => $"Removed: {a}"));
                result.Changes.AddRange(debloatResult.AppliedSettings);
                result.Warnings.AddRange(debloatResult.Warnings);
                
                if (!debloatResult.Success && !string.IsNullOrEmpty(debloatResult.Error))
                {
                    result.Warnings.Add(debloatResult.Error);
                }
            }
            
            // Apply gaming optimizations if enabled
            if (profile.EnableGaming && profile.Gaming != null)
            {
                ReportProgress(progress, "Applying gaming optimizations...", ++currentStep, totalSteps);
                
                var gamingResult = await ApplyGamingOptimizationsAsync(
                    mountPath, profile.Gaming, null, cancellationToken);
                
                result.Changes.AddRange(gamingResult.AppliedOptimizations);
                result.Warnings.AddRange(gamingResult.Warnings);
                
                if (!gamingResult.Success && !string.IsNullOrEmpty(gamingResult.Error))
                {
                    result.Warnings.Add(gamingResult.Error);
                }
            }
            
            // Apply developer environment if enabled
            if (profile.EnableDevEnvironment && profile.DevEnvironment != null)
            {
                ReportProgress(progress, "Configuring developer environment...", ++currentStep, totalSteps);
                
                await ApplyDevEnvironmentAsync(mountPath, profile.DevEnvironment, cancellationToken);
                result.Changes.Add("Configured developer environment");
            }
            
            // Apply browser configuration if enabled
            if (profile.EnableBrowsers && profile.Browsers != null)
            {
                ReportProgress(progress, "Configuring browsers...", ++currentStep, totalSteps);
                
                await ApplyBrowserConfigAsync(mountPath, profile.Browsers, cancellationToken);
                result.Changes.Add("Configured browser settings");
            }
            
            // Apply UI customization if enabled
            if (profile.EnableUICustomization && profile.UICustomization != null)
            {
                ReportProgress(progress, "Applying UI customizations...", ++currentStep, totalSteps);
                
                await ApplyUICustomizationAsync(mountPath, profile.UICustomization, cancellationToken);
                result.Changes.Add("Applied UI customizations");
            }
            
            // Apply privacy hardening if enabled
            if (profile.EnablePrivacyHardening)
            {
                ReportProgress(progress, "Applying privacy hardening...", ++currentStep, totalSteps);
                
                var privacyParams = new Dictionary<string, object>
                {
                    ["MountPath"] = mountPath,
                    ["Level"] = profile.PrivacyLevel.ToString()
                };
                
                await _executor.ExecuteCommandAsync("Set-PrivacySettings", privacyParams, cancellationToken);
                result.Changes.Add($"Applied {profile.PrivacyLevel} privacy hardening");
            }
            
            ReportProgress(progress, "Profile applied successfully", totalSteps, totalSteps);
        }
        catch (Exception ex)
        {
            result.Success = false;
            result.Error = ex.Message;
        }
        
        result.Duration = DateTime.Now - startTime;
        return result;
    }
    
    /// <summary>
    /// Applies developer environment configuration.
    /// </summary>
    private async Task ApplyDevEnvironmentAsync(
        string mountPath, 
        DevEnvironmentConfig config,
        CancellationToken cancellationToken)
    {
        var parameters = new Dictionary<string, object>
        {
            ["MountPath"] = mountPath,
            ["Profile"] = config.Profile.ToString(),
            ["EnableDeveloperMode"] = config.EnableDeveloperMode,
            ["EnableWSL2"] = config.EnableWSL2
        };
        
        if (config.Languages.Count > 0)
        {
            parameters["Languages"] = config.Languages.ToArray();
        }
        
        if (config.IDEs.Count > 0)
        {
            parameters["IDEs"] = config.IDEs.ToArray();
        }
        
        await _executor.ExecuteCommandAsync("Set-DeveloperEnvironment", parameters, cancellationToken);
    }
    
    /// <summary>
    /// Applies browser configuration.
    /// </summary>
    private async Task ApplyBrowserConfigAsync(
        string mountPath,
        BrowserConfig config,
        CancellationToken cancellationToken)
    {
        var parameters = new Dictionary<string, object>
        {
            ["MountPath"] = mountPath,
            ["DefaultBrowser"] = config.DefaultBrowser.ToString(),
            ["InstallChrome"] = config.InstallChrome,
            ["InstallFirefox"] = config.InstallFirefox,
            ["InstallBrave"] = config.InstallBrave,
            ["ApplyPolicies"] = config.ApplyEnterprisePolicies
        };
        
        await _executor.ExecuteCommandAsync("Set-BrowserConfiguration", parameters, cancellationToken);
    }
    
    /// <summary>
    /// Applies UI customization.
    /// </summary>
    private async Task ApplyUICustomizationAsync(
        string mountPath,
        UIConfig config,
        CancellationToken cancellationToken)
    {
        var parameters = new Dictionary<string, object>
        {
            ["MountPath"] = mountPath,
            ["Profile"] = config.Profile.ToString(),
            ["DarkMode"] = config.EnableDarkMode,
            ["DisableWidgets"] = config.DisableWidgets,
            ["DisableNews"] = config.DisableNewsAndInterests,
            ["ClassicContextMenu"] = config.UseClassicContextMenu
        };
        
        await _executor.ExecuteCommandAsync("Set-UICustomization", parameters, cancellationToken);
    }
    
    /// <summary>
    /// Reports progress to the progress handler.
    /// </summary>
    private static void ReportProgress(
        IProgress<ProgressInfo>? progress, 
        string message, 
        int current, 
        int total)
    {
        progress?.Report(new ProgressInfo
        {
            Message = message,
            CurrentStep = current,
            TotalSteps = total,
            Percentage = total > 0 ? (int)((double)current / total * 100) : 0
        });
    }
    
    /// <summary>
    /// Counts the number of gaming optimization steps.
    /// </summary>
    private static int CountGamingSteps(GamingConfig config)
    {
        var steps = 1; // Profile application
        if (config.EnableGameMode) steps++;
        if (config.DisableGameBar) steps++;
        if (config.OptimizeNetwork) steps++;
        if (config.InstallRuntimes) steps++;
        if (config.OptimizeServices) steps++;
        return steps;
    }
    
    /// <summary>
    /// Counts the number of debloat steps.
    /// </summary>
    private static int CountDebloatSteps(DebloatConfig config)
    {
        var steps = 0;
        if (config.RemoveApps.Count > 0) steps++;
        if (config.DisableTelemetry) steps++;
        if (config.DisableCortana) steps++;
        if (config.ApplyPrivacySettings) steps++;
        if (config.DisableDeliveryOptimization) steps++;
        return Math.Max(steps, 1);
    }
    
    /// <summary>
    /// Counts the total number of profile steps.
    /// </summary>
    private static int CountProfileSteps(BuildProfile profile)
    {
        var steps = 0;
        if (profile.EnableDebloat) steps++;
        if (profile.EnableGaming) steps++;
        if (profile.EnableDevEnvironment) steps++;
        if (profile.EnableBrowsers) steps++;
        if (profile.EnableUICustomization) steps++;
        if (profile.EnablePrivacyHardening) steps++;
        return Math.Max(steps, 1);
    }
}
