using DeployForge.Desktop.Services;
using Microsoft.Extensions.Logging;

namespace DeployForge.Desktop.ViewModels;

public partial class DebloatWizardViewModel : ViewModelBase
{
    private readonly IApiClient _apiClient;
    private readonly ILogger<DebloatWizardViewModel> _logger;

    public DebloatWizardViewModel(IApiClient apiClient, ILogger<DebloatWizardViewModel> logger)
    {
        _apiClient = apiClient;
        _logger = logger;
    }
}
