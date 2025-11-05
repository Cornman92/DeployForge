namespace DeployForge.Common.Models;

/// <summary>
/// Configuration for autounattend.xml generation
/// </summary>
public class AutounattendConfig
{
    /// <summary>
    /// Product key (empty for no key)
    /// </summary>
    public string ProductKey { get; set; } = string.Empty;

    /// <summary>
    /// Computer name (empty for auto-generate)
    /// </summary>
    public string ComputerName { get; set; } = string.Empty;

    /// <summary>
    /// Administrator password
    /// </summary>
    public string AdministratorPassword { get; set; } = string.Empty;

    /// <summary>
    /// Full name
    /// </summary>
    public string FullName { get; set; } = "User";

    /// <summary>
    /// Organization
    /// </summary>
    public string Organization { get; set; } = string.Empty;

    /// <summary>
    /// Time zone
    /// </summary>
    public string TimeZone { get; set; } = "Pacific Standard Time";

    /// <summary>
    /// UI Language
    /// </summary>
    public string UILanguage { get; set; } = "en-US";

    /// <summary>
    /// Input locale
    /// </summary>
    public string InputLocale { get; set; } = "en-US";

    /// <summary>
    /// System locale
    /// </summary>
    public string SystemLocale { get; set; } = "en-US";

    /// <summary>
    /// User locale
    /// </summary>
    public string UserLocale { get; set; } = "en-US";

    /// <summary>
    /// Disk configuration
    /// </summary>
    public DiskConfiguration DiskConfig { get; set; } = new();

    /// <summary>
    /// Skip OOBE screens
    /// </summary>
    public bool SkipOOBE { get; set; } = true;

    /// <summary>
    /// Skip privacy settings
    /// </summary>
    public bool SkipPrivacySettings { get; set; } = true;

    /// <summary>
    /// Skip Cortana
    /// </summary>
    public bool SkipCortana { get; set; } = true;

    /// <summary>
    /// Disable Windows Defender
    /// </summary>
    public bool DisableDefender { get; set; }

    /// <summary>
    /// Disable telemetry
    /// </summary>
    public bool DisableTelemetry { get; set; }

    /// <summary>
    /// Auto logon count (0 for disabled)
    /// </summary>
    public int AutoLogonCount { get; set; }

    /// <summary>
    /// First logon commands to execute
    /// </summary>
    public List<FirstLogonCommand> FirstLogonCommands { get; set; } = new();

    /// <summary>
    /// User accounts to create
    /// </summary>
    public List<UserAccount> UserAccounts { get; set; } = new();

    /// <summary>
    /// Network configuration
    /// </summary>
    public NetworkConfiguration? NetworkConfig { get; set; }
}

/// <summary>
/// Disk configuration for installation
/// </summary>
public class DiskConfiguration
{
    /// <summary>
    /// Disk ID to install to (0-based)
    /// </summary>
    public int DiskId { get; set; }

    /// <summary>
    /// Wipe disk before installation
    /// </summary>
    public bool WipeDisk { get; set; } = true;

    /// <summary>
    /// Partition layout
    /// </summary>
    public PartitionLayout Layout { get; set; } = PartitionLayout.UEFI;

    /// <summary>
    /// Install to partition number
    /// </summary>
    public int InstallToPartition { get; set; }
}

/// <summary>
/// Partition layouts
/// </summary>
public enum PartitionLayout
{
    /// <summary>
    /// UEFI GPT layout (EFI + MSR + Windows)
    /// </summary>
    UEFI,

    /// <summary>
    /// Legacy BIOS MBR layout
    /// </summary>
    BIOS,

    /// <summary>
    /// Custom layout
    /// </summary>
    Custom
}

/// <summary>
/// Command to execute on first logon
/// </summary>
public class FirstLogonCommand
{
    /// <summary>
    /// Command order
    /// </summary>
    public int Order { get; set; }

    /// <summary>
    /// Command to execute
    /// </summary>
    public string CommandLine { get; set; } = string.Empty;

    /// <summary>
    /// Description
    /// </summary>
    public string Description { get; set; } = string.Empty;
}

/// <summary>
/// User account to create
/// </summary>
public class UserAccount
{
    /// <summary>
    /// Username
    /// </summary>
    public string Username { get; set; } = string.Empty;

    /// <summary>
    /// Password
    /// </summary>
    public string Password { get; set; } = string.Empty;

    /// <summary>
    /// Display name
    /// </summary>
    public string DisplayName { get; set; } = string.Empty;

    /// <summary>
    /// Group (Administrators, Users, etc.)
    /// </summary>
    public string Group { get; set; } = "Users";
}

/// <summary>
/// Network configuration
/// </summary>
public class NetworkConfiguration
{
    /// <summary>
    /// Use DHCP
    /// </summary>
    public bool UseDHCP { get; set; } = true;

    /// <summary>
    /// Static IP address (if not DHCP)
    /// </summary>
    public string? IPAddress { get; set; }

    /// <summary>
    /// Subnet mask
    /// </summary>
    public string? SubnetMask { get; set; }

    /// <summary>
    /// Default gateway
    /// </summary>
    public string? DefaultGateway { get; set; }

    /// <summary>
    /// DNS servers
    /// </summary>
    public List<string> DNSServers { get; set; } = new();

    /// <summary>
    /// Domain to join
    /// </summary>
    public string? Domain { get; set; }

    /// <summary>
    /// Domain credentials
    /// </summary>
    public DomainCredentials? DomainCredentials { get; set; }
}

/// <summary>
/// Credentials for domain join
/// </summary>
public class DomainCredentials
{
    /// <summary>
    /// Domain username
    /// </summary>
    public string Username { get; set; } = string.Empty;

    /// <summary>
    /// Domain password
    /// </summary>
    public string Password { get; set; } = string.Empty;
}
