namespace DeployForge.App.Models;

public record Profile
{
    public string Id { get; init; } = Guid.NewGuid().ToString();
    public string Name { get; init; } = string.Empty;
    public string Description { get; init; } = string.Empty;
    public ProfileType Type { get; init; }
    public string IconGlyph { get; init; } = "\uE71C";
    public bool IsBuiltIn { get; init; }
    public ProfileFeatures Features { get; init; } = new();
    public DateTime CreatedAt { get; init; } = DateTime.Now;
    public DateTime ModifiedAt { get; init; } = DateTime.Now;
}

public enum ProfileType
{
    Gaming,
    Developer,
    Enterprise,
    Student,
    Creator,
    Minimal,
    Custom
}

public record ProfileFeatures
{
    // Debloat
    public bool RemoveBloatware { get; init; }
    public DebloatLevel DebloatLevel { get; init; } = DebloatLevel.Moderate;
    
    // Privacy
    public bool DisableTelemetry { get; init; }
    public bool DisableCortana { get; init; }
    public bool BlockTelemetryDomains { get; init; }
    public PrivacyLevel PrivacyLevel { get; init; } = PrivacyLevel.Balanced;
    
    // Gaming
    public bool EnableGameMode { get; init; }
    public bool InstallGamingRuntimes { get; init; }
    public bool OptimizeNetwork { get; init; }
    public GamingProfile GamingProfile { get; init; } = GamingProfile.Balanced;
    
    // Developer
    public bool EnableDeveloperMode { get; init; }
    public bool InstallWSL2 { get; init; }
    public List<string> DevTools { get; init; } = new();
    
    // Performance
    public bool OptimizeServices { get; init; }
    public bool DisableAnimations { get; init; }
    public bool EnableUltimatePerformance { get; init; }
    
    // UI
    public bool CustomizeTaskbar { get; init; }
    public bool DarkTheme { get; init; }
    
    // Additional
    public List<string> BrowsersToInstall { get; init; } = new();
    public List<string> DriversToInject { get; init; } = new();
    public List<RegistryTweak> RegistryTweaks { get; init; } = new();
}

public enum DebloatLevel { Light, Moderate, Aggressive, Extreme }
public enum PrivacyLevel { Minimal, Balanced, Aggressive, Paranoid }
public enum GamingProfile { Minimal, Balanced, Performance, Extreme }

public record RegistryTweak
{
    public string Hive { get; init; } = string.Empty;
    public string Path { get; init; } = string.Empty;
    public string Name { get; init; } = string.Empty;
    public string Value { get; init; } = string.Empty;
    public string Type { get; init; } = "REG_DWORD";
}
