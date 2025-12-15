namespace DeployForge.Core.Models;

/// <summary>
/// Configuration for generating Windows answer files (unattend.xml).
/// </summary>
public class UnattendConfig
{
    /// <summary>
    /// Computer name (empty for random).
    /// </summary>
    public string ComputerName { get; set; } = string.Empty;
    
    /// <summary>
    /// Organization name.
    /// </summary>
    public string Organization { get; set; } = string.Empty;
    
    /// <summary>
    /// Owner name.
    /// </summary>
    public string Owner { get; set; } = string.Empty;
    
    /// <summary>
    /// Product key (empty for trial).
    /// </summary>
    public string ProductKey { get; set; } = string.Empty;
    
    /// <summary>
    /// User accounts to create.
    /// </summary>
    public List<UserAccount> Users { get; set; } = new();
    
    /// <summary>
    /// Regional settings.
    /// </summary>
    public RegionalSettings Regional { get; set; } = new();
    
    /// <summary>
    /// OOBE (Out of Box Experience) settings.
    /// </summary>
    public OobeSettings Oobe { get; set; } = new();
    
    /// <summary>
    /// Network configuration.
    /// </summary>
    public NetworkSettings Network { get; set; } = new();
    
    /// <summary>
    /// Disk configuration for the answer file.
    /// </summary>
    public DiskSettings? Disk { get; set; }
    
    /// <summary>
    /// First-run commands to execute.
    /// </summary>
    public List<FirstRunCommand> FirstRunCommands { get; set; } = new();
    
    /// <summary>
    /// Skip OOBE entirely.
    /// </summary>
    public bool SkipOobe { get; set; } = true;
    
    /// <summary>
    /// Auto-login to first user.
    /// </summary>
    public bool AutoLogon { get; set; }
    
    /// <summary>
    /// Number of auto-logon attempts.
    /// </summary>
    public int AutoLogonCount { get; set; } = 1;
    
    /// <summary>
    /// Creates a basic unattend configuration.
    /// </summary>
    public static UnattendConfig CreateBasic(
        string computerName = "", 
        string userName = "User", 
        string password = "",
        string locale = "en-US")
    {
        return new UnattendConfig
        {
            ComputerName = computerName,
            SkipOobe = true,
            Users = new List<UserAccount>
            {
                new()
                {
                    Name = userName,
                    Password = password,
                    IsAdministrator = true,
                    AutoLogon = true
                }
            },
            Regional = new RegionalSettings
            {
                UILanguage = locale,
                InputLocale = locale,
                SystemLocale = locale,
                UserLocale = locale
            }
        };
    }
    
    /// <summary>
    /// Creates an enterprise configuration.
    /// </summary>
    public static UnattendConfig CreateEnterprise(
        string organization,
        string productKey = "",
        string locale = "en-US")
    {
        return new UnattendConfig
        {
            Organization = organization,
            ProductKey = productKey,
            SkipOobe = true,
            Regional = new RegionalSettings
            {
                UILanguage = locale,
                InputLocale = locale,
                SystemLocale = locale,
                UserLocale = locale
            },
            Oobe = new OobeSettings
            {
                HideEULAPage = true,
                HideOEMRegistrationScreen = true,
                HideOnlineAccountScreens = true,
                HideWirelessSetupInOOBE = false,
                NetworkLocation = "Work",
                ProtectYourPC = 3 // Don't enable
            },
            Network = new NetworkSettings
            {
                JoinDomain = true
            }
        };
    }
}

/// <summary>
/// User account configuration.
/// </summary>
public class UserAccount
{
    /// <summary>
    /// User account name.
    /// </summary>
    public string Name { get; set; } = string.Empty;
    
    /// <summary>
    /// Account password.
    /// </summary>
    public string Password { get; set; } = string.Empty;
    
    /// <summary>
    /// Display name.
    /// </summary>
    public string DisplayName { get; set; } = string.Empty;
    
    /// <summary>
    /// Account description.
    /// </summary>
    public string Description { get; set; } = string.Empty;
    
    /// <summary>
    /// Whether the user is an administrator.
    /// </summary>
    public bool IsAdministrator { get; set; }
    
    /// <summary>
    /// Enable auto-logon for this user.
    /// </summary>
    public bool AutoLogon { get; set; }
    
    /// <summary>
    /// Whether password expires.
    /// </summary>
    public bool PasswordExpires { get; set; }
    
    /// <summary>
    /// Group memberships.
    /// </summary>
    public List<string> Groups { get; set; } = new() { "Users" };
}

/// <summary>
/// Regional and language settings.
/// </summary>
public class RegionalSettings
{
    /// <summary>
    /// UI language (e.g., en-US).
    /// </summary>
    public string UILanguage { get; set; } = "en-US";
    
    /// <summary>
    /// Input locale.
    /// </summary>
    public string InputLocale { get; set; } = "en-US";
    
    /// <summary>
    /// System locale.
    /// </summary>
    public string SystemLocale { get; set; } = "en-US";
    
    /// <summary>
    /// User locale.
    /// </summary>
    public string UserLocale { get; set; } = "en-US";
    
    /// <summary>
    /// Timezone (e.g., Pacific Standard Time).
    /// </summary>
    public string TimeZone { get; set; } = "Pacific Standard Time";
    
    /// <summary>
    /// Keyboard layout.
    /// </summary>
    public string KeyboardLayout { get; set; } = "0409:00000409";
    
    /// <summary>
    /// Fallback languages.
    /// </summary>
    public List<string> UILanguageFallback { get; set; } = new();
}

/// <summary>
/// OOBE (Out of Box Experience) settings.
/// </summary>
public class OobeSettings
{
    /// <summary>
    /// Hide the EULA page.
    /// </summary>
    public bool HideEULAPage { get; set; } = true;
    
    /// <summary>
    /// Hide OEM registration.
    /// </summary>
    public bool HideOEMRegistrationScreen { get; set; } = true;
    
    /// <summary>
    /// Hide online account screens.
    /// </summary>
    public bool HideOnlineAccountScreens { get; set; } = true;
    
    /// <summary>
    /// Hide wireless setup.
    /// </summary>
    public bool HideWirelessSetupInOOBE { get; set; }
    
    /// <summary>
    /// Hide local account screen.
    /// </summary>
    public bool HideLocalAccountScreen { get; set; }
    
    /// <summary>
    /// Network location (Home, Work, Public).
    /// </summary>
    public string NetworkLocation { get; set; } = "Home";
    
    /// <summary>
    /// Protect your PC option (1=On, 2=Off, 3=Skip).
    /// </summary>
    public int ProtectYourPC { get; set; } = 3;
    
    /// <summary>
    /// Skip machine OOBE.
    /// </summary>
    public bool SkipMachineOOBE { get; set; } = true;
    
    /// <summary>
    /// Skip user OOBE.
    /// </summary>
    public bool SkipUserOOBE { get; set; } = true;
}

/// <summary>
/// Network configuration settings.
/// </summary>
public class NetworkSettings
{
    /// <summary>
    /// Join a domain.
    /// </summary>
    public bool JoinDomain { get; set; }
    
    /// <summary>
    /// Domain name to join.
    /// </summary>
    public string DomainName { get; set; } = string.Empty;
    
    /// <summary>
    /// Domain join account.
    /// </summary>
    public string DomainAccount { get; set; } = string.Empty;
    
    /// <summary>
    /// Domain join password.
    /// </summary>
    public string DomainPassword { get; set; } = string.Empty;
    
    /// <summary>
    /// Organizational unit for the computer.
    /// </summary>
    public string OrganizationalUnit { get; set; } = string.Empty;
    
    /// <summary>
    /// Static IP configuration.
    /// </summary>
    public StaticIpConfig? StaticIp { get; set; }
}

/// <summary>
/// Static IP configuration.
/// </summary>
public class StaticIpConfig
{
    /// <summary>
    /// IP address.
    /// </summary>
    public string IpAddress { get; set; } = string.Empty;
    
    /// <summary>
    /// Subnet mask.
    /// </summary>
    public string SubnetMask { get; set; } = "255.255.255.0";
    
    /// <summary>
    /// Default gateway.
    /// </summary>
    public string Gateway { get; set; } = string.Empty;
    
    /// <summary>
    /// DNS servers.
    /// </summary>
    public List<string> DnsServers { get; set; } = new();
}

/// <summary>
/// Disk configuration for answer file.
/// </summary>
public class DiskSettings
{
    /// <summary>
    /// Disk number to use.
    /// </summary>
    public int DiskNumber { get; set; }
    
    /// <summary>
    /// Whether to wipe the disk.
    /// </summary>
    public bool WipeDisk { get; set; } = true;
    
    /// <summary>
    /// Partition configurations.
    /// </summary>
    public List<UnattendPartition> Partitions { get; set; } = new();
    
    /// <summary>
    /// Creates a standard UEFI disk configuration.
    /// </summary>
    public static DiskSettings CreateUefi()
    {
        return new DiskSettings
        {
            WipeDisk = true,
            Partitions = new List<UnattendPartition>
            {
                new() { Order = 1, Type = "EFI", Size = 260, Format = "FAT32", Label = "System" },
                new() { Order = 2, Type = "MSR", Size = 16 },
                new() { Order = 3, Type = "Primary", Format = "NTFS", Label = "Windows", Extend = true },
                new() { Order = 4, Type = "Recovery", Size = 1024, Format = "NTFS", Label = "Recovery" }
            }
        };
    }
}

/// <summary>
/// Partition configuration for answer file.
/// </summary>
public class UnattendPartition
{
    /// <summary>
    /// Partition order.
    /// </summary>
    public int Order { get; set; }
    
    /// <summary>
    /// Partition type (EFI, MSR, Primary, Recovery).
    /// </summary>
    public string Type { get; set; } = "Primary";
    
    /// <summary>
    /// Size in MB (0 = extend).
    /// </summary>
    public int Size { get; set; }
    
    /// <summary>
    /// Whether to extend to fill remaining space.
    /// </summary>
    public bool Extend { get; set; }
    
    /// <summary>
    /// File system format.
    /// </summary>
    public string Format { get; set; } = "NTFS";
    
    /// <summary>
    /// Partition label.
    /// </summary>
    public string Label { get; set; } = string.Empty;
}

/// <summary>
/// First-run command to execute.
/// </summary>
public class FirstRunCommand
{
    /// <summary>
    /// Command order (execution priority).
    /// </summary>
    public int Order { get; set; }
    
    /// <summary>
    /// Command description.
    /// </summary>
    public string Description { get; set; } = string.Empty;
    
    /// <summary>
    /// Command to execute.
    /// </summary>
    public string Command { get; set; } = string.Empty;
    
    /// <summary>
    /// Whether to require network.
    /// </summary>
    public bool RequireNetwork { get; set; }
    
    /// <summary>
    /// Whether to run asynchronously.
    /// </summary>
    public bool RunAsync { get; set; }
}
