using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;
using DeployForge.App.ViewModels;

namespace DeployForge.App.Views;

public sealed partial class BuildPage : Page
{
    public BuildViewModel ViewModel { get; }
    
    public BuildPage()
    {
        this.InitializeComponent();
        ViewModel = App.GetService<BuildViewModel>();
    }
    
    protected override void OnNavigatedTo(NavigationEventArgs e)
    {
        base.OnNavigatedTo(e);
        ViewModel.Initialize(e.Parameter);
    }
}
