using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;
using DeployForge.App.ViewModels;

namespace DeployForge.App.Views;

public sealed partial class SettingsPage : Page
{
    public SettingsViewModel ViewModel { get; }
    
    public SettingsPage()
    {
        this.InitializeComponent();
        ViewModel = App.GetService<SettingsViewModel>();
    }
    
    protected override void OnNavigatedTo(NavigationEventArgs e)
    {
        base.OnNavigatedTo(e);
        ViewModel.Initialize();
    }
}
