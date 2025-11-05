namespace DeployForge.Common.Models;

/// <summary>
/// Represents a registry key
/// </summary>
public class RegistryKeyInfo
{
    /// <summary>
    /// Full path to the registry key
    /// </summary>
    public string Path { get; set; } = string.Empty;

    /// <summary>
    /// Key name
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// Parent key path
    /// </summary>
    public string ParentPath { get; set; } = string.Empty;

    /// <summary>
    /// Subkey count
    /// </summary>
    public int SubKeyCount { get; set; }

    /// <summary>
    /// Value count
    /// </summary>
    public int ValueCount { get; set; }

    /// <summary>
    /// Last write time
    /// </summary>
    public DateTime? LastWriteTime { get; set; }
}

/// <summary>
/// Represents a registry value
/// </summary>
public class RegistryValueInfo
{
    /// <summary>
    /// Value name
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// Value type
    /// </summary>
    public RegistryValueType Type { get; set; }

    /// <summary>
    /// Value data
    /// </summary>
    public object? Data { get; set; }

    /// <summary>
    /// String representation of data
    /// </summary>
    public string DataString { get; set; } = string.Empty;

    /// <summary>
    /// Parent key path
    /// </summary>
    public string KeyPath { get; set; } = string.Empty;
}

/// <summary>
/// Registry value types
/// </summary>
public enum RegistryValueType
{
    /// <summary>
    /// String value (REG_SZ)
    /// </summary>
    String,

    /// <summary>
    /// Expandable string (REG_EXPAND_SZ)
    /// </summary>
    ExpandString,

    /// <summary>
    /// Binary data (REG_BINARY)
    /// </summary>
    Binary,

    /// <summary>
    /// DWORD (32-bit integer, REG_DWORD)
    /// </summary>
    DWord,

    /// <summary>
    /// QWORD (64-bit integer, REG_QWORD)
    /// </summary>
    QWord,

    /// <summary>
    /// Multi-string (REG_MULTI_SZ)
    /// </summary>
    MultiString,

    /// <summary>
    /// Unknown or unsupported type
    /// </summary>
    Unknown
}

/// <summary>
/// Registry hive types
/// </summary>
public enum RegistryHiveType
{
    /// <summary>
    /// HKEY_LOCAL_MACHINE\SOFTWARE
    /// </summary>
    Software,

    /// <summary>
    /// HKEY_LOCAL_MACHINE\SYSTEM
    /// </summary>
    System,

    /// <summary>
    /// HKEY_USERS\.DEFAULT (Default user profile)
    /// </summary>
    DefaultUser,

    /// <summary>
    /// NTUSER.DAT (User profile)
    /// </summary>
    User,

    /// <summary>
    /// Custom hive
    /// </summary>
    Custom
}
