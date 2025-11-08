using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.Input;
using DeployForge.Desktop.Services;
using Microsoft.Extensions.Logging;

namespace DeployForge.Desktop.ViewModels;

/// <summary>
/// Schedules Manager ViewModel for schedule management
/// </summary>
public partial class SchedulesManagerViewModel : ViewModelBase
{
    private readonly IApiClient _apiClient;
    private readonly ILogger<SchedulesManagerViewModel> _logger;

    private ScheduleDisplay? _selectedSchedule;
    private ScheduleExecutionDisplay? _selectedExecution;
    private bool _isEditing;
    private bool _showEnabledOnly = true;

    // Schedule form fields
    private string _scheduleId = string.Empty;
    private string _scheduleName = string.Empty;
    private string _cronExpression = "0 0 2 * * ?"; // Default: 2 AM daily
    private string _batchOperationId = string.Empty;
    private bool _isEnabled = true;
    private int _maxRetries = 3;
    private int _maxConcurrentExecutions = 1;
    private bool _skipOnFailure;
    private bool _sendNotifications = true;

    public ScheduleDisplay? SelectedSchedule
    {
        get => _selectedSchedule;
        set
        {
            SetProperty(ref _selectedSchedule, value);
            if (value != null)
            {
                LoadScheduleForEditing(value);
            }
        }
    }

    public ScheduleExecutionDisplay? SelectedExecution
    {
        get => _selectedExecution;
        set => SetProperty(ref _selectedExecution, value);
    }

    public bool IsEditing
    {
        get => _isEditing;
        set => SetProperty(ref _isEditing, value);
    }

    public bool ShowEnabledOnly
    {
        get => _showEnabledOnly;
        set
        {
            SetProperty(ref _showEnabledOnly, value);
            _ = LoadSchedulesAsync();
        }
    }

    // Schedule Form Properties
    public string ScheduleId
    {
        get => _scheduleId;
        set => SetProperty(ref _scheduleId, value);
    }

    public string ScheduleName
    {
        get => _scheduleName;
        set => SetProperty(ref _scheduleName, value);
    }

    public string CronExpression
    {
        get => _cronExpression;
        set => SetProperty(ref _cronExpression, value);
    }

    public string BatchOperationId
    {
        get => _batchOperationId;
        set => SetProperty(ref _batchOperationId, value);
    }

    public bool IsEnabled
    {
        get => _isEnabled;
        set => SetProperty(ref _isEnabled, value);
    }

    public int MaxRetries
    {
        get => _maxRetries;
        set => SetProperty(ref _maxRetries, value);
    }

    public int MaxConcurrentExecutions
    {
        get => _maxConcurrentExecutions;
        set => SetProperty(ref _maxConcurrentExecutions, value);
    }

    public bool SkipOnFailure
    {
        get => _skipOnFailure;
        set => SetProperty(ref _skipOnFailure, value);
    }

    public bool SendNotifications
    {
        get => _sendNotifications;
        set => SetProperty(ref _sendNotifications, value);
    }

    public ObservableCollection<ScheduleDisplay> Schedules { get; } = new();
    public ObservableCollection<ScheduleExecutionDisplay> Executions { get; } = new();
    public ObservableCollection<string> CronPresets { get; } = new()
    {
        "0 0 * * * ? (Every hour)",
        "0 0 2 * * ? (Daily at 2 AM)",
        "0 0 2 * * MON (Weekly on Monday at 2 AM)",
        "0 0 2 1 * ? (Monthly on 1st at 2 AM)",
        "0 */15 * * * ? (Every 15 minutes)"
    };

    public SchedulesManagerViewModel(
        IApiClient apiClient,
        ILogger<SchedulesManagerViewModel> logger)
    {
        _apiClient = apiClient;
        _logger = logger;
    }

    public override async Task InitializeAsync()
    {
        await base.InitializeAsync();
        await LoadSchedulesAsync();
    }

    [RelayCommand]
    private void NewSchedule()
    {
        ClearForm();
        IsEditing = true;
        ScheduleId = Guid.NewGuid().ToString();
        StatusMessage = "Creating new schedule...";
    }

    [RelayCommand]
    private void EditSchedule()
    {
        if (SelectedSchedule == null) return;
        IsEditing = true;
        StatusMessage = $"Editing schedule: {SelectedSchedule.Name}";
    }

    [RelayCommand]
    private void CancelEdit()
    {
        ClearForm();
        IsEditing = false;
        StatusMessage = "Cancelled";
    }

    [RelayCommand]
    private async Task SaveScheduleAsync()
    {
        try
        {
            IsBusy = true;
            StatusMessage = "Saving schedule...";

            var schedule = new
            {
                Id = ScheduleId,
                Name = ScheduleName,
                CronExpression,
                BatchOperationId,
                IsEnabled,
                Policy = new
                {
                    MaxRetries,
                    MaxConcurrentExecutions,
                    SkipOnFailure,
                    SendNotifications
                }
            };

            var isNew = !Schedules.Any(s => s.Id == ScheduleId);
            if (isNew)
            {
                await _apiClient.PostAsync<object, object>("schedules", schedule);
                StatusMessage = "Schedule created successfully";
                _logger.LogInformation("Created schedule: {ScheduleName}", ScheduleName);
            }
            else
            {
                // PUT request - need to add this to IApiClient
                // For now, use POST with the ID in the URL
                await _apiClient.PostAsync<object, object>($"schedules", schedule);
                StatusMessage = "Schedule updated successfully";
                _logger.LogInformation("Updated schedule: {ScheduleName}", ScheduleName);
            }

            await LoadSchedulesAsync();
            ClearForm();
            IsEditing = false;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to save schedule");
            StatusMessage = $"Failed to save schedule: {ex.Message}";
        }
        finally
        {
            IsBusy = false;
        }
    }

    [RelayCommand]
    private async Task DeleteScheduleAsync()
    {
        if (SelectedSchedule == null) return;

        try
        {
            IsBusy = true;
            StatusMessage = "Deleting schedule...";

            var deleted = await _apiClient.DeleteAsync($"schedules/{SelectedSchedule.Id}");
            if (deleted)
            {
                Schedules.Remove(SelectedSchedule);
                SelectedSchedule = null;
                ClearForm();
                IsEditing = false;
                StatusMessage = "Schedule deleted successfully";
                _logger.LogInformation("Deleted schedule");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to delete schedule");
            StatusMessage = "Failed to delete schedule";
        }
        finally
        {
            IsBusy = false;
        }
    }

    [RelayCommand]
    private async Task ExecuteScheduleAsync()
    {
        if (SelectedSchedule == null) return;

        try
        {
            IsBusy = true;
            StatusMessage = "Executing schedule...";

            var result = await _apiClient.PostAsync<object, ExecutionResult>(
                $"schedules/{SelectedSchedule.Id}/execute",
                new { });

            if (result != null)
            {
                StatusMessage = $"Schedule execution started: {result.ExecutionId}";
                _logger.LogInformation("Executed schedule: {ScheduleId}, ExecutionId: {ExecutionId}",
                    SelectedSchedule.Id, result.ExecutionId);

                // Reload execution history
                await Task.Delay(1000);
                await LoadExecutionHistoryAsync();
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to execute schedule");
            StatusMessage = "Failed to execute schedule";
        }
        finally
        {
            IsBusy = false;
        }
    }

    [RelayCommand]
    private async Task ViewExecutionHistoryAsync()
    {
        if (SelectedSchedule == null) return;
        await LoadExecutionHistoryAsync();
    }

    [RelayCommand]
    private async Task RefreshAsync()
    {
        await LoadSchedulesAsync();
    }

    private async Task LoadSchedulesAsync()
    {
        try
        {
            IsBusy = true;
            StatusMessage = "Loading schedules...";

            var endpoint = ShowEnabledOnly
                ? "schedules?enabledOnly=true"
                : "schedules";

            var schedules = await _apiClient.GetAsync<List<ScheduleDisplay>>(endpoint);
            if (schedules != null)
            {
                Schedules.Clear();
                foreach (var schedule in schedules.OrderBy(s => s.Name))
                {
                    Schedules.Add(schedule);
                }
                StatusMessage = $"Loaded {schedules.Count} schedules";
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to load schedules");
            StatusMessage = "Failed to load schedules";
        }
        finally
        {
            IsBusy = false;
        }
    }

    private async Task LoadExecutionHistoryAsync()
    {
        if (SelectedSchedule == null) return;

        try
        {
            var executions = await _apiClient.GetAsync<List<ScheduleExecutionDisplay>>(
                $"schedules/{SelectedSchedule.Id}/history");

            if (executions != null)
            {
                Executions.Clear();
                foreach (var execution in executions.OrderByDescending(e => e.StartedAt))
                {
                    Executions.Add(execution);
                }
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to load execution history");
        }
    }

    private void LoadScheduleForEditing(ScheduleDisplay schedule)
    {
        ScheduleId = schedule.Id;
        ScheduleName = schedule.Name;
        CronExpression = schedule.CronExpression;
        BatchOperationId = schedule.BatchOperationId ?? string.Empty;
        IsEnabled = schedule.IsEnabled;

        // Load execution history
        _ = LoadExecutionHistoryAsync();
    }

    private void ClearForm()
    {
        ScheduleId = string.Empty;
        ScheduleName = string.Empty;
        CronExpression = "0 0 2 * * ?";
        BatchOperationId = string.Empty;
        IsEnabled = true;
        MaxRetries = 3;
        MaxConcurrentExecutions = 1;
        SkipOnFailure = false;
        SendNotifications = true;
        Executions.Clear();
    }
}

public class ScheduleDisplay
{
    public string Id { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public string CronExpression { get; set; } = string.Empty;
    public string? BatchOperationId { get; set; }
    public bool IsEnabled { get; set; }
    public DateTime? NextRunTime { get; set; }
    public DateTime? LastRunTime { get; set; }
    public string NextRunDisplay => NextRunTime?.ToString("g") ?? "Not scheduled";
    public string LastRunDisplay => LastRunTime?.ToString("g") ?? "Never";
    public string StatusDisplay => IsEnabled ? "Enabled" : "Disabled";
}

public class ScheduleExecutionDisplay
{
    public string Id { get; set; } = string.Empty;
    public string ScheduleId { get; set; } = string.Empty;
    public DateTime StartedAt { get; set; }
    public DateTime? CompletedAt { get; set; }
    public string Status { get; set; } = string.Empty;
    public string? ErrorMessage { get; set; }
    public TimeSpan Duration => CompletedAt.HasValue
        ? CompletedAt.Value - StartedAt
        : DateTime.Now - StartedAt;
    public string DurationDisplay => $"{(int)Duration.TotalMinutes}m {Duration.Seconds}s";
}

public class ExecutionResult
{
    public string ExecutionId { get; set; } = string.Empty;
    public string Message { get; set; } = string.Empty;
}
