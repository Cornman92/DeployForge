using System.Text.Json;
using DeployForge.App.Models;

namespace DeployForge.App.Services;

public interface IProfileService
{
    IReadOnlyList<Profile> BuiltInProfiles { get; }
    IReadOnlyList<Profile> CustomProfiles { get; }
    IReadOnlyList<Profile> AllProfiles { get; }
    
    Task LoadProfilesAsync();
    Task SaveProfileAsync(Profile profile);
    Task DeleteProfileAsync(string profileId);
    Profile? GetProfileById(string id);
    Profile CreateFromType(ProfileType type);
}

public class ProfileService : IProfileService
{
    private readonly ISettingsService _settingsService;
    private readonly List<Profile> _builtInProfiles;
    private readonly List<Profile> _customProfiles = new();
    
    public IReadOnlyList<Profile> BuiltInProfiles => _builtInProfiles;
    public IReadOnlyList<Profile> CustomProfiles => _customProfiles;
    public IReadOnlyList<Profile> AllProfiles => _builtInProfiles.Concat(_customProfiles).ToList();
    
    public ProfileService(ISettingsService settingsService)
    {
        _settingsService = settingsService;
        _builtInProfiles = CreateBuiltInProfiles();
    }
    
    private static List<Profile> CreateBuiltInProfiles() => new()
    {
        new Profile
        {
            Id = "gaming", Name = "Gaming", Description = "Optimized for gaming performance with reduced latency and maximum FPS",
            Type = ProfileType.Gaming, IconGlyph = "\uE7FC", IsBuiltIn = true,
            Features = new ProfileFeatures
            {
                RemoveBloatware = true, DebloatLevel = DebloatLevel.Moderate,
                DisableTelemetry = true, DisableCortana = true, PrivacyLevel = PrivacyLevel.Balanced,
                EnableGameMode = true, InstallGamingRuntimes = true, OptimizeNetwork = true, GamingProfile = GamingProfile.Performance,
                OptimizeServices = true
            }
        },
        new Profile
        {
            Id = "developer", Name = "Developer", Description = "Full development environment with WSL2, VS Code, and popular tools",
            Type = ProfileType.Developer, IconGlyph = "\uE943", IsBuiltIn = true,
            Features = new ProfileFeatures
            {
                RemoveBloatware = true, DebloatLevel = DebloatLevel.Light,
                DisableTelemetry = true, PrivacyLevel = PrivacyLevel.Minimal,
                EnableDeveloperMode = true, InstallWSL2 = true,
                DevTools = new List<string> { "vscode", "git", "docker", "terminal", "pwsh" }
            }
        },
        new Profile
        {
            Id = "enterprise", Name = "Enterprise", Description = "Secure deployment for corporate environments with compliance features",
            Type = ProfileType.Enterprise, IconGlyph = "\uE770", IsBuiltIn = true,
            Features = new ProfileFeatures
            {
                RemoveBloatware = true, DebloatLevel = DebloatLevel.Aggressive,
                DisableTelemetry = true, DisableCortana = true, BlockTelemetryDomains = true, PrivacyLevel = PrivacyLevel.Aggressive,
                OptimizeServices = true
            }
        },
        new Profile
        {
            Id = "student", Name = "Student", Description = "Balanced setup for education with productivity apps",
            Type = ProfileType.Student, IconGlyph = "\uE7BE", IsBuiltIn = true,
            Features = new ProfileFeatures
            {
                RemoveBloatware = true, DebloatLevel = DebloatLevel.Light,
                DisableTelemetry = true, PrivacyLevel = PrivacyLevel.Balanced
            }
        },
        new Profile
        {
            Id = "creator", Name = "Creator", Description = "Optimized for content creation, streaming, and media production",
            Type = ProfileType.Creator, IconGlyph = "\uE8B3", IsBuiltIn = true,
            Features = new ProfileFeatures
            {
                RemoveBloatware = true, DebloatLevel = DebloatLevel.Moderate,
                DisableTelemetry = true, PrivacyLevel = PrivacyLevel.Balanced,
                OptimizeServices = true
            }
        },
        new Profile
        {
            Id = "minimal", Name = "Minimal", Description = "Clean Windows installation with essential apps only",
            Type = ProfileType.Minimal, IconGlyph = "\uE71D", IsBuiltIn = true,
            Features = new ProfileFeatures
            {
                RemoveBloatware = true, DebloatLevel = DebloatLevel.Extreme,
                DisableTelemetry = true, DisableCortana = true, BlockTelemetryDomains = true, PrivacyLevel = PrivacyLevel.Paranoid,
                OptimizeServices = true, DisableAnimations = true
            }
        }
    };
    
    public async Task LoadProfilesAsync()
    {
        var profilesPath = _settingsService.Settings.Paths.ProfilesDirectory;
        
        if (!Directory.Exists(profilesPath)) return;
        
        _customProfiles.Clear();
        
        foreach (var file in Directory.GetFiles(profilesPath, "*.json"))
        {
            try
            {
                var json = await File.ReadAllTextAsync(file);
                var profile = JsonSerializer.Deserialize<Profile>(json, new JsonSerializerOptions { PropertyNameCaseInsensitive = true });
                if (profile != null)
                {
                    _customProfiles.Add(profile);
                }
            }
            catch { /* Skip invalid profiles */ }
        }
    }
    
    public async Task SaveProfileAsync(Profile profile)
    {
        var profilesPath = _settingsService.Settings.Paths.ProfilesDirectory;
        Directory.CreateDirectory(profilesPath);
        
        var filePath = Path.Combine(profilesPath, $"{profile.Id}.json");
        var json = JsonSerializer.Serialize(profile, new JsonSerializerOptions { WriteIndented = true });
        await File.WriteAllTextAsync(filePath, json);
        
        var existing = _customProfiles.FindIndex(p => p.Id == profile.Id);
        if (existing >= 0)
            _customProfiles[existing] = profile;
        else
            _customProfiles.Add(profile);
    }
    
    public async Task DeleteProfileAsync(string profileId)
    {
        var profilesPath = _settingsService.Settings.Paths.ProfilesDirectory;
        var filePath = Path.Combine(profilesPath, $"{profileId}.json");
        
        if (File.Exists(filePath))
        {
            await Task.Run(() => File.Delete(filePath));
        }
        
        _customProfiles.RemoveAll(p => p.Id == profileId);
    }
    
    public Profile? GetProfileById(string id) => AllProfiles.FirstOrDefault(p => p.Id == id);
    
    public Profile CreateFromType(ProfileType type) =>
        _builtInProfiles.FirstOrDefault(p => p.Type == type) ?? _builtInProfiles[0];
}
