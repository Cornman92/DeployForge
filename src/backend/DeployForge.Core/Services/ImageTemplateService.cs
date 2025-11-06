using DeployForge.Common.Models;
using DeployForge.Core.Interfaces;
using System.IO;
using System.Text.Json;
using System.Runtime.Versioning;

namespace DeployForge.Core.Services;

/// <summary>
/// Image template service implementation
/// </summary>
[SupportedOSPlatform("windows")]
public class ImageTemplateService : IImageTemplateService
{
    private readonly ILogger<ImageTemplateService> _logger;
    private readonly string _templatesPath;
    private readonly JsonSerializerOptions _jsonOptions;
    private readonly IComponentService _componentService;
    private readonly IDebloatService _debloatService;
    private readonly IUpdateService _updateService;
    private readonly IRegistryService _registryService;
    private readonly ILanguageService _languageService;

    public ImageTemplateService(
        ILogger<ImageTemplateService> logger,
        IComponentService componentService,
        IDebloatService debloatService,
        IUpdateService updateService,
        IRegistryService registryService,
        ILanguageService languageService)
    {
        _logger = logger;
        _componentService = componentService;
        _debloatService = debloatService;
        _updateService = updateService;
        _registryService = registryService;
        _languageService = languageService;

        var appDataPath = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
        _templatesPath = Path.Combine(appDataPath, "DeployForge", "Templates");
        Directory.CreateDirectory(_templatesPath);

        _jsonOptions = new JsonSerializerOptions
        {
            WriteIndented = true,
            PropertyNameCaseInsensitive = true
        };

        // Initialize predefined templates
        _ = InitializePredefinedTemplatesAsync();
    }

    public async Task<OperationResult<List<ImageTemplate>>> GetTemplatesAsync(string? tag = null, CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                var templates = new List<ImageTemplate>();
                var files = Directory.GetFiles(_templatesPath, "*.json");

                foreach (var file in files)
                {
                    var json = File.ReadAllText(file);
                    var template = JsonSerializer.Deserialize<ImageTemplate>(json, _jsonOptions);

                    if (template != null)
                    {
                        if (string.IsNullOrEmpty(tag) || template.Tags.Contains(tag, StringComparer.OrdinalIgnoreCase))
                        {
                            templates.Add(template);
                        }
                    }
                }

                return OperationResult<List<ImageTemplate>>.SuccessResult(
                    templates.OrderBy(t => t.Name).ToList());
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get templates");
                return OperationResult<List<ImageTemplate>>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult<ImageTemplate>> GetTemplateAsync(string templateId, CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                var filePath = Path.Combine(_templatesPath, $"{templateId}.json");

                if (!File.Exists(filePath))
                {
                    return OperationResult<ImageTemplate>.FailureResult($"Template not found: {templateId}");
                }

                var json = File.ReadAllText(filePath);
                var template = JsonSerializer.Deserialize<ImageTemplate>(json, _jsonOptions);

                if (template == null)
                {
                    return OperationResult<ImageTemplate>.FailureResult("Failed to deserialize template");
                }

                return OperationResult<ImageTemplate>.SuccessResult(template);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get template {TemplateId}", templateId);
                return OperationResult<ImageTemplate>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult<ImageTemplate>> CreateTemplateAsync(ImageTemplate template, CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                template.Id = Guid.NewGuid().ToString();
                template.CreatedDate = DateTime.UtcNow;
                template.ModifiedDate = DateTime.UtcNow;

                var filePath = Path.Combine(_templatesPath, $"{template.Id}.json");
                var json = JsonSerializer.Serialize(template, _jsonOptions);
                File.WriteAllText(filePath, json);

                _logger.LogInformation("Created template {TemplateId}: {TemplateName}", template.Id, template.Name);

                return OperationResult<ImageTemplate>.SuccessResult(template);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to create template");
                return OperationResult<ImageTemplate>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult<ImageTemplate>> UpdateTemplateAsync(ImageTemplate template, CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                var filePath = Path.Combine(_templatesPath, $"{template.Id}.json");

                if (!File.Exists(filePath))
                {
                    return OperationResult<ImageTemplate>.FailureResult($"Template not found: {template.Id}");
                }

                template.ModifiedDate = DateTime.UtcNow;

                var json = JsonSerializer.Serialize(template, _jsonOptions);
                File.WriteAllText(filePath, json);

                _logger.LogInformation("Updated template {TemplateId}", template.Id);

                return OperationResult<ImageTemplate>.SuccessResult(template);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to update template");
                return OperationResult<ImageTemplate>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult> DeleteTemplateAsync(string templateId, CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                var filePath = Path.Combine(_templatesPath, $"{templateId}.json");

                if (!File.Exists(filePath))
                {
                    return OperationResult.FailureResult($"Template not found: {templateId}");
                }

                File.Delete(filePath);
                _logger.LogInformation("Deleted template {TemplateId}", templateId);

                return OperationResult.SuccessResult();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to delete template {TemplateId}", templateId);
                return OperationResult.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult<ApplyTemplateResult>> ApplyTemplateAsync(ApplyTemplateRequest request, CancellationToken cancellationToken = default)
    {
        var startTime = DateTime.UtcNow;
        var result = new ApplyTemplateResult();

        try
        {
            _logger.LogInformation("Applying template {TemplateId} to image {ImagePath}",
                request.TemplateId, request.ImagePath);

            // Get template
            var templateResult = await GetTemplateAsync(request.TemplateId, cancellationToken);
            if (!templateResult.Success || templateResult.Data == null)
            {
                return OperationResult<ApplyTemplateResult>.FailureResult(
                    templateResult.ErrorMessage ?? "Failed to load template");
            }

            var template = templateResult.Data;

            // Apply debloat configuration
            if (template.Debloat != null)
            {
                try
                {
                    var debloatResult = await _debloatService.ApplyPresetAsync(new ApplyDebloatRequest
                    {
                        MountPath = request.MountPath,
                        PresetId = template.Debloat.PresetId,
                        DryRun = request.DryRun
                    }, cancellationToken);

                    if (debloatResult.Success)
                    {
                        result.AppliedSteps.Add("Debloat configuration applied");
                    }
                    else
                    {
                        result.FailedSteps.Add($"Debloat failed: {debloatResult.ErrorMessage}");
                    }
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, "Failed to apply debloat configuration");
                    result.FailedSteps.Add($"Debloat error: {ex.Message}");
                }
            }

            // Apply component configuration
            if (template.Components != null)
            {
                if (template.Components.ComponentsToRemove.Any())
                {
                    try
                    {
                        var componentResult = await _componentService.RemoveComponentsAsync(new ComponentOperationRequest
                        {
                            MountPath = request.MountPath,
                            ComponentIds = template.Components.ComponentsToRemove
                        }, cancellationToken);

                        if (componentResult.Success)
                        {
                            result.AppliedSteps.Add("Components removed");
                        }
                        else
                        {
                            result.FailedSteps.Add($"Component removal failed: {componentResult.ErrorMessage}");
                        }
                    }
                    catch (Exception ex)
                    {
                        result.FailedSteps.Add($"Component removal error: {ex.Message}");
                    }
                }
            }

            // Apply update configuration
            if (template.Updates != null && template.Updates.UpdatePaths.Any())
            {
                try
                {
                    var updateResult = await _updateService.InstallUpdatesAsync(new UpdateOperationRequest
                    {
                        MountPath = request.MountPath,
                        UpdatePaths = template.Updates.UpdatePaths
                    }, cancellationToken);

                    if (updateResult.Success)
                    {
                        result.AppliedSteps.Add("Updates installed");
                    }
                    else
                    {
                        result.FailedSteps.Add($"Update installation failed: {updateResult.ErrorMessage}");
                    }
                }
                catch (Exception ex)
                {
                    result.FailedSteps.Add($"Update installation error: {ex.Message}");
                }
            }

            result.Duration = DateTime.UtcNow - startTime;
            result.Success = result.FailedSteps.Count == 0;
            result.Message = result.Success
                ? $"Template applied successfully. {result.AppliedSteps.Count} steps completed."
                : $"Template applied with errors. {result.AppliedSteps.Count} succeeded, {result.FailedSteps.Count} failed.";

            return OperationResult<ApplyTemplateResult>.SuccessResult(result);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to apply template");
            result.Duration = DateTime.UtcNow - startTime;
            result.Success = false;
            result.Message = ex.Message;
            return OperationResult<ApplyTemplateResult>.ExceptionResult(ex);
        }
    }

    public async Task<OperationResult<string>> ExportTemplateAsync(string templateId, string destinationPath, CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                var templateResult = GetTemplateAsync(templateId, cancellationToken).Result;
                if (!templateResult.Success || templateResult.Data == null)
                {
                    return OperationResult<string>.FailureResult("Template not found");
                }

                var json = JsonSerializer.Serialize(templateResult.Data, _jsonOptions);
                File.WriteAllText(destinationPath, json);

                _logger.LogInformation("Exported template {TemplateId} to {Path}", templateId, destinationPath);

                return OperationResult<string>.SuccessResult(destinationPath);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to export template");
                return OperationResult<string>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult<ImageTemplate>> ImportTemplateAsync(string filePath, CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                if (!File.Exists(filePath))
                {
                    return OperationResult<ImageTemplate>.FailureResult("File not found");
                }

                var json = File.ReadAllText(filePath);
                var template = JsonSerializer.Deserialize<ImageTemplate>(json, _jsonOptions);

                if (template == null)
                {
                    return OperationResult<ImageTemplate>.FailureResult("Failed to deserialize template");
                }

                // Generate new ID to avoid conflicts
                template.Id = Guid.NewGuid().ToString();

                return CreateTemplateAsync(template, cancellationToken).Result;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to import template");
                return OperationResult<ImageTemplate>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult<List<string>>> ValidateTemplateAsync(ImageTemplate template, CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            var errors = new List<string>();

            if (string.IsNullOrWhiteSpace(template.Name))
            {
                errors.Add("Template name is required");
            }

            if (string.IsNullOrWhiteSpace(template.Version))
            {
                errors.Add("Template version is required");
            }

            // Validate debloat configuration
            if (template.Debloat != null && string.IsNullOrWhiteSpace(template.Debloat.PresetId))
            {
                errors.Add("Debloat preset ID is required");
            }

            return OperationResult<List<string>>.SuccessResult(errors);
        }, cancellationToken);
    }

    public async Task<OperationResult<List<ImageTemplate>>> GetPredefinedTemplatesAsync(CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            var templates = new List<ImageTemplate>
            {
                new ImageTemplate
                {
                    Id = "gaming-edition-predefined",
                    Name = "Windows 11 Gaming Edition",
                    Description = "Optimized Windows 11 for gaming with bloatware removed and performance tweaks",
                    Author = "DeployForge Team",
                    Version = "1.0.0",
                    Tags = new List<string> { "gaming", "performance", "windows11" },
                    TargetVersions = new List<string> { "Windows 11" },
                    Debloat = new DebloatConfiguration
                    {
                        PresetId = "moderate",
                        AdditionalComponentsToRemove = new List<string> { "Microsoft.XboxGameOverlay" }
                    }
                },
                new ImageTemplate
                {
                    Id = "developer-workstation-predefined",
                    Name = "Developer Workstation",
                    Description = "Clean Windows installation optimized for development",
                    Author = "DeployForge Team",
                    Version = "1.0.0",
                    Tags = new List<string> { "development", "productivity" },
                    TargetVersions = new List<string> { "Windows 10", "Windows 11" },
                    Debloat = new DebloatConfiguration
                    {
                        PresetId = "moderate"
                    }
                },
                new ImageTemplate
                {
                    Id = "privacy-focused-predefined",
                    Name = "Privacy-Focused Windows",
                    Description = "Maximum privacy settings with telemetry disabled",
                    Author = "DeployForge Team",
                    Version = "1.0.0",
                    Tags = new List<string> { "privacy", "security" },
                    TargetVersions = new List<string> { "Windows 10", "Windows 11" },
                    Debloat = new DebloatConfiguration
                    {
                        PresetId = "aggressive"
                    }
                }
            };

            return OperationResult<List<ImageTemplate>>.SuccessResult(templates);
        }, cancellationToken);
    }

    private async Task InitializePredefinedTemplatesAsync()
    {
        try
        {
            var predefined = await GetPredefinedTemplatesAsync();
            if (predefined.Success && predefined.Data != null)
            {
                foreach (var template in predefined.Data)
                {
                    var exists = File.Exists(Path.Combine(_templatesPath, $"{template.Id}.json"));
                    if (!exists)
                    {
                        await CreateTemplateAsync(template);
                    }
                }
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to initialize predefined templates");
        }
    }
}
