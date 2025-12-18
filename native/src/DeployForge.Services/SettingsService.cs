using DeployForge.Core.Interfaces;
using Newtonsoft.Json;

namespace DeployForge.Services;

/// <summary>
/// Service for managing application settings.
/// </summary>
public class SettingsService : ISettingsService
{
    private readonly string _settingsPath;
    private readonly JsonSerializerSettings _jsonSettings;
    private Dictionary<string, object> _settings;
    private const int MaxRecentImages = 10;
    
    /// <inheritdoc />
    public string DefaultMountPath
    {
        get => GetSetting<string>("DefaultMountPath", GetDefaultMountPath()) ?? GetDefaultMountPath();
        set => SetSetting("DefaultMountPath", value);
    }
    
    /// <inheritdoc />
    public string Theme
    {
        get => GetSetting<string>("Theme", "Dark") ?? "Dark";
        set => SetSetting("Theme", value);
    }
    
    /// <inheritdoc />
    public bool ShowAdvancedOptions
    {
        get => GetSetting<bool>("ShowAdvancedOptions", false);
        set => SetSetting("ShowAdvancedOptions", value);
    }
    
    /// <inheritdoc />
    public List<string> RecentImages
    {
        get
        {
            var recent = GetSetting<List<string>>("RecentImages");
            return recent ?? new List<string>();
        }
    }
    
    /// <summary>
    /// Whether to check for updates on startup.
    /// </summary>
    public bool CheckForUpdates
    {
        get => GetSetting<bool>("CheckForUpdates", true);
        set => SetSetting("CheckForUpdates", value);
    }
    
    /// <summary>
    /// Whether to create backups before modifying images.
    /// </summary>
    public bool CreateBackups
    {
        get => GetSetting<bool>("CreateBackups", true);
        set => SetSetting("CreateBackups", value);
    }
    
    /// <summary>
    /// Backup directory path.
    /// </summary>
    public string BackupDirectory
    {
        get => GetSetting<string>("BackupDirectory", GetDefaultBackupPath()) ?? GetDefaultBackupPath();
        set => SetSetting("BackupDirectory", value);
    }
    
    /// <summary>
    /// Whether to show confirmation dialogs.
    /// </summary>
    public bool ShowConfirmations
    {
        get => GetSetting<bool>("ShowConfirmations", true);
        set => SetSetting("ShowConfirmations", value);
    }
    
    /// <summary>
    /// Log level (Debug, Info, Warning, Error).
    /// </summary>
    public string LogLevel
    {
        get => GetSetting<string>("LogLevel", "Info") ?? "Info";
        set => SetSetting("LogLevel", value);
    }
    
    /// <summary>
    /// Maximum number of concurrent operations.
    /// </summary>
    public int MaxConcurrentOperations
    {
        get => GetSetting<int>("MaxConcurrentOperations", 4);
        set => SetSetting("MaxConcurrentOperations", value);
    }
    
    /// <summary>
    /// Creates a new SettingsService.
    /// </summary>
    public SettingsService(string? settingsPath = null)
    {
        _settingsPath = settingsPath ?? GetDefaultSettingsPath();
        _settings = new Dictionary<string, object>();
        
        _jsonSettings = new JsonSerializerSettings
        {
            Formatting = Formatting.Indented,
            NullValueHandling = NullValueHandling.Ignore
        };
        
        // Ensure directory exists
        var directory = Path.GetDirectoryName(_settingsPath);
        if (!string.IsNullOrEmpty(directory) && !Directory.Exists(directory))
        {
            Directory.CreateDirectory(directory);
        }
    }
    
    /// <summary>
    /// Gets the default settings file path.
    /// </summary>
    private static string GetDefaultSettingsPath()
    {
        var appData = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
        return Path.Combine(appData, "DeployForge", "settings.json");
    }
    
    /// <summary>
    /// Gets the default mount path.
    /// </summary>
    private static string GetDefaultMountPath()
    {
        var temp = Path.GetTempPath();
        return Path.Combine(temp, "DeployForge", "Mount");
    }
    
    /// <summary>
    /// Gets the default backup path.
    /// </summary>
    private static string GetDefaultBackupPath()
    {
        var appData = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
        return Path.Combine(appData, "DeployForge", "Backups");
    }
    
    /// <inheritdoc />
    public T? GetSetting<T>(string key, T? defaultValue = default)
    {
        if (_settings.TryGetValue(key, out var value))
        {
            try
            {
                if (value is T typedValue)
                {
                    return typedValue;
                }
                
                // Handle JSON conversion for complex types
                if (value is Newtonsoft.Json.Linq.JToken jToken)
                {
                    return jToken.ToObject<T>();
                }
                
                return (T)Convert.ChangeType(value, typeof(T));
            }
            catch
            {
                return defaultValue;
            }
        }
        
        return defaultValue;
    }
    
    /// <inheritdoc />
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
    }
    
    /// <inheritdoc />
    public void AddRecentImage(string path)
    {
        if (string.IsNullOrWhiteSpace(path))
            return;
        
        var recent = GetSetting<List<string>>("RecentImages") ?? new List<string>();
        
        // Remove if already exists
        recent.RemoveAll(p => p.Equals(path, StringComparison.OrdinalIgnoreCase));
        
        // Add to beginning
        recent.Insert(0, path);
        
        // Limit size
        if (recent.Count > MaxRecentImages)
        {
            recent.RemoveRange(MaxRecentImages, recent.Count - MaxRecentImages);
        }
        
        SetSetting("RecentImages", recent);
    }
    
    /// <summary>
    /// Clears the recent images list.
    /// </summary>
    public void ClearRecentImages()
    {
        SetSetting("RecentImages", new List<string>());
    }
    
    /// <inheritdoc />
    public async Task SaveAsync()
    {
        var json = JsonConvert.SerializeObject(_settings, _jsonSettings);
        await File.WriteAllTextAsync(_settingsPath, json);
    }
    
    /// <inheritdoc />
    public async Task LoadAsync()
    {
        if (!File.Exists(_settingsPath))
        {
            _settings = new Dictionary<string, object>();
            return;
        }
        
        try
        {
            var json = await File.ReadAllTextAsync(_settingsPath);
            _settings = JsonConvert.DeserializeObject<Dictionary<string, object>>(json, _jsonSettings)
                ?? new Dictionary<string, object>();
        }
        catch
        {
            _settings = new Dictionary<string, object>();
        }
    }
    
    /// <summary>
    /// Resets all settings to defaults.
    /// </summary>
    public async Task ResetAsync()
    {
        _settings = new Dictionary<string, object>();
        await SaveAsync();
    }
    
    /// <summary>
    /// Exports settings to a file.
    /// </summary>
    public async Task ExportAsync(string path)
    {
        var json = JsonConvert.SerializeObject(_settings, _jsonSettings);
        await File.WriteAllTextAsync(path, json);
    }
    
    /// <summary>
    /// Imports settings from a file.
    /// </summary>
    public async Task ImportAsync(string path)
    {
        if (!File.Exists(path))
            throw new FileNotFoundException("Settings file not found", path);
        
        var json = await File.ReadAllTextAsync(path);
        _settings = JsonConvert.DeserializeObject<Dictionary<string, object>>(json, _jsonSettings)
            ?? new Dictionary<string, object>();
    }
}
