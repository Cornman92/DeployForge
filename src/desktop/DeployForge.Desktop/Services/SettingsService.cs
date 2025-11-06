using System.IO;
using System.Text.Json;
using Microsoft.Extensions.Logging;

namespace DeployForge.Desktop.Services;

/// <summary>
/// Settings service implementation using JSON file storage
/// </summary>
public class SettingsService : ISettingsService
{
    private readonly ILogger<SettingsService> _logger;
    private readonly string _settingsPath;
    private Dictionary<string, object> _settings = new();
    private readonly JsonSerializerOptions _jsonOptions;

    public SettingsService(ILogger<SettingsService> logger)
    {
        _logger = logger;

        var appDataPath = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
        var appFolder = Path.Combine(appDataPath, "DeployForge");
        Directory.CreateDirectory(appFolder);
        _settingsPath = Path.Combine(appFolder, "settings.json");

        _jsonOptions = new JsonSerializerOptions
        {
            WriteIndented = true,
            PropertyNameCaseInsensitive = true
        };

        // Load settings on construction
        _ = LoadAsync();
    }

    public T? GetSetting<T>(string key, T? defaultValue = default)
    {
        if (_settings.TryGetValue(key, out var value))
        {
            try
            {
                if (value is JsonElement jsonElement)
                {
                    return jsonElement.Deserialize<T>(_jsonOptions);
                }

                if (value is T typedValue)
                {
                    return typedValue;
                }

                // Try to convert
                var json = JsonSerializer.Serialize(value, _jsonOptions);
                return JsonSerializer.Deserialize<T>(json, _jsonOptions);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error getting setting {Key}", key);
                return defaultValue;
            }
        }

        return defaultValue;
    }

    public void SetSetting<T>(string key, T value)
    {
        if (value == null)
        {
            _settings.Remove(key);
        }
        else
        {
            _settings[key] = value;
        }

        _logger.LogDebug("Setting {Key} updated", key);
    }

    public void DeleteSetting(string key)
    {
        _settings.Remove(key);
        _logger.LogDebug("Setting {Key} deleted", key);
    }

    public bool HasSetting(string key)
    {
        return _settings.ContainsKey(key);
    }

    public async Task SaveAsync()
    {
        try
        {
            var json = JsonSerializer.Serialize(_settings, _jsonOptions);
            await File.WriteAllTextAsync(_settingsPath, json);
            _logger.LogInformation("Settings saved to {Path}", _settingsPath);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to save settings");
        }
    }

    public async Task LoadAsync()
    {
        try
        {
            if (File.Exists(_settingsPath))
            {
                var json = await File.ReadAllTextAsync(_settingsPath);
                var loaded = JsonSerializer.Deserialize<Dictionary<string, object>>(json, _jsonOptions);

                if (loaded != null)
                {
                    _settings = loaded;
                    _logger.LogInformation("Settings loaded from {Path}", _settingsPath);
                }
            }
            else
            {
                _logger.LogInformation("No settings file found, using defaults");
                InitializeDefaults();
                await SaveAsync();
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to load settings, using defaults");
            InitializeDefaults();
        }
    }

    public Dictionary<string, object> GetAllSettings()
    {
        return new Dictionary<string, object>(_settings);
    }

    public void ClearAll()
    {
        _settings.Clear();
        _logger.LogWarning("All settings cleared");
    }

    private void InitializeDefaults()
    {
        _settings = new Dictionary<string, object>
        {
            ["ApiBaseUrl"] = "http://localhost:5000/api/",
            ["Theme"] = "Dark",
            ["AutoSaveInterval"] = 300, // 5 minutes
            ["MaxRecentFiles"] = 10,
            ["DefaultMountPath"] = @"C:\Mount",
            ["EnableLogging"] = true,
            ["LogLevel"] = "Information",
            ["CheckForUpdates"] = true,
            ["EnableTelemetry"] = false
        };
    }
}
