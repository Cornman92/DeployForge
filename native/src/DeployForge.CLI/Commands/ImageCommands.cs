using System.CommandLine;
using Microsoft.Extensions.DependencyInjection;
using Spectre.Console;
using DeployForge.Core.Interfaces;

namespace DeployForge.CLI.Commands;

/// <summary>
/// Image management commands.
/// </summary>
public static class ImageCommands
{
    /// <summary>
    /// Creates the image command group.
    /// </summary>
    public static Command Create()
    {
        var imageCommand = new Command("image", "Image management commands");
        
        imageCommand.AddCommand(CreateInfoCommand());
        imageCommand.AddCommand(CreateMountCommand());
        imageCommand.AddCommand(CreateUnmountCommand());
        imageCommand.AddCommand(CreateListCommand());
        imageCommand.AddCommand(CreateAddCommand());
        imageCommand.AddCommand(CreateRemoveCommand());
        imageCommand.AddCommand(CreateExtractCommand());
        
        return imageCommand;
    }
    
    /// <summary>
    /// Creates the info command.
    /// </summary>
    private static Command CreateInfoCommand()
    {
        var pathArg = new Argument<string>("path", "Path to the image file");
        var indexOption = new Option<int?>("--index", "Specific image index to query");
        
        var command = new Command("info", "Get information about an image")
        {
            pathArg,
            indexOption
        };
        
        command.SetHandler(async (string path, int? index) =>
        {
            await AnsiConsole.Status()
                .StartAsync("Reading image info...", async ctx =>
                {
                    var imageService = Program.Services.GetRequiredService<IImageService>();
                    var info = await imageService.GetInfoAsync(path, index);
                    
                    ctx.Status("Displaying info...");
                    
                    var table = new Table();
                    table.AddColumn("Property");
                    table.AddColumn("Value");
                    
                    table.AddRow("Path", info.Path);
                    table.AddRow("Format", info.Format.ToString());
                    table.AddRow("File Size", FormatFileSize(info.FileSize));
                    table.AddRow("Index Count", info.Indexes.Count.ToString());
                    
                    AnsiConsole.Write(table);
                    
                    if (info.Indexes.Count > 0)
                    {
                        AnsiConsole.WriteLine();
                        AnsiConsole.MarkupLine("[bold]Image Indexes:[/]");
                        
                        var indexTable = new Table();
                        indexTable.AddColumn("Index");
                        indexTable.AddColumn("Name");
                        indexTable.AddColumn("Size");
                        indexTable.AddColumn("Architecture");
                        
                        foreach (var idx in info.Indexes)
                        {
                            indexTable.AddRow(
                                idx.Index.ToString(),
                                idx.Name,
                                FormatFileSize(idx.Size),
                                idx.Architecture);
                        }
                        
                        AnsiConsole.Write(indexTable);
                    }
                });
        }, pathArg, indexOption);
        
        return command;
    }
    
    /// <summary>
    /// Creates the mount command.
    /// </summary>
    private static Command CreateMountCommand()
    {
        var pathArg = new Argument<string>("path", "Path to the image file");
        var indexOption = new Option<int>("--index", () => 1, "Image index to mount");
        var mountPathOption = new Option<string?>("--mount-path", "Custom mount path");
        var readOnlyOption = new Option<bool>("--read-only", () => false, "Mount as read-only");
        
        var command = new Command("mount", "Mount an image")
        {
            pathArg,
            indexOption,
            mountPathOption,
            readOnlyOption
        };
        
        command.SetHandler(async (string path, int index, string? mountPath, bool readOnly) =>
        {
            await AnsiConsole.Progress()
                .StartAsync(async ctx =>
                {
                    var task = ctx.AddTask("[green]Mounting image[/]");
                    
                    var imageService = Program.Services.GetRequiredService<IImageService>();
                    
                    var progress = new Progress<ProgressInfo>(info =>
                    {
                        task.Value = info.Percentage;
                    });
                    
                    var result = await imageService.MountAsync(path, index, mountPath, readOnly, progress);
                    
                    task.Value = 100;
                    
                    AnsiConsole.MarkupLine($"[green]✓[/] Image mounted at: [bold]{result.MountPath}[/]");
                });
        }, pathArg, indexOption, mountPathOption, readOnlyOption);
        
        return command;
    }
    
    /// <summary>
    /// Creates the unmount command.
    /// </summary>
    private static Command CreateUnmountCommand()
    {
        var pathArg = new Argument<string>("mount-path", "Mount path to unmount");
        var saveOption = new Option<bool>("--save", () => false, "Save changes before unmounting");
        
        var command = new Command("unmount", "Unmount an image")
        {
            pathArg,
            saveOption
        };
        
        command.SetHandler(async (string mountPath, bool save) =>
        {
            await AnsiConsole.Progress()
                .StartAsync(async ctx =>
                {
                    var task = ctx.AddTask(save ? "[yellow]Saving and unmounting[/]" : "[green]Unmounting[/]");
                    
                    var imageService = Program.Services.GetRequiredService<IImageService>();
                    
                    var progress = new Progress<ProgressInfo>(info =>
                    {
                        task.Value = info.Percentage;
                    });
                    
                    await imageService.UnmountAsync(mountPath, save, progress);
                    
                    task.Value = 100;
                    
                    AnsiConsole.MarkupLine($"[green]✓[/] Image unmounted" + (save ? " (changes saved)" : ""));
                });
        }, pathArg, saveOption);
        
        return command;
    }
    
    /// <summary>
    /// Creates the list command.
    /// </summary>
    private static Command CreateListCommand()
    {
        var mountPathArg = new Argument<string>("mount-path", "Mount path");
        var pathOption = new Option<string>("--path", () => "", "Path within image to list");
        var recurseOption = new Option<bool>("--recurse", () => false, "List recursively");
        
        var command = new Command("list", "List files in mounted image")
        {
            mountPathArg,
            pathOption,
            recurseOption
        };
        
        command.SetHandler(async (string mountPath, string path, bool recurse) =>
        {
            var imageService = Program.Services.GetRequiredService<IImageService>();
            var files = await imageService.ListFilesAsync(mountPath, path, recurse);
            
            var table = new Table();
            table.AddColumn("Name");
            table.AddColumn("Type");
            table.AddColumn("Size");
            table.AddColumn("Modified");
            
            foreach (var file in files)
            {
                table.AddRow(
                    file.Name,
                    file.IsDirectory ? "[blue]DIR[/]" : "FILE",
                    file.IsDirectory ? "" : FormatFileSize(file.Size),
                    file.LastModified?.ToString("g") ?? "");
            }
            
            AnsiConsole.Write(table);
        }, mountPathArg, pathOption, recurseOption);
        
        return command;
    }
    
    /// <summary>
    /// Creates the add command.
    /// </summary>
    private static Command CreateAddCommand()
    {
        var mountPathArg = new Argument<string>("mount-path", "Mount path");
        var sourceArg = new Argument<string>("source", "Source file path");
        var destArg = new Argument<string>("destination", "Destination path in image");
        
        var command = new Command("add", "Add a file to mounted image")
        {
            mountPathArg,
            sourceArg,
            destArg
        };
        
        command.SetHandler(async (string mountPath, string source, string destination) =>
        {
            await AnsiConsole.Status()
                .StartAsync("Adding file...", async ctx =>
                {
                    var imageService = Program.Services.GetRequiredService<IImageService>();
                    await imageService.AddFileAsync(mountPath, source, destination);
                    
                    AnsiConsole.MarkupLine($"[green]✓[/] Added: {destination}");
                });
        }, mountPathArg, sourceArg, destArg);
        
        return command;
    }
    
    /// <summary>
    /// Creates the remove command.
    /// </summary>
    private static Command CreateRemoveCommand()
    {
        var mountPathArg = new Argument<string>("mount-path", "Mount path");
        var pathArg = new Argument<string>("path", "Path to remove");
        var recurseOption = new Option<bool>("--recurse", () => false, "Remove recursively");
        
        var command = new Command("remove", "Remove a file from mounted image")
        {
            mountPathArg,
            pathArg,
            recurseOption
        };
        
        command.SetHandler(async (string mountPath, string path, bool recurse) =>
        {
            await AnsiConsole.Status()
                .StartAsync("Removing file...", async ctx =>
                {
                    var imageService = Program.Services.GetRequiredService<IImageService>();
                    await imageService.RemoveFileAsync(mountPath, path, recurse);
                    
                    AnsiConsole.MarkupLine($"[green]✓[/] Removed: {path}");
                });
        }, mountPathArg, pathArg, recurseOption);
        
        return command;
    }
    
    /// <summary>
    /// Creates the extract command.
    /// </summary>
    private static Command CreateExtractCommand()
    {
        var mountPathArg = new Argument<string>("mount-path", "Mount path");
        var sourceArg = new Argument<string>("source", "Source path in image");
        var destArg = new Argument<string>("destination", "Destination path on host");
        
        var command = new Command("extract", "Extract a file from mounted image")
        {
            mountPathArg,
            sourceArg,
            destArg
        };
        
        command.SetHandler(async (string mountPath, string source, string destination) =>
        {
            await AnsiConsole.Status()
                .StartAsync("Extracting file...", async ctx =>
                {
                    var imageService = Program.Services.GetRequiredService<IImageService>();
                    await imageService.ExtractFileAsync(mountPath, source, destination);
                    
                    AnsiConsole.MarkupLine($"[green]✓[/] Extracted to: {destination}");
                });
        }, mountPathArg, sourceArg, destArg);
        
        return command;
    }
    
    private static string FormatFileSize(long bytes)
    {
        string[] sizes = { "B", "KB", "MB", "GB", "TB" };
        double size = bytes;
        int order = 0;
        
        while (size >= 1024 && order < sizes.Length - 1)
        {
            order++;
            size /= 1024;
        }
        
        return $"{size:0.##} {sizes[order]}";
    }
}
