using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using DeployForge.Core.Enums;
using DeployForge.Core.Interfaces;
using DeployForge.Core.Models;

namespace DeployForge.App.ViewModels;

/// <summary>
/// ViewModel for the Profiles page.
/// </summary>
public partial class ProfilesViewModel : PageViewModelBase
{
    private readonly MainViewModel _mainViewModel;
    private readonly ITemplateService _templateService;
    
    public override string Title => "Profiles";
    public override string Icon => "\uE77B";
    
    [ObservableProperty]
    private BuildProfile? _selectedProfile;
    
    [ObservableProperty]
    private bool _isEditing;
    
    [ObservableProperty]
    private string _editProfileName = string.Empty;
    
    [ObservableProperty]
    private string _editProfileDescription = string.Empty;
    
    /// <summary>
    /// Built-in profiles.
    /// </summary>
    public ObservableCollection<ProfileCard> BuiltInProfiles { get; } = new();
    
    /// <summary>
    /// Custom user profiles.
    /// </summary>
    public ObservableCollection<ProfileCard> CustomProfiles { get; } = new();
    
    public ProfilesViewModel(
        MainViewModel mainViewModel,
        ITemplateService templateService)
    {
        _mainViewModel = mainViewModel;
        _templateService = templateService;
        
        LoadBuiltInProfiles();
    }
    
    public override async Task OnNavigatedToAsync()
    {
        await LoadCustomProfilesAsync();
    }
    
    /// <summary>
    /// Loads the built-in profiles.
    /// </summary>
    private void LoadBuiltInProfiles()
    {
        BuiltInProfiles.Clear();
        
        foreach (var profile in _templateService.GetBuiltInProfiles())
        {
            BuiltInProfiles.Add(new ProfileCard
            {
                Profile = profile,
                Name = profile.Name,
                Description = profile.Description,
                Icon = profile.Icon,
                Type = profile.Type,
                IsBuiltIn = true
            });
        }
    }
    
    /// <summary>
    /// Loads custom profiles from disk.
    /// </summary>
    private async Task LoadCustomProfilesAsync()
    {
        CustomProfiles.Clear();
        
        try
        {
            var profiles = await _templateService.GetCustomTemplatesAsync();
            
            foreach (var profile in profiles)
            {
                CustomProfiles.Add(new ProfileCard
                {
                    Profile = profile,
                    Name = profile.Name,
                    Description = profile.Description,
                    Icon = profile.Icon,
                    Type = profile.Type,
                    IsBuiltIn = false
                });
            }
        }
        catch
        {
            // Handle error silently
        }
    }
    
    /// <summary>
    /// Selects a profile by type.
    /// </summary>
    public void SelectProfile(BuildProfileType type)
    {
        var card = BuiltInProfiles.FirstOrDefault(p => p.Type == type);
        if (card != null)
        {
            SelectedProfile = card.Profile;
            _mainViewModel.BuildPage.ApplyProfile(card.Profile);
        }
    }
    
    /// <summary>
    /// Applies the selected profile.
    /// </summary>
    [RelayCommand]
    private async Task ApplyProfileAsync(ProfileCard card)
    {
        if (card?.Profile == null) return;
        
        SelectedProfile = card.Profile;
        _mainViewModel.BuildPage.ApplyProfile(card.Profile);
        
        await _mainViewModel.NavigateToCommand.ExecuteAsync(_mainViewModel.BuildPage);
    }
    
    /// <summary>
    /// Creates a new custom profile.
    /// </summary>
    [RelayCommand]
    private void CreateNewProfile()
    {
        IsEditing = true;
        EditProfileName = "New Profile";
        EditProfileDescription = "Custom profile description";
        SelectedProfile = new BuildProfile
        {
            Name = EditProfileName,
            Description = EditProfileDescription,
            Type = BuildProfileType.Custom
        };
    }
    
    /// <summary>
    /// Edits an existing custom profile.
    /// </summary>
    [RelayCommand]
    private void EditProfile(ProfileCard card)
    {
        if (card?.Profile == null || card.IsBuiltIn) return;
        
        IsEditing = true;
        SelectedProfile = card.Profile;
        EditProfileName = card.Profile.Name;
        EditProfileDescription = card.Profile.Description;
    }
    
    /// <summary>
    /// Saves the current profile.
    /// </summary>
    [RelayCommand]
    private async Task SaveProfileAsync()
    {
        if (SelectedProfile == null) return;
        
        SelectedProfile.Name = EditProfileName;
        SelectedProfile.Description = EditProfileDescription;
        
        if (_templateService is TemplateService ts)
        {
            await ts.SaveTemplateAsync(SelectedProfile);
        }
        
        IsEditing = false;
        await LoadCustomProfilesAsync();
    }
    
    /// <summary>
    /// Cancels editing.
    /// </summary>
    [RelayCommand]
    private void CancelEdit()
    {
        IsEditing = false;
        EditProfileName = string.Empty;
        EditProfileDescription = string.Empty;
    }
    
    /// <summary>
    /// Deletes a custom profile.
    /// </summary>
    [RelayCommand]
    private async Task DeleteProfileAsync(ProfileCard card)
    {
        if (card?.Profile == null || card.IsBuiltIn) return;
        
        if (_templateService is TemplateService ts)
        {
            var path = Path.Combine(
                ts.GetTemplatesDirectory(), 
                SanitizeFileName(card.Profile.Name) + ".json");
            
            await _templateService.DeleteTemplateAsync(path);
        }
        
        CustomProfiles.Remove(card);
    }
    
    /// <summary>
    /// Duplicates a profile.
    /// </summary>
    [RelayCommand]
    private async Task DuplicateProfileAsync(ProfileCard card)
    {
        if (card?.Profile == null) return;
        
        if (_templateService is TemplateService ts)
        {
            var newProfile = ts.CreateFromBuiltIn(card.Type, $"{card.Profile.Name} (Copy)");
            
            // Copy all settings from original
            newProfile.Gaming = card.Profile.Gaming;
            newProfile.Debloat = card.Profile.Debloat;
            newProfile.DevEnvironment = card.Profile.DevEnvironment;
            newProfile.Browsers = card.Profile.Browsers;
            newProfile.UICustomization = card.Profile.UICustomization;
            newProfile.EnableGaming = card.Profile.EnableGaming;
            newProfile.EnableDebloat = card.Profile.EnableDebloat;
            newProfile.EnableDevEnvironment = card.Profile.EnableDevEnvironment;
            newProfile.EnableBrowsers = card.Profile.EnableBrowsers;
            newProfile.EnableUICustomization = card.Profile.EnableUICustomization;
            newProfile.PrivacyLevel = card.Profile.PrivacyLevel;
            
            await ts.SaveTemplateAsync(newProfile);
            await LoadCustomProfilesAsync();
        }
    }
    
    /// <summary>
    /// Exports a profile to file.
    /// </summary>
    [RelayCommand]
    private async Task ExportProfileAsync(ProfileCard card)
    {
        if (card?.Profile == null) return;
        
        // File save dialog will be handled in View
        await Task.CompletedTask;
    }
    
    /// <summary>
    /// Imports a profile from file.
    /// </summary>
    [RelayCommand]
    private async Task ImportProfileAsync()
    {
        // File open dialog will be handled in View
        await Task.CompletedTask;
    }
    
    /// <summary>
    /// Imports a profile from a path.
    /// </summary>
    public async Task ImportFromPathAsync(string path)
    {
        try
        {
            var profile = await _templateService.LoadTemplateAsync(path);
            profile.Type = BuildProfileType.Custom;
            
            if (_templateService is TemplateService ts)
            {
                await ts.SaveTemplateAsync(profile);
            }
            
            await LoadCustomProfilesAsync();
        }
        catch (Exception ex)
        {
            SetError($"Failed to import profile: {ex.Message}");
        }
    }
    
    private static string SanitizeFileName(string name)
    {
        var invalid = Path.GetInvalidFileNameChars();
        return string.Join("_", name.Split(invalid, StringSplitOptions.RemoveEmptyEntries));
    }
}

/// <summary>
/// Profile card for display in UI.
/// </summary>
public partial class ProfileCard : ObservableObject
{
    public BuildProfile Profile { get; set; } = new();
    
    [ObservableProperty]
    private string _name = string.Empty;
    
    [ObservableProperty]
    private string _description = string.Empty;
    
    [ObservableProperty]
    private string _icon = "⚙️";
    
    [ObservableProperty]
    private BuildProfileType _type;
    
    [ObservableProperty]
    private bool _isBuiltIn;
    
    /// <summary>
    /// Features summary for display.
    /// </summary>
    public string FeaturesSummary
    {
        get
        {
            var features = new List<string>();
            
            if (Profile.EnableGaming) features.Add("Gaming");
            if (Profile.EnableDebloat) features.Add("Debloat");
            if (Profile.EnableDevEnvironment) features.Add("Dev Tools");
            if (Profile.EnableBrowsers) features.Add("Browsers");
            if (Profile.EnableUICustomization) features.Add("UI Customization");
            if (Profile.EnablePrivacyHardening) features.Add("Privacy");
            
            return features.Count > 0 
                ? string.Join(" • ", features) 
                : "No features configured";
        }
    }
}
