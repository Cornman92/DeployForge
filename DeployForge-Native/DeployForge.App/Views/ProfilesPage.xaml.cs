using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;
using DeployForge.App.ViewModels;

namespace DeployForge.App.Views;

public sealed partial class ProfilesPage : Page
{
    public ProfilesViewModel ViewModel { get; }
    
    public ProfilesPage()
    {
        this.InitializeComponent();
        ViewModel = App.GetService<ProfilesViewModel>();
    }
    
    protected override async void OnNavigatedTo(NavigationEventArgs e)
    {
        base.OnNavigatedTo(e);
        await ViewModel.InitializeAsync();
    }
}
