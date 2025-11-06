using DeployForge.Desktop.Services;
using Microsoft.Extensions.Logging;

namespace DeployForge.Desktop.ViewModels;

public partial class ComponentManagerViewModel : ViewModelBase
{
    private readonly IApiClient _apiClient;
    private readonly ILogger<ComponentManagerViewModel> _logger;

    public ComponentManagerViewModel(IApiClient apiClient, ILogger<ComponentManagerViewModel> logger)
    {
        _apiClient = apiClient;
        _logger = logger;
    }
}
