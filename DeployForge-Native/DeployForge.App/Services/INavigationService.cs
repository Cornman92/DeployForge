using Microsoft.UI.Xaml.Controls;

namespace DeployForge.App.Services;

public interface INavigationService
{
    bool CanGoBack { get; }
    Frame? Frame { get; set; }
    string CurrentPageKey { get; }
    
    bool NavigateTo(string pageKey, object? parameter = null, bool clearNavigation = false);
    bool GoBack();
    void Initialize(Frame frame);
}

public class NavigationService : INavigationService
{
    private Frame? _frame;
    private string _currentPageKey = string.Empty;
    
    private readonly Dictionary<string, Type> _pages = new()
    {
        { "Welcome", typeof(Views.WelcomePage) },
        { "Build", typeof(Views.BuildPage) },
        { "Profiles", typeof(Views.ProfilesPage) },
        { "Analyze", typeof(Views.AnalyzePage) },
        { "Settings", typeof(Views.SettingsPage) }
    };
    
    public bool CanGoBack => _frame?.CanGoBack ?? false;
    public string CurrentPageKey => _currentPageKey;
    
    public Frame? Frame
    {
        get => _frame;
        set => _frame = value;
    }
    
    public void Initialize(Frame frame)
    {
        _frame = frame;
    }
    
    public bool NavigateTo(string pageKey, object? parameter = null, bool clearNavigation = false)
    {
        if (_frame == null || !_pages.TryGetValue(pageKey, out var pageType))
            return false;
        
        if (clearNavigation)
            _frame.BackStack.Clear();
        
        var result = _frame.Navigate(pageType, parameter);
        if (result)
            _currentPageKey = pageKey;
        
        return result;
    }
    
    public bool GoBack()
    {
        if (_frame == null || !_frame.CanGoBack)
            return false;
        
        _frame.GoBack();
        return true;
    }
}
