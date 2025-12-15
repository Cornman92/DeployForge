using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using DeployForge.App.ViewModels;

namespace DeployForge.App.Views;

/// <summary>
/// Build configuration page.
/// </summary>
public sealed partial class BuildPage : Page
{
    /// <summary>
    /// Page ViewModel.
    /// </summary>
    public BuildViewModel ViewModel { get; }
    
    public BuildPage()
    {
        this.InitializeComponent();
        
        var mainViewModel = App.GetService<MainViewModel>();
        ViewModel = mainViewModel.BuildPage;
        
        this.DataContext = ViewModel;
    }
    
    /// <summary>
    /// Helper to convert boolean to visibility.
    /// </summary>
    private Visibility GetVisibility(bool value, bool invert)
    {
        var visible = invert ? !value : value;
        return visible ? Visibility.Visible : Visibility.Collapsed;
    }
    
    /// <summary>
    /// Helper to check if build can start.
    /// </summary>
    private bool CanBuild(bool isMounted, bool isBuilding)
    {
        return isMounted && !isBuilding;
    }
    
    /// <summary>
    /// Handles save template button click.
    /// </summary>
    private async void SaveTemplate_Click(object sender, RoutedEventArgs e)
    {
        var dialog = new ContentDialog
        {
            Title = "Save as Template",
            PrimaryButtonText = "Save",
            CloseButtonText = "Cancel",
            DefaultButton = ContentDialogButton.Primary,
            XamlRoot = this.XamlRoot
        };
        
        var textBox = new TextBox
        {
            Header = "Template Name",
            PlaceholderText = "Enter template name"
        };
        
        dialog.Content = textBox;
        
        var result = await dialog.ShowAsync();
        
        if (result == ContentDialogResult.Primary && !string.IsNullOrWhiteSpace(textBox.Text))
        {
            await ViewModel.SaveAsTemplateCommand.ExecuteAsync(textBox.Text);
        }
    }
}
