using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.Input;
using DeployForge.Desktop.Services;
using Microsoft.Extensions.Logging;
using Microsoft.Win32;

namespace DeployForge.Desktop.ViewModels;

/// <summary>
/// Reports Dashboard ViewModel for report generation and management
/// </summary>
public partial class ReportsDashboardViewModel : ViewModelBase
{
    private readonly IApiClient _apiClient;
    private readonly ILogger<ReportsDashboardViewModel> _logger;

    private ReportDisplay? _selectedReport;
    private string _selectedReportType = "Validation";
    private string _selectedFormat = "Html";
    private DateTime _startDate = DateTime.Today.AddDays(-7);
    private DateTime _endDate = DateTime.Today;
    private string _batchOperationId = string.Empty;
    private string _reportFilter = string.Empty;

    public ReportDisplay? SelectedReport
    {
        get => _selectedReport;
        set => SetProperty(ref _selectedReport, value);
    }

    public string SelectedReportType
    {
        get => _selectedReportType;
        set => SetProperty(ref _selectedReportType, value);
    }

    public string SelectedFormat
    {
        get => _selectedFormat;
        set => SetProperty(ref _selectedFormat, value);
    }

    public DateTime StartDate
    {
        get => _startDate;
        set => SetProperty(ref _startDate, value);
    }

    public DateTime EndDate
    {
        get => _endDate;
        set => SetProperty(ref _endDate, value);
    }

    public string BatchOperationId
    {
        get => _batchOperationId;
        set => SetProperty(ref _batchOperationId, value);
    }

    public string ReportFilter
    {
        get => _reportFilter;
        set
        {
            SetProperty(ref _reportFilter, value);
            FilterReports();
        }
    }

    public ObservableCollection<string> ReportTypes { get; } = new()
    {
        "Validation",
        "Audit",
        "Statistics",
        "BatchOperation",
        "SystemHealth"
    };

    public ObservableCollection<string> ReportFormats { get; } = new()
    {
        "Html",
        "Json",
        "Markdown",
        "Pdf"
    };

    public ObservableCollection<ReportDisplay> Reports { get; } = new();
    public ObservableCollection<ReportDisplay> FilteredReports { get; } = new();

    public ReportsDashboardViewModel(
        IApiClient apiClient,
        ILogger<ReportsDashboardViewModel> logger)
    {
        _apiClient = apiClient;
        _logger = logger;
    }

    public override async Task InitializeAsync()
    {
        await base.InitializeAsync();
        await LoadReportsAsync();
    }

    [RelayCommand]
    private async Task GenerateReportAsync()
    {
        try
        {
            IsBusy = true;
            StatusMessage = $"Generating {SelectedReportType} report...";

            string endpoint = SelectedReportType switch
            {
                "Validation" => $"reports/validation?format={SelectedFormat}",
                "Audit" => $"reports/audit?startDate={StartDate:yyyy-MM-dd}&endDate={EndDate:yyyy-MM-dd}&format={SelectedFormat}",
                "Statistics" => $"reports/statistics?startDate={StartDate:yyyy-MM-dd}&endDate={EndDate:yyyy-MM-dd}&format={SelectedFormat}",
                "BatchOperation" => $"reports/batchoperation?batchOperationId={BatchOperationId}&format={SelectedFormat}",
                _ => $"reports?format={SelectedFormat}"
            };

            object? requestBody = SelectedReportType == "Validation"
                ? new { ImagePath = "C:\\temp\\test.wim" }  // Placeholder
                : null;

            var report = requestBody != null
                ? await _apiClient.PostAsync<object, ReportDisplay>(endpoint, requestBody)
                : await _apiClient.PostAsync<object, ReportDisplay>(endpoint, new { });

            if (report != null)
            {
                StatusMessage = "Report generated successfully";
                _logger.LogInformation("Generated {ReportType} report: {ReportId}", SelectedReportType, report.Id);
                await LoadReportsAsync();
            }
            else
            {
                StatusMessage = "Failed to generate report";
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to generate report");
            StatusMessage = $"Failed to generate report: {ex.Message}";
        }
        finally
        {
            IsBusy = false;
        }
    }

    [RelayCommand]
    private async Task RefreshAsync()
    {
        await LoadReportsAsync();
    }

    [RelayCommand]
    private async Task ViewReportAsync()
    {
        if (SelectedReport == null) return;

        try
        {
            IsBusy = true;
            StatusMessage = $"Loading report {SelectedReport.Title}...";

            var report = await _apiClient.GetAsync<ReportDisplay>($"reports/{SelectedReport.Id}");
            if (report != null)
            {
                // Open report content in default browser or viewer
                if (!string.IsNullOrEmpty(report.FilePath) && System.IO.File.Exists(report.FilePath))
                {
                    System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo
                    {
                        FileName = report.FilePath,
                        UseShellExecute = true
                    });
                    StatusMessage = "Report opened successfully";
                }
                else
                {
                    StatusMessage = "Report file not found";
                }
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to view report");
            StatusMessage = "Failed to view report";
        }
        finally
        {
            IsBusy = false;
        }
    }

    [RelayCommand]
    private async Task ExportReportAsync()
    {
        if (SelectedReport == null) return;

        try
        {
            var dialog = new SaveFileDialog
            {
                Title = "Export Report",
                Filter = "HTML Files (*.html)|*.html|PDF Files (*.pdf)|*.pdf|JSON Files (*.json)|*.json|Markdown Files (*.md)|*.md|All Files (*.*)|*.*",
                FileName = $"{SelectedReport.Title}_{DateTime.Now:yyyyMMdd}"
            };

            if (dialog.ShowDialog() == true)
            {
                IsBusy = true;
                StatusMessage = "Exporting report...";

                var targetFormat = System.IO.Path.GetExtension(dialog.FileName).TrimStart('.') switch
                {
                    "html" => "Html",
                    "pdf" => "Pdf",
                    "json" => "Json",
                    "md" => "Markdown",
                    _ => "Html"
                };

                var exported = await _apiClient.PostAsync<object, ReportDisplay>(
                    $"reports/{SelectedReport.Id}/export?targetFormat={targetFormat}&outputPath={dialog.FileName}",
                    new { });

                if (exported != null)
                {
                    StatusMessage = $"Report exported to {dialog.FileName}";
                    _logger.LogInformation("Exported report to {FilePath}", dialog.FileName);
                }
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to export report");
            StatusMessage = "Failed to export report";
        }
        finally
        {
            IsBusy = false;
        }
    }

    [RelayCommand]
    private async Task DeleteReportAsync()
    {
        if (SelectedReport == null) return;

        try
        {
            IsBusy = true;
            StatusMessage = "Deleting report...";

            var deleted = await _apiClient.DeleteAsync($"reports/{SelectedReport.Id}");
            if (deleted)
            {
                Reports.Remove(SelectedReport);
                FilteredReports.Remove(SelectedReport);
                SelectedReport = null;
                StatusMessage = "Report deleted successfully";
                _logger.LogInformation("Deleted report");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to delete report");
            StatusMessage = "Failed to delete report";
        }
        finally
        {
            IsBusy = false;
        }
    }

    private async Task LoadReportsAsync()
    {
        try
        {
            IsBusy = true;
            StatusMessage = "Loading reports...";

            var reports = await _apiClient.GetAsync<List<ReportDisplay>>("reports");
            if (reports != null)
            {
                Reports.Clear();
                foreach (var report in reports.OrderByDescending(r => r.GeneratedAt))
                {
                    Reports.Add(report);
                }
                FilterReports();
                StatusMessage = $"Loaded {reports.Count} reports";
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to load reports");
            StatusMessage = "Failed to load reports";
        }
        finally
        {
            IsBusy = false;
        }
    }

    private void FilterReports()
    {
        FilteredReports.Clear();

        var filtered = string.IsNullOrWhiteSpace(ReportFilter)
            ? Reports
            : Reports.Where(r =>
                r.Title.Contains(ReportFilter, StringComparison.OrdinalIgnoreCase) ||
                r.Type.Contains(ReportFilter, StringComparison.OrdinalIgnoreCase));

        foreach (var report in filtered)
        {
            FilteredReports.Add(report);
        }
    }
}

public class ReportDisplay
{
    public string Id { get; set; } = string.Empty;
    public string Title { get; set; } = string.Empty;
    public string Type { get; set; } = string.Empty;
    public string Format { get; set; } = string.Empty;
    public DateTime GeneratedAt { get; set; }
    public string? FilePath { get; set; }
    public long FileSizeBytes { get; set; }
    public string FileSizeDisplay => $"{FileSizeBytes / 1024.0:F2} KB";
}
