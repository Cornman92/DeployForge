using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using DeployForge.App.ViewModels;
using Windows.Storage.Pickers;

namespace DeployForge.App.Views;

/// <summary>
/// Profiles management page.
/// </summary>
public sealed partial class ProfilesPage : Page
{
    /// <summary>
    /// Page ViewModel.
    /// </summary>
    public ProfilesViewModel ViewModel { get; }
    
    public ProfilesPage()
    {
        this.InitializeComponent();
        
        var mainViewModel = App.GetService<MainViewModel>();
        ViewModel = mainViewModel.ProfilesPage;
        
        this.DataContext = ViewModel;
    }
    
    /// <summary>
    /// Handles profile card click.
    /// </summary>
    private async void ProfileCard_Click(object sender, ItemClickEventArgs e)
    {
        if (e.ClickedItem is ProfileCard card)
        {
            await ViewModel.ApplyProfileCommand.ExecuteAsync(card);
        }
    }
    
    /// <summary>
    /// Handles edit profile menu item click.
    /// </summary>
    private async void EditProfile_Click(object sender, RoutedEventArgs e)
    {
        if (sender is FrameworkElement element && GetProfileCard(element) is ProfileCard card)
        {
            ViewModel.EditProfileCommand.Execute(card);
            EditProfileDialog.XamlRoot = this.XamlRoot;
            await EditProfileDialog.ShowAsync();
        }
    }
    
    /// <summary>
    /// Handles duplicate profile menu item click.
    /// </summary>
    private async void DuplicateProfile_Click(object sender, RoutedEventArgs e)
    {
        if (sender is FrameworkElement element && GetProfileCard(element) is ProfileCard card)
        {
            await ViewModel.DuplicateProfileCommand.ExecuteAsync(card);
        }
    }
    
    /// <summary>
    /// Handles export profile menu item click.
    /// </summary>
    private async void ExportProfile_Click(object sender, RoutedEventArgs e)
    {
        if (sender is FrameworkElement element && GetProfileCard(element) is ProfileCard card)
        {
            var picker = new FileSavePicker();
            
            var hwnd = WinRT.Interop.WindowNative.GetWindowHandle(App.MainWindow);
            WinRT.Interop.InitializeWithWindow.Initialize(picker, hwnd);
            
            picker.SuggestedStartLocation = PickerLocationId.DocumentsLibrary;
            picker.SuggestedFileName = $"{card.Name}.json";
            picker.FileTypeChoices.Add("JSON Profile", new List<string> { ".json" });
            
            var file = await picker.PickSaveFileAsync();
            
            if (file != null)
            {
                var templateService = App.GetService<Core.Interfaces.ITemplateService>();
                await templateService.SaveTemplateAsync(card.Profile, file.Path);
            }
        }
    }
    
    /// <summary>
    /// Handles delete profile menu item click.
    /// </summary>
    private async void DeleteProfile_Click(object sender, RoutedEventArgs e)
    {
        if (sender is FrameworkElement element && GetProfileCard(element) is ProfileCard card)
        {
            var dialog = new ContentDialog
            {
                Title = "Delete Profile",
                Content = $"Are you sure you want to delete '{card.Name}'?",
                PrimaryButtonText = "Delete",
                CloseButtonText = "Cancel",
                DefaultButton = ContentDialogButton.Close,
                XamlRoot = this.XamlRoot
            };
            
            var result = await dialog.ShowAsync();
            
            if (result == ContentDialogResult.Primary)
            {
                await ViewModel.DeleteProfileCommand.ExecuteAsync(card);
            }
        }
    }
    
    /// <summary>
    /// Handles edit profile dialog save.
    /// </summary>
    private async void EditProfileDialog_Save(ContentDialog sender, ContentDialogButtonClickEventArgs args)
    {
        await ViewModel.SaveProfileCommand.ExecuteAsync();
    }
    
    /// <summary>
    /// Gets the ProfileCard from a nested element.
    /// </summary>
    private static ProfileCard? GetProfileCard(FrameworkElement element)
    {
        var current = element;
        
        while (current != null)
        {
            if (current.DataContext is ProfileCard card)
            {
                return card;
            }
            
            current = current.Parent as FrameworkElement;
        }
        
        return null;
    }
    
    /// <summary>
    /// Helper to check if there are custom profiles.
    /// </summary>
    private Visibility HasCustomProfiles(int count)
    {
        return count > 0 ? Visibility.Visible : Visibility.Collapsed;
    }
    
    /// <summary>
    /// Helper to check if there are no custom profiles.
    /// </summary>
    private Visibility NoCustomProfiles(int count)
    {
        return count == 0 ? Visibility.Visible : Visibility.Collapsed;
    }
}
