using DeployForge.Core.Interfaces;
using DeployForge.Core.Services;
using DeployForge.DismEngine;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;

namespace DeployForge.Api;

/// <summary>
/// Extension methods for configuring application services
/// </summary>
public static class ServiceConfiguration
{
    /// <summary>
    /// Configures all application services
    /// </summary>
    public static IServiceCollection ConfigureApplicationServices(
        this IServiceCollection services,
        IConfiguration configuration)
    {
        // Add database context
        // services.AddDbContext<DeployForgeDbContext>(options =>
        //     options.UseSqlite(configuration.GetConnectionString("DefaultConnection")));

        // Add Redis cache (if enabled)
        var redisConnection = configuration.GetConnectionString("RedisConnection");
        if (!string.IsNullOrEmpty(redisConnection))
        {
            services.AddStackExchangeRedisCache(options =>
            {
                options.Configuration = redisConnection;
                options.InstanceName = "DeployForge_";
            });
        }
        else
        {
            services.AddDistributedMemoryCache(); // Fallback to in-memory cache
        }

        // Register DISM manager as singleton (thread-safe)
        services.AddSingleton<DismManager>();

        // Register application services
        services.AddScoped<IImageService, ImageService>();
        services.AddScoped<IComponentService, ComponentService>();
        services.AddScoped<IDriverService, DriverService>();
        services.AddScoped<IUpdateService, UpdateService>();
        services.AddScoped<IRegistryService, RegistryService>();
        services.AddScoped<IDebloatService, DebloatService>();
        services.AddScoped<IWorkflowService, WorkflowService>();
        services.AddScoped<IDeploymentService, DeploymentService>();

        // Register background services
        // services.AddHostedService<CleanupService>();

        // Add memory cache
        services.AddMemoryCache();

        return services;
    }
}
