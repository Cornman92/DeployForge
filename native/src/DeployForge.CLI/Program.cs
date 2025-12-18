using System.CommandLine;
using Microsoft.Extensions.DependencyInjection;
using Spectre.Console;
using DeployForge.CLI.Commands;
using DeployForge.Core.Interfaces;
using DeployForge.Services;

namespace DeployForge.CLI;

/// <summary>
/// DeployForge Command-Line Interface
/// </summary>
public class Program
{
    /// <summary>
    /// Service provider for dependency injection.
    /// </summary>
    public static IServiceProvider Services { get; private set; } = null!;
    
    public static async Task<int> Main(string[] args)
    {
        // Configure services
        var services = new ServiceCollection();
        ConfigureServices(services);
        Services = services.BuildServiceProvider();
        
        // Display banner
        DisplayBanner();
        
        // Build command tree
        var rootCommand = new RootCommand("DeployForge - Windows Deployment Suite CLI")
        {
            Name = "deployforge"
        };
        
        // Add commands
        rootCommand.AddCommand(ImageCommands.Create());
        rootCommand.AddCommand(BuildCommands.Create());
        rootCommand.AddCommand(ProfileCommands.Create());
        rootCommand.AddCommand(InfoCommand.Create());
        
        // Parse and execute
        return await rootCommand.InvokeAsync(args);
    }
    
    private static void ConfigureServices(IServiceCollection services)
    {
        services.AddDeployForgeServices();
    }
    
    private static void DisplayBanner()
    {
        AnsiConsole.Write(
            new FigletText("DeployForge")
                .Color(Color.Blue));
        
        AnsiConsole.MarkupLine("[grey]Windows Deployment Suite - Native Edition[/]");
        AnsiConsole.MarkupLine("[grey]Version 2.0.0[/]");
        AnsiConsole.WriteLine();
    }
}
