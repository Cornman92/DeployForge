using DeployForge.Core.Enums;
using DeployForge.Core.Models;
using DeployForge.Services;
using Xunit;

namespace DeployForge.Services.Tests;

/// <summary>
/// Tests for TemplateService.
/// </summary>
public class TemplateServiceTests : IDisposable
{
    private readonly string _testDirectory;
    private readonly TemplateService _service;
    
    public TemplateServiceTests()
    {
        _testDirectory = Path.Combine(Path.GetTempPath(), "DeployForgeTests", Guid.NewGuid().ToString());
        Directory.CreateDirectory(_testDirectory);
        _service = new TemplateService(_testDirectory);
    }
    
    public void Dispose()
    {
        if (Directory.Exists(_testDirectory))
        {
            Directory.Delete(_testDirectory, true);
        }
    }
    
    [Fact]
    public void GetBuiltInProfiles_ReturnsExpectedProfiles()
    {
        var profiles = _service.GetBuiltInProfiles().ToList();
        
        Assert.NotEmpty(profiles);
        Assert.Contains(profiles, p => p.Type == BuildProfileType.Gaming);
        Assert.Contains(profiles, p => p.Type == BuildProfileType.Developer);
        Assert.Contains(profiles, p => p.Type == BuildProfileType.Enterprise);
        Assert.Contains(profiles, p => p.Type == BuildProfileType.Student);
        Assert.Contains(profiles, p => p.Type == BuildProfileType.Creator);
    }
    
    [Fact]
    public async Task SaveAndLoadTemplate_RoundTrips()
    {
        var profile = new BuildProfile
        {
            Name = "Test Profile",
            Description = "Test Description",
            Type = BuildProfileType.Custom,
            EnableGaming = true,
            Gaming = new GamingConfig
            {
                Profile = GamingProfile.Balanced,
                EnableGameMode = true
            }
        };
        
        var path = Path.Combine(_testDirectory, "test.json");
        
        await _service.SaveTemplateAsync(profile, path);
        Assert.True(File.Exists(path));
        
        var loaded = await _service.LoadTemplateAsync(path);
        
        Assert.Equal(profile.Name, loaded.Name);
        Assert.Equal(profile.Description, loaded.Description);
        Assert.Equal(profile.Type, loaded.Type);
        Assert.Equal(profile.EnableGaming, loaded.EnableGaming);
        Assert.NotNull(loaded.Gaming);
        Assert.Equal(profile.Gaming.Profile, loaded.Gaming.Profile);
    }
    
    [Fact]
    public async Task DeleteTemplate_RemovesFile()
    {
        var path = Path.Combine(_testDirectory, "delete-test.json");
        await File.WriteAllTextAsync(path, "{}");
        
        Assert.True(File.Exists(path));
        
        await _service.DeleteTemplateAsync(path);
        
        Assert.False(File.Exists(path));
    }
    
    [Fact]
    public async Task GetCustomTemplates_ReturnsEmptyWhenNoTemplates()
    {
        var templates = await _service.GetCustomTemplatesAsync();
        
        Assert.Empty(templates);
    }
    
    [Fact]
    public async Task GetCustomTemplates_ReturnsSavedTemplates()
    {
        var profile1 = new BuildProfile { Name = "Profile 1", Type = BuildProfileType.Custom };
        var profile2 = new BuildProfile { Name = "Profile 2", Type = BuildProfileType.Custom };
        
        await _service.SaveTemplateAsync(profile1, Path.Combine(_testDirectory, "profile1.json"));
        await _service.SaveTemplateAsync(profile2, Path.Combine(_testDirectory, "profile2.json"));
        
        var templates = (await _service.GetCustomTemplatesAsync()).ToList();
        
        Assert.Equal(2, templates.Count);
    }
    
    [Fact]
    public void GetBuiltInProfile_ReturnsCorrectProfile()
    {
        var gaming = _service.GetBuiltInProfile(BuildProfileType.Gaming);
        
        Assert.NotNull(gaming);
        Assert.Equal(BuildProfileType.Gaming, gaming.Type);
        Assert.True(gaming.EnableGaming);
    }
    
    [Fact]
    public void CreateFromBuiltIn_CopiesSettings()
    {
        var custom = _service.CreateFromBuiltIn(BuildProfileType.Gaming, "My Gaming Profile");
        
        Assert.Equal("My Gaming Profile", custom.Name);
        Assert.Equal(BuildProfileType.Custom, custom.Type);
        Assert.NotNull(custom.Gaming);
    }
    
    [Fact]
    public void ExportToJson_ProducesValidJson()
    {
        var profile = BuildProfile.CreateGamingProfile();
        
        var json = _service.ExportToJson(profile);
        
        Assert.NotNull(json);
        Assert.Contains("Gaming PC", json);
        Assert.Contains("GamingProfile", json);
    }
    
    [Fact]
    public void ImportFromJson_ParsesCorrectly()
    {
        var profile = BuildProfile.CreateDeveloperProfile();
        var json = _service.ExportToJson(profile);
        
        var imported = _service.ImportFromJson(json);
        
        Assert.Equal(profile.Name, imported.Name);
        Assert.Equal(profile.Type, imported.Type);
    }
}
