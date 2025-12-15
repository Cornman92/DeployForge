using DeployForge.Core.Enums;

namespace DeployForge.Core.Models;

/// <summary>
/// Complete build profile for image customization.
/// </summary>
public class BuildProfile
{
    /// <summary>
    /// Profile name.
    /// </summary>
    public string Name { get; set; } = string.Empty;
    
    /// <summary>
    /// Profile description.
    /// </summary>
    public string Description { get; set; } = string.Empty;
    
    /// <summary>
    /// Profile type.
    /// </summary>
    public BuildProfileType Type { get; set; } = BuildProfileType.Custom;
    
    /// <summary>
    /// Profile icon (emoji or icon name).
    /// </summary>
    public string Icon { get; set; } = "⚙️";
    
    // Feature Toggles
    
    /// <summary>
    /// Gaming optimization settings.
    /// </summary>
    public GamingConfig? Gaming { get; set; }
    
    /// <summary>
    /// Debloat and privacy settings.
    /// </summary>
    public DebloatConfig? Debloat { get; set; }
    
    /// <summary>
    /// Developer environment settings.
    /// </summary>
    public DevEnvironmentConfig? DevEnvironment { get; set; }
    
    /// <summary>
    /// Browser configuration.
    /// </summary>
    public BrowserConfig? Browsers { get; set; }
    
    /// <summary>
    /// UI customization settings.
    /// </summary>
    public UIConfig? UICustomization { get; set; }
    
    /// <summary>
    /// Privacy hardening level.
    /// </summary>
    public PrivacyLevel PrivacyLevel { get; set; } = PrivacyLevel.Standard;
    
    // Feature Flags
    
    /// <summary>
    /// Enable gaming optimizations.
    /// </summary>
    public bool EnableGaming { get; set; }
    
    /// <summary>
    /// Enable bloatware removal.
    /// </summary>
    public bool EnableDebloat { get; set; }
    
    /// <summary>
    /// Enable developer environment.
    /// </summary>
    public bool EnableDevEnvironment { get; set; }
    
    /// <summary>
    /// Enable browser installation.
    /// </summary>
    public bool EnableBrowsers { get; set; }
    
    /// <summary>
    /// Enable UI customization.
    /// </summary>
    public bool EnableUICustomization { get; set; }
    
    /// <summary>
    /// Enable privacy hardening.
    /// </summary>
    public bool EnablePrivacyHardening { get; set; }
    
    /// <summary>
    /// Enable Windows feature management.
    /// </summary>
    public bool EnableFeatureManagement { get; set; }
    
    /// <summary>
    /// Enable driver integration.
    /// </summary>
    public bool EnableDrivers { get; set; }
    
    /// <summary>
    /// Enable updates integration.
    /// </summary>
    public bool EnableUpdates { get; set; }

    /// <summary>
    /// Creates a Gaming profile.
    /// </summary>
    public static BuildProfile CreateGamingProfile() => new()
    {
        Name = "Gaming",
        Description = "Optimized for gaming performance with reduced latency and bloatware removal",
        Type = BuildProfileType.Gaming,
        Icon = "🎮",
        EnableGaming = true,
        EnableDebloat = true,
        EnablePrivacyHardening = true,
        Gaming = GamingConfig.FromProfile(GamingProfile.Competitive),
        Debloat = DebloatConfig.Default,
        PrivacyLevel = PrivacyLevel.Standard
    };

    /// <summary>
    /// Creates a Developer profile.
    /// </summary>
    public static BuildProfile CreateDeveloperProfile() => new()
    {
        Name = "Developer",
        Description = "Full-stack development environment with IDEs, languages, and tools",
        Type = BuildProfileType.Developer,
        Icon = "💻",
        EnableDevEnvironment = true,
        EnableBrowsers = true,
        EnableDebloat = true,
        DevEnvironment = new DevEnvironmentConfig
        {
            Profile = DevelopmentProfile.FullStack,
            EnableDeveloperMode = true,
            EnableWSL2 = true,
            InstallGit = true,
            InstallDocker = true
        },
        Browsers = new BrowserConfig
        {
            Profile = BrowserProfile.Developer,
            Browsers = new List<BrowserType> { BrowserType.Chrome, BrowserType.Firefox, BrowserType.Edge }
        },
        Debloat = DebloatConfig.Default
    };

    /// <summary>
    /// Creates an Enterprise profile.
    /// </summary>
    public static BuildProfile CreateEnterpriseProfile() => new()
    {
        Name = "Enterprise",
        Description = "Corporate workstation with security hardening and policy compliance",
        Type = BuildProfileType.Enterprise,
        Icon = "🏢",
        EnableDebloat = true,
        EnablePrivacyHardening = true,
        EnableBrowsers = true,
        PrivacyLevel = PrivacyLevel.Maximum,
        Browsers = new BrowserConfig
        {
            Profile = BrowserProfile.Enterprise,
            Browsers = new List<BrowserType> { BrowserType.Edge, BrowserType.Chrome }
        },
        Debloat = new DebloatConfig
        {
            Level = DebloatLevel.Aggressive,
            DisableTelemetry = true,
            DisableCortana = true
        }
    };

    /// <summary>
    /// Creates a Student profile.
    /// </summary>
    public static BuildProfile CreateStudentProfile() => new()
    {
        Name = "Student",
        Description = "Education-focused setup with productivity tools and learning resources",
        Type = BuildProfileType.Student,
        Icon = "📚",
        EnableDebloat = true,
        EnableBrowsers = true,
        Debloat = new DebloatConfig { Level = DebloatLevel.Minimal },
        Browsers = new BrowserConfig
        {
            Browsers = new List<BrowserType> { BrowserType.Chrome, BrowserType.Edge }
        }
    };

    /// <summary>
    /// Creates a Creator profile.
    /// </summary>
    public static BuildProfile CreateCreatorProfile() => new()
    {
        Name = "Creator",
        Description = "Content creation setup with multimedia tools and creative software",
        Type = BuildProfileType.Creator,
        Icon = "🎨",
        EnableDebloat = true,
        EnableBrowsers = true,
        Debloat = new DebloatConfig { Level = DebloatLevel.Minimal },
        Browsers = new BrowserConfig
        {
            Browsers = new List<BrowserType> { BrowserType.Chrome, BrowserType.Firefox }
        }
    };
}

/// <summary>
/// Developer environment configuration.
/// </summary>
public class DevEnvironmentConfig
{
    /// <summary>
    /// Development profile.
    /// </summary>
    public DevelopmentProfile Profile { get; set; } = DevelopmentProfile.Minimal;
    
    /// <summary>
    /// Enable Windows Developer Mode.
    /// </summary>
    public bool EnableDeveloperMode { get; set; } = true;
    
    /// <summary>
    /// Enable WSL2.
    /// </summary>
    public bool EnableWSL2 { get; set; } = true;
    
    /// <summary>
    /// Install Git.
    /// </summary>
    public bool InstallGit { get; set; } = true;
    
    /// <summary>
    /// Install Docker Desktop.
    /// </summary>
    public bool InstallDocker { get; set; } = false;
    
    /// <summary>
    /// IDEs to install.
    /// </summary>
    public List<string> IDEs { get; set; } = new() { "vscode" };
    
    /// <summary>
    /// Programming languages to install.
    /// </summary>
    public List<string> Languages { get; set; } = new() { "python", "nodejs" };
    
    /// <summary>
    /// Development tools to install.
    /// </summary>
    public List<string> Tools { get; set; } = new();
    
    /// <summary>
    /// Cloud CLI tools to install.
    /// </summary>
    public List<string> CloudTools { get; set; } = new();
}

/// <summary>
/// Browser configuration.
/// </summary>
public class BrowserConfig
{
    /// <summary>
    /// Browser profile.
    /// </summary>
    public BrowserProfile Profile { get; set; } = BrowserProfile.Minimal;
    
    /// <summary>
    /// Browsers to install.
    /// </summary>
    public List<BrowserType> Browsers { get; set; } = new() { BrowserType.Chrome };
    
    /// <summary>
    /// Default browser.
    /// </summary>
    public BrowserType? DefaultBrowser { get; set; }
    
    /// <summary>
    /// Block third-party cookies.
    /// </summary>
    public bool BlockThirdPartyCookies { get; set; } = true;
    
    /// <summary>
    /// Enable Do Not Track.
    /// </summary>
    public bool EnableDoNotTrack { get; set; } = true;
    
    /// <summary>
    /// Disable browser telemetry.
    /// </summary>
    public bool DisableTelemetry { get; set; } = false;
    
    /// <summary>
    /// Configure enterprise policies.
    /// </summary>
    public bool ConfigureEnterprisePolicies { get; set; } = false;
}

/// <summary>
/// UI customization configuration.
/// </summary>
public class UIConfig
{
    /// <summary>
    /// UI profile.
    /// </summary>
    public UIProfile Profile { get; set; } = UIProfile.Minimal;
    
    /// <summary>
    /// Enable dark mode.
    /// </summary>
    public bool EnableDarkMode { get; set; } = true;
    
    /// <summary>
    /// Hide taskbar search.
    /// </summary>
    public bool HideTaskbarSearch { get; set; } = false;
    
    /// <summary>
    /// Hide task view button.
    /// </summary>
    public bool HideTaskView { get; set; } = false;
    
    /// <summary>
    /// Hide widgets.
    /// </summary>
    public bool HideWidgets { get; set; } = true;
    
    /// <summary>
    /// Hide chat icon.
    /// </summary>
    public bool HideChat { get; set; } = true;
    
    /// <summary>
    /// Use small taskbar icons.
    /// </summary>
    public bool SmallTaskbarIcons { get; set; } = false;
    
    /// <summary>
    /// Show file extensions.
    /// </summary>
    public bool ShowFileExtensions { get; set; } = true;
    
    /// <summary>
    /// Show hidden files.
    /// </summary>
    public bool ShowHiddenFiles { get; set; } = false;
}
