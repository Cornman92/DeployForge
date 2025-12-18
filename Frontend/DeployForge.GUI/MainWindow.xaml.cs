using Microsoft.UI.Xaml;
using DeployForge.GUI.ViewModels;

namespace DeployForge.GUI
{
    public sealed partial class MainWindow : Window
    {
        public MainViewModel ViewModel { get; }

        public MainWindow()
        {
            this.InitializeComponent();
            ViewModel = new MainViewModel();
        }
    }
}
