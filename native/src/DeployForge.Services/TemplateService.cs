using DeployForge.Core.Enums;
using DeployForge.Core.Interfaces;
using DeployForge.Core.Models;
using Newtonsoft.Json;

namespace DeployForge.Services;

/// <summary>
/// Service for managing build profiles and templates.
/// </summary>
public class TemplateService : ITemplateService
{
    private readonly string _templatesDirectory;
    private readonly JsonSerializerSettings _jsonSettings;
    
    /// <summary>
    /// Creates a new TemplateService.
    /// </summary>
    /// <param name="templatesDirectory">Optional custom templates directory.</param>
    public TemplateService(string? templatesDirectory = null)
    {
        _templatesDirectory = templatesDirectory ?? GetDefaultTemplatesDirectory();
        
        _jsonSettings = new JsonSerializerSettings
        {
            Formatting = Formatting.Indented,
            NullValueHandling = NullValueHandling.Ignore,
            Converters = new List<JsonConverter> { new Newtonsoft.Json.Converters.StringEnumConverter() }
        };
        
        // Ensure templates directory exists
        if (!Directory.Exists(_templatesDirectory))
        {
            Directory.CreateDirectory(_templatesDirectory);
        }
    }
    
    /// <summary>
    /// Gets the default templates directory.
    /// </summary>
    private static string GetDefaultTemplatesDirectory()
    {
        var appData = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
        return Path.Combine(appData, "DeployForge", "Templates");
    }
    
    /// <inheritdoc />
    public IEnumerable<BuildProfile> GetBuiltInProfiles()
    {
        return new List<BuildProfile>
        {
            BuildProfile.CreateGamingProfile(),
            BuildProfile.CreateDeveloperProfile(),
            BuildProfile.CreateEnterpriseProfile(),
            BuildProfile.CreateStudentProfile(),
            BuildProfile.CreateCreatorProfile()
        };
    }
    
    /// <inheritdoc />
    public async Task<IEnumerable<BuildProfile>> GetCustomTemplatesAsync()
    {
        var templates = new List<BuildProfile>();
        
        if (!Directory.Exists(_templatesDirectory))
        {
            return templates;
        }
        
        var files = Directory.GetFiles(_templatesDirectory, "*.json");
        
        foreach (var file in files)
        {
            try
            {
                var template = await LoadTemplateAsync(file);
                templates.Add(template);
            }
            catch
            {
                // Skip invalid templates
            }
        }
        
        return templates;
    }
    
    /// <inheritdoc />
    public async Task SaveTemplateAsync(BuildProfile profile, string path)
    {
        if (profile == null)
            throw new ArgumentNullException(nameof(profile));
        
        if (string.IsNullOrWhiteSpace(path))
            throw new ArgumentException("Path is required", nameof(path));
        
        // Ensure directory exists
        var directory = Path.GetDirectoryName(path);
        if (!string.IsNullOrEmpty(directory) && !Directory.Exists(directory))
        {
            Directory.CreateDirectory(directory);
        }
        
        var json = JsonConvert.SerializeObject(profile, _jsonSettings);
        await File.WriteAllTextAsync(path, json);
    }
    
    /// <summary>
    /// Saves a template to the default templates directory.
    /// </summary>
    public async Task SaveTemplateAsync(BuildProfile profile)
    {
        var fileName = SanitizeFileName(profile.Name) + ".json";
        var path = Path.Combine(_templatesDirectory, fileName);
        await SaveTemplateAsync(profile, path);
    }
    
    /// <inheritdoc />
    public async Task<BuildProfile> LoadTemplateAsync(string path)
    {
        if (!File.Exists(path))
            throw new FileNotFoundException("Template not found", path);
        
        var json = await File.ReadAllTextAsync(path);
        var profile = JsonConvert.DeserializeObject<BuildProfile>(json, _jsonSettings);
        
        if (profile == null)
            throw new InvalidOperationException("Failed to parse template");
        
        return profile;
    }
    
    /// <inheritdoc />
    public Task DeleteTemplateAsync(string path)
    {
        if (File.Exists(path))
        {
            File.Delete(path);
        }
        
        return Task.CompletedTask;
    }
    
    /// <summary>
    /// Gets a built-in profile by type.
    /// </summary>
    public BuildProfile? GetBuiltInProfile(BuildProfileType type)
    {
        return type switch
        {
            BuildProfileType.Gaming => BuildProfile.CreateGamingProfile(),
            BuildProfileType.Developer => BuildProfile.CreateDeveloperProfile(),
            BuildProfileType.Enterprise => BuildProfile.CreateEnterpriseProfile(),
            BuildProfileType.Student => BuildProfile.CreateStudentProfile(),
            BuildProfileType.Creator => BuildProfile.CreateCreatorProfile(),
            _ => null
        };
    }
    
    /// <summary>
    /// Creates a new custom profile based on a built-in profile.
    /// </summary>
    public BuildProfile CreateFromBuiltIn(BuildProfileType baseType, string name)
    {
        var baseProfile = GetBuiltInProfile(baseType) ?? new BuildProfile();
        
        return new BuildProfile
        {
            Name = name,
            Description = $"Custom profile based on {baseType}",
            Type = BuildProfileType.Custom,
            Icon = baseProfile.Icon,
            Gaming = baseProfile.Gaming,
            Debloat = baseProfile.Debloat,
            DevEnvironment = baseProfile.DevEnvironment,
            Browsers = baseProfile.Browsers,
            UICustomization = baseProfile.UICustomization,
            PrivacyLevel = baseProfile.PrivacyLevel,
            EnableGaming = baseProfile.EnableGaming,
            EnableDebloat = baseProfile.EnableDebloat,
            EnableDevEnvironment = baseProfile.EnableDevEnvironment,
            EnableBrowsers = baseProfile.EnableBrowsers,
            EnableUICustomization = baseProfile.EnableUICustomization,
            EnablePrivacyHardening = baseProfile.EnablePrivacyHardening
        };
    }
    
    /// <summary>
    /// Exports a profile to JSON string.
    /// </summary>
    public string ExportToJson(BuildProfile profile)
    {
        return JsonConvert.SerializeObject(profile, _jsonSettings);
    }
    
    /// <summary>
    /// Imports a profile from JSON string.
    /// </summary>
    public BuildProfile ImportFromJson(string json)
    {
        var profile = JsonConvert.DeserializeObject<BuildProfile>(json, _jsonSettings);
        
        if (profile == null)
            throw new InvalidOperationException("Failed to parse profile JSON");
        
        return profile;
    }
    
    /// <summary>
    /// Gets the templates directory path.
    /// </summary>
    public string GetTemplatesDirectory() => _templatesDirectory;
    
    /// <summary>
    /// Sanitizes a file name by removing invalid characters.
    /// </summary>
    private static string SanitizeFileName(string name)
    {
        var invalid = Path.GetInvalidFileNameChars();
        return string.Join("_", name.Split(invalid, StringSplitOptions.RemoveEmptyEntries));
    }
}
