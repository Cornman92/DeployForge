using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;
using DeployForge.App.ViewModels;

namespace DeployForge.App.Views;

public sealed partial class WelcomePage : Page
{
    public WelcomeViewModel ViewModel { get; }
    
    public WelcomePage()
    {
        this.InitializeComponent();
        ViewModel = App.GetService<WelcomeViewModel>();
    }
    
    protected override void OnNavigatedTo(NavigationEventArgs e)
    {
        base.OnNavigatedTo(e);
        
        if (e.Parameter is string imagePath)
        {
            ViewModel.LoadImageCommand.Execute(imagePath);
        }
    }
}
