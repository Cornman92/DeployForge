namespace DeployForge.Desktop.Services;

/// <summary>
/// Service for displaying dialogs
/// </summary>
public interface IDialogService
{
    /// <summary>
    /// Show information message
    /// </summary>
    void ShowInfo(string title, string message);

    /// <summary>
    /// Show warning message
    /// </summary>
    void ShowWarning(string title, string message);

    /// <summary>
    /// Show error message
    /// </summary>
    void ShowError(string title, string message);

    /// <summary>
    /// Show confirmation dialog
    /// </summary>
    bool ShowConfirmation(string title, string message);

    /// <summary>
    /// Show yes/no/cancel dialog
    /// </summary>
    DialogResult ShowYesNoCancel(string title, string message);

    /// <summary>
    /// Show open file dialog
    /// </summary>
    string? ShowOpenFileDialog(string filter, string title = "Open File");

    /// <summary>
    /// Show save file dialog
    /// </summary>
    string? ShowSaveFileDialog(string filter, string title = "Save File");

    /// <summary>
    /// Show folder browser dialog
    /// </summary>
    string? ShowFolderBrowserDialog(string title = "Select Folder");

    /// <summary>
    /// Show progress dialog
    /// </summary>
    IProgressDialog ShowProgressDialog(string title, string message);
}

/// <summary>
/// Dialog result
/// </summary>
public enum DialogResult
{
    Yes,
    No,
    Cancel
}

/// <summary>
/// Progress dialog interface
/// </summary>
public interface IProgressDialog : IDisposable
{
    void UpdateProgress(int percentage, string message);
    void Complete();
    void SetIndeterminate(bool indeterminate);
}
