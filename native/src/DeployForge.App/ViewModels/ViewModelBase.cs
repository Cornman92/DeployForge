using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using DeployForge.Core.Interfaces;

namespace DeployForge.App.ViewModels;

/// <summary>
/// Base class for all ViewModels.
/// </summary>
public abstract partial class ViewModelBase : ObservableObject
{
    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(IsNotBusy))]
    private bool _isBusy;
    
    [ObservableProperty]
    private string _busyMessage = string.Empty;
    
    [ObservableProperty]
    private string _errorMessage = string.Empty;
    
    [ObservableProperty]
    private bool _hasError;
    
    /// <summary>
    /// Whether the ViewModel is not busy.
    /// </summary>
    public bool IsNotBusy => !IsBusy;
    
    /// <summary>
    /// Progress reporter for operations.
    /// </summary>
    protected IProgress<ProgressInfo> Progress { get; }
    
    protected ViewModelBase()
    {
        Progress = new Progress<ProgressInfo>(OnProgressChanged);
    }
    
    /// <summary>
    /// Called when progress is reported.
    /// </summary>
    protected virtual void OnProgressChanged(ProgressInfo progress)
    {
        BusyMessage = progress.Message;
    }
    
    /// <summary>
    /// Sets the busy state with a message.
    /// </summary>
    protected void SetBusy(string message = "Working...")
    {
        IsBusy = true;
        BusyMessage = message;
        ClearError();
    }
    
    /// <summary>
    /// Clears the busy state.
    /// </summary>
    protected void ClearBusy()
    {
        IsBusy = false;
        BusyMessage = string.Empty;
    }
    
    /// <summary>
    /// Sets an error message.
    /// </summary>
    protected void SetError(string message)
    {
        ErrorMessage = message;
        HasError = true;
    }
    
    /// <summary>
    /// Clears the error state.
    /// </summary>
    protected void ClearError()
    {
        ErrorMessage = string.Empty;
        HasError = false;
    }
    
    /// <summary>
    /// Executes an async operation with busy state management.
    /// </summary>
    protected async Task ExecuteAsync(
        Func<Task> operation, 
        string busyMessage = "Working...",
        string? successMessage = null)
    {
        try
        {
            SetBusy(busyMessage);
            await operation();
            
            if (!string.IsNullOrEmpty(successMessage))
            {
                BusyMessage = successMessage;
            }
        }
        catch (Exception ex)
        {
            SetError(ex.Message);
        }
        finally
        {
            ClearBusy();
        }
    }
    
    /// <summary>
    /// Executes an async operation with result and busy state management.
    /// </summary>
    protected async Task<T?> ExecuteAsync<T>(
        Func<Task<T>> operation,
        string busyMessage = "Working...")
    {
        try
        {
            SetBusy(busyMessage);
            return await operation();
        }
        catch (Exception ex)
        {
            SetError(ex.Message);
            return default;
        }
        finally
        {
            ClearBusy();
        }
    }
}

/// <summary>
/// Base class for page ViewModels.
/// </summary>
public abstract class PageViewModelBase : ViewModelBase
{
    /// <summary>
    /// Page title for navigation.
    /// </summary>
    public abstract string Title { get; }
    
    /// <summary>
    /// Page icon (Segoe MDL2 Assets glyph).
    /// </summary>
    public virtual string Icon => "\uE80F";
    
    /// <summary>
    /// Called when the page is navigated to.
    /// </summary>
    public virtual Task OnNavigatedToAsync() => Task.CompletedTask;
    
    /// <summary>
    /// Called when the page is navigated from.
    /// </summary>
    public virtual Task OnNavigatedFromAsync() => Task.CompletedTask;
}
