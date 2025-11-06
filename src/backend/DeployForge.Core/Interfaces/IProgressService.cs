namespace DeployForge.Core.Interfaces;

/// <summary>
/// Service for reporting operation progress
/// </summary>
public interface IProgressService
{
    /// <summary>
    /// Report progress for an operation
    /// </summary>
    Task ReportProgressAsync(string operationId, int percentage, string message, string? stage = null);

    /// <summary>
    /// Report operation completion
    /// </summary>
    Task ReportCompletionAsync(string operationId, bool success, string message);

    /// <summary>
    /// Report operation error
    /// </summary>
    Task ReportErrorAsync(string operationId, string errorMessage);

    /// <summary>
    /// Create a progress reporter for an operation
    /// </summary>
    IProgress<ProgressReport> CreateProgressReporter(string operationId);
}

/// <summary>
/// Progress report data
/// </summary>
public class ProgressReport
{
    public int Percentage { get; set; }
    public string Message { get; set; } = string.Empty;
    public string? Stage { get; set; }
}
