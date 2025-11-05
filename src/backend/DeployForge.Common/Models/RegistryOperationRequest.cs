namespace DeployForge.Common.Models;

/// <summary>
/// Request to load a registry hive
/// </summary>
public class LoadHiveRequest
{
    /// <summary>
    /// Path to mounted image
    /// </summary>
    public string MountPath { get; set; } = string.Empty;

    /// <summary>
    /// Type of hive to load
    /// </summary>
    public RegistryHiveType HiveType { get; set; }

    /// <summary>
    /// Custom hive file path (if HiveType is Custom)
    /// </summary>
    public string? CustomHivePath { get; set; }

    /// <summary>
    /// Mount point in registry (e.g., "HKLM\TempHive")
    /// </summary>
    public string MountPoint { get; set; } = "HKLM\\DeployForge_Temp";
}

/// <summary>
/// Request to set a registry value
/// </summary>
public class SetRegistryValueRequest
{
    /// <summary>
    /// Mount point where hive is loaded
    /// </summary>
    public string MountPoint { get; set; } = string.Empty;

    /// <summary>
    /// Full key path
    /// </summary>
    public string KeyPath { get; set; } = string.Empty;

    /// <summary>
    /// Value name
    /// </summary>
    public string ValueName { get; set; } = string.Empty;

    /// <summary>
    /// Value type
    /// </summary>
    public RegistryValueType ValueType { get; set; }

    /// <summary>
    /// Value data
    /// </summary>
    public object? Data { get; set; }
}

/// <summary>
/// Request to delete a registry key or value
/// </summary>
public class DeleteRegistryRequest
{
    /// <summary>
    /// Mount point where hive is loaded
    /// </summary>
    public string MountPoint { get; set; } = string.Empty;

    /// <summary>
    /// Full key path
    /// </summary>
    public string KeyPath { get; set; } = string.Empty;

    /// <summary>
    /// Value name (null to delete entire key)
    /// </summary>
    public string? ValueName { get; set; }

    /// <summary>
    /// Recursive delete (for keys with subkeys)
    /// </summary>
    public bool Recursive { get; set; }
}

/// <summary>
/// Request to import a .reg file
/// </summary>
public class ImportRegFileRequest
{
    /// <summary>
    /// Path to mounted image
    /// </summary>
    public string MountPath { get; set; } = string.Empty;

    /// <summary>
    /// Path to .reg file
    /// </summary>
    public string RegFilePath { get; set; } = string.Empty;

    /// <summary>
    /// Hive type to apply changes to
    /// </summary>
    public RegistryHiveType HiveType { get; set; }
}

/// <summary>
/// Request to export registry keys to .reg file
/// </summary>
public class ExportRegFileRequest
{
    /// <summary>
    /// Mount point where hive is loaded
    /// </summary>
    public string MountPoint { get; set; } = string.Empty;

    /// <summary>
    /// Key paths to export
    /// </summary>
    public List<string> KeyPaths { get; set; } = new();

    /// <summary>
    /// Output .reg file path
    /// </summary>
    public string OutputPath { get; set; } = string.Empty;
}

/// <summary>
/// Registry tweak preset
/// </summary>
public class RegistryTweakPreset
{
    /// <summary>
    /// Preset name
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// Preset description
    /// </summary>
    public string Description { get; set; } = string.Empty;

    /// <summary>
    /// Category (Performance, Privacy, Gaming, etc.)
    /// </summary>
    public string Category { get; set; } = string.Empty;

    /// <summary>
    /// List of registry modifications
    /// </summary>
    public List<RegistryTweak> Tweaks { get; set; } = new();
}

/// <summary>
/// Individual registry tweak
/// </summary>
public class RegistryTweak
{
    /// <summary>
    /// Hive type
    /// </summary>
    public RegistryHiveType HiveType { get; set; }

    /// <summary>
    /// Key path (relative to hive)
    /// </summary>
    public string KeyPath { get; set; } = string.Empty;

    /// <summary>
    /// Value name
    /// </summary>
    public string ValueName { get; set; } = string.Empty;

    /// <summary>
    /// Value type
    /// </summary>
    public RegistryValueType ValueType { get; set; }

    /// <summary>
    /// Value data
    /// </summary>
    public object? Data { get; set; }

    /// <summary>
    /// Description of what this tweak does
    /// </summary>
    public string Description { get; set; } = string.Empty;
}
