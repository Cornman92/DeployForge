using System;
using System.Collections.ObjectModel;
using System.Management.Automation;
using System.Threading.Tasks;

namespace DeployForge.GUI.Services
{
    public class PowerShellService
    {
        public event EventHandler<string> OutputReceived;
        public event EventHandler<string> ErrorReceived;
        public event EventHandler<int> ProgressReceived;

        public async Task ExecuteScriptAsync(string script, Dictionary<string, object> parameters = null)
        {
            await Task.Run(() =>
            {
                using (var ps = PowerShell.Create())
                {
                    ps.AddScript(script);

                    if (parameters != null)
                    {
                        foreach (var param in parameters)
                        {
                            ps.AddParameter(param.Key, param.Value);
                        }
                    }

                    var outputCollection = new PSDataCollection<PSObject>();
                    outputCollection.DataAdded += (sender, e) =>
                    {
                        var data = outputCollection[e.Index];
                        OutputReceived?.Invoke(this, data.ToString());
                    };

                    ps.Streams.Error.DataAdded += (sender, e) =>
                    {
                        var error = ps.Streams.Error[e.Index];
                        ErrorReceived?.Invoke(this, error.ToString());
                    };

                    ps.Streams.Progress.DataAdded += (sender, e) =>
                    {
                        var progress = ps.Streams.Progress[e.Index];
                        ProgressReceived?.Invoke(this, progress.PercentComplete);
                    };

                    try 
                    {
                        ps.Invoke(null, outputCollection);
                    }
                    catch (Exception ex)
                    {
                        ErrorReceived?.Invoke(this, ex.Message);
                    }
                }
            });
        }
    }
}
