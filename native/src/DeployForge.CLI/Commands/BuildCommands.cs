using System.CommandLine;
using Microsoft.Extensions.DependencyInjection;
using Spectre.Console;
using DeployForge.Core.Enums;
using DeployForge.Core.Interfaces;
using DeployForge.Core.Models;

namespace DeployForge.CLI.Commands;

/// <summary>
/// Build commands for applying customizations.
/// </summary>
public static class BuildCommands
{
    /// <summary>
    /// Creates the build command group.
    /// </summary>
    public static Command Create()
    {
        var buildCommand = new Command("build", "Build and apply customizations to images");
        
        buildCommand.AddCommand(CreateApplyCommand());
        buildCommand.AddCommand(CreateGamingCommand());
        buildCommand.AddCommand(CreateDebloatCommand());
        buildCommand.AddCommand(CreateDevCommand());
        
        return buildCommand;
    }
    
    /// <summary>
    /// Creates the apply command for applying a full profile.
    /// </summary>
    private static Command CreateApplyCommand()
    {
        var mountPathArg = new Argument<string>("mount-path", "Mount path of the image");
        var profileOption = new Option<string>("--profile", "Built-in profile to apply (Gaming, Developer, Enterprise, Student, Creator)");
        var templateOption = new Option<string?>("--template", "Path to template file");
        
        var command = new Command("apply", "Apply a build profile to mounted image")
        {
            mountPathArg,
            profileOption,
            templateOption
        };
        
        command.SetHandler(async (string mountPath, string profileName, string? templatePath) =>
        {
            BuildProfile? profile = null;
            
            // Load profile
            if (!string.IsNullOrEmpty(templatePath))
            {
                var templateService = Program.Services.GetRequiredService<ITemplateService>();
                profile = await templateService.LoadTemplateAsync(templatePath);
                AnsiConsole.MarkupLine($"[blue]Loading template:[/] {templatePath}");
            }
            else if (!string.IsNullOrEmpty(profileName))
            {
                profile = profileName.ToLowerInvariant() switch
                {
                    "gaming" => BuildProfile.CreateGamingProfile(),
                    "developer" => BuildProfile.CreateDeveloperProfile(),
                    "enterprise" => BuildProfile.CreateEnterpriseProfile(),
                    "student" => BuildProfile.CreateStudentProfile(),
                    "creator" => BuildProfile.CreateCreatorProfile(),
                    _ => null
                };
                
                if (profile == null)
                {
                    AnsiConsole.MarkupLine($"[red]Unknown profile:[/] {profileName}");
                    return;
                }
                
                AnsiConsole.MarkupLine($"[blue]Using built-in profile:[/] {profile.Name}");
            }
            else
            {
                AnsiConsole.MarkupLine("[red]Please specify --profile or --template[/]");
                return;
            }
            
            await AnsiConsole.Progress()
                .Columns(new ProgressColumn[]
                {
                    new TaskDescriptionColumn(),
                    new ProgressBarColumn(),
                    new PercentageColumn(),
                    new SpinnerColumn()
                })
                .StartAsync(async ctx =>
                {
                    var task = ctx.AddTask($"[green]Applying {profile.Name}[/]");
                    
                    var featureService = Program.Services.GetRequiredService<IFeatureService>();
                    
                    var progress = new Progress<ProgressInfo>(info =>
                    {
                        task.Description = info.Message;
                        task.Value = info.Percentage;
                    });
                    
                    var result = await featureService.ApplyProfileAsync(mountPath, profile, progress);
                    
                    task.Value = 100;
                    
                    AnsiConsole.WriteLine();
                    
                    if (result.Success)
                    {
                        AnsiConsole.MarkupLine($"[green]✓[/] Build completed in [bold]{result.Duration.TotalSeconds:0.0}s[/]");
                        
                        if (result.Changes.Count > 0)
                        {
                            AnsiConsole.WriteLine();
                            AnsiConsole.MarkupLine("[bold]Changes applied:[/]");
                            foreach (var change in result.Changes)
                            {
                                AnsiConsole.MarkupLine($"  [green]•[/] {change}");
                            }
                        }
                    }
                    else
                    {
                        AnsiConsole.MarkupLine($"[red]✗[/] Build failed: {result.Error}");
                    }
                    
                    if (result.Warnings.Count > 0)
                    {
                        AnsiConsole.WriteLine();
                        AnsiConsole.MarkupLine("[yellow]Warnings:[/]");
                        foreach (var warning in result.Warnings)
                        {
                            AnsiConsole.MarkupLine($"  [yellow]![/] {warning}");
                        }
                    }
                });
        }, mountPathArg, profileOption, templateOption);
        
        return command;
    }
    
    /// <summary>
    /// Creates the gaming optimization command.
    /// </summary>
    private static Command CreateGamingCommand()
    {
        var mountPathArg = new Argument<string>("mount-path", "Mount path of the image");
        var profileOption = new Option<GamingProfile>("--profile", () => GamingProfile.Balanced, "Gaming profile (Minimal, Balanced, Performance, Extreme)");
        var gameModeOption = new Option<bool>("--game-mode", () => true, "Enable Game Mode");
        var gameBarOption = new Option<bool>("--no-game-bar", () => false, "Disable Xbox Game Bar");
        var networkOption = new Option<bool>("--optimize-network", () => true, "Optimize network for gaming");
        var runtimesOption = new Option<bool>("--install-runtimes", () => true, "Install gaming runtimes");
        
        var command = new Command("gaming", "Apply gaming optimizations")
        {
            mountPathArg,
            profileOption,
            gameModeOption,
            gameBarOption,
            networkOption,
            runtimesOption
        };
        
        command.SetHandler(async (string mountPath, GamingProfile profile, bool gameMode, bool noGameBar, bool network, bool runtimes) =>
        {
            var config = new GamingConfig
            {
                Profile = profile,
                EnableGameMode = gameMode,
                DisableGameBar = noGameBar,
                OptimizeNetwork = network,
                InstallRuntimes = runtimes
            };
            
            await AnsiConsole.Progress()
                .StartAsync(async ctx =>
                {
                    var task = ctx.AddTask("[green]Applying gaming optimizations[/]");
                    
                    var featureService = Program.Services.GetRequiredService<IFeatureService>();
                    
                    var progress = new Progress<ProgressInfo>(info =>
                    {
                        task.Description = info.Message;
                        task.Value = info.Percentage;
                    });
                    
                    var result = await featureService.ApplyGamingOptimizationsAsync(mountPath, config, progress);
                    
                    task.Value = 100;
                    
                    AnsiConsole.WriteLine();
                    
                    if (result.Success)
                    {
                        AnsiConsole.MarkupLine("[green]✓[/] Gaming optimizations applied");
                        
                        foreach (var opt in result.AppliedOptimizations)
                        {
                            AnsiConsole.MarkupLine($"  [green]•[/] {opt}");
                        }
                    }
                    else
                    {
                        AnsiConsole.MarkupLine($"[red]✗[/] Failed: {result.Error}");
                    }
                });
        }, mountPathArg, profileOption, gameModeOption, gameBarOption, networkOption, runtimesOption);
        
        return command;
    }
    
    /// <summary>
    /// Creates the debloat command.
    /// </summary>
    private static Command CreateDebloatCommand()
    {
        var mountPathArg = new Argument<string>("mount-path", "Mount path of the image");
        var levelOption = new Option<DebloatLevel>("--level", () => DebloatLevel.Standard, "Debloat level (Minimal, Standard, Aggressive, Extreme)");
        var telemetryOption = new Option<bool>("--disable-telemetry", () => true, "Disable telemetry");
        var cortanaOption = new Option<bool>("--disable-cortana", () => true, "Disable Cortana");
        var privacyOption = new Option<PrivacyLevel>("--privacy", () => PrivacyLevel.Standard, "Privacy level");
        
        var command = new Command("debloat", "Remove bloatware and apply privacy settings")
        {
            mountPathArg,
            levelOption,
            telemetryOption,
            cortanaOption,
            privacyOption
        };
        
        command.SetHandler(async (string mountPath, DebloatLevel level, bool telemetry, bool cortana, PrivacyLevel privacy) =>
        {
            var config = DebloatConfig.Default;
            config.Level = level;
            config.DisableTelemetry = telemetry;
            config.DisableCortana = cortana;
            config.PrivacyLevel = privacy;
            
            await AnsiConsole.Progress()
                .StartAsync(async ctx =>
                {
                    var task = ctx.AddTask("[green]Removing bloatware[/]");
                    
                    var featureService = Program.Services.GetRequiredService<IFeatureService>();
                    
                    var progress = new Progress<ProgressInfo>(info =>
                    {
                        task.Description = info.Message;
                        task.Value = info.Percentage;
                    });
                    
                    var result = await featureService.RemoveBloatwareAsync(mountPath, config, progress);
                    
                    task.Value = 100;
                    
                    AnsiConsole.WriteLine();
                    
                    if (result.Success)
                    {
                        AnsiConsole.MarkupLine("[green]✓[/] Debloat completed");
                        
                        if (result.RemovedApps.Count > 0)
                        {
                            AnsiConsole.MarkupLine($"  Removed {result.RemovedApps.Count} apps");
                        }
                        
                        foreach (var setting in result.AppliedSettings)
                        {
                            AnsiConsole.MarkupLine($"  [green]•[/] {setting}");
                        }
                    }
                    else
                    {
                        AnsiConsole.MarkupLine($"[red]✗[/] Failed: {result.Error}");
                    }
                });
        }, mountPathArg, levelOption, telemetryOption, cortanaOption, privacyOption);
        
        return command;
    }
    
    /// <summary>
    /// Creates the developer environment command.
    /// </summary>
    private static Command CreateDevCommand()
    {
        var mountPathArg = new Argument<string>("mount-path", "Mount path of the image");
        var profileOption = new Option<DevelopmentProfile>("--profile", () => DevelopmentProfile.General, "Development profile");
        var devModeOption = new Option<bool>("--dev-mode", () => true, "Enable Developer Mode");
        var wslOption = new Option<bool>("--wsl2", () => false, "Enable WSL 2");
        
        var command = new Command("dev", "Configure developer environment")
        {
            mountPathArg,
            profileOption,
            devModeOption,
            wslOption
        };
        
        command.SetHandler(async (string mountPath, DevelopmentProfile profile, bool devMode, bool wsl) =>
        {
            await AnsiConsole.Status()
                .StartAsync($"Configuring {profile} development environment...", async ctx =>
                {
                    var config = new DevEnvironmentConfig
                    {
                        Profile = profile,
                        EnableDeveloperMode = devMode,
                        EnableWSL2 = wsl
                    };
                    
                    var buildProfile = new BuildProfile
                    {
                        Name = "Developer",
                        EnableDevEnvironment = true,
                        DevEnvironment = config
                    };
                    
                    var featureService = Program.Services.GetRequiredService<IFeatureService>();
                    var result = await featureService.ApplyProfileAsync(mountPath, buildProfile);
                    
                    if (result.Success)
                    {
                        AnsiConsole.MarkupLine("[green]✓[/] Developer environment configured");
                        
                        foreach (var change in result.Changes)
                        {
                            AnsiConsole.MarkupLine($"  [green]•[/] {change}");
                        }
                    }
                    else
                    {
                        AnsiConsole.MarkupLine($"[red]✗[/] Failed: {result.Error}");
                    }
                });
        }, mountPathArg, profileOption, devModeOption, wslOption);
        
        return command;
    }
}
