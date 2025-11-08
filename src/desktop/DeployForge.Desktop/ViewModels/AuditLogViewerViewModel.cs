using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.Input;
using DeployForge.Desktop.Services;
using Microsoft.Extensions.Logging;

namespace DeployForge.Desktop.ViewModels;

/// <summary>
/// Audit Log Viewer ViewModel
/// </summary>
public partial class AuditLogViewerViewModel : ViewModelBase
{
    private readonly IApiClient _apiClient;
    private readonly IDialogService _dialogService;
    private readonly ILogger<AuditLogViewerViewModel> _logger;

    private AuditLogEntryDto? _selectedEntry;
    private string _searchText = string.Empty;
    private string _filterCategory = "All";
    private string _filterResult = "All";
    private string _filterSeverity = "All";
    private DateTime? _startDate;
    private DateTime? _endDate;
    private int _currentPage = 1;
    private int _totalPages;
    private int _pageSize = 50;

    public AuditLogEntryDto? SelectedEntry
    {
        get => _selectedEntry;
        set => SetProperty(ref _selectedEntry, value);
    }

    public string SearchText
    {
        get => _searchText;
        set => SetProperty(ref _searchText, value);
    }

    public string FilterCategory
    {
        get => _filterCategory;
        set => SetProperty(ref _filterCategory, value);
    }

    public string FilterResult
    {
        get => _filterResult;
        set => SetProperty(ref _filterResult, value);
    }

    public string FilterSeverity
    {
        get => _filterSeverity;
        set => SetProperty(ref _filterSeverity, value);
    }

    public DateTime? StartDate
    {
        get => _startDate;
        set => SetProperty(ref _startDate, value);
    }

    public DateTime? EndDate
    {
        get => _endDate;
        set => SetProperty(ref _endDate, value);
    }

    public int CurrentPage
    {
        get => _currentPage;
        set
        {
            if (SetProperty(ref _currentPage, value))
            {
                _ = LoadLogsAsync();
            }
        }
    }

    public int TotalPages
    {
        get => _totalPages;
        set => SetProperty(ref _totalPages, value);
    }

    public ObservableCollection<AuditLogEntryDto> LogEntries { get; } = new();
    public ObservableCollection<string> Categories { get; } = new()
    {
        "All", "Image", "Component", "Driver", "Update", "Registry", "Debloat",
        "Workflow", "Deployment", "Backup", "Template", "Configuration", "Validation"
    };
    public ObservableCollection<string> Results { get; } = new()
    {
        "All", "Success", "Failure", "PartialSuccess", "Cancelled", "InProgress"
    };
    public ObservableCollection<string> Severities { get; } = new()
    {
        "All", "Verbose", "Information", "Warning", "Error", "Critical"
    };

    public AuditLogViewerViewModel(
        IApiClient apiClient,
        IDialogService dialogService,
        ILogger<AuditLogViewerViewModel> logger)
    {
        _apiClient = apiClient;
        _dialogService = dialogService;
        _logger = logger;
    }

    public override async Task InitializeAsync()
    {
        await base.InitializeAsync();
        StartDate = DateTime.Today.AddDays(-7); // Last 7 days by default
        EndDate = DateTime.Today.AddDays(1);
        await LoadLogsAsync();
    }

    [RelayCommand]
    private async Task RefreshAsync()
    {
        CurrentPage = 1;
        await LoadLogsAsync();
    }

    [RelayCommand]
    private async Task SearchAsync()
    {
        CurrentPage = 1;
        await LoadLogsAsync();
    }

    [RelayCommand]
    private void ClearFilters()
    {
        SearchText = string.Empty;
        FilterCategory = "All";
        FilterResult = "All";
        FilterSeverity = "All";
        StartDate = DateTime.Today.AddDays(-7);
        EndDate = DateTime.Today.AddDays(1);
    }

    [RelayCommand]
    private async Task PreviousPageAsync()
    {
        if (CurrentPage > 1)
        {
            CurrentPage--;
        }
    }

    [RelayCommand]
    private async Task NextPageAsync()
    {
        if (CurrentPage < TotalPages)
        {
            CurrentPage++;
        }
    }

    [RelayCommand]
    private async Task ExportLogsAsync()
    {
        try
        {
            var filePath = _dialogService.ShowSaveFileDialog(
                "Export Audit Logs",
                "CSV Files (*.csv)|*.csv|JSON Files (*.json)|*.json",
                $"AuditLogs_{DateTime.Now:yyyyMMdd_HHmmss}.csv");

            if (string.IsNullOrEmpty(filePath))
                return;

            IsBusy = true;
            StatusMessage = "Exporting audit logs...";

            var format = filePath.EndsWith(".json", StringComparison.OrdinalIgnoreCase) ? "json" : "csv";

            var request = new ExportAuditLogsRequestDto
            {
                StartDate = StartDate,
                EndDate = EndDate,
                Category = FilterCategory != "All" ? FilterCategory : null,
                Result = FilterResult != "All" ? FilterResult : null,
                Format = format
            };

            await _apiClient.PostAsync($"auditlog/export?outputPath={Uri.EscapeDataString(filePath)}", request);

            StatusMessage = "Audit logs exported successfully";
            _dialogService.ShowSuccessMessage("Success", $"Audit logs exported to {filePath}");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to export audit logs");
            StatusMessage = "Failed to export audit logs";
            _dialogService.ShowErrorMessage("Export Failed", ex.Message);
        }
        finally
        {
            IsBusy = false;
        }
    }

    [RelayCommand]
    private async Task DeleteOldLogsAsync()
    {
        try
        {
            var input = _dialogService.ShowInputDialog(
                "Delete Old Logs",
                "Delete logs older than how many days?",
                "90");

            if (string.IsNullOrWhiteSpace(input) || !int.TryParse(input, out var days))
                return;

            var cutoffDate = DateTime.Now.AddDays(-days);

            var confirm = _dialogService.ShowConfirmation(
                "Delete Old Logs",
                $"Are you sure you want to delete all logs older than {cutoffDate:d}?");

            if (!confirm) return;

            IsBusy = true;
            StatusMessage = "Deleting old logs...";

            var result = await _apiClient.DeleteAsync($"auditlog/delete-old?olderThan={cutoffDate:o}");

            StatusMessage = "Old logs deleted successfully";
            _dialogService.ShowSuccessMessage("Success", "Old logs deleted successfully");
            await LoadLogsAsync();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to delete old logs");
            StatusMessage = "Failed to delete old logs";
            _dialogService.ShowErrorMessage("Delete Failed", ex.Message);
        }
        finally
        {
            IsBusy = false;
        }
    }

    [RelayCommand]
    private async Task ViewDetailsAsync()
    {
        if (SelectedEntry == null) return;

        var details = $"ID: {SelectedEntry.Id}\n" +
                     $"Timestamp: {SelectedEntry.Timestamp:g}\n" +
                     $"User: {SelectedEntry.User}\n" +
                     $"Machine: {SelectedEntry.MachineName}\n" +
                     $"Category: {SelectedEntry.Category}\n" +
                     $"Action: {SelectedEntry.Action}\n" +
                     $"Resource: {SelectedEntry.Resource}\n" +
                     $"Result: {SelectedEntry.Result}\n" +
                     $"Duration: {SelectedEntry.DurationMs}ms\n" +
                     $"Severity: {SelectedEntry.Severity}\n\n" +
                     $"Description:\n{SelectedEntry.Description}";

        if (!string.IsNullOrEmpty(SelectedEntry.ErrorMessage))
        {
            details += $"\n\nError:\n{SelectedEntry.ErrorMessage}";
        }

        _dialogService.ShowInformationMessage("Audit Log Details", details);
    }

    private async Task LoadLogsAsync()
    {
        try
        {
            IsBusy = true;
            StatusMessage = "Loading audit logs...";

            var query = new AuditLogQueryDto
            {
                StartDate = StartDate,
                EndDate = EndDate,
                Category = FilterCategory != "All" ? FilterCategory : null,
                Result = FilterResult != "All" ? FilterResult : null,
                PageNumber = CurrentPage,
                PageSize = _pageSize,
                SortBy = "Timestamp",
                SortDirection = "desc"
            };

            // If search text is provided, use search endpoint
            AuditLogQueryResultDto? result;
            if (!string.IsNullOrWhiteSpace(SearchText))
            {
                result = await _apiClient.GetAsync<AuditLogQueryResultDto>(
                    $"auditlog/search?searchText={Uri.EscapeDataString(SearchText)}&pageNumber={CurrentPage}&pageSize={_pageSize}");
            }
            else
            {
                result = await _apiClient.PostAsync<AuditLogQueryResultDto>("auditlog/query", query);
            }

            if (result != null)
            {
                LogEntries.Clear();
                foreach (var entry in result.Entries)
                {
                    LogEntries.Add(entry);
                }

                TotalPages = result.TotalPages;
                StatusMessage = $"Loaded {result.Entries.Count} of {result.TotalCount} audit logs (Page {CurrentPage} of {TotalPages})";
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to load audit logs");
            StatusMessage = "Failed to load audit logs";
            _dialogService.ShowErrorMessage("Load Failed", ex.Message);
        }
        finally
        {
            IsBusy = false;
        }
    }
}

#region DTOs

public class AuditLogEntryDto
{
    public string Id { get; set; } = string.Empty;
    public DateTime Timestamp { get; set; }
    public string User { get; set; } = string.Empty;
    public string MachineName { get; set; } = string.Empty;
    public string Category { get; set; } = string.Empty;
    public string Action { get; set; } = string.Empty;
    public string Resource { get; set; } = string.Empty;
    public string Result { get; set; } = string.Empty;
    public long DurationMs { get; set; }
    public string? ErrorMessage { get; set; }
    public string Description { get; set; } = string.Empty;
    public string? IpAddress { get; set; }
    public string? OperationId { get; set; }
    public string Severity { get; set; } = "Information";

    public string DurationFormatted => DurationMs > 1000
        ? $"{DurationMs / 1000.0:F2}s"
        : $"{DurationMs}ms";

    public string TimestampFormatted => Timestamp.ToLocalTime().ToString("g");
}

public class AuditLogQueryDto
{
    public DateTime? StartDate { get; set; }
    public DateTime? EndDate { get; set; }
    public string? User { get; set; }
    public string? Category { get; set; }
    public string? Action { get; set; }
    public string? Resource { get; set; }
    public string? Result { get; set; }
    public string? OperationId { get; set; }
    public string? MinSeverity { get; set; }
    public int PageNumber { get; set; } = 1;
    public int PageSize { get; set; } = 50;
    public string SortBy { get; set; } = "Timestamp";
    public string SortDirection { get; set; } = "desc";
}

public class AuditLogQueryResultDto
{
    public List<AuditLogEntryDto> Entries { get; set; } = new();
    public int TotalCount { get; set; }
    public int PageNumber { get; set; }
    public int PageSize { get; set; }
    public int TotalPages { get; set; }
    public bool HasNextPage { get; set; }
    public bool HasPreviousPage { get; set; }
}

public class ExportAuditLogsRequestDto
{
    public DateTime? StartDate { get; set; }
    public DateTime? EndDate { get; set; }
    public string? Category { get; set; }
    public string? Result { get; set; }
    public string Format { get; set; } = "csv";
}

#endregion
