namespace DeployForge.App.Models;

public record BuildConfiguration
{
    public string Id { get; init; } = Guid.NewGuid().ToString();
    public string Name { get; init; } = string.Empty;
    public string SourceImage { get; init; } = string.Empty;
    public int SourceIndex { get; init; } = 1;
    public string OutputPath { get; init; } = string.Empty;
    public OutputFormat OutputFormat { get; init; } = OutputFormat.WIM;
    public string? ProfileId { get; init; }
    public ProfileFeatures Features { get; init; } = new();
    public UnattendConfiguration? Unattend { get; init; }
    public List<string> DriverPaths { get; init; } = new();
    public List<string> LanguagePacks { get; init; } = new();
    public DateTime CreatedAt { get; init; } = DateTime.Now;
}

public enum OutputFormat { WIM, ESD, ISO, VHD, VHDX }

public record UnattendConfiguration
{
    public string? ProductKey { get; init; }
    public string ComputerName { get; init; } = "DESKTOP-PC";
    public string TimeZone { get; init; } = "Pacific Standard Time";
    public string Username { get; init; } = "Admin";
    public string? Password { get; init; }
    public string? Organization { get; init; }
    public string? Owner { get; init; }
    public bool SkipOOBE { get; init; } = true;
    public bool HideEula { get; init; } = true;
    public bool EnableAutoLogon { get; init; }
}

public record BuildProgress
{
    public string CurrentStep { get; init; } = string.Empty;
    public int StepNumber { get; init; }
    public int TotalSteps { get; init; }
    public double PercentComplete { get; init; }
    public string StatusMessage { get; init; } = string.Empty;
    public TimeSpan Elapsed { get; init; }
    public TimeSpan? EstimatedRemaining { get; init; }
    public bool IsComplete { get; init; }
    public bool HasErrors { get; init; }
    public List<string> Logs { get; init; } = new();
}

public record BuildResult
{
    public bool Success { get; init; }
    public string OutputPath { get; init; } = string.Empty;
    public TimeSpan Duration { get; init; }
    public List<string> AppliedFeatures { get; init; } = new();
    public List<BuildWarning> Warnings { get; init; } = new();
    public List<BuildError> Errors { get; init; } = new();
}

public record BuildWarning(string Message, string? Component = null);
public record BuildError(string Message, string? Component = null, Exception? Exception = null);
