using System.Windows;
using DeployForge.Desktop.Services;
using DeployForge.Desktop.ViewModels;
using DeployForge.Desktop.Views;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Serilog;

namespace DeployForge.Desktop;

public partial class App : Application
{
    private readonly IHost _host;

    public App()
    {
        // Configure Serilog
        Log.Logger = new LoggerConfiguration()
            .MinimumLevel.Debug()
            .WriteTo.Console()
            .WriteTo.File("logs/deployforge-desktop-.log", rollingInterval: RollingInterval.Day)
            .CreateLogger();

        _host = Host.CreateDefaultBuilder()
            .UseSerilog()
            .ConfigureServices((context, services) =>
            {
                // Register services
                services.AddSingleton<IApiClient, ApiClient>();
                services.AddSingleton<ISignalRService, SignalRService>();
                services.AddSingleton<ISettingsService, SettingsService>();
                services.AddSingleton<IDialogService, DialogService>();

                // Register ViewModels
                services.AddTransient<MainViewModel>();
                services.AddTransient<DashboardViewModel>();
                services.AddTransient<ImageManagementViewModel>();
                services.AddTransient<ComponentManagerViewModel>();
                services.AddTransient<WorkflowDesignerViewModel>();
                services.AddTransient<DebloatWizardViewModel>();
                services.AddTransient<BackupManagerViewModel>();
                services.AddTransient<SettingsViewModel>();

                // Register Views
                services.AddTransient<MainWindow>();
                services.AddTransient<DashboardView>();
                services.AddTransient<ImageManagementView>();
                services.AddTransient<ComponentManagerView>();
                services.AddTransient<WorkflowDesignerView>();
                services.AddTransient<DebloatWizardView>();
                services.AddTransient<BackupManagerView>();
                services.AddTransient<SettingsView>();
            })
            .Build();
    }

    protected override async void OnStartup(StartupEventArgs e)
    {
        await _host.StartAsync();

        Log.Information("DeployForge Desktop starting...");

        // Check for administrator privileges
        if (!IsRunningAsAdministrator())
        {
            var result = MessageBox.Show(
                "DeployForge requires administrator privileges to function properly.\n\n" +
                "Would you like to restart as administrator?",
                "Administrator Required",
                MessageBoxButton.YesNo,
                MessageBoxImage.Warning);

            if (result == MessageBoxResult.Yes)
            {
                RestartAsAdministrator();
            }

            Shutdown();
            return;
        }

        var mainWindow = _host.Services.GetRequiredService<MainWindow>();
        mainWindow.Show();

        base.OnStartup(e);
    }

    protected override async void OnExit(ExitEventArgs e)
    {
        using (_host)
        {
            await _host.StopAsync(TimeSpan.FromSeconds(5));
        }

        Log.CloseAndFlush();
        base.OnExit(e);
    }

    private bool IsRunningAsAdministrator()
    {
        var identity = System.Security.Principal.WindowsIdentity.GetCurrent();
        var principal = new System.Security.Principal.WindowsPrincipal(identity);
        return principal.IsInRole(System.Security.Principal.WindowsBuiltInRole.Administrator);
    }

    private void RestartAsAdministrator()
    {
        var processInfo = new System.Diagnostics.ProcessStartInfo
        {
            FileName = System.Diagnostics.Process.GetCurrentProcess().MainModule?.FileName ?? "",
            UseShellExecute = true,
            Verb = "runas"
        };

        try
        {
            System.Diagnostics.Process.Start(processInfo);
        }
        catch (Exception ex)
        {
            Log.Error(ex, "Failed to restart as administrator");
            MessageBox.Show("Failed to restart as administrator: " + ex.Message,
                "Error", MessageBoxButton.OK, MessageBoxImage.Error);
        }
    }

    public static T GetService<T>() where T : class
    {
        return ((App)Current)._host.Services.GetRequiredService<T>();
    }
}
