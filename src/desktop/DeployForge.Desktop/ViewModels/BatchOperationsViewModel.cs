using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.Input;
using DeployForge.Desktop.Services;
using Microsoft.Extensions.Logging;
using System.Timers;

namespace DeployForge.Desktop.ViewModels;

/// <summary>
/// Batch Operations ViewModel
/// </summary>
public partial class BatchOperationsViewModel : ViewModelBase
{
    private readonly IApiClient _apiClient;
    private readonly IDialogService _dialogService;
    private readonly ILogger<BatchOperationsViewModel> _logger;
    private readonly System.Timers.Timer _refreshTimer;

    private BatchOperationDto? _selectedOperation;
    private string _filterStatus = "All";
    private string _filterType = "All";
    private bool _autoRefresh = true;

    public BatchOperationDto? SelectedOperation
    {
        get => _selectedOperation;
        set
        {
            if (SetProperty(ref _selectedOperation, value))
            {
                StartOperationCommand.NotifyCanExecuteChanged();
                PauseOperationCommand.NotifyCanExecuteChanged();
                ResumeOperationCommand.NotifyCanExecuteChanged();
                CancelOperationCommand.NotifyCanExecuteChanged();
                DeleteOperationCommand.NotifyCanExecuteChanged();
                RetryFailedCommand.NotifyCanExecuteChanged();
            }
        }
    }

    public string FilterStatus
    {
        get => _filterStatus;
        set
        {
            if (SetProperty(ref _filterStatus, value))
            {
                _ = LoadOperationsAsync();
            }
        }
    }

    public string FilterType
    {
        get => _filterType;
        set
        {
            if (SetProperty(ref _filterType, value))
            {
                _ = LoadOperationsAsync();
            }
        }
    }

    public bool AutoRefresh
    {
        get => _autoRefresh;
        set
        {
            if (SetProperty(ref _autoRefresh, value))
            {
                if (_autoRefresh)
                {
                    _refreshTimer.Start();
                }
                else
                {
                    _refreshTimer.Stop();
                }
            }
        }
    }

    public ObservableCollection<BatchOperationDto> Operations { get; } = new();
    public ObservableCollection<string> StatusFilters { get; } = new()
    {
        "All", "Pending", "Running", "Paused", "Completed", "CompletedWithErrors", "Failed", "Cancelled"
    };
    public ObservableCollection<string> TypeFilters { get; } = new()
    {
        "All", "ApplyTemplate", "MountImages", "UnmountImages", "ValidateImages",
        "OptimizeImages", "ConvertImages", "DebloatImages", "InstallUpdates"
    };

    public BatchOperationsViewModel(
        IApiClient apiClient,
        IDialogService dialogService,
        ILogger<BatchOperationsViewModel> logger)
    {
        _apiClient = apiClient;
        _dialogService = dialogService;
        _logger = logger;

        _refreshTimer = new System.Timers.Timer(5000); // Refresh every 5 seconds
        _refreshTimer.Elapsed += RefreshTimer_Elapsed;
        _refreshTimer.AutoReset = true;
    }

    public override async Task InitializeAsync()
    {
        await base.InitializeAsync();
        await LoadOperationsAsync();
        if (AutoRefresh)
        {
            _refreshTimer.Start();
        }
    }

    public override Task CleanupAsync()
    {
        _refreshTimer.Stop();
        _refreshTimer.Dispose();
        return base.CleanupAsync();
    }

    private async void RefreshTimer_Elapsed(object? sender, ElapsedEventArgs e)
    {
        await LoadOperationsAsync();
    }

    [RelayCommand]
    private async Task RefreshAsync()
    {
        await LoadOperationsAsync();
    }

    [RelayCommand]
    private async Task CreateOperationAsync()
    {
        try
        {
            // For now, create a simple dialog to get basic info
            var name = _dialogService.ShowInputDialog("Create Batch Operation", "Enter operation name:");
            if (string.IsNullOrWhiteSpace(name))
                return;

            var description = _dialogService.ShowInputDialog("Create Batch Operation", "Enter operation description:");

            // Get operation type
            var typeDialog = _dialogService.ShowInputDialog("Create Batch Operation",
                "Enter operation type (ApplyTemplate, MountImages, ValidateImages, etc.):");
            if (string.IsNullOrWhiteSpace(typeDialog))
                return;

            // Get image paths
            var imagePaths = _dialogService.ShowMultipleOpenFileDialog(
                "Select Image Files",
                "Windows Image Files (*.wim;*.esd)|*.wim;*.esd");

            if (imagePaths == null || imagePaths.Length == 0)
            {
                _dialogService.ShowWarningMessage("No Images", "Please select at least one image.");
                return;
            }

            IsBusy = true;
            StatusMessage = "Creating batch operation...";

            var request = new CreateBatchOperationRequestDto
            {
                Name = name,
                Description = description ?? string.Empty,
                Type = typeDialog,
                TargetImages = imagePaths.Select(path => new BatchTargetImageDto
                {
                    ImagePath = path,
                    ImageIndex = 1
                }).ToList(),
                Priority = 5,
                MaxParallelOperations = 2,
                ContinueOnError = true,
                StartImmediately = false
            };

            var result = await _apiClient.PostAsync<BatchOperationDto>("batchoperations", request);

            if (result != null)
            {
                StatusMessage = "Batch operation created successfully";
                _dialogService.ShowSuccessMessage("Success", $"Batch operation '{name}' created with {imagePaths.Length} images");
                await LoadOperationsAsync();
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to create batch operation");
            StatusMessage = "Failed to create batch operation";
            _dialogService.ShowErrorMessage("Create Failed", ex.Message);
        }
        finally
        {
            IsBusy = false;
        }
    }

    [RelayCommand(CanExecute = nameof(CanStartOperation))]
    private async Task StartOperationAsync()
    {
        if (SelectedOperation == null) return;

        try
        {
            IsBusy = true;
            StatusMessage = $"Starting batch operation '{SelectedOperation.Name}'...";

            await _apiClient.PostAsync($"batchoperations/{SelectedOperation.Id}/start", null);

            StatusMessage = "Batch operation started";
            _dialogService.ShowSuccessMessage("Success", "Batch operation started successfully");
            await LoadOperationsAsync();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to start batch operation");
            StatusMessage = "Failed to start batch operation";
            _dialogService.ShowErrorMessage("Start Failed", ex.Message);
        }
        finally
        {
            IsBusy = false;
        }
    }

    private bool CanStartOperation() => SelectedOperation?.Status == "Pending" || SelectedOperation?.Status == "Paused";

    [RelayCommand(CanExecute = nameof(CanPauseOperation))]
    private async Task PauseOperationAsync()
    {
        if (SelectedOperation == null) return;

        try
        {
            IsBusy = true;
            StatusMessage = $"Pausing batch operation '{SelectedOperation.Name}'...";

            await _apiClient.PostAsync($"batchoperations/{SelectedOperation.Id}/pause", null);

            StatusMessage = "Batch operation paused";
            await LoadOperationsAsync();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to pause batch operation");
            StatusMessage = "Failed to pause batch operation";
            _dialogService.ShowErrorMessage("Pause Failed", ex.Message);
        }
        finally
        {
            IsBusy = false;
        }
    }

    private bool CanPauseOperation() => SelectedOperation?.Status == "Running";

    [RelayCommand(CanExecute = nameof(CanResumeOperation))]
    private async Task ResumeOperationAsync()
    {
        if (SelectedOperation == null) return;

        try
        {
            IsBusy = true;
            StatusMessage = $"Resuming batch operation '{SelectedOperation.Name}'...";

            await _apiClient.PostAsync($"batchoperations/{SelectedOperation.Id}/resume", null);

            StatusMessage = "Batch operation resumed";
            await LoadOperationsAsync();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to resume batch operation");
            StatusMessage = "Failed to resume batch operation";
            _dialogService.ShowErrorMessage("Resume Failed", ex.Message);
        }
        finally
        {
            IsBusy = false;
        }
    }

    private bool CanResumeOperation() => SelectedOperation?.Status == "Paused";

    [RelayCommand(CanExecute = nameof(CanCancelOperation))]
    private async Task CancelOperationAsync()
    {
        if (SelectedOperation == null) return;

        var confirm = _dialogService.ShowConfirmation(
            "Cancel Batch Operation",
            $"Are you sure you want to cancel '{SelectedOperation.Name}'?");

        if (!confirm) return;

        try
        {
            IsBusy = true;
            StatusMessage = $"Cancelling batch operation '{SelectedOperation.Name}'...";

            await _apiClient.PostAsync($"batchoperations/{SelectedOperation.Id}/cancel", null);

            StatusMessage = "Batch operation cancelled";
            await LoadOperationsAsync();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to cancel batch operation");
            StatusMessage = "Failed to cancel batch operation";
            _dialogService.ShowErrorMessage("Cancel Failed", ex.Message);
        }
        finally
        {
            IsBusy = false;
        }
    }

    private bool CanCancelOperation() => SelectedOperation?.Status == "Running" || SelectedOperation?.Status == "Paused";

    [RelayCommand(CanExecute = nameof(CanDeleteOperation))]
    private async Task DeleteOperationAsync()
    {
        if (SelectedOperation == null) return;

        var confirm = _dialogService.ShowConfirmation(
            "Delete Batch Operation",
            $"Are you sure you want to delete '{SelectedOperation.Name}'?");

        if (!confirm) return;

        try
        {
            IsBusy = true;
            StatusMessage = $"Deleting batch operation '{SelectedOperation.Name}'...";

            await _apiClient.DeleteAsync($"batchoperations/{SelectedOperation.Id}");

            StatusMessage = "Batch operation deleted";
            await LoadOperationsAsync();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to delete batch operation");
            StatusMessage = "Failed to delete batch operation";
            _dialogService.ShowErrorMessage("Delete Failed", ex.Message);
        }
        finally
        {
            IsBusy = false;
        }
    }

    private bool CanDeleteOperation() => SelectedOperation?.Status == "Completed" ||
                                         SelectedOperation?.Status == "Failed" ||
                                         SelectedOperation?.Status == "Cancelled";

    [RelayCommand(CanExecute = nameof(CanRetryFailed))]
    private async Task RetryFailedAsync()
    {
        if (SelectedOperation == null) return;

        try
        {
            IsBusy = true;
            StatusMessage = $"Retrying failed images in '{SelectedOperation.Name}'...";

            await _apiClient.PostAsync($"batchoperations/{SelectedOperation.Id}/retry", null);

            StatusMessage = "Retry started";
            _dialogService.ShowSuccessMessage("Success", "Retrying failed images");
            await LoadOperationsAsync();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to retry failed images");
            StatusMessage = "Failed to retry failed images";
            _dialogService.ShowErrorMessage("Retry Failed", ex.Message);
        }
        finally
        {
            IsBusy = false;
        }
    }

    private bool CanRetryFailed() => SelectedOperation?.Summary?.FailedImages > 0;

    private async Task LoadOperationsAsync()
    {
        try
        {
            IsBusy = true;

            var endpoint = "batchoperations/active";
            var operations = await _apiClient.GetAsync<List<BatchOperationDto>>(endpoint);

            // Apply filters
            if (operations != null)
            {
                if (FilterStatus != "All")
                {
                    operations = operations.Where(o => o.Status == FilterStatus).ToList();
                }

                if (FilterType != "All")
                {
                    operations = operations.Where(o => o.Type == FilterType).ToList();
                }

                // Update collection without clearing to maintain selection if possible
                var selectedId = SelectedOperation?.Id;
                Operations.Clear();
                foreach (var operation in operations.OrderByDescending(o => o.CreatedAt))
                {
                    Operations.Add(operation);
                }

                // Restore selection if exists
                if (selectedId != null)
                {
                    SelectedOperation = Operations.FirstOrDefault(o => o.Id == selectedId);
                }
            }

            StatusMessage = $"Loaded {Operations.Count} batch operations";
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to load batch operations");
            StatusMessage = "Failed to load batch operations";
        }
        finally
        {
            IsBusy = false;
        }
    }
}

#region DTOs

public class BatchOperationDto
{
    public string Id { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public string Type { get; set; } = string.Empty;
    public string Status { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; }
    public DateTime? StartedAt { get; set; }
    public DateTime? CompletedAt { get; set; }
    public long DurationMs { get; set; }
    public string CreatedBy { get; set; } = string.Empty;
    public List<BatchTargetImageDto> TargetImages { get; set; } = new();
    public int Priority { get; set; }
    public int MaxParallelOperations { get; set; }
    public bool ContinueOnError { get; set; }
    public int ProgressPercentage { get; set; }
    public string StatusMessage { get; set; } = string.Empty;
    public BatchOperationSummaryDto? Summary { get; set; }
    public string? ErrorMessage { get; set; }
    public List<string> Tags { get; set; } = new();

    public string DurationFormatted => DurationMs > 0
        ? TimeSpan.FromMilliseconds(DurationMs).ToString(@"hh\:mm\:ss")
        : "N/A";

    public string ProgressDisplay => $"{ProgressPercentage}%";
}

public class BatchTargetImageDto
{
    public string ImagePath { get; set; } = string.Empty;
    public int ImageIndex { get; set; }
    public string? MountPath { get; set; }
    public string Status { get; set; } = "Pending";
    public int ProgressPercentage { get; set; }
    public string StatusMessage { get; set; } = string.Empty;
    public string? ErrorMessage { get; set; }
    public DateTime? StartedAt { get; set; }
    public DateTime? CompletedAt { get; set; }
    public long DurationMs { get; set; }

    public string ImageName => System.IO.Path.GetFileName(ImagePath);
    public string DurationFormatted => DurationMs > 0
        ? TimeSpan.FromMilliseconds(DurationMs).ToString(@"hh\:mm\:ss")
        : "N/A";
}

public class BatchOperationSummaryDto
{
    public int TotalImages { get; set; }
    public int SuccessfulImages { get; set; }
    public int FailedImages { get; set; }
    public int SkippedImages { get; set; }
    public int CancelledImages { get; set; }
    public double SuccessRate { get; set; }
    public double AverageDurationMs { get; set; }
    public long TotalBytesProcessed { get; set; }
}

public class CreateBatchOperationRequestDto
{
    public string Name { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public string Type { get; set; } = string.Empty;
    public List<BatchTargetImageDto> TargetImages { get; set; } = new();
    public int Priority { get; set; } = 5;
    public int MaxParallelOperations { get; set; } = 2;
    public bool ContinueOnError { get; set; } = true;
    public bool StartImmediately { get; set; }
    public List<string> Tags { get; set; } = new();
}

#endregion
