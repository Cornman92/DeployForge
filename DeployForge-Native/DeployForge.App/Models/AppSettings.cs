namespace DeployForge.App.Models;

public record AppSettings
{
    public GeneralSettings General { get; init; } = new();
    public PathSettings Paths { get; init; } = new();
    public BuildSettings Build { get; init; } = new();
    public UISettings UI { get; init; } = new();
}

public record GeneralSettings
{
    public bool CheckForUpdates { get; init; } = true;
    public bool SendAnonymousUsage { get; init; } = false;
    public string Language { get; init; } = "en-US";
    public bool ShowAdvancedOptions { get; init; } = false;
    public bool ConfirmOnExit { get; init; } = true;
}

public record PathSettings
{
    public string DefaultOutputDirectory { get; init; } = Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments);
    public string TempDirectory { get; init; } = Path.Combine(Path.GetTempPath(), "DeployForge");
    public string LogDirectory { get; init; } = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "DeployForge", "Logs");
    public string ProfilesDirectory { get; init; } = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), "DeployForge", "Profiles");
    public string TemplatesDirectory { get; init; } = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), "DeployForge", "Templates");
}

public record BuildSettings
{
    public int MaxParallelOperations { get; init; } = 4;
    public bool OptimizeImageAfterBuild { get; init; } = true;
    public bool CreateBackupBeforeModify { get; init; } = true;
    public CompressionLevel DefaultCompression { get; init; } = CompressionLevel.Maximum;
    public bool CleanupTempFilesAfterBuild { get; init; } = true;
}

public enum CompressionLevel { None, Fast, Normal, Maximum }

public record UISettings
{
    public AppTheme Theme { get; init; } = AppTheme.System;
    public AccentColor AccentColor { get; init; } = AccentColor.Blue;
    public bool ShowStatusBar { get; init; } = true;
    public bool ShowMiniProgress { get; init; } = true;
    public bool EnableAnimations { get; init; } = true;
    public WindowSize DefaultWindowSize { get; init; } = new(1280, 800);
}

public enum AppTheme { Light, Dark, System }
public enum AccentColor { Blue, Purple, Green, Orange, Red, Pink, Custom }
public record WindowSize(int Width, int Height);
