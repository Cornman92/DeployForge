using System.Text.Json;
using DeployForge.Common.Models;
using DeployForge.Core.Interfaces;
using Microsoft.Extensions.Logging;

namespace DeployForge.Core.Services;

/// <summary>
/// Service for managing user configuration profiles
/// </summary>
public class ConfigurationProfileService : IConfigurationProfileService
{
    private readonly ILogger<ConfigurationProfileService> _logger;
    private readonly string _profilesDirectory;
    private readonly JsonSerializerOptions _jsonOptions;

    public ConfigurationProfileService(ILogger<ConfigurationProfileService> logger)
    {
        _logger = logger;

        // Store profiles in AppData\DeployForge\Profiles
        var appDataPath = Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData);
        _profilesDirectory = Path.Combine(appDataPath, "DeployForge", "Profiles");

        // Ensure directory exists
        Directory.CreateDirectory(_profilesDirectory);

        _jsonOptions = new JsonSerializerOptions
        {
            WriteIndented = true,
            PropertyNameCaseInsensitive = true
        };

        _logger.LogInformation("Configuration profile service initialized with storage at: {Path}", _profilesDirectory);
    }

    public async Task<OperationResult<List<ConfigurationProfile>>> GetProfilesAsync(
        bool includeShared = true,
        string? tag = null,
        CancellationToken cancellationToken = default)
    {
        try
        {
            var profiles = new List<ConfigurationProfile>();
            var files = Directory.GetFiles(_profilesDirectory, "*.json");

            foreach (var file in files)
            {
                try
                {
                    var json = await File.ReadAllTextAsync(file, cancellationToken);
                    var profile = JsonSerializer.Deserialize<ConfigurationProfile>(json, _jsonOptions);

                    if (profile != null)
                    {
                        // Filter by shared status
                        if (!includeShared && profile.IsShared)
                            continue;

                        // Filter by tag
                        if (!string.IsNullOrEmpty(tag) && !profile.Tags.Contains(tag, StringComparer.OrdinalIgnoreCase))
                            continue;

                        profiles.Add(profile);
                    }
                }
                catch (Exception ex)
                {
                    _logger.LogWarning(ex, "Failed to load profile from {File}", file);
                }
            }

            _logger.LogInformation("Retrieved {Count} configuration profiles", profiles.Count);
            return OperationResult<List<ConfigurationProfile>>.SuccessResult(profiles);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to get configuration profiles");
            return OperationResult<List<ConfigurationProfile>>.FailureResult($"Failed to get profiles: {ex.Message}");
        }
    }

    public async Task<OperationResult<ConfigurationProfile>> GetProfileAsync(
        string profileId,
        CancellationToken cancellationToken = default)
    {
        try
        {
            var filePath = GetProfileFilePath(profileId);

            if (!File.Exists(filePath))
            {
                return OperationResult<ConfigurationProfile>.FailureResult($"Profile '{profileId}' not found");
            }

            var json = await File.ReadAllTextAsync(filePath, cancellationToken);
            var profile = JsonSerializer.Deserialize<ConfigurationProfile>(json, _jsonOptions);

            if (profile == null)
            {
                return OperationResult<ConfigurationProfile>.FailureResult("Failed to deserialize profile");
            }

            _logger.LogInformation("Retrieved profile: {ProfileId}", profileId);
            return OperationResult<ConfigurationProfile>.SuccessResult(profile);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to get profile {ProfileId}", profileId);
            return OperationResult<ConfigurationProfile>.FailureResult($"Failed to get profile: {ex.Message}");
        }
    }

    public async Task<OperationResult<ConfigurationProfile>> GetDefaultProfileAsync(
        CancellationToken cancellationToken = default)
    {
        try
        {
            var profilesResult = await GetProfilesAsync(true, null, cancellationToken);
            if (!profilesResult.Success || profilesResult.Data == null)
            {
                return await CreateDefaultProfileAsync(cancellationToken);
            }

            var defaultProfile = profilesResult.Data.FirstOrDefault(p => p.IsDefault);
            if (defaultProfile == null)
            {
                return await CreateDefaultProfileAsync(cancellationToken);
            }

            _logger.LogInformation("Retrieved default profile: {ProfileId}", defaultProfile.Id);
            return OperationResult<ConfigurationProfile>.SuccessResult(defaultProfile);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to get default profile");
            return OperationResult<ConfigurationProfile>.FailureResult($"Failed to get default profile: {ex.Message}");
        }
    }

    public async Task<OperationResult<ConfigurationProfile>> CreateProfileAsync(
        ConfigurationProfile profile,
        CancellationToken cancellationToken = default)
    {
        try
        {
            // Validate profile
            var validationResult = await ValidateProfileAsync(profile, cancellationToken);
            if (!validationResult.Success || (validationResult.Data?.Count ?? 0) > 0)
            {
                var errors = string.Join(", ", validationResult.Data ?? new List<string> { "Unknown validation error" });
                return OperationResult<ConfigurationProfile>.FailureResult($"Profile validation failed: {errors}");
            }

            // Ensure unique ID
            if (string.IsNullOrEmpty(profile.Id))
            {
                profile.Id = Guid.NewGuid().ToString();
            }

            // Check for duplicate
            var existingFilePath = GetProfileFilePath(profile.Id);
            if (File.Exists(existingFilePath))
            {
                return OperationResult<ConfigurationProfile>.FailureResult($"Profile with ID '{profile.Id}' already exists");
            }

            // If this is set as default, unset others
            if (profile.IsDefault)
            {
                await UnsetAllDefaultProfilesAsync(cancellationToken);
            }

            // Set timestamps
            profile.CreatedAt = DateTime.UtcNow;
            profile.ModifiedAt = DateTime.UtcNow;

            // Save profile
            await SaveProfileAsync(profile, cancellationToken);

            _logger.LogInformation("Created configuration profile: {ProfileId} - {Name}", profile.Id, profile.Name);
            return OperationResult<ConfigurationProfile>.SuccessResult(profile);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to create profile");
            return OperationResult<ConfigurationProfile>.FailureResult($"Failed to create profile: {ex.Message}");
        }
    }

    public async Task<OperationResult<ConfigurationProfile>> UpdateProfileAsync(
        ConfigurationProfile profile,
        CancellationToken cancellationToken = default)
    {
        try
        {
            // Validate profile
            var validationResult = await ValidateProfileAsync(profile, cancellationToken);
            if (!validationResult.Success || (validationResult.Data?.Count ?? 0) > 0)
            {
                var errors = string.Join(", ", validationResult.Data ?? new List<string> { "Unknown validation error" });
                return OperationResult<ConfigurationProfile>.FailureResult($"Profile validation failed: {errors}");
            }

            // Check if profile exists
            var existingResult = await GetProfileAsync(profile.Id, cancellationToken);
            if (!existingResult.Success)
            {
                return OperationResult<ConfigurationProfile>.FailureResult($"Profile '{profile.Id}' not found");
            }

            // If this is set as default, unset others
            if (profile.IsDefault && !existingResult.Data!.IsDefault)
            {
                await UnsetAllDefaultProfilesAsync(cancellationToken);
            }

            // Update timestamp
            profile.ModifiedAt = DateTime.UtcNow;

            // Save profile
            await SaveProfileAsync(profile, cancellationToken);

            _logger.LogInformation("Updated configuration profile: {ProfileId} - {Name}", profile.Id, profile.Name);
            return OperationResult<ConfigurationProfile>.SuccessResult(profile);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to update profile {ProfileId}", profile.Id);
            return OperationResult<ConfigurationProfile>.FailureResult($"Failed to update profile: {ex.Message}");
        }
    }

    public async Task<OperationResult> DeleteProfileAsync(
        string profileId,
        CancellationToken cancellationToken = default)
    {
        try
        {
            var filePath = GetProfileFilePath(profileId);

            if (!File.Exists(filePath))
            {
                return OperationResult.FailureResult($"Profile '{profileId}' not found");
            }

            // Check if this is the default profile
            var profileResult = await GetProfileAsync(profileId, cancellationToken);
            if (profileResult.Success && profileResult.Data?.IsDefault == true)
            {
                return OperationResult.FailureResult("Cannot delete the default profile. Set another profile as default first.");
            }

            File.Delete(filePath);

            _logger.LogInformation("Deleted configuration profile: {ProfileId}", profileId);
            return OperationResult.SuccessResult();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to delete profile {ProfileId}", profileId);
            return OperationResult.FailureResult($"Failed to delete profile: {ex.Message}");
        }
    }

    public async Task<OperationResult> SetDefaultProfileAsync(
        string profileId,
        CancellationToken cancellationToken = default)
    {
        try
        {
            // Get the profile to set as default
            var profileResult = await GetProfileAsync(profileId, cancellationToken);
            if (!profileResult.Success || profileResult.Data == null)
            {
                return OperationResult.FailureResult($"Profile '{profileId}' not found");
            }

            // Unset all default profiles
            await UnsetAllDefaultProfilesAsync(cancellationToken);

            // Set this profile as default
            var profile = profileResult.Data;
            profile.IsDefault = true;
            profile.ModifiedAt = DateTime.UtcNow;

            await SaveProfileAsync(profile, cancellationToken);

            _logger.LogInformation("Set default profile: {ProfileId}", profileId);
            return OperationResult.SuccessResult();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to set default profile {ProfileId}", profileId);
            return OperationResult.FailureResult($"Failed to set default profile: {ex.Message}");
        }
    }

    public async Task<OperationResult<string>> ExportProfileAsync(
        string profileId,
        string destinationPath,
        CancellationToken cancellationToken = default)
    {
        try
        {
            var profileResult = await GetProfileAsync(profileId, cancellationToken);
            if (!profileResult.Success || profileResult.Data == null)
            {
                return OperationResult<string>.FailureResult($"Profile '{profileId}' not found");
            }

            // Ensure destination directory exists
            var destDir = Path.GetDirectoryName(destinationPath);
            if (!string.IsNullOrEmpty(destDir))
            {
                Directory.CreateDirectory(destDir);
            }

            // Export as JSON
            var json = JsonSerializer.Serialize(profileResult.Data, _jsonOptions);
            await File.WriteAllTextAsync(destinationPath, json, cancellationToken);

            _logger.LogInformation("Exported profile {ProfileId} to {Path}", profileId, destinationPath);
            return OperationResult<string>.SuccessResult(destinationPath);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to export profile {ProfileId}", profileId);
            return OperationResult<string>.FailureResult($"Failed to export profile: {ex.Message}");
        }
    }

    public async Task<OperationResult<ConfigurationProfile>> ImportProfileAsync(
        string filePath,
        bool setAsDefault = false,
        CancellationToken cancellationToken = default)
    {
        try
        {
            if (!File.Exists(filePath))
            {
                return OperationResult<ConfigurationProfile>.FailureResult($"File '{filePath}' not found");
            }

            // Read and deserialize
            var json = await File.ReadAllTextAsync(filePath, cancellationToken);
            var profile = JsonSerializer.Deserialize<ConfigurationProfile>(json, _jsonOptions);

            if (profile == null)
            {
                return OperationResult<ConfigurationProfile>.FailureResult("Failed to deserialize profile");
            }

            // Generate new ID to avoid conflicts
            var originalId = profile.Id;
            profile.Id = Guid.NewGuid().ToString();
            profile.CreatedAt = DateTime.UtcNow;
            profile.ModifiedAt = DateTime.UtcNow;
            profile.IsDefault = setAsDefault;

            // Validate and create
            var createResult = await CreateProfileAsync(profile, cancellationToken);

            _logger.LogInformation("Imported profile from {Path} (original ID: {OriginalId}, new ID: {NewId})",
                filePath, originalId, profile.Id);

            return createResult;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to import profile from {Path}", filePath);
            return OperationResult<ConfigurationProfile>.FailureResult($"Failed to import profile: {ex.Message}");
        }
    }

    public async Task<OperationResult<ConfigurationProfile>> DuplicateProfileAsync(
        string profileId,
        string newName,
        CancellationToken cancellationToken = default)
    {
        try
        {
            var profileResult = await GetProfileAsync(profileId, cancellationToken);
            if (!profileResult.Success || profileResult.Data == null)
            {
                return OperationResult<ConfigurationProfile>.FailureResult($"Profile '{profileId}' not found");
            }

            // Create a copy
            var original = profileResult.Data;
            var duplicate = new ConfigurationProfile
            {
                Id = Guid.NewGuid().ToString(),
                Name = newName,
                Description = original.Description,
                Owner = Environment.UserName,
                IsDefault = false,
                IsShared = false,
                Tags = new List<string>(original.Tags),
                General = CloneSettings(original.General),
                ImageOperations = CloneSettings(original.ImageOperations),
                Deployment = CloneSettings(original.Deployment),
                Backup = CloneSettings(original.Backup),
                Workflow = CloneSettings(original.Workflow),
                Advanced = CloneSettings(original.Advanced)
            };

            var createResult = await CreateProfileAsync(duplicate, cancellationToken);

            _logger.LogInformation("Duplicated profile {SourceId} to {NewId} with name '{NewName}'",
                profileId, duplicate.Id, newName);

            return createResult;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to duplicate profile {ProfileId}", profileId);
            return OperationResult<ConfigurationProfile>.FailureResult($"Failed to duplicate profile: {ex.Message}");
        }
    }

    public Task<OperationResult<List<string>>> ValidateProfileAsync(
        ConfigurationProfile profile,
        CancellationToken cancellationToken = default)
    {
        var errors = new List<string>();

        try
        {
            // Validate basic properties
            if (string.IsNullOrWhiteSpace(profile.Name))
                errors.Add("Profile name is required");

            // Validate general settings
            if (profile.General != null)
            {
                if (string.IsNullOrWhiteSpace(profile.General.DefaultMountPath))
                    errors.Add("Default mount path is required");

                if (profile.General.MaxLogFileSizeMB <= 0)
                    errors.Add("Max log file size must be greater than 0");

                if (profile.General.LogRetentionCount < 0)
                    errors.Add("Log retention count cannot be negative");
            }

            // Validate image operation settings
            if (profile.ImageOperations != null)
            {
                if (profile.ImageOperations.DefaultImageIndex < 1)
                    errors.Add("Default image index must be 1 or greater");

                if (profile.ImageOperations.CheckpointIntervalMinutes < 0)
                    errors.Add("Checkpoint interval cannot be negative");

                if (profile.ImageOperations.WimSplitSizeMB <= 0)
                    errors.Add("WIM split size must be greater than 0");

                var validCompressionTypes = new[] { "None", "Fast", "Maximum", "LZX", "LZMS" };
                if (!validCompressionTypes.Contains(profile.ImageOperations.DefaultCompressionType))
                    errors.Add($"Invalid compression type. Must be one of: {string.Join(", ", validCompressionTypes)}");
            }

            // Validate backup settings
            if (profile.Backup != null)
            {
                if (string.IsNullOrWhiteSpace(profile.Backup.DefaultBackupPath))
                    errors.Add("Default backup path is required");

                if (profile.Backup.BackupRetentionDays < 0)
                    errors.Add("Backup retention days cannot be negative");

                if (profile.Backup.MaxBackupsPerImage < 0)
                    errors.Add("Max backups per image cannot be negative");
            }

            // Validate workflow settings
            if (profile.Workflow != null)
            {
                if (profile.Workflow.MaxParallelSteps < 1)
                    errors.Add("Max parallel steps must be at least 1");

                if (profile.Workflow.StepTimeoutMinutes < 0)
                    errors.Add("Step timeout cannot be negative");

                if (profile.Workflow.MaxRetryAttempts < 0)
                    errors.Add("Max retry attempts cannot be negative");
            }

            // Validate advanced settings
            if (profile.Advanced != null)
            {
                if (profile.Advanced.MaxConcurrentOperations < 1)
                    errors.Add("Max concurrent operations must be at least 1");

                if (profile.Advanced.MemoryLimitMB < 0)
                    errors.Add("Memory limit cannot be negative");

                if (profile.Advanced.CacheSizeMB < 0)
                    errors.Add("Cache size cannot be negative");

                if (profile.Advanced.CacheExpirationHours < 0)
                    errors.Add("Cache expiration cannot be negative");

                var validCleanupPolicies = new[] { "Immediate", "OnCompletion", "Manual" };
                if (!validCleanupPolicies.Contains(profile.Advanced.TempFileCleanupPolicy))
                    errors.Add($"Invalid cleanup policy. Must be one of: {string.Join(", ", validCleanupPolicies)}");
            }

            _logger.LogInformation("Validated profile '{Name}': {ErrorCount} errors found", profile.Name, errors.Count);
            return Task.FromResult(OperationResult<List<string>>.SuccessResult(errors));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to validate profile");
            return Task.FromResult(OperationResult<List<string>>.FailureResult($"Validation error: {ex.Message}"));
        }
    }

    public async Task<OperationResult<ConfigurationProfile>> ApplyProfileWithOverridesAsync(
        string profileId,
        Dictionary<string, object>? overrides = null,
        CancellationToken cancellationToken = default)
    {
        try
        {
            var profileResult = await GetProfileAsync(profileId, cancellationToken);
            if (!profileResult.Success || profileResult.Data == null)
            {
                return OperationResult<ConfigurationProfile>.FailureResult($"Profile '{profileId}' not found");
            }

            var profile = profileResult.Data;

            // If no overrides, return the profile as-is
            if (overrides == null || overrides.Count == 0)
            {
                return OperationResult<ConfigurationProfile>.SuccessResult(profile);
            }

            // Create a clone to apply overrides
            var effectiveProfile = CloneProfile(profile);

            // Apply overrides using reflection
            foreach (var kvp in overrides)
            {
                ApplyOverride(effectiveProfile, kvp.Key, kvp.Value);
            }

            _logger.LogInformation("Applied profile {ProfileId} with {OverrideCount} overrides", profileId, overrides.Count);
            return OperationResult<ConfigurationProfile>.SuccessResult(effectiveProfile);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to apply profile with overrides");
            return OperationResult<ConfigurationProfile>.FailureResult($"Failed to apply overrides: {ex.Message}");
        }
    }

    public async Task<OperationResult<ConfigurationProfile>> ResetProfileAsync(
        string profileId,
        CancellationToken cancellationToken = default)
    {
        try
        {
            var profileResult = await GetProfileAsync(profileId, cancellationToken);
            if (!profileResult.Success || profileResult.Data == null)
            {
                return OperationResult<ConfigurationProfile>.FailureResult($"Profile '{profileId}' not found");
            }

            var profile = profileResult.Data;

            // Reset to default settings
            profile.General = new GeneralSettings();
            profile.ImageOperations = new ImageOperationSettings();
            profile.Deployment = new DeploymentSettings();
            profile.Backup = new BackupSettings();
            profile.Workflow = new WorkflowSettings();
            profile.Advanced = new AdvancedSettings();
            profile.ModifiedAt = DateTime.UtcNow;

            await SaveProfileAsync(profile, cancellationToken);

            _logger.LogInformation("Reset profile {ProfileId} to defaults", profileId);
            return OperationResult<ConfigurationProfile>.SuccessResult(profile);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to reset profile {ProfileId}", profileId);
            return OperationResult<ConfigurationProfile>.FailureResult($"Failed to reset profile: {ex.Message}");
        }
    }

    // Private helper methods

    private string GetProfileFilePath(string profileId)
    {
        return Path.Combine(_profilesDirectory, $"{profileId}.json");
    }

    private async Task SaveProfileAsync(ConfigurationProfile profile, CancellationToken cancellationToken)
    {
        var filePath = GetProfileFilePath(profile.Id);
        var json = JsonSerializer.Serialize(profile, _jsonOptions);
        await File.WriteAllTextAsync(filePath, json, cancellationToken);
    }

    private async Task UnsetAllDefaultProfilesAsync(CancellationToken cancellationToken)
    {
        var profilesResult = await GetProfilesAsync(true, null, cancellationToken);
        if (!profilesResult.Success || profilesResult.Data == null)
            return;

        foreach (var profile in profilesResult.Data.Where(p => p.IsDefault))
        {
            profile.IsDefault = false;
            profile.ModifiedAt = DateTime.UtcNow;
            await SaveProfileAsync(profile, cancellationToken);
        }
    }

    private async Task<OperationResult<ConfigurationProfile>> CreateDefaultProfileAsync(CancellationToken cancellationToken)
    {
        var defaultProfile = new ConfigurationProfile
        {
            Id = "default",
            Name = "Default Profile",
            Description = "Default configuration profile",
            IsDefault = true,
            Tags = new List<string> { "default", "system" }
        };

        return await CreateProfileAsync(defaultProfile, cancellationToken);
    }

    private T CloneSettings<T>(T settings) where T : new()
    {
        var json = JsonSerializer.Serialize(settings, _jsonOptions);
        return JsonSerializer.Deserialize<T>(json, _jsonOptions) ?? new T();
    }

    private ConfigurationProfile CloneProfile(ConfigurationProfile profile)
    {
        var json = JsonSerializer.Serialize(profile, _jsonOptions);
        return JsonSerializer.Deserialize<ConfigurationProfile>(json, _jsonOptions)
            ?? throw new InvalidOperationException("Failed to clone profile");
    }

    private void ApplyOverride(ConfigurationProfile profile, string path, object value)
    {
        // Simple dot-notation path resolver (e.g., "General.DefaultMountPath")
        var parts = path.Split('.');
        if (parts.Length != 2)
            return;

        var settingsName = parts[0];
        var propertyName = parts[1];

        object? settingsObject = settingsName switch
        {
            "General" => profile.General,
            "ImageOperations" => profile.ImageOperations,
            "Deployment" => profile.Deployment,
            "Backup" => profile.Backup,
            "Workflow" => profile.Workflow,
            "Advanced" => profile.Advanced,
            _ => null
        };

        if (settingsObject == null)
            return;

        var property = settingsObject.GetType().GetProperty(propertyName);
        if (property != null && property.CanWrite)
        {
            var convertedValue = Convert.ChangeType(value, property.PropertyType);
            property.SetValue(settingsObject, convertedValue);
        }
    }
}
