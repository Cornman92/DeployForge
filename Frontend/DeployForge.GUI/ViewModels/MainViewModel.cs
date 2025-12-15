using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using DeployForge.GUI.Services;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Threading.Tasks;

namespace DeployForge.GUI.ViewModels
{
    public partial class MainViewModel : ObservableObject
    {
        private readonly PowerShellService _psService;

        [ObservableProperty]
        private string _imagePath;

        [ObservableProperty]
        private string _statusMessage;

        [ObservableProperty]
        private int _progress;

        [ObservableProperty]
        private bool _isBusy;

        // Features
        [ObservableProperty]
        private bool _enableGaming;

        [ObservableProperty]
        private bool _enablePrivacy;

        [ObservableProperty]
        private bool _enableDevEnv;

        public ObservableCollection<string> Logs { get; } = new();

        public MainViewModel()
        {
            _psService = new PowerShellService();
            _psService.OutputReceived += (s, e) => {
                App.MainWindow.DispatcherQueue.TryEnqueue(() => Logs.Add(e));
            };
            _psService.ProgressReceived += (s, e) => {
                App.MainWindow.DispatcherQueue.TryEnqueue(() => Progress = e);
            };
        }

        [RelayCommand]
        private async Task BuildImage()
        {
            if (string.IsNullOrEmpty(ImagePath)) return;

            IsBusy = true;
            StatusMessage = "Building Image...";
            Logs.Clear();

            var config = new Dictionary<string, object>
            {
                { "Gaming", EnableGaming ? new { Profile = "Competitive" } : null },
                { "Privacy", EnablePrivacy ? new { DisableTelemetry = true } : null },
                { "Devenv", EnableDevEnv ? new { Profile = "FullStack" } : null }
            };

            var script = @"
                Import-Module .\Backend\DeployForge\DeployForge.psd1
                New-ImageBuild -ImagePath $ImagePath -Config $Config
            ";

            var parameters = new Dictionary<string, object>
            {
                { "ImagePath", ImagePath },
                { "Config", config }
            };

            await _psService.ExecuteScriptAsync(script, parameters);

            IsBusy = false;
            StatusMessage = "Build Complete";
        }
    }
}
