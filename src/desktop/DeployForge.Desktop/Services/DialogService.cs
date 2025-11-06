using System.Windows;
using Microsoft.Extensions.Logging;
using Microsoft.Win32;

namespace DeployForge.Desktop.Services;

/// <summary>
/// Dialog service implementation
/// </summary>
public class DialogService : IDialogService
{
    private readonly ILogger<DialogService> _logger;

    public DialogService(ILogger<DialogService> logger)
    {
        _logger = logger;
    }

    public void ShowInfo(string title, string message)
    {
        _logger.LogInformation("Info dialog: {Title} - {Message}", title, message);
        MessageBox.Show(message, title, MessageBoxButton.OK, MessageBoxImage.Information);
    }

    public void ShowWarning(string title, string message)
    {
        _logger.LogWarning("Warning dialog: {Title} - {Message}", title, message);
        MessageBox.Show(message, title, MessageBoxButton.OK, MessageBoxImage.Warning);
    }

    public void ShowError(string title, string message)
    {
        _logger.LogError("Error dialog: {Title} - {Message}", title, message);
        MessageBox.Show(message, title, MessageBoxButton.OK, MessageBoxImage.Error);
    }

    public bool ShowConfirmation(string title, string message)
    {
        _logger.LogInformation("Confirmation dialog: {Title}", title);
        var result = MessageBox.Show(message, title, MessageBoxButton.YesNo, MessageBoxImage.Question);
        return result == MessageBoxResult.Yes;
    }

    public DialogResult ShowYesNoCancel(string title, string message)
    {
        _logger.LogInformation("YesNoCancel dialog: {Title}", title);
        var result = MessageBox.Show(message, title, MessageBoxButton.YesNoCancel, MessageBoxImage.Question);

        return result switch
        {
            MessageBoxResult.Yes => DialogResult.Yes,
            MessageBoxResult.No => DialogResult.No,
            _ => DialogResult.Cancel
        };
    }

    public string? ShowOpenFileDialog(string filter, string title = "Open File")
    {
        _logger.LogInformation("Open file dialog: {Title}", title);

        var dialog = new OpenFileDialog
        {
            Title = title,
            Filter = filter,
            CheckFileExists = true,
            CheckPathExists = true
        };

        return dialog.ShowDialog() == true ? dialog.FileName : null;
    }

    public string? ShowSaveFileDialog(string filter, string title = "Save File")
    {
        _logger.LogInformation("Save file dialog: {Title}", title);

        var dialog = new SaveFileDialog
        {
            Title = title,
            Filter = filter,
            CheckPathExists = true
        };

        return dialog.ShowDialog() == true ? dialog.FileName : null;
    }

    public string? ShowFolderBrowserDialog(string title = "Select Folder")
    {
        _logger.LogInformation("Folder browser dialog: {Title}", title);

        var dialog = new OpenFolderDialog
        {
            Title = title,
            Multiselect = false
        };

        return dialog.ShowDialog() == true ? dialog.FolderName : null;
    }

    public IProgressDialog ShowProgressDialog(string title, string message)
    {
        _logger.LogInformation("Progress dialog: {Title}", title);
        return new ProgressDialogImpl(title, message);
    }

    private class ProgressDialogImpl : IProgressDialog
    {
        private readonly Window _window;
        private bool _disposed;

        public ProgressDialogImpl(string title, string message)
        {
            // For now, return a simple implementation
            // In a full implementation, this would show a custom WPF window
            _window = new Window
            {
                Title = title,
                Width = 400,
                Height = 150,
                WindowStartupLocation = WindowStartupLocation.CenterScreen,
                ResizeMode = ResizeMode.NoResize
            };
        }

        public void UpdateProgress(int percentage, string message)
        {
            // Update progress (implementation would update UI controls)
        }

        public void Complete()
        {
            Dispose();
        }

        public void SetIndeterminate(bool indeterminate)
        {
            // Set indeterminate state
        }

        public void Dispose()
        {
            if (!_disposed)
            {
                _window?.Close();
                _disposed = true;
            }
        }
    }
}
