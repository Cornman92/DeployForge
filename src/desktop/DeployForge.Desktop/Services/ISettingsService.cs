namespace DeployForge.Desktop.Services;

/// <summary>
/// Service for managing application settings
/// </summary>
public interface ISettingsService
{
    /// <summary>
    /// Get setting value
    /// </summary>
    T? GetSetting<T>(string key, T? defaultValue = default);

    /// <summary>
    /// Set setting value
    /// </summary>
    void SetSetting<T>(string key, T value);

    /// <summary>
    /// Delete setting
    /// </summary>
    void DeleteSetting(string key);

    /// <summary>
    /// Check if setting exists
    /// </summary>
    bool HasSetting(string key);

    /// <summary>
    /// Save settings to disk
    /// </summary>
    Task SaveAsync();

    /// <summary>
    /// Load settings from disk
    /// </summary>
    Task LoadAsync();

    /// <summary>
    /// Get all settings
    /// </summary>
    Dictionary<string, object> GetAllSettings();

    /// <summary>
    /// Clear all settings
    /// </summary>
    void ClearAll();
}
