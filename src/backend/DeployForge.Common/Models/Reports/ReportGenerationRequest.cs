namespace DeployForge.Common.Models.Reports;

/// <summary>
/// Report generation request
/// </summary>
public class ReportGenerationRequest
{
    /// <summary>
    /// Report type
    /// </summary>
    public ReportType Type { get; set; }

    /// <summary>
    /// Report format
    /// </summary>
    public ReportFormat Format { get; set; } = ReportFormat.Html;

    /// <summary>
    /// Report title
    /// </summary>
    public string? Title { get; set; }

    /// <summary>
    /// Include sections
    /// </summary>
    public List<string>? IncludeSections { get; set; }

    /// <summary>
    /// Exclude sections
    /// </summary>
    public List<string>? ExcludeSections { get; set; }

    /// <summary>
    /// Date range start (for time-based reports)
    /// </summary>
    public DateTime? StartDate { get; set; }

    /// <summary>
    /// Date range end (for time-based reports)
    /// </summary>
    public DateTime? EndDate { get; set; }

    /// <summary>
    /// Resource ID (e.g., operationId, imageId)
    /// </summary>
    public string? ResourceId { get; set; }

    /// <summary>
    /// Additional parameters
    /// </summary>
    public Dictionary<string, object> Parameters { get; set; } = new();

    /// <summary>
    /// Output file path (if null, content is returned in-memory)
    /// </summary>
    public string? OutputPath { get; set; }
}
