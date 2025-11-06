using DeployForge.Desktop.Services;
using Microsoft.Extensions.Logging;

namespace DeployForge.Desktop.ViewModels;

public partial class BackupManagerViewModel : ViewModelBase
{
    private readonly IApiClient _apiClient;
    private readonly ILogger<BackupManagerViewModel> _logger;

    public BackupManagerViewModel(IApiClient apiClient, ILogger<BackupManagerViewModel> logger)
    {
        _apiClient = apiClient;
        _logger = logger;
    }
}
