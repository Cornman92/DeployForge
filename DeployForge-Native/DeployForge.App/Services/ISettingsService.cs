using System.Text.Json;
using DeployForge.App.Models;

namespace DeployForge.App.Services;

public interface ISettingsService
{
    AppSettings Settings { get; }
    Task LoadAsync();
    Task SaveAsync();
    void Reset();
}

public class SettingsService : ISettingsService
{
    private readonly string _settingsPath;
    private AppSettings _settings = new();
    
    public AppSettings Settings => _settings;
    
    public SettingsService()
    {
        var appDataPath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), "DeployForge");
        Directory.CreateDirectory(appDataPath);
        _settingsPath = Path.Combine(appDataPath, "settings.json");
    }
    
    public async Task LoadAsync()
    {
        try
        {
            if (File.Exists(_settingsPath))
            {
                var json = await File.ReadAllTextAsync(_settingsPath);
                _settings = JsonSerializer.Deserialize<AppSettings>(json, new JsonSerializerOptions { PropertyNameCaseInsensitive = true }) ?? new();
            }
        }
        catch
        {
            _settings = new AppSettings();
        }
        
        EnsureDirectories();
    }
    
    public async Task SaveAsync()
    {
        try
        {
            var json = JsonSerializer.Serialize(_settings, new JsonSerializerOptions { WriteIndented = true });
            await File.WriteAllTextAsync(_settingsPath, json);
        }
        catch
        {
            // Log error
        }
    }
    
    public void Reset()
    {
        _settings = new AppSettings();
    }
    
    private void EnsureDirectories()
    {
        Directory.CreateDirectory(_settings.Paths.TempDirectory);
        Directory.CreateDirectory(_settings.Paths.LogDirectory);
        Directory.CreateDirectory(_settings.Paths.ProfilesDirectory);
        Directory.CreateDirectory(_settings.Paths.TemplatesDirectory);
    }
}
