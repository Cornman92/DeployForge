using DeployForge.Desktop.Services;
using Microsoft.Extensions.Logging;

namespace DeployForge.Desktop.ViewModels;

public partial class WorkflowDesignerViewModel : ViewModelBase
{
    private readonly IApiClient _apiClient;
    private readonly ILogger<WorkflowDesignerViewModel> _logger;

    public WorkflowDesignerViewModel(IApiClient apiClient, ILogger<WorkflowDesignerViewModel> logger)
    {
        _apiClient = apiClient;
        _logger = logger;
    }
}
