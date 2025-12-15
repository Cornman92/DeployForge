using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using DeployForge.App.Models;
using DeployForge.App.Services;

namespace DeployForge.App.ViewModels;

public partial class ProfilesViewModel : ObservableObject
{
    private readonly IProfileService _profileService;
    private readonly IDialogService _dialogService;
    private readonly INavigationService _navigationService;
    
    [ObservableProperty]
    private List<Profile> _builtInProfiles = new();
    
    [ObservableProperty]
    private List<Profile> _customProfiles = new();
    
    [ObservableProperty]
    private Profile? _selectedProfile;
    
    [ObservableProperty]
    private bool _isEditing;
    
    // Editable profile properties
    [ObservableProperty] private string _editName = "";
    [ObservableProperty] private string _editDescription = "";
    [ObservableProperty] private bool _editRemoveBloatware;
    [ObservableProperty] private DebloatLevel _editDebloatLevel = DebloatLevel.Moderate;
    [ObservableProperty] private bool _editDisableTelemetry;
    [ObservableProperty] private bool _editDisableCortana;
    [ObservableProperty] private PrivacyLevel _editPrivacyLevel = PrivacyLevel.Balanced;
    [ObservableProperty] private bool _editEnableGameMode;
    [ObservableProperty] private GamingProfile _editGamingProfile = GamingProfile.Balanced;
    [ObservableProperty] private bool _editEnableDeveloperMode;
    [ObservableProperty] private bool _editInstallWsl2;
    [ObservableProperty] private bool _editOptimizeServices;
    
    public ProfilesViewModel(
        IProfileService profileService,
        IDialogService dialogService,
        INavigationService navigationService)
    {
        _profileService = profileService;
        _dialogService = dialogService;
        _navigationService = navigationService;
    }
    
    public async Task InitializeAsync()
    {
        await _profileService.LoadProfilesAsync();
        RefreshProfiles();
    }
    
    private void RefreshProfiles()
    {
        BuiltInProfiles = _profileService.BuiltInProfiles.ToList();
        CustomProfiles = _profileService.CustomProfiles.ToList();
    }
    
    [RelayCommand]
    private void SelectProfile(Profile profile)
    {
        SelectedProfile = profile;
        LoadProfileForEditing(profile);
    }
    
    private void LoadProfileForEditing(Profile profile)
    {
        EditName = profile.Name;
        EditDescription = profile.Description;
        EditRemoveBloatware = profile.Features.RemoveBloatware;
        EditDebloatLevel = profile.Features.DebloatLevel;
        EditDisableTelemetry = profile.Features.DisableTelemetry;
        EditDisableCortana = profile.Features.DisableCortana;
        EditPrivacyLevel = profile.Features.PrivacyLevel;
        EditEnableGameMode = profile.Features.EnableGameMode;
        EditGamingProfile = profile.Features.GamingProfile;
        EditEnableDeveloperMode = profile.Features.EnableDeveloperMode;
        EditInstallWsl2 = profile.Features.InstallWSL2;
        EditOptimizeServices = profile.Features.OptimizeServices;
    }
    
    [RelayCommand]
    private void CreateNewProfile()
    {
        SelectedProfile = null;
        IsEditing = true;
        
        EditName = "New Profile";
        EditDescription = "";
        EditRemoveBloatware = true;
        EditDebloatLevel = DebloatLevel.Moderate;
        EditDisableTelemetry = true;
        EditDisableCortana = false;
        EditPrivacyLevel = PrivacyLevel.Balanced;
        EditEnableGameMode = false;
        EditGamingProfile = GamingProfile.Balanced;
        EditEnableDeveloperMode = false;
        EditInstallWsl2 = false;
        EditOptimizeServices = false;
    }
    
    [RelayCommand]
    private void EditProfile()
    {
        if (SelectedProfile == null || SelectedProfile.IsBuiltIn) return;
        IsEditing = true;
    }
    
    [RelayCommand]
    private void DuplicateProfile()
    {
        if (SelectedProfile == null) return;
        
        SelectedProfile = null;
        IsEditing = true;
        EditName = EditName + " (Copy)";
    }
    
    [RelayCommand]
    private async Task SaveProfileAsync()
    {
        if (string.IsNullOrWhiteSpace(EditName))
        {
            await _dialogService.ShowDialogAsync("Error", "Profile name is required.");
            return;
        }
        
        var profile = new Profile
        {
            Id = SelectedProfile?.Id ?? Guid.NewGuid().ToString(),
            Name = EditName,
            Description = EditDescription,
            Type = ProfileType.Custom,
            IconGlyph = "\uE71C",
            IsBuiltIn = false,
            ModifiedAt = DateTime.Now,
            Features = new ProfileFeatures
            {
                RemoveBloatware = EditRemoveBloatware,
                DebloatLevel = EditDebloatLevel,
                DisableTelemetry = EditDisableTelemetry,
                DisableCortana = EditDisableCortana,
                PrivacyLevel = EditPrivacyLevel,
                EnableGameMode = EditEnableGameMode,
                GamingProfile = EditGamingProfile,
                EnableDeveloperMode = EditEnableDeveloperMode,
                InstallWSL2 = EditInstallWsl2,
                OptimizeServices = EditOptimizeServices
            }
        };
        
        await _profileService.SaveProfileAsync(profile);
        IsEditing = false;
        RefreshProfiles();
        SelectedProfile = profile;
    }
    
    [RelayCommand]
    private void CancelEdit()
    {
        IsEditing = false;
        if (SelectedProfile != null)
        {
            LoadProfileForEditing(SelectedProfile);
        }
    }
    
    [RelayCommand]
    private async Task DeleteProfileAsync()
    {
        if (SelectedProfile == null || SelectedProfile.IsBuiltIn) return;
        
        var result = await _dialogService.ShowDialogAsync(
            "Delete Profile",
            $"Are you sure you want to delete '{SelectedProfile.Name}'?",
            "Delete", "Cancel");
        
        if (result == Microsoft.UI.Xaml.Controls.ContentDialogResult.Primary)
        {
            await _profileService.DeleteProfileAsync(SelectedProfile.Id);
            SelectedProfile = null;
            RefreshProfiles();
        }
    }
    
    [RelayCommand]
    private void UseProfile()
    {
        if (SelectedProfile != null)
        {
            _navigationService.NavigateTo("Build", new BuildConfiguration
            {
                ProfileId = SelectedProfile.Id,
                Features = SelectedProfile.Features
            });
        }
    }
}
