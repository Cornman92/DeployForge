using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;
using DeployForge.App.ViewModels;

namespace DeployForge.App.Views;

public sealed partial class AnalyzePage : Page
{
    public AnalyzeViewModel ViewModel { get; }
    
    public AnalyzePage()
    {
        this.InitializeComponent();
        ViewModel = App.GetService<AnalyzeViewModel>();
    }
    
    protected override void OnNavigatedTo(NavigationEventArgs e)
    {
        base.OnNavigatedTo(e);
        ViewModel.Initialize(e.Parameter);
    }
}
