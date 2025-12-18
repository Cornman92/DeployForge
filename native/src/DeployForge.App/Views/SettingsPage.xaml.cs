using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using DeployForge.App.ViewModels;
using Windows.Storage.Pickers;

namespace DeployForge.App.Views;

/// <summary>
/// Settings page.
/// </summary>
public sealed partial class SettingsPage : Page
{
    /// <summary>
    /// Page ViewModel.
    /// </summary>
    public SettingsViewModel ViewModel { get; }
    
    public SettingsPage()
    {
        this.InitializeComponent();
        
        var mainViewModel = App.GetService<MainViewModel>();
        ViewModel = mainViewModel.SettingsPage;
        
        this.DataContext = ViewModel;
    }
    
    /// <summary>
    /// Handles browse mount path button click.
    /// </summary>
    private async void BrowseMountPath_Click(object sender, RoutedEventArgs e)
    {
        var picker = new FolderPicker();
        
        var hwnd = WinRT.Interop.WindowNative.GetWindowHandle(App.MainWindow);
        WinRT.Interop.InitializeWithWindow.Initialize(picker, hwnd);
        
        picker.SuggestedStartLocation = PickerLocationId.ComputerFolder;
        picker.FileTypeFilter.Add("*");
        
        var folder = await picker.PickSingleFolderAsync();
        
        if (folder != null)
        {
            ViewModel.SetMountPath(folder.Path);
        }
    }
    
    /// <summary>
    /// Handles browse backup directory button click.
    /// </summary>
    private async void BrowseBackupDirectory_Click(object sender, RoutedEventArgs e)
    {
        var picker = new FolderPicker();
        
        var hwnd = WinRT.Interop.WindowNative.GetWindowHandle(App.MainWindow);
        WinRT.Interop.InitializeWithWindow.Initialize(picker, hwnd);
        
        picker.SuggestedStartLocation = PickerLocationId.DocumentsLibrary;
        picker.FileTypeFilter.Add("*");
        
        var folder = await picker.PickSingleFolderAsync();
        
        if (folder != null)
        {
            ViewModel.SetBackupDirectory(folder.Path);
        }
    }
    
    /// <summary>
    /// Handles export settings button click.
    /// </summary>
    private async void ExportSettings_Click(object sender, RoutedEventArgs e)
    {
        var picker = new FileSavePicker();
        
        var hwnd = WinRT.Interop.WindowNative.GetWindowHandle(App.MainWindow);
        WinRT.Interop.InitializeWithWindow.Initialize(picker, hwnd);
        
        picker.SuggestedStartLocation = PickerLocationId.DocumentsLibrary;
        picker.SuggestedFileName = "deployforge-settings.json";
        picker.FileTypeChoices.Add("JSON Settings", new List<string> { ".json" });
        
        var file = await picker.PickSaveFileAsync();
        
        if (file != null)
        {
            await ViewModel.ExportToPathAsync(file.Path);
        }
    }
    
    /// <summary>
    /// Handles import settings button click.
    /// </summary>
    private async void ImportSettings_Click(object sender, RoutedEventArgs e)
    {
        var picker = new FileOpenPicker();
        
        var hwnd = WinRT.Interop.WindowNative.GetWindowHandle(App.MainWindow);
        WinRT.Interop.InitializeWithWindow.Initialize(picker, hwnd);
        
        picker.SuggestedStartLocation = PickerLocationId.DocumentsLibrary;
        picker.FileTypeFilter.Add(".json");
        
        var file = await picker.PickSingleFileAsync();
        
        if (file != null)
        {
            await ViewModel.ImportFromPathAsync(file.Path);
        }
    }
    
    /// <summary>
    /// Handles reset settings button click.
    /// </summary>
    private async void ResetSettings_Click(object sender, RoutedEventArgs e)
    {
        var dialog = new ContentDialog
        {
            Title = "Reset Settings",
            Content = "Are you sure you want to reset all settings to their defaults?",
            PrimaryButtonText = "Reset",
            CloseButtonText = "Cancel",
            DefaultButton = ContentDialogButton.Close,
            XamlRoot = this.XamlRoot
        };
        
        var result = await dialog.ShowAsync();
        
        if (result == ContentDialogResult.Primary)
        {
            await ViewModel.ResetSettingsCommand.ExecuteAsync();
        }
    }
}
