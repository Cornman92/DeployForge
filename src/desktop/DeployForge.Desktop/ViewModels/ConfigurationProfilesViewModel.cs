using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.Input;
using DeployForge.Desktop.Services;
using Microsoft.Extensions.Logging;

namespace DeployForge.Desktop.ViewModels;

/// <summary>
/// Configuration Profiles ViewModel
/// </summary>
public partial class ConfigurationProfilesViewModel : ViewModelBase
{
    private readonly IApiClient _apiClient;
    private readonly IDialogService _dialogService;
    private readonly ILogger<ConfigurationProfilesViewModel> _logger;

    private ConfigurationProfileDto? _selectedProfile;
    private string _searchText = string.Empty;

    public ConfigurationProfileDto? SelectedProfile
    {
        get => _selectedProfile;
        set
        {
            if (SetProperty(ref _selectedProfile, value))
            {
                EditProfileCommand.NotifyCanExecuteChanged();
                DeleteProfileCommand.NotifyCanExecuteChanged();
                SetDefaultCommand.NotifyCanExecuteChanged();
                DuplicateProfileCommand.NotifyCanExecuteChanged();
                ExportProfileCommand.NotifyCanExecuteChanged();
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
                FilterProfiles();
            }
        }
    }

    public ObservableCollection<ConfigurationProfileDto> Profiles { get; } = new();
    public ObservableCollection<ConfigurationProfileDto> FilteredProfiles { get; } = new();

    public ConfigurationProfilesViewModel(
        IApiClient apiClient,
        IDialogService dialogService,
        ILogger<ConfigurationProfilesViewModel> logger)
    {
        _apiClient = apiClient;
        _dialogService = dialogService;
        _logger = logger;
    }

    public override async Task InitializeAsync()
    {
        await base.InitializeAsync();
        await LoadProfilesAsync();
    }

    [RelayCommand]
    private async Task RefreshAsync()
    {
        await LoadProfilesAsync();
    }

    [RelayCommand]
    private async Task CreateProfileAsync()
    {
        try
        {
            var name = _dialogService.ShowInputDialog("Create Profile", "Enter profile name:");
            if (string.IsNullOrWhiteSpace(name))
                return;

            var description = _dialogService.ShowInputDialog("Create Profile", "Enter profile description:");

            IsBusy = true;
            StatusMessage = "Creating profile...";

            var newProfile = new ConfigurationProfileDto
            {
                Name = name,
                Description = description ?? string.Empty,
                Owner = Environment.UserName,
                IsDefault = false,
                IsShared = false,
                General = new GeneralSettingsDto(),
                ImageOperations = new ImageOperationSettingsDto(),
                Deployment = new DeploymentSettingsDto(),
                Backup = new BackupSettingsDto(),
                Workflow = new WorkflowSettingsDto(),
                Advanced = new AdvancedSettingsDto()
            };

            var result = await _apiClient.PostAsync<ConfigurationProfileDto>("configurationprofiles", newProfile);

            if (result != null)
            {
                StatusMessage = "Profile created successfully";
                _dialogService.ShowSuccessMessage("Success", $"Profile '{name}' created successfully");
                await LoadProfilesAsync();
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to create profile");
            StatusMessage = "Failed to create profile";
            _dialogService.ShowErrorMessage("Create Failed", ex.Message);
        }
        finally
        {
            IsBusy = false;
        }
    }

    [RelayCommand(CanExecute = nameof(CanEditProfile))]
    private async Task EditProfileAsync()
    {
        if (SelectedProfile == null) return;

        try
        {
            var name = _dialogService.ShowInputDialog("Edit Profile", "Enter profile name:", SelectedProfile.Name);
            if (string.IsNullOrWhiteSpace(name))
                return;

            var description = _dialogService.ShowInputDialog("Edit Profile", "Enter profile description:", SelectedProfile.Description);

            IsBusy = true;
            StatusMessage = "Updating profile...";

            var updatedProfile = SelectedProfile;
            updatedProfile.Name = name;
            updatedProfile.Description = description ?? string.Empty;

            var result = await _apiClient.PutAsync<ConfigurationProfileDto>(
                $"configurationprofiles/{SelectedProfile.Id}",
                updatedProfile);

            if (result != null)
            {
                StatusMessage = "Profile updated successfully";
                _dialogService.ShowSuccessMessage("Success", "Profile updated successfully");
                await LoadProfilesAsync();
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to update profile");
            StatusMessage = "Failed to update profile";
            _dialogService.ShowErrorMessage("Update Failed", ex.Message);
        }
        finally
        {
            IsBusy = false;
        }
    }

    private bool CanEditProfile() => SelectedProfile != null;

    [RelayCommand(CanExecute = nameof(CanDeleteProfile))]
    private async Task DeleteProfileAsync()
    {
        if (SelectedProfile == null) return;

        if (SelectedProfile.IsDefault)
        {
            _dialogService.ShowWarningMessage("Cannot Delete", "Cannot delete the default profile.");
            return;
        }

        var confirm = _dialogService.ShowConfirmation(
            "Delete Profile",
            $"Are you sure you want to delete profile '{SelectedProfile.Name}'?");

        if (!confirm) return;

        try
        {
            IsBusy = true;
            StatusMessage = "Deleting profile...";

            await _apiClient.DeleteAsync($"configurationprofiles/{SelectedProfile.Id}");

            StatusMessage = "Profile deleted successfully";
            _dialogService.ShowSuccessMessage("Success", "Profile deleted successfully");
            await LoadProfilesAsync();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to delete profile");
            StatusMessage = "Failed to delete profile";
            _dialogService.ShowErrorMessage("Delete Failed", ex.Message);
        }
        finally
        {
            IsBusy = false;
        }
    }

    private bool CanDeleteProfile() => SelectedProfile != null && !SelectedProfile.IsDefault;

    [RelayCommand(CanExecute = nameof(CanSetDefault))]
    private async Task SetDefaultAsync()
    {
        if (SelectedProfile == null) return;

        try
        {
            IsBusy = true;
            StatusMessage = $"Setting '{SelectedProfile.Name}' as default profile...";

            await _apiClient.PostAsync($"configurationprofiles/{SelectedProfile.Id}/set-default", null);

            StatusMessage = "Default profile set successfully";
            _dialogService.ShowSuccessMessage("Success", $"'{SelectedProfile.Name}' is now the default profile");
            await LoadProfilesAsync();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to set default profile");
            StatusMessage = "Failed to set default profile";
            _dialogService.ShowErrorMessage("Set Default Failed", ex.Message);
        }
        finally
        {
            IsBusy = false;
        }
    }

    private bool CanSetDefault() => SelectedProfile != null && !SelectedProfile.IsDefault;

    [RelayCommand(CanExecute = nameof(CanDuplicateProfile))]
    private async Task DuplicateProfileAsync()
    {
        if (SelectedProfile == null) return;

        try
        {
            var name = _dialogService.ShowInputDialog(
                "Duplicate Profile",
                "Enter name for the new profile:",
                $"{SelectedProfile.Name} (Copy)");

            if (string.IsNullOrWhiteSpace(name))
                return;

            IsBusy = true;
            StatusMessage = "Duplicating profile...";

            var newProfile = new ConfigurationProfileDto
            {
                Name = name,
                Description = SelectedProfile.Description,
                Owner = Environment.UserName,
                IsDefault = false,
                IsShared = false,
                Tags = new List<string>(SelectedProfile.Tags),
                General = SelectedProfile.General,
                ImageOperations = SelectedProfile.ImageOperations,
                Deployment = SelectedProfile.Deployment,
                Backup = SelectedProfile.Backup,
                Workflow = SelectedProfile.Workflow,
                Advanced = SelectedProfile.Advanced
            };

            var result = await _apiClient.PostAsync<ConfigurationProfileDto>("configurationprofiles", newProfile);

            if (result != null)
            {
                StatusMessage = "Profile duplicated successfully";
                _dialogService.ShowSuccessMessage("Success", $"Profile duplicated as '{name}'");
                await LoadProfilesAsync();
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to duplicate profile");
            StatusMessage = "Failed to duplicate profile";
            _dialogService.ShowErrorMessage("Duplicate Failed", ex.Message);
        }
        finally
        {
            IsBusy = false;
        }
    }

    private bool CanDuplicateProfile() => SelectedProfile != null;

    [RelayCommand(CanExecute = nameof(CanExportProfile))]
    private async Task ExportProfileAsync()
    {
        if (SelectedProfile == null) return;

        try
        {
            var filePath = _dialogService.ShowSaveFileDialog(
                "Export Profile",
                "JSON Files (*.json)|*.json",
                $"{SelectedProfile.Name}.json");

            if (string.IsNullOrEmpty(filePath))
                return;

            IsBusy = true;
            StatusMessage = "Exporting profile...";

            var result = await _apiClient.PostAsync<ExportProfileResponseDto>(
                $"configurationprofiles/{SelectedProfile.Id}/export?outputPath={Uri.EscapeDataString(filePath)}",
                null);

            if (result != null)
            {
                StatusMessage = "Profile exported successfully";
                _dialogService.ShowSuccessMessage("Success", $"Profile exported to {filePath}");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to export profile");
            StatusMessage = "Failed to export profile";
            _dialogService.ShowErrorMessage("Export Failed", ex.Message);
        }
        finally
        {
            IsBusy = false;
        }
    }

    private bool CanExportProfile() => SelectedProfile != null;

    [RelayCommand]
    private async Task ImportProfileAsync()
    {
        try
        {
            var filePath = _dialogService.ShowOpenFileDialog(
                "Import Profile",
                "JSON Files (*.json)|*.json");

            if (string.IsNullOrEmpty(filePath))
                return;

            IsBusy = true;
            StatusMessage = "Importing profile...";

            var request = new ImportProfileRequestDto
            {
                FilePath = filePath
            };

            var result = await _apiClient.PostAsync<ConfigurationProfileDto>("configurationprofiles/import", request);

            if (result != null)
            {
                StatusMessage = "Profile imported successfully";
                _dialogService.ShowSuccessMessage("Success", $"Profile '{result.Name}' imported successfully");
                await LoadProfilesAsync();
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to import profile");
            StatusMessage = "Failed to import profile";
            _dialogService.ShowErrorMessage("Import Failed", ex.Message);
        }
        finally
        {
            IsBusy = false;
        }
    }

    private async Task LoadProfilesAsync()
    {
        try
        {
            IsBusy = true;
            StatusMessage = "Loading profiles...";

            var profiles = await _apiClient.GetAsync<List<ConfigurationProfileDto>>("configurationprofiles");

            Profiles.Clear();
            if (profiles != null)
            {
                foreach (var profile in profiles.OrderByDescending(p => p.IsDefault).ThenBy(p => p.Name))
                {
                    Profiles.Add(profile);
                }
            }

            FilterProfiles();
            StatusMessage = $"Loaded {Profiles.Count} profiles";
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to load profiles");
            StatusMessage = "Failed to load profiles";
            _dialogService.ShowErrorMessage("Load Failed", ex.Message);
        }
        finally
        {
            IsBusy = false;
        }
    }

    private void FilterProfiles()
    {
        FilteredProfiles.Clear();

        var filtered = Profiles.AsEnumerable();

        if (!string.IsNullOrWhiteSpace(SearchText))
        {
            filtered = filtered.Where(p =>
                p.Name.Contains(SearchText, StringComparison.OrdinalIgnoreCase) ||
                p.Description.Contains(SearchText, StringComparison.OrdinalIgnoreCase));
        }

        foreach (var profile in filtered)
        {
            FilteredProfiles.Add(profile);
        }
    }
}

#region DTOs

public class ConfigurationProfileDto
{
    public string Id { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public string Owner { get; set; } = string.Empty;
    public bool IsDefault { get; set; }
    public bool IsShared { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime ModifiedAt { get; set; }
    public List<string> Tags { get; set; } = new();
    public GeneralSettingsDto? General { get; set; }
    public ImageOperationSettingsDto? ImageOperations { get; set; }
    public DeploymentSettingsDto? Deployment { get; set; }
    public BackupSettingsDto? Backup { get; set; }
    public WorkflowSettingsDto? Workflow { get; set; }
    public AdvancedSettingsDto? Advanced { get; set; }
}

public class GeneralSettingsDto
{
    public string DefaultMountPath { get; set; } = @"C:\Mount";
    public string DefaultScratchPath { get; set; } = @"C:\Scratch";
    public string DefaultLogPath { get; set; } = @"C:\DeployForge\Logs";
    public bool AutoCreateDirectories { get; set; } = true;
    public string LogLevel { get; set; } = "Information";
}

public class ImageOperationSettingsDto
{
    public int DefaultImageIndex { get; set; } = 1;
    public bool VerifyIntegrityBeforeOperation { get; set; } = true;
    public bool AutoOptimizeAfterModification { get; set; } = true;
    public string DefaultCompressionType { get; set; } = "Maximum";
}

public class DeploymentSettingsDto
{
    public string DefaultDeploymentMethod { get; set; } = "USB";
    public bool VerifyAfterDeployment { get; set; } = true;
    public bool AutoEjectAfterDeployment { get; set; } = true;
}

public class BackupSettingsDto
{
    public bool AutoBackupBeforeModification { get; set; } = true;
    public string DefaultBackupPath { get; set; } = @"C:\DeployForge\Backups";
    public int MaxBackupCount { get; set; } = 5;
}

public class WorkflowSettingsDto
{
    public bool AutoSaveWorkflows { get; set; } = true;
    public bool ContinueOnError { get; set; } = false;
}

public class AdvancedSettingsDto
{
    public int MaxParallelOperations { get; set; } = 2;
    public bool EnableTelemetry { get; set; } = true;
    public bool EnableDebugLogging { get; set; } = false;
}

public class ExportProfileResponseDto
{
    public string Path { get; set; } = string.Empty;
}

public class ImportProfileRequestDto
{
    public string FilePath { get; set; } = string.Empty;
}

#endregion
