namespace DeployForge.Core.Enums;

/// <summary>
/// Supported Windows deployment image formats.
/// </summary>
public enum ImageFormat
{
    /// <summary>Windows Imaging Format</summary>
    WIM,
    
    /// <summary>Electronic Software Distribution (compressed WIM)</summary>
    ESD,
    
    /// <summary>Virtual Hard Disk (legacy)</summary>
    VHD,
    
    /// <summary>Hyper-V Virtual Hard Disk</summary>
    VHDX,
    
    /// <summary>ISO 9660 optical disc image</summary>
    ISO,
    
    /// <summary>Provisioning Package</summary>
    PPKG
}

/// <summary>
/// Gaming optimization profiles.
/// </summary>
public enum GamingProfile
{
    /// <summary>Maximum performance with minimal latency for competitive gaming</summary>
    Competitive,
    
    /// <summary>Good performance with some quality features enabled</summary>
    Balanced,
    
    /// <summary>Best visual quality with gaming optimizations</summary>
    Quality,
    
    /// <summary>Optimized for game streaming</summary>
    Streaming
}

/// <summary>
/// Development environment profiles.
/// </summary>
public enum DevelopmentProfile
{
    /// <summary>HTML, CSS, JavaScript, TypeScript, React, Vue, Angular</summary>
    WebFrontend,
    
    /// <summary>Node.js, Python, Java, databases</summary>
    WebBackend,
    
    /// <summary>Complete web development stack</summary>
    FullStack,
    
    /// <summary>Android, iOS, React Native, Flutter</summary>
    Mobile,
    
    /// <summary>Python, R, Jupyter, ML frameworks</summary>
    DataScience,
    
    /// <summary>Docker, Kubernetes, Terraform, CI/CD</summary>
    DevOps,
    
    /// <summary>Unity, Unreal, C++, game development</summary>
    GameDev,
    
    /// <summary>C, C++, Arduino, embedded systems</summary>
    Embedded,
    
    /// <summary>.NET, Electron, Qt, wxWidgets</summary>
    Desktop,
    
    /// <summary>Just essentials (Git, editor, one language)</summary>
    Minimal
}

/// <summary>
/// Bloatware removal levels.
/// </summary>
public enum DebloatLevel
{
    /// <summary>Remove only obvious bloat apps</summary>
    Minimal,
    
    /// <summary>Remove most unnecessary apps (default)</summary>
    Moderate,
    
    /// <summary>Remove everything non-essential</summary>
    Aggressive
}

/// <summary>
/// Browser types for installation.
/// </summary>
public enum BrowserType
{
    Chrome,
    Firefox,
    Edge,
    Brave,
    Opera,
    OperaGX,
    Vivaldi,
    TorBrowser,
    LibreWolf,
    Waterfox,
    ChromeDev,
    ChromeCanary,
    FirefoxDeveloper,
    FirefoxNightly,
    EdgeDev,
    Chromium,
    UngoogledChromium
}

/// <summary>
/// Browser configuration profiles.
/// </summary>
public enum BrowserProfile
{
    /// <summary>Privacy-centric browsers with hardened settings</summary>
    PrivacyFocused,
    
    /// <summary>Speed-optimized browsers</summary>
    Performance,
    
    /// <summary>Multiple browsers for cross-browser testing</summary>
    Developer,
    
    /// <summary>Corporate-managed browsers with policies</summary>
    Enterprise,
    
    /// <summary>Single mainstream browser</summary>
    Minimal,
    
    /// <summary>All major browsers for maximum compatibility</summary>
    Complete
}

/// <summary>
/// Privacy hardening levels.
/// </summary>
public enum PrivacyLevel
{
    /// <summary>Basic privacy settings</summary>
    Basic,
    
    /// <summary>Standard privacy (disable telemetry, ads)</summary>
    Standard,
    
    /// <summary>Enhanced privacy (disable Cortana, web search)</summary>
    Enhanced,
    
    /// <summary>Maximum privacy (all tracking disabled)</summary>
    Maximum
}

/// <summary>
/// GPT partition types.
/// </summary>
public enum PartitionType
{
    /// <summary>EFI System Partition</summary>
    EfiSystem,
    
    /// <summary>Microsoft Reserved Partition</summary>
    MicrosoftReserved,
    
    /// <summary>Basic data partition (NTFS/FAT32)</summary>
    BasicData,
    
    /// <summary>Windows Recovery Environment</summary>
    WindowsRecovery,
    
    /// <summary>Linux filesystem</summary>
    LinuxFilesystem,
    
    /// <summary>Linux swap</summary>
    LinuxSwap
}

/// <summary>
/// Filesystem types.
/// </summary>
public enum FileSystemType
{
    NTFS,
    FAT32,
    ReFS,
    exFAT,
    ext4,
    btrfs
}

/// <summary>
/// UI customization profiles.
/// </summary>
public enum UIProfile
{
    /// <summary>Clean minimal interface</summary>
    Minimal,
    
    /// <summary>Productivity focused layout</summary>
    Productivity,
    
    /// <summary>Gaming optimized UI</summary>
    Gaming,
    
    /// <summary>Classic Windows look</summary>
    Classic,
    
    /// <summary>Touch-friendly interface</summary>
    Touch,
    
    /// <summary>Accessibility enhanced</summary>
    Accessibility
}

/// <summary>
/// Backup configuration profiles.
/// </summary>
public enum BackupProfile
{
    /// <summary>Basic system restore points</summary>
    Basic,
    
    /// <summary>File History enabled</summary>
    FileHistory,
    
    /// <summary>Full system backup</summary>
    Full,
    
    /// <summary>Enterprise backup with VSS</summary>
    Enterprise,
    
    /// <summary>No backup configuration</summary>
    None
}

/// <summary>
/// Build profile types for image customization.
/// </summary>
public enum BuildProfileType
{
    /// <summary>Optimized for gaming</summary>
    Gaming,
    
    /// <summary>Developer workstation</summary>
    Developer,
    
    /// <summary>Enterprise deployment</summary>
    Enterprise,
    
    /// <summary>Student/education use</summary>
    Student,
    
    /// <summary>Content creator</summary>
    Creator,
    
    /// <summary>Custom configuration</summary>
    Custom
}
