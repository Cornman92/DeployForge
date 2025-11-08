using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.Input;
using DeployForge.Desktop.Services;
using Microsoft.Extensions.Logging;

namespace DeployForge.Desktop.ViewModels;

/// <summary>
/// Template Manager ViewModel
/// </summary>
public partial class TemplateManagerViewModel : ViewModelBase
{
    private readonly IApiClient _apiClient;
    private readonly IDialogService _dialogService;
    private readonly ILogger<TemplateManagerViewModel> _logger;

    private ImageTemplate? _selectedTemplate;
    private string _searchText = string.Empty;
    private string _selectedTag = string.Empty;
    private bool _showPredefinedOnly;

    public ImageTemplate? SelectedTemplate
    {
        get => _selectedTemplate;
        set
        {
            if (SetProperty(ref _selectedTemplate, value))
            {
                DeleteTemplateCommand.NotifyCanExecuteChanged();
                EditTemplateCommand.NotifyCanExecuteChanged();
                ApplyTemplateCommand.NotifyCanExecuteChanged();
                ExportTemplateCommand.NotifyCanExecuteChanged();
            }
        }
    }

    public string SearchText
    {
        get => _searchText;
        set
        {
            if (SetProperty(ref _searchText, value))
            {
                FilterTemplates();
            }
        }
    }

    public string SelectedTag
    {
        get => _selectedTag;
        set
        {
            if (SetProperty(ref _selectedTag, value))
            {
                _ = LoadTemplatesAsync();
            }
        }
    }

    public bool ShowPredefinedOnly
    {
        get => _showPredefinedOnly;
        set
        {
            if (SetProperty(ref _showPredefinedOnly, value))
            {
                _ = LoadTemplatesAsync();
            }
        }
    }

    public ObservableCollection<ImageTemplate> Templates { get; } = new();
    public ObservableCollection<ImageTemplate> FilteredTemplates { get; } = new();
    public ObservableCollection<string> AvailableTags { get; } = new();

    public TemplateManagerViewModel(
        IApiClient apiClient,
        IDialogService dialogService,
        ILogger<TemplateManagerViewModel> logger)
    {
        _apiClient = apiClient;
        _dialogService = dialogService;
        _logger = logger;
    }

    public override async Task InitializeAsync()
    {
        await base.InitializeAsync();
        await LoadTemplatesAsync();
        await LoadTagsAsync();
    }

    [RelayCommand]
    private async Task RefreshAsync()
    {
        await LoadTemplatesAsync();
        await LoadTagsAsync();
    }

    [RelayCommand]
    private async Task CreateTemplateAsync()
    {
        try
        {
            // Create a template creation dialog (for now, we'll create a basic template)
            var name = _dialogService.ShowInputDialog("Create Template", "Enter template name:");
            if (string.IsNullOrWhiteSpace(name))
                return;

            var description = _dialogService.ShowInputDialog("Create Template", "Enter template description:");
            if (string.IsNullOrWhiteSpace(description))
                return;

            IsBusy = true;
            StatusMessage = "Creating template...";

            var newTemplate = new ImageTemplate
            {
                Name = name,
                Description = description,
                Author = Environment.UserName,
                Version = "1.0.0",
                Tags = new List<string>()
            };

            var result = await _apiClient.PostAsync<ImageTemplate>("imagetemplates", newTemplate);

            if (result != null)
            {
                StatusMessage = "Template created successfully";
                _dialogService.ShowSuccessMessage("Success", $"Template '{name}' created successfully");
                await LoadTemplatesAsync();
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to create template");
            StatusMessage = "Failed to create template";
            _dialogService.ShowErrorMessage("Create Failed", ex.Message);
        }
        finally
        {
            IsBusy = false;
        }
    }

    [RelayCommand(CanExecute = nameof(CanEditTemplate))]
    private async Task EditTemplateAsync()
    {
        if (SelectedTemplate == null) return;

        try
        {
            // For now, we'll just allow editing name and description
            var name = _dialogService.ShowInputDialog("Edit Template", "Enter template name:", SelectedTemplate.Name);
            if (string.IsNullOrWhiteSpace(name))
                return;

            var description = _dialogService.ShowInputDialog("Edit Template", "Enter template description:", SelectedTemplate.Description);
            if (string.IsNullOrWhiteSpace(description))
                return;

            IsBusy = true;
            StatusMessage = "Updating template...";

            var updatedTemplate = SelectedTemplate;
            updatedTemplate.Name = name;
            updatedTemplate.Description = description;

            var result = await _apiClient.PutAsync<ImageTemplate>(
                $"imagetemplates/{SelectedTemplate.Id}",
                updatedTemplate);

            if (result != null)
            {
                StatusMessage = "Template updated successfully";
                _dialogService.ShowSuccessMessage("Success", "Template updated successfully");
                await LoadTemplatesAsync();
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to update template");
            StatusMessage = "Failed to update template";
            _dialogService.ShowErrorMessage("Update Failed", ex.Message);
        }
        finally
        {
            IsBusy = false;
        }
    }

    private bool CanEditTemplate() => SelectedTemplate != null;

    [RelayCommand(CanExecute = nameof(CanDeleteTemplate))]
    private async Task DeleteTemplateAsync()
    {
        if (SelectedTemplate == null) return;

        var confirm = _dialogService.ShowConfirmation(
            "Delete Template",
            $"Are you sure you want to delete template '{SelectedTemplate.Name}'?");

        if (!confirm) return;

        try
        {
            IsBusy = true;
            StatusMessage = "Deleting template...";

            await _apiClient.DeleteAsync($"imagetemplates/{SelectedTemplate.Id}");

            StatusMessage = "Template deleted successfully";
            _dialogService.ShowSuccessMessage("Success", "Template deleted successfully");
            await LoadTemplatesAsync();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to delete template");
            StatusMessage = "Failed to delete template";
            _dialogService.ShowErrorMessage("Delete Failed", ex.Message);
        }
        finally
        {
            IsBusy = false;
        }
    }

    private bool CanDeleteTemplate() => SelectedTemplate != null;

    [RelayCommand(CanExecute = nameof(CanApplyTemplate))]
    private async Task ApplyTemplateAsync()
    {
        if (SelectedTemplate == null) return;

        try
        {
            var imagePath = _dialogService.ShowOpenFileDialog(
                "Select Image File",
                "Windows Image Files (*.wim;*.esd)|*.wim;*.esd");

            if (string.IsNullOrEmpty(imagePath))
                return;

            var mountPath = _dialogService.ShowFolderBrowserDialog("Select Mount Directory");
            if (string.IsNullOrEmpty(mountPath))
                return;

            IsBusy = true;
            StatusMessage = $"Applying template '{SelectedTemplate.Name}'...";

            var request = new ApplyTemplateRequestDto
            {
                TemplateId = SelectedTemplate.Id,
                ImagePath = imagePath,
                MountPath = mountPath,
                ImageIndex = 1,
                DryRun = false
            };

            var result = await _apiClient.PostAsync<ApplyTemplateResultDto>("imagetemplates/apply", request);

            if (result != null)
            {
                var message = result.Success
                    ? $"Template applied successfully.\n\nApplied: {result.AppliedSteps.Count}\nFailed: {result.FailedSteps.Count}\nDuration: {result.Duration.TotalSeconds:F1}s"
                    : $"Template applied with errors.\n\n{result.Message}";

                if (result.Success)
                {
                    _dialogService.ShowSuccessMessage("Success", message);
                }
                else
                {
                    _dialogService.ShowWarningMessage("Partial Success", message);
                }

                StatusMessage = result.Success ? "Template applied successfully" : "Template applied with errors";
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to apply template");
            StatusMessage = "Failed to apply template";
            _dialogService.ShowErrorMessage("Apply Failed", ex.Message);
        }
        finally
        {
            IsBusy = false;
        }
    }

    private bool CanApplyTemplate() => SelectedTemplate != null;

    [RelayCommand(CanExecute = nameof(CanExportTemplate))]
    private async Task ExportTemplateAsync()
    {
        if (SelectedTemplate == null) return;

        try
        {
            var filePath = _dialogService.ShowSaveFileDialog(
                "Export Template",
                "JSON Files (*.json)|*.json",
                $"{SelectedTemplate.Name}.json");

            if (string.IsNullOrEmpty(filePath))
                return;

            IsBusy = true;
            StatusMessage = "Exporting template...";

            var request = new ExportTemplateRequestDto
            {
                DestinationPath = filePath
            };

            var result = await _apiClient.PostAsync<ExportTemplateResponseDto>(
                $"imagetemplates/{SelectedTemplate.Id}/export",
                request);

            if (result != null)
            {
                StatusMessage = "Template exported successfully";
                _dialogService.ShowSuccessMessage("Success", $"Template exported to {filePath}");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to export template");
            StatusMessage = "Failed to export template";
            _dialogService.ShowErrorMessage("Export Failed", ex.Message);
        }
        finally
        {
            IsBusy = false;
        }
    }

    private bool CanExportTemplate() => SelectedTemplate != null;

    [RelayCommand]
    private async Task ImportTemplateAsync()
    {
        try
        {
            var filePath = _dialogService.ShowOpenFileDialog(
                "Import Template",
                "JSON Files (*.json)|*.json");

            if (string.IsNullOrEmpty(filePath))
                return;

            IsBusy = true;
            StatusMessage = "Importing template...";

            var request = new ImportTemplateRequestDto
            {
                FilePath = filePath
            };

            var result = await _apiClient.PostAsync<ImageTemplate>("imagetemplates/import", request);

            if (result != null)
            {
                StatusMessage = "Template imported successfully";
                _dialogService.ShowSuccessMessage("Success", $"Template '{result.Name}' imported successfully");
                await LoadTemplatesAsync();
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to import template");
            StatusMessage = "Failed to import template";
            _dialogService.ShowErrorMessage("Import Failed", ex.Message);
        }
        finally
        {
            IsBusy = false;
        }
    }

    [RelayCommand]
    private async Task LoadPredefinedTemplatesAsync()
    {
        try
        {
            IsBusy = true;
            StatusMessage = "Loading predefined templates...";

            var templates = await _apiClient.GetAsync<List<ImageTemplate>>("imagetemplates/predefined");

            if (templates != null && templates.Count > 0)
            {
                StatusMessage = $"Loaded {templates.Count} predefined templates";
                _dialogService.ShowInformationMessage(
                    "Predefined Templates",
                    $"Found {templates.Count} predefined templates:\n\n" +
                    string.Join("\n", templates.Select(t => $"• {t.Name}")));
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to load predefined templates");
            StatusMessage = "Failed to load predefined templates";
            _dialogService.ShowErrorMessage("Load Failed", ex.Message);
        }
        finally
        {
            IsBusy = false;
        }
    }

    private async Task LoadTemplatesAsync()
    {
        try
        {
            IsBusy = true;
            StatusMessage = "Loading templates...";

            List<ImageTemplate>? templates;

            if (ShowPredefinedOnly)
            {
                templates = await _apiClient.GetAsync<List<ImageTemplate>>("imagetemplates/predefined");
            }
            else
            {
                var endpoint = string.IsNullOrEmpty(SelectedTag)
                    ? "imagetemplates"
                    : $"imagetemplates?tag={SelectedTag}";

                templates = await _apiClient.GetAsync<List<ImageTemplate>>(endpoint);
            }

            Templates.Clear();
            if (templates != null)
            {
                foreach (var template in templates.OrderBy(t => t.Name))
                {
                    Templates.Add(template);
                }
            }

            FilterTemplates();
            StatusMessage = $"Loaded {Templates.Count} templates";
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to load templates");
            StatusMessage = "Failed to load templates";
            _dialogService.ShowErrorMessage("Load Failed", ex.Message);
        }
        finally
        {
            IsBusy = false;
        }
    }

    private async Task LoadTagsAsync()
    {
        try
        {
            var templates = await _apiClient.GetAsync<List<ImageTemplate>>("imagetemplates");

            AvailableTags.Clear();
            AvailableTags.Add("All");

            if (templates != null)
            {
                var tags = templates
                    .SelectMany(t => t.Tags)
                    .Distinct()
                    .OrderBy(t => t);

                foreach (var tag in tags)
                {
                    AvailableTags.Add(tag);
                }
            }

            SelectedTag = "All";
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to load tags");
        }
    }

    private void FilterTemplates()
    {
        FilteredTemplates.Clear();

        var filtered = Templates.AsEnumerable();

        if (!string.IsNullOrWhiteSpace(SearchText))
        {
            filtered = filtered.Where(t =>
                t.Name.Contains(SearchText, StringComparison.OrdinalIgnoreCase) ||
                t.Description.Contains(SearchText, StringComparison.OrdinalIgnoreCase) ||
                t.Author.Contains(SearchText, StringComparison.OrdinalIgnoreCase));
        }

        foreach (var template in filtered)
        {
            FilteredTemplates.Add(template);
        }
    }
}

#region DTOs

public class ImageTemplate
{
    public string Id { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public string Author { get; set; } = string.Empty;
    public string Version { get; set; } = string.Empty;
    public DateTime CreatedDate { get; set; }
    public DateTime ModifiedDate { get; set; }
    public List<string> Tags { get; set; } = new();
    public List<string> TargetVersions { get; set; } = new();
    public DebloatConfig? Debloat { get; set; }
    public ComponentConfig? Components { get; set; }
    public UpdateConfig? Updates { get; set; }
}

public class DebloatConfig
{
    public string PresetId { get; set; } = string.Empty;
    public List<string> AdditionalComponentsToRemove { get; set; } = new();
}

public class ComponentConfig
{
    public List<string> ComponentsToRemove { get; set; } = new();
    public List<string> FeaturesToDisable { get; set; } = new();
}

public class UpdateConfig
{
    public List<string> UpdatePaths { get; set; } = new();
}

public class ApplyTemplateRequestDto
{
    public string TemplateId { get; set; } = string.Empty;
    public string ImagePath { get; set; } = string.Empty;
    public string MountPath { get; set; } = string.Empty;
    public int ImageIndex { get; set; }
    public bool DryRun { get; set; }
}

public class ApplyTemplateResultDto
{
    public bool Success { get; set; }
    public string Message { get; set; } = string.Empty;
    public List<string> AppliedSteps { get; set; } = new();
    public List<string> FailedSteps { get; set; } = new();
    public TimeSpan Duration { get; set; }
}

public class ExportTemplateRequestDto
{
    public string DestinationPath { get; set; } = string.Empty;
}

public class ExportTemplateResponseDto
{
    public string Path { get; set; } = string.Empty;
}

public class ImportTemplateRequestDto
{
    public string FilePath { get; set; } = string.Empty;
}

#endregion
