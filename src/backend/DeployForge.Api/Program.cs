using DeployForge.Api;
using DeployForge.Api.Middleware;
using DeployForge.Core.Interfaces;
using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Serilog;

// Configure Serilog
Log.Logger = new LoggerConfiguration()
    .WriteTo.Console()
    .WriteTo.File(
        path: "logs/deployforge-.log",
        rollingInterval: RollingInterval.Day,
        outputTemplate: "{Timestamp:yyyy-MM-dd HH:mm:ss.fff zzz} [{Level:u3}] {Message:lj}{NewLine}{Exception}")
    .CreateLogger();

try
{
    Log.Information("Starting DeployForge API");

    var builder = WebApplication.CreateBuilder(args);

    // Add Serilog
    builder.Host.UseSerilog();

    // Add services to the container
    builder.Services.AddControllers();
    builder.Services.AddEndpointsApiExplorer();
    builder.Services.AddSwaggerGen(options =>
    {
        options.SwaggerDoc("v1", new Microsoft.OpenApi.Models.OpenApiInfo
        {
            Title = "DeployForge API",
            Version = "v1.0.0-alpha",
            Description = "REST API for Windows Image Management and Deployment",
            Contact = new Microsoft.OpenApi.Models.OpenApiContact
            {
                Name = "DeployForge Team",
                Url = new Uri("https://github.com/Cornman92/DeployForge")
            },
            License = new Microsoft.OpenApi.Models.OpenApiLicense
            {
                Name = "GPL-3.0",
                Url = new Uri("https://github.com/Cornman92/DeployForge/blob/main/LICENSE")
            }
        });

        // Include XML comments if available
        var xmlFile = $"{System.Reflection.Assembly.GetExecutingAssembly().GetName().Name}.xml";
        var xmlPath = Path.Combine(AppContext.BaseDirectory, xmlFile);
        if (File.Exists(xmlPath))
        {
            options.IncludeXmlComments(xmlPath);
        }
    });

    // CORS configuration
    builder.Services.AddCors(options =>
    {
        options.AddPolicy("AllowFrontend", policy =>
        {
            policy.WithOrigins("http://localhost:5173", "http://localhost:3000")
                  .AllowAnyHeader()
                  .AllowAnyMethod()
                  .AllowCredentials();
        });
    });

    // Add SignalR for real-time updates
    builder.Services.AddSignalR();

    // Health checks
    builder.Services.AddHealthChecks();

    // Configure application services
    builder.Services.ConfigureApplicationServices(builder.Configuration);

    var app = builder.Build();

    // Configure the HTTP request pipeline
    if (app.Environment.IsDevelopment())
    {
        app.UseSwagger();
        app.UseSwaggerUI(c =>
        {
            c.SwaggerEndpoint("/swagger/v1/swagger.json", "DeployForge API v1");
            c.RoutePrefix = string.Empty; // Serve Swagger UI at root
        });
    }

    // Custom middleware
    app.UseErrorHandling();
    app.UseRequestLogging();

    app.UseSerilogRequestLogging();

    app.UseHttpsRedirection();

    app.UseCors("AllowFrontend");

    app.UseAuthorization();

    app.MapControllers();

    app.MapHealthChecks("/health");

    // Map SignalR hubs
    app.MapHub<ProgressHub>("/hubs/progress");

    // Start monitoring service
    var monitoringService = app.Services.GetRequiredService<IMonitoringService>();
    await monitoringService.StartMonitoringAsync();
    Log.Information("Monitoring service started");

    app.Run();

    Log.Information("DeployForge API started successfully");
}
catch (Exception ex)
{
    Log.Fatal(ex, "DeployForge API failed to start");
    throw;
}
finally
{
    Log.CloseAndFlush();
}
