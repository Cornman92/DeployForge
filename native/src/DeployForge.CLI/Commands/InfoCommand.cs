using System.CommandLine;
using System.Reflection;
using Spectre.Console;

namespace DeployForge.CLI.Commands;

/// <summary>
/// Info command to display application information.
/// </summary>
public static class InfoCommand
{
    /// <summary>
    /// Creates the info command.
    /// </summary>
    public static Command Create()
    {
        var command = new Command("info", "Display application information");
        
        command.SetHandler(() =>
        {
            var version = Assembly.GetExecutingAssembly().GetName().Version?.ToString() ?? "2.0.0";
            
            var panel = new Panel(new Rows(
                new Text("DeployForge - Windows Deployment Suite", new Style(Color.Blue, null, Decoration.Bold)),
                new Text($"Version: {version}"),
                new Text(""),
                new Text("A comprehensive tool for customizing Windows deployment images."),
                new Text(""),
                new Text("Features:", new Style(Color.Yellow)),
                new Text("  • Image Management (WIM, ESD, VHD, VHDX, ISO)"),
                new Text("  • Gaming Optimization"),
                new Text("  • Debloat & Privacy"),
                new Text("  • Developer Environment"),
                new Text("  • Browser Configuration"),
                new Text("  • UI Customization"),
                new Text("  • Build Profiles & Templates"),
                new Text(""),
                new Text("Platform: Windows Native (.NET 8 + PowerShell)", new Style(Color.Grey)),
                new Text("Architecture: MVVM + WinUI 3", new Style(Color.Grey))
            ))
            {
                Header = new PanelHeader(" DeployForge ", Justify.Center),
                Border = BoxBorder.Rounded,
                BorderStyle = new Style(Color.Blue),
                Padding = new Padding(2, 1, 2, 1)
            };
            
            AnsiConsole.Write(panel);
            
            AnsiConsole.WriteLine();
            
            // System info
            var sysTable = new Table();
            sysTable.AddColumn("System Information");
            sysTable.AddColumn("");
            
            sysTable.AddRow("OS", Environment.OSVersion.ToString());
            sysTable.AddRow(".NET Version", Environment.Version.ToString());
            sysTable.AddRow("Machine Name", Environment.MachineName);
            sysTable.AddRow("User", Environment.UserName);
            sysTable.AddRow("64-bit OS", Environment.Is64BitOperatingSystem.ToString());
            sysTable.AddRow("64-bit Process", Environment.Is64BitProcess.ToString());
            
            AnsiConsole.Write(sysTable);
            
            AnsiConsole.WriteLine();
            
            // Commands help
            AnsiConsole.MarkupLine("[bold]Available Commands:[/]");
            AnsiConsole.WriteLine();
            
            var cmdTable = new Table();
            cmdTable.AddColumn("Command");
            cmdTable.AddColumn("Description");
            
            cmdTable.AddRow("[blue]image[/]", "Image management (info, mount, unmount, list, add, remove, extract)");
            cmdTable.AddRow("[blue]build[/]", "Build operations (apply, gaming, debloat, dev)");
            cmdTable.AddRow("[blue]profile[/]", "Profile management (list, show, export, import)");
            cmdTable.AddRow("[blue]info[/]", "Display this information");
            
            AnsiConsole.Write(cmdTable);
            
            AnsiConsole.WriteLine();
            AnsiConsole.MarkupLine("[grey]Use 'deployforge <command> --help' for more information on a command.[/]");
        });
        
        return command;
    }
}
