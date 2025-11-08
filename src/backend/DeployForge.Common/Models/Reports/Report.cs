namespace DeployForge.Common.Models.Reports;

/// <summary>
/// Generated report
/// </summary>
public class Report
{
    /// <summary>
    /// Report ID
    /// </summary>
    public string Id { get; set; } = Guid.NewGuid().ToString();

    /// <summary>
    /// Report type
    /// </summary>
    public ReportType Type { get; set; }

    /// <summary>
    /// Report format
    /// </summary>
    public ReportFormat Format { get; set; }

    /// <summary>
    /// Report title
    /// </summary>
    public string Title { get; set; } = string.Empty;

    /// <summary>
    /// Report description
    /// </summary>
    public string Description { get; set; } = string.Empty;

    /// <summary>
    /// Generated timestamp
    /// </summary>
    public DateTime GeneratedAt { get; set; } = DateTime.UtcNow;

    /// <summary>
    /// Report sections
    /// </summary>
    public List<ReportSection> Sections { get; set; } = new();

    /// <summary>
    /// Report metadata
    /// </summary>
    public Dictionary<string, object> Metadata { get; set; } = new();

    /// <summary>
    /// File path where report is saved
    /// </summary>
    public string? FilePath { get; set; }

    /// <summary>
    /// Report content (for in-memory reports)
    /// </summary>
    public string? Content { get; set; }
}

/// <summary>
/// Report type enumeration
/// </summary>
public enum ReportType
{
    Validation,
    Audit,
    Statistics,
    BatchOperation,
    ImageComparison,
    SystemHealth,
    PerformanceAnalysis
}

/// <summary>
/// Report format enumeration
/// </summary>
public enum ReportFormat
{
    Html,
    Json,
    Pdf,
    Csv,
    Markdown
}
