using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Input;
using Windows.ApplicationModel.DataTransfer;
using Windows.Storage;
using Windows.Storage.Pickers;
using DeployForge.App.ViewModels;
using DeployForge.Core.Enums;

namespace DeployForge.App.Views;

/// <summary>
/// Welcome page with image selection and quick actions.
/// </summary>
public sealed partial class WelcomePage : Page
{
    /// <summary>
    /// Page ViewModel.
    /// </summary>
    public WelcomeViewModel ViewModel { get; }
    
    /// <summary>
    /// Main ViewModel for navigation.
    /// </summary>
    private MainViewModel MainViewModel { get; }
    
    public WelcomePage()
    {
        this.InitializeComponent();
        
        MainViewModel = App.GetService<MainViewModel>();
        ViewModel = MainViewModel.WelcomePage;
        
        this.DataContext = ViewModel;
    }
    
    /// <summary>
    /// Handles browse button click.
    /// </summary>
    private async void BrowseButton_Click(object sender, RoutedEventArgs e)
    {
        var picker = new FileOpenPicker();
        
        // Initialize with window handle
        var hwnd = WinRT.Interop.WindowNative.GetWindowHandle(App.MainWindow);
        WinRT.Interop.InitializeWithWindow.Initialize(picker, hwnd);
        
        picker.ViewMode = PickerViewMode.List;
        picker.SuggestedStartLocation = PickerLocationId.DocumentsLibrary;
        picker.FileTypeFilter.Add(".wim");
        picker.FileTypeFilter.Add(".esd");
        picker.FileTypeFilter.Add(".vhd");
        picker.FileTypeFilter.Add(".vhdx");
        picker.FileTypeFilter.Add(".iso");
        
        var file = await picker.PickSingleFileAsync();
        
        if (file != null)
        {
            await ViewModel.OpenImageCommand.ExecuteAsync(file.Path);
        }
    }
    
    /// <summary>
    /// Handles drag over on drop zone.
    /// </summary>
    private void DropZone_DragOver(object sender, DragEventArgs e)
    {
        e.AcceptedOperation = DataPackageOperation.Copy;
        
        if (e.DragUIOverride != null)
        {
            e.DragUIOverride.Caption = "Open Image";
            e.DragUIOverride.IsCaptionVisible = true;
            e.DragUIOverride.IsGlyphVisible = true;
        }
        
        DropZone.Style = (Style)Resources["DropZoneActiveStyle"] 
            ?? (Style)Application.Current.Resources["DropZoneActiveStyle"];
        
        ViewModel.SetDragOverCommand.Execute(true);
    }
    
    /// <summary>
    /// Handles drag leave on drop zone.
    /// </summary>
    private void DropZone_DragLeave(object sender, DragEventArgs e)
    {
        DropZone.Style = (Style)Resources["DropZoneStyle"]
            ?? (Style)Application.Current.Resources["DropZoneStyle"];
        
        ViewModel.SetDragOverCommand.Execute(false);
    }
    
    /// <summary>
    /// Handles drop on drop zone.
    /// </summary>
    private async void DropZone_Drop(object sender, DragEventArgs e)
    {
        DropZone.Style = (Style)Resources["DropZoneStyle"]
            ?? (Style)Application.Current.Resources["DropZoneStyle"];
        
        if (e.DataView.Contains(StandardDataFormats.StorageItems))
        {
            var items = await e.DataView.GetStorageItemsAsync();
            
            if (items.Count > 0 && items[0] is StorageFile file)
            {
                var extension = file.FileType.ToLowerInvariant();
                
                if (extension is ".wim" or ".esd" or ".vhd" or ".vhdx" or ".iso")
                {
                    await ViewModel.HandleDropCommand.ExecuteAsync(file.Path);
                }
            }
        }
    }
    
    /// <summary>
    /// Handles gaming profile button click.
    /// </summary>
    private async void GamingProfile_Click(object sender, RoutedEventArgs e)
    {
        MainViewModel.ProfilesPage.SelectProfile(BuildProfileType.Gaming);
        await MainViewModel.NavigateToCommand.ExecuteAsync(MainViewModel.BuildPage);
    }
    
    /// <summary>
    /// Handles developer profile button click.
    /// </summary>
    private async void DeveloperProfile_Click(object sender, RoutedEventArgs e)
    {
        MainViewModel.ProfilesPage.SelectProfile(BuildProfileType.Developer);
        await MainViewModel.NavigateToCommand.ExecuteAsync(MainViewModel.BuildPage);
    }
    
    /// <summary>
    /// Handles enterprise profile button click.
    /// </summary>
    private async void EnterpriseProfile_Click(object sender, RoutedEventArgs e)
    {
        MainViewModel.ProfilesPage.SelectProfile(BuildProfileType.Enterprise);
        await MainViewModel.NavigateToCommand.ExecuteAsync(MainViewModel.BuildPage);
    }
    
    /// <summary>
    /// Handles custom build button click.
    /// </summary>
    private async void CustomBuild_Click(object sender, RoutedEventArgs e)
    {
        await MainViewModel.NavigateToCommand.ExecuteAsync(MainViewModel.BuildPage);
    }
    
    /// <summary>
    /// Handles recent image click.
    /// </summary>
    private async void RecentImage_Click(object sender, PointerRoutedEventArgs e)
    {
        if (sender is FrameworkElement element && element.DataContext is RecentImageItem item)
        {
            await ViewModel.OpenRecentCommand.ExecuteAsync(item);
        }
    }
    
    /// <summary>
    /// Helper to check if there are recent images.
    /// </summary>
    private Visibility HasRecentImages(int count)
    {
        return count > 0 ? Visibility.Visible : Visibility.Collapsed;
    }
}
