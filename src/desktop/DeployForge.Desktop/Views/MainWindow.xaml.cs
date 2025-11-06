using System.Windows;
using DeployForge.Desktop.ViewModels;

namespace DeployForge.Desktop.Views;

public partial class MainWindow : Window
{
    public MainWindow(MainViewModel viewModel)
    {
        InitializeComponent();
        DataContext = viewModel;

        Loaded += async (s, e) => await viewModel.InitializeAsync();
        Closing += async (s, e) =>
        {
            e.Cancel = true;
            await viewModel.CleanupAsync();
            e.Cancel = false;
        };
    }
}
