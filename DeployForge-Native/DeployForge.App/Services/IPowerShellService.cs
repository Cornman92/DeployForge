using System.Management.Automation;
using System.Management.Automation.Runspaces;

namespace DeployForge.App.Services;

public interface IPowerShellService
{
    bool IsInitialized { get; }
    Task InitializeAsync();
    Task<PowerShellResult> InvokeAsync(string command, Dictionary<string, object?>? parameters = null);
    Task<T?> InvokeFunctionAsync<T>(string functionName, Dictionary<string, object?>? parameters = null);
    event EventHandler<string>? OutputReceived;
    event EventHandler<string>? ErrorReceived;
    event EventHandler<int>? ProgressUpdated;
}

public record PowerShellResult(bool Success, object? Result, List<string> Output, List<string> Errors);

public class PowerShellService : IPowerShellService, IDisposable
{
    private Runspace? _runspace;
    private bool _isInitialized;
    
    public bool IsInitialized => _isInitialized;
    
    public event EventHandler<string>? OutputReceived;
    public event EventHandler<string>? ErrorReceived;
    public event EventHandler<int>? ProgressUpdated;
    
    public async Task InitializeAsync()
    {
        await Task.Run(() =>
        {
            var initialState = InitialSessionState.CreateDefault();
            
            // Get the module path
            var modulePath = Path.Combine(AppContext.BaseDirectory, "PowerShell", "DeployForge.psd1");
            if (!File.Exists(modulePath))
            {
                modulePath = Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", "DeployForge.PowerShell", "DeployForge.psd1");
            }
            
            if (File.Exists(modulePath))
            {
                initialState.ImportPSModule(new[] { modulePath });
            }
            
            _runspace = RunspaceFactory.CreateRunspace(initialState);
            _runspace.Open();
            
            _isInitialized = true;
        });
    }
    
    public async Task<PowerShellResult> InvokeAsync(string command, Dictionary<string, object?>? parameters = null)
    {
        if (!_isInitialized || _runspace == null)
        {
            return new PowerShellResult(false, null, new(), new() { "PowerShell service not initialized" });
        }
        
        return await Task.Run(() =>
        {
            using var ps = System.Management.Automation.PowerShell.Create();
            ps.Runspace = _runspace;
            ps.AddScript(command);
            
            if (parameters != null)
            {
                foreach (var (key, value) in parameters)
                {
                    ps.AddParameter(key, value);
                }
            }
            
            var output = new List<string>();
            var errors = new List<string>();
            
            ps.Streams.Information.DataAdded += (s, e) =>
            {
                var info = ps.Streams.Information[e.Index];
                output.Add(info.MessageData.ToString() ?? "");
                OutputReceived?.Invoke(this, info.MessageData.ToString() ?? "");
            };
            
            ps.Streams.Error.DataAdded += (s, e) =>
            {
                var error = ps.Streams.Error[e.Index];
                errors.Add(error.Exception.Message);
                ErrorReceived?.Invoke(this, error.Exception.Message);
            };
            
            ps.Streams.Progress.DataAdded += (s, e) =>
            {
                var progress = ps.Streams.Progress[e.Index];
                ProgressUpdated?.Invoke(this, progress.PercentComplete);
            };
            
            try
            {
                var results = ps.Invoke();
                var resultObj = results.Count > 0 ? results[0].BaseObject : null;
                
                foreach (var item in results)
                {
                    output.Add(item.ToString() ?? "");
                }
                
                return new PowerShellResult(!ps.HadErrors, resultObj, output, errors);
            }
            catch (Exception ex)
            {
                return new PowerShellResult(false, null, output, new() { ex.Message });
            }
        });
    }
    
    public async Task<T?> InvokeFunctionAsync<T>(string functionName, Dictionary<string, object?>? parameters = null)
    {
        var paramString = "";
        if (parameters != null && parameters.Count > 0)
        {
            var parts = parameters.Select(p => $"-{p.Key} ${p.Key}").ToList();
            paramString = " " + string.Join(" ", parts);
        }
        
        var script = $"{functionName}{paramString}";
        var result = await InvokeAsync(script, parameters);
        
        if (result.Success && result.Result is T typedResult)
        {
            return typedResult;
        }
        
        return default;
    }
    
    public void Dispose()
    {
        _runspace?.Close();
        _runspace?.Dispose();
    }
}
