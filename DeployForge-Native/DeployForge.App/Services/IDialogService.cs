using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Windows.Storage.Pickers;

namespace DeployForge.App.Services;

public interface IDialogService
{
    void Initialize(XamlRoot xamlRoot, nint windowHandle);
    Task<ContentDialogResult> ShowDialogAsync(string title, string content, string primaryButton = "OK", string? secondaryButton = null, string? closeButton = null);
    Task<string?> ShowInputDialogAsync(string title, string placeholder = "");
    Task<string?> PickFileAsync(string[] extensions, string title = "Select File");
    Task<string?> PickFolderAsync(string title = "Select Folder");
    Task<string?> SaveFileAsync(string suggestedName, string[] extensions, string title = "Save File");
    void ShowNotification(string title, string message, NotificationType type = NotificationType.Info);
}

public enum NotificationType { Info, Success, Warning, Error }

public class DialogService : IDialogService
{
    private XamlRoot? _xamlRoot;
    private nint _windowHandle;
    
    public void Initialize(XamlRoot xamlRoot, nint windowHandle)
    {
        _xamlRoot = xamlRoot;
        _windowHandle = windowHandle;
    }
    
    public async Task<ContentDialogResult> ShowDialogAsync(string title, string content, string primaryButton = "OK", string? secondaryButton = null, string? closeButton = null)
    {
        if (_xamlRoot == null) return ContentDialogResult.None;
        
        var dialog = new ContentDialog
        {
            Title = title,
            Content = content,
            PrimaryButtonText = primaryButton,
            SecondaryButtonText = secondaryButton ?? string.Empty,
            CloseButtonText = closeButton ?? string.Empty,
            XamlRoot = _xamlRoot,
            DefaultButton = ContentDialogButton.Primary
        };
        
        return await dialog.ShowAsync();
    }
    
    public async Task<string?> ShowInputDialogAsync(string title, string placeholder = "")
    {
        if (_xamlRoot == null) return null;
        
        var inputBox = new TextBox { PlaceholderText = placeholder, Width = 300 };
        
        var dialog = new ContentDialog
        {
            Title = title,
            Content = inputBox,
            PrimaryButtonText = "OK",
            CloseButtonText = "Cancel",
            XamlRoot = _xamlRoot,
            DefaultButton = ContentDialogButton.Primary
        };
        
        var result = await dialog.ShowAsync();
        return result == ContentDialogResult.Primary ? inputBox.Text : null;
    }
    
    public async Task<string?> PickFileAsync(string[] extensions, string title = "Select File")
    {
        var picker = new FileOpenPicker
        {
            ViewMode = PickerViewMode.List,
            SuggestedStartLocation = PickerLocationId.DocumentsLibrary
        };
        
        WinRT.Interop.InitializeWithWindow.Initialize(picker, _windowHandle);
        
        foreach (var ext in extensions)
            picker.FileTypeFilter.Add(ext.StartsWith(".") ? ext : $".{ext}");
        
        var file = await picker.PickSingleFileAsync();
        return file?.Path;
    }
    
    public async Task<string?> PickFolderAsync(string title = "Select Folder")
    {
        var picker = new FolderPicker
        {
            SuggestedStartLocation = PickerLocationId.DocumentsLibrary
        };
        picker.FileTypeFilter.Add("*");
        
        WinRT.Interop.InitializeWithWindow.Initialize(picker, _windowHandle);
        
        var folder = await picker.PickSingleFolderAsync();
        return folder?.Path;
    }
    
    public async Task<string?> SaveFileAsync(string suggestedName, string[] extensions, string title = "Save File")
    {
        var picker = new FileSavePicker
        {
            SuggestedStartLocation = PickerLocationId.DocumentsLibrary,
            SuggestedFileName = suggestedName
        };
        
        WinRT.Interop.InitializeWithWindow.Initialize(picker, _windowHandle);
        
        foreach (var ext in extensions)
        {
            var e = ext.StartsWith(".") ? ext : $".{ext}";
            picker.FileTypeChoices.Add($"{e.ToUpper()} File", new List<string> { e });
        }
        
        var file = await picker.PickSaveFileAsync();
        return file?.Path;
    }
    
    public void ShowNotification(string title, string message, NotificationType type = NotificationType.Info)
    {
        // TODO: Implement InfoBar or Toast notification
    }
}
