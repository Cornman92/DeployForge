using DeployForge.Core.Interfaces;
using Microsoft.Extensions.DependencyInjection;

namespace DeployForge.Services;

/// <summary>
/// Extension methods for registering DeployForge services.
/// </summary>
public static class ServiceCollectionExtensions
{
    /// <summary>
    /// Adds DeployForge services to the service collection.
    /// </summary>
    public static IServiceCollection AddDeployForgeServices(this IServiceCollection services)
    {
        // Register PowerShell executor as singleton (maintains runspace)
        services.AddSingleton<IPowerShellExecutor, PowerShellExecutor>();
        
        // Register services as scoped or transient as appropriate
        services.AddTransient<IImageService, ImageService>();
        services.AddTransient<IFeatureService, FeatureService>();
        services.AddSingleton<ITemplateService, TemplateService>();
        services.AddSingleton<ISettingsService, SettingsService>();
        
        return services;
    }
    
    /// <summary>
    /// Adds DeployForge services with custom configuration.
    /// </summary>
    public static IServiceCollection AddDeployForgeServices(
        this IServiceCollection services,
        Action<DeployForgeServiceOptions> configure)
    {
        var options = new DeployForgeServiceOptions();
        configure(options);
        
        // Register PowerShell executor with custom module path
        services.AddSingleton<IPowerShellExecutor>(_ => 
            new PowerShellExecutor(options.PowerShellModulePath));
        
        // Register services
        services.AddTransient<IImageService, ImageService>();
        services.AddTransient<IFeatureService, FeatureService>();
        
        services.AddSingleton<ITemplateService>(_ => 
            new TemplateService(options.TemplatesDirectory));
        
        services.AddSingleton<ISettingsService>(_ => 
            new SettingsService(options.SettingsPath));
        
        return services;
    }
}

/// <summary>
/// Options for configuring DeployForge services.
/// </summary>
public class DeployForgeServiceOptions
{
    /// <summary>
    /// Custom path to the PowerShell module.
    /// </summary>
    public string? PowerShellModulePath { get; set; }
    
    /// <summary>
    /// Custom path for templates directory.
    /// </summary>
    public string? TemplatesDirectory { get; set; }
    
    /// <summary>
    /// Custom path for settings file.
    /// </summary>
    public string? SettingsPath { get; set; }
}
