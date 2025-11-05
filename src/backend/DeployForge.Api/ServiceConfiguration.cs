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

        // Register application services
        // services.AddScoped<IImageService, ImageService>();
        // services.AddScoped<IDismService, DismService>();
        // services.AddScoped<IComponentService, ComponentService>();
        // services.AddScoped<IRegistryService, RegistryService>();
        // services.AddScoped<IWorkflowService, WorkflowService>();

        // Register background services
        // services.AddHostedService<CleanupService>();

        // Add memory cache
        services.AddMemoryCache();

        return services;
    }
}
