using System.Management.Automation;
using System.Management.Automation.Runspaces;
using DeployForge.Core.Exceptions;
using DeployForge.Core.Interfaces;

namespace DeployForge.Services;

/// <summary>
/// Executes PowerShell scripts and commands with the DeployForge module.
/// </summary>
public class PowerShellExecutor : IPowerShellExecutor, IDisposable
{
    private readonly Runspace _runspace;
    private readonly object _lock = new();
    private bool _isModuleLoaded;
    private bool _disposed;
    
    /// <summary>
    /// Path to the PowerShell module.
    /// </summary>
    public string ModulePath { get; }
    
    /// <inheritdoc />
    public bool IsModuleLoaded => _isModuleLoaded;
    
    /// <summary>
    /// Creates a new PowerShell executor.
    /// </summary>
    /// <param name="modulePath">Optional custom path to the PowerShell module.</param>
    public PowerShellExecutor(string? modulePath = null)
    {
        ModulePath = modulePath ?? GetDefaultModulePath();
        
        // Create runspace with initial session state
        var iss = InitialSessionState.CreateDefault();
        iss.ExecutionPolicy = Microsoft.PowerShell.ExecutionPolicy.RemoteSigned;
        
        _runspace = RunspaceFactory.CreateRunspace(iss);
        _runspace.Open();
    }
    
    /// <summary>
    /// Gets the default module path relative to the application.
    /// </summary>
    private static string GetDefaultModulePath()
    {
        var appDir = AppContext.BaseDirectory;
        var modulePath = Path.Combine(appDir, "PowerShell", "DeployForge.psd1");
        
        // Fallback to development path
        if (!File.Exists(modulePath))
        {
            modulePath = Path.Combine(appDir, "..", "..", "..", "..", 
                "DeployForge.PowerShell", "DeployForge.psd1");
        }
        
        return Path.GetFullPath(modulePath);
    }
    
    /// <inheritdoc />
    public async Task ImportModuleAsync()
    {
        if (_isModuleLoaded) return;
        
        await Task.Run(() =>
        {
            lock (_lock)
            {
                if (_isModuleLoaded) return;
                
                if (!File.Exists(ModulePath))
                {
                    throw new PowerShellException(
                        $"DeployForge PowerShell module not found at: {ModulePath}");
                }
                
                using var ps = PowerShell.Create();
                ps.Runspace = _runspace;
                
                // Import the module
                ps.AddCommand("Import-Module")
                    .AddParameter("Name", ModulePath)
                    .AddParameter("Force")
                    .AddParameter("Global");
                
                ps.Invoke();
                
                if (ps.HadErrors)
                {
                    var errors = string.Join(Environment.NewLine, 
                        ps.Streams.Error.Select(e => e.ToString()));
                    throw new PowerShellException($"Failed to import module: {errors}");
                }
                
                _isModuleLoaded = true;
            }
        });
    }
    
    /// <inheritdoc />
    public async Task<PowerShellResult> ExecuteAsync(
        string script, 
        Dictionary<string, object>? parameters = null,
        CancellationToken cancellationToken = default)
    {
        if (!_isModuleLoaded)
        {
            await ImportModuleAsync();
        }
        
        return await Task.Run(() =>
        {
            lock (_lock)
            {
                cancellationToken.ThrowIfCancellationRequested();
                
                using var ps = PowerShell.Create();
                ps.Runspace = _runspace;
                
                ps.AddScript(script);
                
                if (parameters != null)
                {
                    foreach (var param in parameters)
                    {
                        ps.AddParameter(param.Key, param.Value);
                    }
                }
                
                return ExecuteAndCollectResults(ps, cancellationToken);
            }
        }, cancellationToken);
    }
    
    /// <inheritdoc />
    public async Task<PowerShellResult> ExecuteCommandAsync(
        string command, 
        Dictionary<string, object>? parameters = null,
        CancellationToken cancellationToken = default)
    {
        if (!_isModuleLoaded)
        {
            await ImportModuleAsync();
        }
        
        return await Task.Run(() =>
        {
            lock (_lock)
            {
                cancellationToken.ThrowIfCancellationRequested();
                
                using var ps = PowerShell.Create();
                ps.Runspace = _runspace;
                
                ps.AddCommand(command);
                
                if (parameters != null)
                {
                    foreach (var param in parameters)
                    {
                        ps.AddParameter(param.Key, param.Value);
                    }
                }
                
                return ExecuteAndCollectResults(ps, cancellationToken);
            }
        }, cancellationToken);
    }
    
    /// <summary>
    /// Executes a PowerShell command and collects results.
    /// </summary>
    private static PowerShellResult ExecuteAndCollectResults(
        PowerShell ps, 
        CancellationToken cancellationToken)
    {
        var result = new PowerShellResult();
        
        try
        {
            // Set up async invocation with cancellation
            var asyncResult = ps.BeginInvoke();
            
            // Wait for completion or cancellation
            while (!asyncResult.IsCompleted)
            {
                if (cancellationToken.IsCancellationRequested)
                {
                    ps.Stop();
                    cancellationToken.ThrowIfCancellationRequested();
                }
                Thread.Sleep(100);
            }
            
            var output = ps.EndInvoke(asyncResult);
            
            // Collect output objects
            foreach (var item in output)
            {
                if (item?.BaseObject != null)
                {
                    result.Output.Add(item.BaseObject);
                }
            }
            
            // Collect errors
            foreach (var error in ps.Streams.Error)
            {
                result.Errors.Add(error.ToString());
            }
            
            // Collect warnings
            foreach (var warning in ps.Streams.Warning)
            {
                result.Warnings.Add(warning.ToString());
            }
            
            // Collect verbose
            foreach (var verbose in ps.Streams.Verbose)
            {
                result.Verbose.Add(verbose.ToString());
            }
            
            result.Success = !ps.HadErrors;
        }
        catch (Exception ex) when (ex is not OperationCanceledException)
        {
            result.Success = false;
            result.Errors.Add(ex.Message);
        }
        
        return result;
    }
    
    /// <summary>
    /// Executes a command with typed result conversion.
    /// </summary>
    public async Task<T?> ExecuteCommandAsync<T>(
        string command,
        Dictionary<string, object>? parameters = null,
        CancellationToken cancellationToken = default) where T : class
    {
        var result = await ExecuteCommandAsync(command, parameters, cancellationToken);
        
        if (!result.Success)
        {
            throw new PowerShellException(string.Join(Environment.NewLine, result.Errors));
        }
        
        return result.GetOutput<T>();
    }
    
    /// <summary>
    /// Executes a command and converts result to dictionary.
    /// </summary>
    public async Task<Dictionary<string, object>?> ExecuteCommandAsDictionaryAsync(
        string command,
        Dictionary<string, object>? parameters = null,
        CancellationToken cancellationToken = default)
    {
        var result = await ExecuteCommandAsync(command, parameters, cancellationToken);
        
        if (!result.Success)
        {
            throw new PowerShellException(string.Join(Environment.NewLine, result.Errors));
        }
        
        if (result.Output.FirstOrDefault() is PSObject psObject)
        {
            var dict = new Dictionary<string, object>();
            foreach (var prop in psObject.Properties)
            {
                dict[prop.Name] = prop.Value;
            }
            return dict;
        }
        
        return null;
    }
    
    /// <inheritdoc />
    public void Dispose()
    {
        if (_disposed) return;
        
        _runspace?.Close();
        _runspace?.Dispose();
        _disposed = true;
        
        GC.SuppressFinalize(this);
    }
}
