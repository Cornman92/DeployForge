using DeployForge.Common.Models;
using DeployForge.Core.Interfaces;
using DeployForge.DismEngine;
using Microsoft.Dism;
using System.Runtime.Versioning;

namespace DeployForge.Core.Services;

/// <summary>
/// Service for managing Windows components
/// </summary>
[SupportedOSPlatform("windows")]
public class ComponentService : IComponentService
{
    private readonly DismManager _dismManager;
    private readonly ILogger<ComponentService> _logger;
    private static readonly Dictionary<string, string> ComponentCategories = InitializeCategories();

    public ComponentService(DismManager dismManager, ILogger<ComponentService> logger)
    {
        _dismManager = dismManager;
        _logger = logger;
    }

    public async Task<OperationResult<List<ComponentInfo>>> GetComponentsAsync(
        string mountPath,
        ComponentType? type = null,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                var components = new List<ComponentInfo>();

                // Get packages if requested or no filter
                if (type == null || type == ComponentType.Package)
                {
                    var packagesResult = _dismManager.GetPackages(mountPath);
                    if (packagesResult.Success && packagesResult.Data != null)
                    {
                        components.AddRange(MapPackagesToComponents(packagesResult.Data));
                    }
                }

                // Get features if requested or no filter
                if (type == null || type == ComponentType.Feature)
                {
                    var featuresResult = _dismManager.GetFeatures(mountPath);
                    if (featuresResult.Success && featuresResult.Data != null)
                    {
                        components.AddRange(MapFeaturesToComponents(featuresResult.Data));
                    }
                }

                // Get capabilities if requested or no filter
                if (type == null || type == ComponentType.Capability)
                {
                    var capabilitiesResult = _dismManager.GetCapabilities(mountPath);
                    if (capabilitiesResult.Success && capabilitiesResult.Data != null)
                    {
                        components.AddRange(MapCapabilitiesToComponents(capabilitiesResult.Data));
                    }
                }

                // Get app packages if requested or no filter
                if (type == null || type == ComponentType.AppPackage)
                {
                    var appsResult = _dismManager.GetProvisionedAppPackages(mountPath);
                    if (appsResult.Success && appsResult.Data != null)
                    {
                        components.AddRange(MapAppPackagesToComponents(appsResult.Data));
                    }
                }

                return OperationResult<List<ComponentInfo>>.SuccessResult(components);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get components from {MountPath}", mountPath);
                return OperationResult<List<ComponentInfo>>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult<ComponentInfo>> GetComponentInfoAsync(
        string mountPath,
        string componentId,
        ComponentType type,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                ComponentInfo? component = null;

                switch (type)
                {
                    case ComponentType.Package:
                        var pkgResult = _dismManager.GetPackageInfo(mountPath, componentId);
                        if (pkgResult.Success && pkgResult.Data != null)
                        {
                            component = MapPackageInfoToComponent(pkgResult.Data);
                        }
                        break;

                    case ComponentType.Feature:
                        var featResult = _dismManager.GetFeatureInfo(mountPath, componentId);
                        if (featResult.Success && featResult.Data != null)
                        {
                            component = MapFeatureInfoToComponent(featResult.Data);
                        }
                        break;

                    case ComponentType.Capability:
                        var capResult = _dismManager.GetCapabilityInfo(mountPath, componentId);
                        if (capResult.Success && capResult.Data != null)
                        {
                            component = MapCapabilityInfoToComponent(capResult.Data);
                        }
                        break;

                    case ComponentType.AppPackage:
                        // App packages don't have individual info method, get from list
                        var appsResult = _dismManager.GetProvisionedAppPackages(mountPath);
                        if (appsResult.Success && appsResult.Data != null)
                        {
                            var app = appsResult.Data.FirstOrDefault(a => a.PackageName == componentId);
                            if (app != null)
                            {
                                component = MapAppPackageToComponent(app);
                            }
                        }
                        break;
                }

                if (component == null)
                {
                    return OperationResult<ComponentInfo>.FailureResult($"Component {componentId} not found");
                }

                return OperationResult<ComponentInfo>.SuccessResult(component);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get component info for {ComponentId}", componentId);
                return OperationResult<ComponentInfo>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult<ComponentOperationResult>> RemoveComponentsAsync(
        ComponentOperationRequest request,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            var result = new ComponentOperationResult();
            var successful = new List<string>();
            var failed = new List<ComponentOperationError>();

            try
            {
                foreach (var componentId in request.ComponentIds)
                {
                    if (cancellationToken.IsCancellationRequested)
                        break;

                    OperationResult removeResult;

                    // Determine component type and remove appropriately
                    var componentType = DetermineComponentType(componentId);

                    removeResult = componentType switch
                    {
                        ComponentType.Package => _dismManager.RemovePackage(request.MountPath, componentId),
                        ComponentType.Feature => _dismManager.DisableFeature(request.MountPath, componentId, null, true),
                        ComponentType.Capability => _dismManager.RemoveCapability(request.MountPath, componentId),
                        ComponentType.AppPackage => _dismManager.RemoveProvisionedAppPackage(request.MountPath, componentId),
                        _ => OperationResult.FailureResult("Unknown component type")
                    };

                    if (removeResult.Success)
                    {
                        successful.Add(componentId);
                        _logger.LogInformation("Successfully removed component {ComponentId}", componentId);
                    }
                    else
                    {
                        failed.Add(new ComponentOperationError
                        {
                            ComponentId = componentId,
                            ErrorMessage = removeResult.ErrorMessage ?? "Unknown error"
                        });
                        _logger.LogWarning("Failed to remove component {ComponentId}: {Error}",
                            componentId, removeResult.ErrorMessage);
                    }
                }

                result.SuccessfulComponents = successful;
                result.FailedComponents = failed;
                result.Success = successful.Count > 0;
                result.RestartRequired = true;
                result.Message = $"Removed {successful.Count} of {request.ComponentIds.Count} components";

                return OperationResult<ComponentOperationResult>.SuccessResult(result);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to remove components");
                return OperationResult<ComponentOperationResult>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult<ComponentOperationResult>> AddComponentsAsync(
        ComponentOperationRequest request,
        List<string> packagePaths,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            var result = new ComponentOperationResult();
            var successful = new List<string>();
            var failed = new List<ComponentOperationError>();

            try
            {
                foreach (var packagePath in packagePaths)
                {
                    if (cancellationToken.IsCancellationRequested)
                        break;

                    var addResult = _dismManager.AddPackage(request.MountPath, packagePath);

                    if (addResult.Success)
                    {
                        successful.Add(Path.GetFileName(packagePath));
                        _logger.LogInformation("Successfully added package {PackagePath}", packagePath);
                    }
                    else
                    {
                        failed.Add(new ComponentOperationError
                        {
                            ComponentId = Path.GetFileName(packagePath),
                            ErrorMessage = addResult.ErrorMessage ?? "Unknown error"
                        });
                        _logger.LogWarning("Failed to add package {PackagePath}: {Error}",
                            packagePath, addResult.ErrorMessage);
                    }
                }

                result.SuccessfulComponents = successful;
                result.FailedComponents = failed;
                result.Success = successful.Count > 0;
                result.RestartRequired = true;
                result.Message = $"Added {successful.Count} of {packagePaths.Count} packages";

                return OperationResult<ComponentOperationResult>.SuccessResult(result);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to add components");
                return OperationResult<ComponentOperationResult>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult<ComponentOperationResult>> ToggleFeaturesAsync(
        ComponentOperationRequest request,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            var result = new ComponentOperationResult();
            var successful = new List<string>();
            var failed = new List<ComponentOperationError>();

            try
            {
                foreach (var featureName in request.ComponentIds)
                {
                    if (cancellationToken.IsCancellationRequested)
                        break;

                    OperationResult toggleResult = request.Operation == ComponentOperation.Enable
                        ? _dismManager.EnableFeature(request.MountPath, featureName)
                        : _dismManager.DisableFeature(request.MountPath, featureName);

                    if (toggleResult.Success)
                    {
                        successful.Add(featureName);
                        _logger.LogInformation("Successfully toggled feature {FeatureName}", featureName);
                    }
                    else
                    {
                        failed.Add(new ComponentOperationError
                        {
                            ComponentId = featureName,
                            ErrorMessage = toggleResult.ErrorMessage ?? "Unknown error"
                        });
                        _logger.LogWarning("Failed to toggle feature {FeatureName}: {Error}",
                            featureName, toggleResult.ErrorMessage);
                    }
                }

                result.SuccessfulComponents = successful;
                result.FailedComponents = failed;
                result.Success = successful.Count > 0;
                result.RestartRequired = true;
                result.Message = $"Toggled {successful.Count} of {request.ComponentIds.Count} features";

                return OperationResult<ComponentOperationResult>.SuccessResult(result);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to toggle features");
                return OperationResult<ComponentOperationResult>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult<ComponentDependencyGraph>> AnalyzeDependenciesAsync(
        string mountPath,
        List<string> componentIds,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                var graph = new ComponentDependencyGraph();
                // This is a simplified implementation
                // In a production system, this would analyze actual dependencies from DISM

                _logger.LogInformation("Analyzing dependencies for {Count} components", componentIds.Count);

                // For now, return a basic graph structure
                return OperationResult<ComponentDependencyGraph>.SuccessResult(graph);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to analyze dependencies");
                return OperationResult<ComponentDependencyGraph>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult<List<ComponentInfo>>> GetComponentsByCategoryAsync(
        string mountPath,
        string category,
        CancellationToken cancellationToken = default)
    {
        var allComponentsResult = await GetComponentsAsync(mountPath, null, cancellationToken);

        if (!allComponentsResult.Success || allComponentsResult.Data == null)
        {
            return allComponentsResult;
        }

        var filtered = allComponentsResult.Data
            .Where(c => c.Category.Equals(category, StringComparison.OrdinalIgnoreCase))
            .ToList();

        return OperationResult<List<ComponentInfo>>.SuccessResult(filtered);
    }

    #region Private Helper Methods

    private static Dictionary<string, string> InitializeCategories()
    {
        return new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
        {
            // Bloatware
            { "Microsoft.BingWeather", "Bloatware" },
            { "Microsoft.BingNews", "Bloatware" },
            { "Microsoft.GetHelp", "Bloatware" },
            { "Microsoft.Getstarted", "Bloatware" },
            { "Microsoft.Microsoft3DViewer", "Bloatware" },
            { "Microsoft.MicrosoftOfficeHub", "Bloatware" },
            { "Microsoft.MicrosoftSolitaireCollection", "Bloatware" },
            { "Microsoft.People", "Bloatware" },
            { "Microsoft.SkypeApp", "Bloatware" },
            { "Microsoft.WindowsFeedbackHub", "Bloatware" },
            { "Microsoft.Xbox", "Bloatware" },
            { "Microsoft.XboxGameOverlay", "Bloatware" },
            { "Microsoft.XboxGamingOverlay", "Bloatware" },
            { "Microsoft.XboxIdentityProvider", "Bloatware" },
            { "Microsoft.XboxSpeechToTextOverlay", "Bloatware" },
            { "Microsoft.ZuneMusic", "Bloatware" },
            { "Microsoft.ZuneVideo", "Bloatware" },

            // Media
            { "WindowsMediaPlayer", "Media" },
            { "MediaPlayback", "Media" },

            // Networking
            { "SMB", "Networking" },
            { "NetFx", "Networking" },
            { "SNMP", "Networking" },

            // Core
            { "Foundation", "Core" },
            { "Kernel", "Core" },
            { "Security", "Core" },
        };
    }

    private List<ComponentInfo> MapPackagesToComponents(DismPackageCollection packages)
    {
        return packages.Select(p => new ComponentInfo
        {
            Id = p.PackageName,
            Name = p.PackageName,
            Type = ComponentType.Package,
            State = MapPackageState(p.PackageState),
            Version = p.PackageState.ToString(),
            Description = p.PackageName,
            InstallDate = p.InstallTime == DateTime.MinValue ? null : p.InstallTime,
            IsRemovable = p.PackageState != DismPackageFeatureState.NotPresent,
            Category = DetermineCategory(p.PackageName),
            RestartRequired = p.RestartRequired == DismRestartType.Required
        }).ToList();
    }

    private ComponentInfo MapPackageInfoToComponent(DismPackageInfo package)
    {
        return new ComponentInfo
        {
            Id = package.PackageName,
            Name = package.PackageName,
            Type = ComponentType.Package,
            State = MapPackageState(package.PackageState),
            Version = package.PackageName,
            Description = package.Description ?? package.PackageName,
            InstallDate = package.InstallTime == DateTime.MinValue ? null : package.InstallTime,
            IsRemovable = package.PackageState != DismPackageFeatureState.NotPresent,
            Category = DetermineCategory(package.PackageName),
            RestartRequired = package.RestartRequired == DismRestartType.Required
        };
    }

    private List<ComponentInfo> MapFeaturesToComponents(DismFeatureCollection features)
    {
        return features.Select(f => new ComponentInfo
        {
            Id = f.FeatureName,
            Name = f.FeatureName,
            Type = ComponentType.Feature,
            State = MapFeatureState(f.State),
            Description = f.FeatureName,
            IsRemovable = f.State != DismPackageFeatureState.NotPresent,
            Category = DetermineCategory(f.FeatureName)
        }).ToList();
    }

    private ComponentInfo MapFeatureInfoToComponent(DismFeatureInfo feature)
    {
        return new ComponentInfo
        {
            Id = feature.FeatureName,
            Name = feature.FeatureName,
            Type = ComponentType.Feature,
            State = MapFeatureState(feature.FeatureState),
            Description = feature.Description ?? feature.FeatureName,
            IsRemovable = feature.FeatureState != DismPackageFeatureState.NotPresent,
            Category = DetermineCategory(feature.FeatureName),
            RestartRequired = feature.RestartRequired == DismRestartType.Required
        };
    }

    private List<ComponentInfo> MapCapabilitiesToComponents(DismCapabilityCollection capabilities)
    {
        return capabilities.Select(c => new ComponentInfo
        {
            Id = c.Name,
            Name = c.Name,
            Type = ComponentType.Capability,
            State = MapCapabilityState(c.State),
            Description = c.Name,
            IsRemovable = c.State != DismPackageFeatureState.NotPresent,
            Category = DetermineCategory(c.Name)
        }).ToList();
    }

    private ComponentInfo MapCapabilityInfoToComponent(DismCapabilityInfo capability)
    {
        return new ComponentInfo
        {
            Id = capability.Name,
            Name = capability.Name,
            Type = ComponentType.Capability,
            State = MapCapabilityState(capability.State),
            Description = capability.Description ?? capability.Name,
            IsRemovable = capability.State != DismPackageFeatureState.NotPresent,
            Category = DetermineCategory(capability.Name)
        };
    }

    private List<ComponentInfo> MapAppPackagesToComponents(DismAppxPackageCollection apps)
    {
        return apps.Select(a => MapAppPackageToComponent(a)).ToList();
    }

    private ComponentInfo MapAppPackageToComponent(DismAppxPackage app)
    {
        return new ComponentInfo
        {
            Id = app.PackageName,
            Name = app.DisplayName ?? app.PackageName,
            Type = ComponentType.AppPackage,
            State = ComponentState.Enabled,
            Version = app.Version?.ToString() ?? "Unknown",
            Description = app.PackageName,
            Publisher = app.PublisherId ?? "Unknown",
            IsRemovable = true,
            Category = DetermineCategory(app.PackageName)
        };
    }

    private ComponentState MapPackageState(DismPackageFeatureState state)
    {
        return state switch
        {
            DismPackageFeatureState.Installed => ComponentState.Enabled,
            DismPackageFeatureState.Staged => ComponentState.Staged,
            DismPackageFeatureState.Removed => ComponentState.NotPresent,
            DismPackageFeatureState.NotPresent => ComponentState.NotPresent,
            DismPackageFeatureState.Superseded => ComponentState.Superseded,
            DismPackageFeatureState.InstallPending => ComponentState.InstallPending,
            DismPackageFeatureState.UninstallPending => ComponentState.UninstallPending,
            _ => ComponentState.NotPresent
        };
    }

    private ComponentState MapFeatureState(DismPackageFeatureState state)
    {
        return state switch
        {
            DismPackageFeatureState.Enabled => ComponentState.Enabled,
            DismPackageFeatureState.Disabled => ComponentState.Disabled,
            DismPackageFeatureState.DisabledWithPayloadRemoved => ComponentState.NotPresent,
            DismPackageFeatureState.Staged => ComponentState.Staged,
            DismPackageFeatureState.Superseded => ComponentState.Superseded,
            DismPackageFeatureState.InstallPending => ComponentState.InstallPending,
            DismPackageFeatureState.UninstallPending => ComponentState.UninstallPending,
            _ => ComponentState.NotPresent
        };
    }

    private ComponentState MapCapabilityState(DismPackageFeatureState state)
    {
        return state switch
        {
            DismPackageFeatureState.Installed => ComponentState.Enabled,
            DismPackageFeatureState.Staged => ComponentState.Staged,
            DismPackageFeatureState.NotPresent => ComponentState.NotPresent,
            DismPackageFeatureState.InstallPending => ComponentState.InstallPending,
            DismPackageFeatureState.UninstallPending => ComponentState.UninstallPending,
            _ => ComponentState.NotPresent
        };
    }

    private string DetermineCategory(string componentName)
    {
        foreach (var kvp in ComponentCategories)
        {
            if (componentName.Contains(kvp.Key, StringComparison.OrdinalIgnoreCase))
            {
                return kvp.Value;
            }
        }
        return "Other";
    }

    private ComponentType DetermineComponentType(string componentId)
    {
        // Simple heuristic - can be improved
        if (componentId.Contains("Package-") || componentId.EndsWith(".cab") || componentId.EndsWith(".msu"))
            return ComponentType.Package;
        if (componentId.StartsWith("Microsoft.") && componentId.Contains("_"))
            return ComponentType.AppPackage;
        if (componentId.Contains("Capability"))
            return ComponentType.Capability;

        return ComponentType.Feature;
    }

    #endregion
}
