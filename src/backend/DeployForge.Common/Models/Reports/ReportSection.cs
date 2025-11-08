namespace DeployForge.Common.Models.Reports;

/// <summary>
/// Report section
/// </summary>
public class ReportSection
{
    /// <summary>
    /// Section title
    /// </summary>
    public string Title { get; set; } = string.Empty;

    /// <summary>
    /// Section content
    /// </summary>
    public string Content { get; set; } = string.Empty;

    /// <summary>
    /// Section order
    /// </summary>
    public int Order { get; set; }

    /// <summary>
    /// Section type
    /// </summary>
    public SectionType Type { get; set; } = SectionType.Text;

    /// <summary>
    /// Section data (for tables, charts, etc.)
    /// </summary>
    public object? Data { get; set; }
}

/// <summary>
/// Section type enumeration
/// </summary>
public enum SectionType
{
    Text,
    Table,
    List,
    Chart,
    Image,
    Code
}
