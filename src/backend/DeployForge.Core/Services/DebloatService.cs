using DeployForge.Common.Models;
using DeployForge.Core.Interfaces;
using System.Runtime.Versioning;

namespace DeployForge.Core.Services;

/// <summary>
/// Service for debloating Windows images
/// </summary>
[SupportedOSPlatform("windows")]
public class DebloatService : IDebloatService
{
    private readonly IComponentService _componentService;
    private readonly IRegistryService _registryService;
    private readonly ILogger<DebloatService> _logger;
    private readonly Dictionary<string, DebloatPreset> _presets;

    public DebloatService(
        IComponentService componentService,
        IRegistryService registryService,
        ILogger<DebloatService> logger)
    {
        _componentService = componentService;
        _registryService = registryService;
        _logger = logger;
        _presets = InitializePresets();
    }

    public async Task<OperationResult<List<DebloatPreset>>> GetPresetsAsync(
        DebloatLevel? level = null,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                var presets = _presets.Values.ToList();

                if (level.HasValue)
                {
                    presets = presets.Where(p => p.Level == level.Value).ToList();
                }

                return OperationResult<List<DebloatPreset>>.SuccessResult(presets);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get debloat presets");
                return OperationResult<List<DebloatPreset>>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult<DebloatPreset>> GetPresetAsync(
        string presetId,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                if (!_presets.TryGetValue(presetId, out var preset))
                {
                    return OperationResult<DebloatPreset>.FailureResult($"Preset not found: {presetId}");
                }

                return OperationResult<DebloatPreset>.SuccessResult(preset);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get debloat preset");
                return OperationResult<DebloatPreset>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult<DebloatAnalysis>> AnalyzeImpactAsync(
        ApplyDebloatRequest request,
        CancellationToken cancellationToken = default)
    {
        try
        {
            var preset = request.CustomPreset;
            if (preset == null && !string.IsNullOrEmpty(request.PresetId))
            {
                var presetResult = await GetPresetAsync(request.PresetId, cancellationToken);
                if (!presetResult.Success || presetResult.Data == null)
                {
                    return OperationResult<DebloatAnalysis>.FailureResult("Preset not found");
                }
                preset = presetResult.Data;
            }

            if (preset == null)
            {
                return OperationResult<DebloatAnalysis>.FailureResult("No preset specified");
            }

            var analysis = new DebloatAnalysis
            {
                TotalComponents = preset.Components.Count,
                EstimatedSpaceSavings = preset.EstimatedSpaceSavings * 1024 * 1024, // Convert MB to bytes
                ComponentsByType = preset.Components
                    .GroupBy(c => c.Type)
                    .ToDictionary(g => g.Key, g => g.Count())
            };

            // Analyze risks
            var unsafeComponents = preset.Components.Where(c => !c.SafeToRemove).ToList();
            if (unsafeComponents.Any())
            {
                analysis.Risks.Add($"{unsafeComponents.Count} components have potential risks");
                foreach (var component in unsafeComponents.Take(5))
                {
                    if (!string.IsNullOrEmpty(component.Warning))
                    {
                        analysis.Risks.Add($"{component.Name}: {component.Warning}");
                    }
                }
            }

            // Analyze affected features
            if (preset.Level == DebloatLevel.Aggressive)
            {
                analysis.AffectedFeatures.Add("Windows Store may have reduced functionality");
                analysis.AffectedFeatures.Add("Some UWP apps may not work correctly");
                analysis.AffectedFeatures.Add("Cortana and Search features will be limited");
            }
            else if (preset.Level == DebloatLevel.Moderate)
            {
                analysis.AffectedFeatures.Add("Some Microsoft apps will be removed");
                analysis.AffectedFeatures.Add("Xbox features may be limited");
            }

            // Generate recommendations
            analysis.Recommendations.Add("Test the debloated image thoroughly before deployment");
            analysis.Recommendations.Add("Keep a backup of the original image");

            if (preset.Level == DebloatLevel.Aggressive)
            {
                analysis.Recommendations.Add("Consider Moderate level for production environments");
            }

            _logger.LogInformation("Impact analysis complete: {Total} components, {Savings} MB estimated savings",
                analysis.TotalComponents, preset.EstimatedSpaceSavings);

            return OperationResult<DebloatAnalysis>.SuccessResult(analysis);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to analyze debloat impact");
            return OperationResult<DebloatAnalysis>.ExceptionResult(ex);
        }
    }

    public async Task<OperationResult<DebloatResult>> ApplyPresetAsync(
        ApplyDebloatRequest request,
        CancellationToken cancellationToken = default)
    {
        try
        {
            var result = new DebloatResult();

            // Get preset
            var preset = request.CustomPreset;
            if (preset == null && !string.IsNullOrEmpty(request.PresetId))
            {
                var presetResult = await GetPresetAsync(request.PresetId, cancellationToken);
                if (!presetResult.Success || presetResult.Data == null)
                {
                    return OperationResult<DebloatResult>.FailureResult("Preset not found");
                }
                preset = presetResult.Data;
            }

            if (preset == null)
            {
                return OperationResult<DebloatResult>.FailureResult("No preset specified");
            }

            _logger.LogInformation("Applying debloat preset '{PresetName}' to {MountPath}",
                preset.Name, request.MountPath);

            // Dry run analysis
            if (request.DryRun)
            {
                var analysisResult = await AnalyzeImpactAsync(request, cancellationToken);
                if (analysisResult.Success)
                {
                    result.Analysis = analysisResult.Data;
                }
                result.Success = true;
                result.Message = "Dry run completed - no changes made";
                return OperationResult<DebloatResult>.SuccessResult(result);
            }

            // Remove components
            if (preset.Components.Any())
            {
                var componentIds = preset.Components.Select(c => c.Id).ToList();
                var removeResult = await _componentService.RemoveComponentsAsync(
                    new ComponentOperationRequest
                    {
                        MountPath = request.MountPath,
                        ComponentIds = componentIds,
                        ResolveDependencies = true
                    },
                    cancellationToken);

                if (removeResult.Success && removeResult.Data != null)
                {
                    result.RemovedComponents = removeResult.Data.SuccessfulComponents;
                    result.FailedComponents = removeResult.Data.FailedComponents.Select(f => new DebloatError
                    {
                        ComponentId = f.ComponentId,
                        ErrorMessage = f.ErrorMessage,
                        CanContinue = true
                    }).ToList();
                }
            }

            // Apply registry tweaks
            if (preset.RegistryTweaks.Any())
            {
                var tweakPreset = new RegistryTweakPreset
                {
                    Name = $"{preset.Name} Registry Tweaks",
                    Description = "Registry tweaks from debloat preset",
                    Category = "Debloat",
                    Tweaks = preset.RegistryTweaks
                };

                var registryResult = await _registryService.ApplyTweakPresetAsync(
                    request.MountPath, tweakPreset, cancellationToken);

                if (registryResult.Success)
                {
                    result.RegistryTweaksApplied = preset.RegistryTweaks.Count;
                }
            }

            // Calculate space saved (estimate based on removed components)
            result.SpaceSaved = result.RemovedComponents.Count * 10 * 1024 * 1024; // Rough estimate: 10MB per component

            result.Success = result.RemovedComponents.Count > 0 || result.RegistryTweaksApplied > 0;
            result.Message = $"Debloat completed: {result.RemovedComponents.Count} components removed, {result.RegistryTweaksApplied} registry tweaks applied";

            // Add warnings
            if (preset.Level == DebloatLevel.Aggressive)
            {
                result.Warnings.Add("Aggressive debloat applied - some features may be affected");
            }

            if (result.FailedComponents.Any())
            {
                result.Warnings.Add($"{result.FailedComponents.Count} components failed to remove");
            }

            _logger.LogInformation("Debloat preset '{PresetName}' applied successfully. Removed: {Removed}, Failed: {Failed}",
                preset.Name, result.RemovedComponents.Count, result.FailedComponents.Count);

            return OperationResult<DebloatResult>.SuccessResult(result);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to apply debloat preset");
            return OperationResult<DebloatResult>.ExceptionResult(ex);
        }
    }

    #region Private Helper Methods

    private Dictionary<string, DebloatPreset> InitializePresets()
    {
        return new Dictionary<string, DebloatPreset>
        {
            ["conservative"] = new DebloatPreset
            {
                Id = "conservative",
                Name = "Conservative Debloat",
                Description = "Remove only obvious bloatware and unnecessary apps",
                Level = DebloatLevel.Conservative,
                EstimatedSpaceSavings = 500, // MB
                Components = new List<DebloatComponent>
                {
                    new() { Id = "Microsoft.BingWeather", Name = "Bing Weather", Type = ComponentType.AppPackage,
                        Reason = "Bloatware", SafeToRemove = true },
                    new() { Id = "Microsoft.BingNews", Name = "Bing News", Type = ComponentType.AppPackage,
                        Reason = "Bloatware", SafeToRemove = true },
                    new() { Id = "Microsoft.MicrosoftSolitaireCollection", Name = "Solitaire Collection", Type = ComponentType.AppPackage,
                        Reason = "Game bloatware", SafeToRemove = true },
                    new() { Id = "Microsoft.GetHelp", Name = "Get Help", Type = ComponentType.AppPackage,
                        Reason = "Unnecessary app", SafeToRemove = true },
                    new() { Id = "Microsoft.Getstarted", Name = "Get Started (Tips)", Type = ComponentType.AppPackage,
                        Reason = "Unnecessary app", SafeToRemove = true },
                    new() { Id = "Microsoft.Microsoft3DViewer", Name = "3D Viewer", Type = ComponentType.AppPackage,
                        Reason = "Rarely used", SafeToRemove = true },
                    new() { Id = "Microsoft.ZuneMusic", Name = "Groove Music", Type = ComponentType.AppPackage,
                        Reason = "Bloatware", SafeToRemove = true },
                    new() { Id = "Microsoft.ZuneVideo", Name = "Movies & TV", Type = ComponentType.AppPackage,
                        Reason = "Bloatware", SafeToRemove = true }
                }
            },

            ["moderate"] = new DebloatPreset
            {
                Id = "moderate",
                Name = "Moderate Debloat",
                Description = "Remove most unnecessary components and features",
                Level = DebloatLevel.Moderate,
                EstimatedSpaceSavings = 1200, // MB
                Components = new List<DebloatComponent>
                {
                    // Include all conservative components
                    new() { Id = "Microsoft.BingWeather", Name = "Bing Weather", Type = ComponentType.AppPackage,
                        Reason = "Bloatware", SafeToRemove = true },
                    new() { Id = "Microsoft.BingNews", Name = "Bing News", Type = ComponentType.AppPackage,
                        Reason = "Bloatware", SafeToRemove = true },
                    new() { Id = "Microsoft.MicrosoftSolitaireCollection", Name = "Solitaire Collection", Type = ComponentType.AppPackage,
                        Reason = "Game bloatware", SafeToRemove = true },
                    new() { Id = "Microsoft.GetHelp", Name = "Get Help", Type = ComponentType.AppPackage,
                        Reason = "Unnecessary app", SafeToRemove = true },
                    new() { Id = "Microsoft.Getstarted", Name = "Get Started", Type = ComponentType.AppPackage,
                        Reason = "Unnecessary app", SafeToRemove = true },
                    new() { Id = "Microsoft.Microsoft3DViewer", Name = "3D Viewer", Type = ComponentType.AppPackage,
                        Reason = "Rarely used", SafeToRemove = true },
                    new() { Id = "Microsoft.ZuneMusic", Name = "Groove Music", Type = ComponentType.AppPackage,
                        Reason = "Bloatware", SafeToRemove = true },
                    new() { Id = "Microsoft.ZuneVideo", Name = "Movies & TV", Type = ComponentType.AppPackage,
                        Reason = "Bloatware", SafeToRemove = true },
                    // Additional moderate removals
                    new() { Id = "Microsoft.People", Name = "People", Type = ComponentType.AppPackage,
                        Reason = "Rarely used", SafeToRemove = true },
                    new() { Id = "Microsoft.MicrosoftOfficeHub", Name = "Office Hub", Type = ComponentType.AppPackage,
                        Reason = "Promotional app", SafeToRemove = true },
                    new() { Id = "Microsoft.SkypeApp", Name = "Skype", Type = ComponentType.AppPackage,
                        Reason = "Bloatware", SafeToRemove = true },
                    new() { Id = "Microsoft.WindowsFeedbackHub", Name = "Feedback Hub", Type = ComponentType.AppPackage,
                        Reason = "Telemetry app", SafeToRemove = true },
                    new() { Id = "Microsoft.Xbox.TCUI", Name = "Xbox TCUI", Type = ComponentType.AppPackage,
                        Reason = "Xbox component", SafeToRemove = true },
                    new() { Id = "Microsoft.XboxGameOverlay", Name = "Xbox Game Overlay", Type = ComponentType.AppPackage,
                        Reason = "Xbox component", SafeToRemove = true },
                    new() { Id = "Microsoft.XboxGamingOverlay", Name = "Xbox Gaming Overlay", Type = ComponentType.AppPackage,
                        Reason = "Xbox component", SafeToRemove = true }
                },
                RegistryTweaks = new List<RegistryTweak>
                {
                    new() { HiveType = RegistryHiveType.Software, KeyPath = "Policies\\Microsoft\\Windows\\DataCollection",
                        ValueName = "AllowTelemetry", ValueType = RegistryValueType.DWord, Data = 0,
                        Description = "Disable telemetry" }
                }
            },

            ["aggressive"] = new DebloatPreset
            {
                Id = "aggressive",
                Name = "Aggressive Debloat",
                Description = "Maximum debloating - may affect some features",
                Level = DebloatLevel.Aggressive,
                EstimatedSpaceSavings = 2500, // MB
                Components = new List<DebloatComponent>
                {
                    // All moderate components plus aggressive removals
                    new() { Id = "Microsoft.BingWeather", Name = "Bing Weather", Type = ComponentType.AppPackage,
                        Reason = "Bloatware", SafeToRemove = true },
                    new() { Id = "Microsoft.BingNews", Name = "Bing News", Type = ComponentType.AppPackage,
                        Reason = "Bloatware", SafeToRemove = true },
                    new() { Id = "Microsoft.MicrosoftSolitaireCollection", Name = "Solitaire", Type = ComponentType.AppPackage,
                        Reason = "Game bloatware", SafeToRemove = true },
                    new() { Id = "Microsoft.GetHelp", Name = "Get Help", Type = ComponentType.AppPackage,
                        Reason = "Unnecessary", SafeToRemove = true },
                    new() { Id = "Microsoft.Getstarted", Name = "Get Started", Type = ComponentType.AppPackage,
                        Reason = "Unnecessary", SafeToRemove = true },
                    new() { Id = "Microsoft.Microsoft3DViewer", Name = "3D Viewer", Type = ComponentType.AppPackage,
                        Reason = "Rarely used", SafeToRemove = true },
                    new() { Id = "Microsoft.ZuneMusic", Name = "Groove Music", Type = ComponentType.AppPackage,
                        Reason = "Bloatware", SafeToRemove = true },
                    new() { Id = "Microsoft.ZuneVideo", Name = "Movies & TV", Type = ComponentType.AppPackage,
                        Reason = "Bloatware", SafeToRemove = true },
                    new() { Id = "Microsoft.People", Name = "People", Type = ComponentType.AppPackage,
                        Reason = "Rarely used", SafeToRemove = true },
                    new() { Id = "Microsoft.MicrosoftOfficeHub", Name = "Office Hub", Type = ComponentType.AppPackage,
                        Reason = "Promotional", SafeToRemove = true },
                    new() { Id = "Microsoft.SkypeApp", Name = "Skype", Type = ComponentType.AppPackage,
                        Reason = "Bloatware", SafeToRemove = true },
                    new() { Id = "Microsoft.WindowsFeedbackHub", Name = "Feedback Hub", Type = ComponentType.AppPackage,
                        Reason = "Telemetry", SafeToRemove = true },
                    new() { Id = "Microsoft.Xbox.TCUI", Name = "Xbox TCUI", Type = ComponentType.AppPackage,
                        Reason = "Xbox component", SafeToRemove = true },
                    new() { Id = "Microsoft.XboxGameOverlay", Name = "Xbox Game Overlay", Type = ComponentType.AppPackage,
                        Reason = "Xbox component", SafeToRemove = true },
                    new() { Id = "Microsoft.XboxGamingOverlay", Name = "Xbox Gaming Overlay", Type = ComponentType.AppPackage,
                        Reason = "Xbox component", SafeToRemove = true },
                    // Aggressive additions
                    new() { Id = "Microsoft.WindowsMaps", Name = "Maps", Type = ComponentType.AppPackage,
                        Reason = "Rarely used", SafeToRemove = true },
                    new() { Id = "Microsoft.YourPhone", Name = "Your Phone", Type = ComponentType.AppPackage,
                        Reason = "Phone companion", SafeToRemove = true },
                    new() { Id = "Microsoft.WindowsSoundRecorder", Name = "Sound Recorder", Type = ComponentType.AppPackage,
                        Reason = "Rarely used", SafeToRemove = true },
                    new() { Id = "Microsoft.WindowsAlarms", Name = "Alarms & Clock", Type = ComponentType.AppPackage,
                        Reason = "Rarely used on desktop", SafeToRemove = true },
                    new() { Id = "Microsoft.WindowsCamera", Name = "Camera", Type = ComponentType.AppPackage,
                        Reason = "Rarely used on desktop", SafeToRemove = true,
                        Warning = "May affect apps that use camera" },
                    new() { Id = "OneDrive", Name = "OneDrive", Type = ComponentType.Feature,
                        Reason = "Cloud storage", SafeToRemove = false,
                        Warning = "Removal may affect file sync and backup" }
                },
                RegistryTweaks = new List<RegistryTweak>
                {
                    new() { HiveType = RegistryHiveType.Software, KeyPath = "Policies\\Microsoft\\Windows\\DataCollection",
                        ValueName = "AllowTelemetry", ValueType = RegistryValueType.DWord, Data = 0,
                        Description = "Disable telemetry" },
                    new() { HiveType = RegistryHiveType.Software, KeyPath = "Policies\\Microsoft\\Windows\\DataCollection",
                        ValueName = "DoNotShowFeedbackNotifications", ValueType = RegistryValueType.DWord, Data = 1,
                        Description = "Disable feedback notifications" },
                    new() { HiveType = RegistryHiveType.Software, KeyPath = "Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
                        ValueName = "ShowSyncProviderNotifications", ValueType = RegistryValueType.DWord, Data = 0,
                        Description = "Disable OneDrive notifications" }
                }
            }
        };
    }

    #endregion
}
