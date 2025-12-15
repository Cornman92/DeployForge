using Microsoft.UI.Xaml;
using DeployForge.App.Models;

namespace DeployForge.App.Services;

public interface IThemeService
{
    AppTheme CurrentTheme { get; }
    ElementTheme ElementTheme { get; }
    event EventHandler<AppTheme>? ThemeChanged;
    
    void SetTheme(AppTheme theme);
    void Initialize(Window window);
}

public class ThemeService : IThemeService
{
    private Window? _window;
    private AppTheme _currentTheme = AppTheme.System;
    
    public AppTheme CurrentTheme => _currentTheme;
    
    public ElementTheme ElementTheme => _currentTheme switch
    {
        AppTheme.Light => ElementTheme.Light,
        AppTheme.Dark => ElementTheme.Dark,
        _ => ElementTheme.Default
    };
    
    public event EventHandler<AppTheme>? ThemeChanged;
    
    public void Initialize(Window window)
    {
        _window = window;
        ApplyTheme();
    }
    
    public void SetTheme(AppTheme theme)
    {
        if (_currentTheme == theme) return;
        
        _currentTheme = theme;
        ApplyTheme();
        ThemeChanged?.Invoke(this, theme);
    }
    
    private void ApplyTheme()
    {
        if (_window?.Content is FrameworkElement rootElement)
        {
            rootElement.RequestedTheme = ElementTheme;
        }
    }
}
