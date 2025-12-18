using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using DeployForge.App.ViewModels;

namespace DeployForge.App.Views;

/// <summary>
/// Main application window with navigation.
/// </summary>
public sealed partial class MainWindow : Window
{
    /// <summary>
    /// Main ViewModel.
    /// </summary>
    public MainViewModel ViewModel { get; }
    
    public MainWindow()
    {
        this.InitializeComponent();
        
        // Get ViewModel from services
        ViewModel = App.GetService<MainViewModel>();
        
        // Set initial navigation
        ContentFrame.Navigate(typeof(WelcomePage));
        
        // Configure window
        Title = "DeployForge - Windows Deployment Suite";
        
        // Set minimum size
        var hwnd = WinRT.Interop.WindowNative.GetWindowHandle(this);
        var windowId = Microsoft.UI.Win32Interop.GetWindowIdFromWindow(hwnd);
        var appWindow = Microsoft.UI.Windowing.AppWindow.GetFromWindowId(windowId);
        
        if (appWindow != null)
        {
            appWindow.TitleBar.ExtendsContentIntoTitleBar = false;
            appWindow.Resize(new Windows.Graphics.SizeInt32(1400, 900));
        }
    }
    
    /// <summary>
    /// Handles navigation view selection changes.
    /// </summary>
    private void NavView_SelectionChanged(NavigationView sender, NavigationViewSelectionChangedEventArgs args)
    {
        if (args.SelectedItemContainer is NavigationViewItem item)
        {
            var tag = item.Tag?.ToString();
            
            Type? pageType = tag switch
            {
                "Welcome" => typeof(WelcomePage),
                "Build" => typeof(BuildPage),
                "Profiles" => typeof(ProfilesPage),
                "Settings" => typeof(SettingsPage),
                _ => null
            };
            
            if (pageType != null && ContentFrame.CurrentSourcePageType != pageType)
            {
                ContentFrame.Navigate(pageType);
            }
        }
    }
    
    /// <summary>
    /// Gets the mount status indicator color.
    /// </summary>
    private SolidColorBrush GetMountStatusColor(bool isMounted)
    {
        return isMounted 
            ? new SolidColorBrush(Windows.UI.Color.FromArgb(255, 46, 204, 113))  // Green
            : new SolidColorBrush(Windows.UI.Color.FromArgb(255, 149, 165, 166)); // Gray
    }
    
    /// <summary>
    /// Gets the mount status text.
    /// </summary>
    private string GetMountStatusText(bool isMounted)
    {
        return isMounted ? "Image Mounted" : "No Image Mounted";
    }
}
