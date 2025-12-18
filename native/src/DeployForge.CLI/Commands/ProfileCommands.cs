using System.CommandLine;
using Microsoft.Extensions.DependencyInjection;
using Spectre.Console;
using DeployForge.Core.Enums;
using DeployForge.Core.Interfaces;
using DeployForge.Core.Models;
using DeployForge.Services;

namespace DeployForge.CLI.Commands;

/// <summary>
/// Profile management commands.
/// </summary>
public static class ProfileCommands
{
    /// <summary>
    /// Creates the profile command group.
    /// </summary>
    public static Command Create()
    {
        var profileCommand = new Command("profile", "Profile and template management");
        
        profileCommand.AddCommand(CreateListCommand());
        profileCommand.AddCommand(CreateShowCommand());
        profileCommand.AddCommand(CreateExportCommand());
        profileCommand.AddCommand(CreateImportCommand());
        
        return profileCommand;
    }
    
    /// <summary>
    /// Creates the list command.
    /// </summary>
    private static Command CreateListCommand()
    {
        var command = new Command("list", "List available profiles");
        
        command.SetHandler(async () =>
        {
            var templateService = Program.Services.GetRequiredService<ITemplateService>();
            
            AnsiConsole.MarkupLine("[bold]Built-in Profiles:[/]");
            AnsiConsole.WriteLine();
            
            var builtInTable = new Table();
            builtInTable.AddColumn("Name");
            builtInTable.AddColumn("Type");
            builtInTable.AddColumn("Description");
            builtInTable.AddColumn("Features");
            
            foreach (var profile in templateService.GetBuiltInProfiles())
            {
                var features = GetFeaturesList(profile);
                builtInTable.AddRow(
                    $"[bold]{profile.Name}[/]",
                    profile.Type.ToString(),
                    profile.Description,
                    features);
            }
            
            AnsiConsole.Write(builtInTable);
            
            // Custom profiles
            var customProfiles = await templateService.GetCustomTemplatesAsync();
            var customList = customProfiles.ToList();
            
            if (customList.Count > 0)
            {
                AnsiConsole.WriteLine();
                AnsiConsole.MarkupLine("[bold]Custom Profiles:[/]");
                AnsiConsole.WriteLine();
                
                var customTable = new Table();
                customTable.AddColumn("Name");
                customTable.AddColumn("Description");
                customTable.AddColumn("Features");
                
                foreach (var profile in customList)
                {
                    var features = GetFeaturesList(profile);
                    customTable.AddRow(
                        $"[bold]{profile.Name}[/]",
                        profile.Description,
                        features);
                }
                
                AnsiConsole.Write(customTable);
            }
        });
        
        return command;
    }
    
    /// <summary>
    /// Creates the show command.
    /// </summary>
    private static Command CreateShowCommand()
    {
        var nameArg = new Argument<string>("name", "Profile name or path to template file");
        
        var command = new Command("show", "Show profile details")
        {
            nameArg
        };
        
        command.SetHandler(async (string name) =>
        {
            var templateService = Program.Services.GetRequiredService<ITemplateService>();
            BuildProfile? profile = null;
            
            // Check if it's a file path
            if (File.Exists(name))
            {
                profile = await templateService.LoadTemplateAsync(name);
            }
            else
            {
                // Look for built-in profile
                profile = name.ToLowerInvariant() switch
                {
                    "gaming" => BuildProfile.CreateGamingProfile(),
                    "developer" => BuildProfile.CreateDeveloperProfile(),
                    "enterprise" => BuildProfile.CreateEnterpriseProfile(),
                    "student" => BuildProfile.CreateStudentProfile(),
                    "creator" => BuildProfile.CreateCreatorProfile(),
                    _ => null
                };
            }
            
            if (profile == null)
            {
                AnsiConsole.MarkupLine($"[red]Profile not found:[/] {name}");
                return;
            }
            
            // Display profile details
            var panel = new Panel(new Markup($"[bold]{profile.Name}[/]\n{profile.Description}"))
            {
                Header = new PanelHeader($" {profile.Icon} Profile Details ")
            };
            
            AnsiConsole.Write(panel);
            AnsiConsole.WriteLine();
            
            var table = new Table();
            table.AddColumn("Setting");
            table.AddColumn("Value");
            
            table.AddRow("Type", profile.Type.ToString());
            table.AddRow("Privacy Level", profile.PrivacyLevel.ToString());
            table.AddRow("", "");
            table.AddRow("[bold]Features[/]", "");
            table.AddRow("  Gaming", profile.EnableGaming ? "[green]Enabled[/]" : "[grey]Disabled[/]");
            table.AddRow("  Debloat", profile.EnableDebloat ? "[green]Enabled[/]" : "[grey]Disabled[/]");
            table.AddRow("  Developer", profile.EnableDevEnvironment ? "[green]Enabled[/]" : "[grey]Disabled[/]");
            table.AddRow("  Browsers", profile.EnableBrowsers ? "[green]Enabled[/]" : "[grey]Disabled[/]");
            table.AddRow("  UI Customization", profile.EnableUICustomization ? "[green]Enabled[/]" : "[grey]Disabled[/]");
            table.AddRow("  Privacy Hardening", profile.EnablePrivacyHardening ? "[green]Enabled[/]" : "[grey]Disabled[/]");
            
            if (profile.Gaming != null)
            {
                table.AddRow("", "");
                table.AddRow("[bold]Gaming Settings[/]", "");
                table.AddRow("  Profile", profile.Gaming.Profile.ToString());
                table.AddRow("  Game Mode", profile.Gaming.EnableGameMode.ToString());
                table.AddRow("  Disable Game Bar", profile.Gaming.DisableGameBar.ToString());
                table.AddRow("  Optimize Network", profile.Gaming.OptimizeNetwork.ToString());
            }
            
            if (profile.Debloat != null)
            {
                table.AddRow("", "");
                table.AddRow("[bold]Debloat Settings[/]", "");
                table.AddRow("  Level", profile.Debloat.Level.ToString());
                table.AddRow("  Disable Telemetry", profile.Debloat.DisableTelemetry.ToString());
                table.AddRow("  Disable Cortana", profile.Debloat.DisableCortana.ToString());
            }
            
            if (profile.DevEnvironment != null)
            {
                table.AddRow("", "");
                table.AddRow("[bold]Developer Settings[/]", "");
                table.AddRow("  Profile", profile.DevEnvironment.Profile.ToString());
                table.AddRow("  Developer Mode", profile.DevEnvironment.EnableDeveloperMode.ToString());
                table.AddRow("  WSL 2", profile.DevEnvironment.EnableWSL2.ToString());
            }
            
            AnsiConsole.Write(table);
        }, nameArg);
        
        return command;
    }
    
    /// <summary>
    /// Creates the export command.
    /// </summary>
    private static Command CreateExportCommand()
    {
        var nameArg = new Argument<string>("name", "Profile name");
        var outputOption = new Option<string>("--output", "Output file path") { IsRequired = true };
        
        var command = new Command("export", "Export a profile to file")
        {
            nameArg,
            outputOption
        };
        
        command.SetHandler(async (string name, string output) =>
        {
            var templateService = Program.Services.GetRequiredService<ITemplateService>();
            
            BuildProfile? profile = name.ToLowerInvariant() switch
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
                AnsiConsole.MarkupLine($"[red]Profile not found:[/] {name}");
                return;
            }
            
            await templateService.SaveTemplateAsync(profile, output);
            AnsiConsole.MarkupLine($"[green]✓[/] Exported to: {output}");
        }, nameArg, outputOption);
        
        return command;
    }
    
    /// <summary>
    /// Creates the import command.
    /// </summary>
    private static Command CreateImportCommand()
    {
        var pathArg = new Argument<string>("path", "Path to template file");
        
        var command = new Command("import", "Import a profile from file")
        {
            pathArg
        };
        
        command.SetHandler(async (string path) =>
        {
            var templateService = Program.Services.GetRequiredService<ITemplateService>();
            
            try
            {
                var profile = await templateService.LoadTemplateAsync(path);
                
                if (templateService is TemplateService ts)
                {
                    await ts.SaveTemplateAsync(profile);
                }
                
                AnsiConsole.MarkupLine($"[green]✓[/] Imported profile: {profile.Name}");
            }
            catch (Exception ex)
            {
                AnsiConsole.MarkupLine($"[red]Failed to import:[/] {ex.Message}");
            }
        }, pathArg);
        
        return command;
    }
    
    private static string GetFeaturesList(BuildProfile profile)
    {
        var features = new List<string>();
        
        if (profile.EnableGaming) features.Add("Gaming");
        if (profile.EnableDebloat) features.Add("Debloat");
        if (profile.EnableDevEnvironment) features.Add("Dev");
        if (profile.EnableBrowsers) features.Add("Browsers");
        if (profile.EnableUICustomization) features.Add("UI");
        if (profile.EnablePrivacyHardening) features.Add("Privacy");
        
        return features.Count > 0 ? string.Join(", ", features) : "[grey]None[/]";
    }
}
