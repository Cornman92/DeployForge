using System.Management.Automation;
using DeployForge.Core.Enums;
using DeployForge.Core.Exceptions;
using DeployForge.Core.Interfaces;
using DeployForge.Core.Models;

namespace DeployForge.Services;

/// <summary>
/// Service for managing Windows deployment images via PowerShell backend.
/// </summary>
public class ImageService : IImageService
{
    private readonly IPowerShellExecutor _executor;
    private string? _currentMountPath;
    
    /// <inheritdoc />
    public bool IsMounted => !string.IsNullOrEmpty(_currentMountPath);
    
    /// <summary>
    /// Creates a new ImageService.
    /// </summary>
    public ImageService(IPowerShellExecutor executor)
    {
        _executor = executor ?? throw new ArgumentNullException(nameof(executor));
    }
    
    /// <inheritdoc />
    public string? GetCurrentMountPath() => _currentMountPath;
    
    /// <inheritdoc />
    public async Task<MountResult> MountAsync(
        string imagePath, 
        int index = 1, 
        string? mountPath = null, 
        bool readOnly = false,
        IProgress<ProgressInfo>? progress = null,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(imagePath))
            throw new ArgumentException("Image path is required", nameof(imagePath));
        
        if (!File.Exists(imagePath))
            throw new ImageNotFoundException(imagePath);
        
        progress?.Report(new ProgressInfo
        {
            Message = "Mounting image...",
            Percentage = 0,
            IsIndeterminate = true
        });
        
        var parameters = new Dictionary<string, object>
        {
            ["ImagePath"] = imagePath,
            ["Index"] = index,
            ["ReadOnly"] = readOnly
        };
        
        if (!string.IsNullOrEmpty(mountPath))
        {
            parameters["MountPath"] = mountPath;
        }
        
        var result = await _executor.ExecuteCommandAsync(
            "Mount-DeployForgeImage", 
            parameters, 
            cancellationToken);
        
        if (!result.Success)
        {
            throw new MountException(
                $"Failed to mount image: {string.Join(Environment.NewLine, result.Errors)}");
        }
        
        var mountResult = ParseMountResult(result);
        _currentMountPath = mountResult.MountPath;
        
        progress?.Report(new ProgressInfo
        {
            Message = "Image mounted successfully",
            Percentage = 100
        });
        
        return mountResult;
    }
    
    /// <inheritdoc />
    public async Task<DismountResult> UnmountAsync(
        string mountPath, 
        bool saveChanges = false,
        IProgress<ProgressInfo>? progress = null,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(mountPath))
            throw new ArgumentException("Mount path is required", nameof(mountPath));
        
        progress?.Report(new ProgressInfo
        {
            Message = saveChanges ? "Saving changes and unmounting..." : "Unmounting image...",
            Percentage = 0,
            IsIndeterminate = true
        });
        
        var parameters = new Dictionary<string, object>
        {
            ["MountPath"] = mountPath,
            ["Save"] = saveChanges
        };
        
        var result = await _executor.ExecuteCommandAsync(
            "Dismount-DeployForgeImage", 
            parameters, 
            cancellationToken);
        
        if (!result.Success)
        {
            throw new MountException(
                $"Failed to unmount image: {string.Join(Environment.NewLine, result.Errors)}");
        }
        
        var dismountResult = ParseDismountResult(result);
        
        if (dismountResult.Success && _currentMountPath == mountPath)
        {
            _currentMountPath = null;
        }
        
        progress?.Report(new ProgressInfo
        {
            Message = "Image unmounted successfully",
            Percentage = 100
        });
        
        return dismountResult;
    }
    
    /// <inheritdoc />
    public async Task<ImageInfo> GetInfoAsync(string imagePath, int? index = null)
    {
        if (string.IsNullOrWhiteSpace(imagePath))
            throw new ArgumentException("Image path is required", nameof(imagePath));
        
        if (!File.Exists(imagePath))
            throw new ImageNotFoundException(imagePath);
        
        var parameters = new Dictionary<string, object>
        {
            ["ImagePath"] = imagePath
        };
        
        if (index.HasValue)
        {
            parameters["Index"] = index.Value;
        }
        
        var result = await _executor.ExecuteCommandAsync(
            "Get-DeployForgeImageInfo", 
            parameters);
        
        if (!result.Success)
        {
            throw new DismException(
                $"Failed to get image info: {string.Join(Environment.NewLine, result.Errors)}");
        }
        
        return ParseImageInfo(result, imagePath);
    }
    
    /// <inheritdoc />
    public async Task<IEnumerable<ImageFileInfo>> ListFilesAsync(
        string mountPath, 
        string path = "", 
        bool recurse = false)
    {
        if (string.IsNullOrWhiteSpace(mountPath))
            throw new ArgumentException("Mount path is required", nameof(mountPath));
        
        var parameters = new Dictionary<string, object>
        {
            ["MountPath"] = mountPath,
            ["Path"] = path,
            ["Recurse"] = recurse
        };
        
        var result = await _executor.ExecuteCommandAsync(
            "Get-DeployForgeImageFiles", 
            parameters);
        
        if (!result.Success)
        {
            throw new DeployForgeException(
                $"Failed to list files: {string.Join(Environment.NewLine, result.Errors)}");
        }
        
        return ParseFileList(result);
    }
    
    /// <inheritdoc />
    public async Task AddFileAsync(string mountPath, string source, string destination)
    {
        if (string.IsNullOrWhiteSpace(mountPath))
            throw new ArgumentException("Mount path is required", nameof(mountPath));
        if (string.IsNullOrWhiteSpace(source))
            throw new ArgumentException("Source path is required", nameof(source));
        if (string.IsNullOrWhiteSpace(destination))
            throw new ArgumentException("Destination path is required", nameof(destination));
        
        if (!File.Exists(source) && !Directory.Exists(source))
            throw new FileNotFoundException("Source file not found", source);
        
        var parameters = new Dictionary<string, object>
        {
            ["MountPath"] = mountPath,
            ["Source"] = source,
            ["Destination"] = destination
        };
        
        var result = await _executor.ExecuteCommandAsync("Add-DeployForgeFile", parameters);
        
        if (!result.Success)
        {
            throw new DeployForgeException(
                $"Failed to add file: {string.Join(Environment.NewLine, result.Errors)}");
        }
    }
    
    /// <inheritdoc />
    public async Task RemoveFileAsync(string mountPath, string path, bool recurse = false)
    {
        if (string.IsNullOrWhiteSpace(mountPath))
            throw new ArgumentException("Mount path is required", nameof(mountPath));
        if (string.IsNullOrWhiteSpace(path))
            throw new ArgumentException("Path is required", nameof(path));
        
        var parameters = new Dictionary<string, object>
        {
            ["MountPath"] = mountPath,
            ["Path"] = path,
            ["Recurse"] = recurse
        };
        
        var result = await _executor.ExecuteCommandAsync("Remove-DeployForgeFile", parameters);
        
        if (!result.Success)
        {
            throw new DeployForgeException(
                $"Failed to remove file: {string.Join(Environment.NewLine, result.Errors)}");
        }
    }
    
    /// <inheritdoc />
    public async Task ExtractFileAsync(string mountPath, string source, string destination)
    {
        if (string.IsNullOrWhiteSpace(mountPath))
            throw new ArgumentException("Mount path is required", nameof(mountPath));
        if (string.IsNullOrWhiteSpace(source))
            throw new ArgumentException("Source path is required", nameof(source));
        if (string.IsNullOrWhiteSpace(destination))
            throw new ArgumentException("Destination path is required", nameof(destination));
        
        var parameters = new Dictionary<string, object>
        {
            ["MountPath"] = mountPath,
            ["Source"] = source,
            ["Destination"] = destination
        };
        
        var result = await _executor.ExecuteCommandAsync("Copy-DeployForgeFile", parameters);
        
        if (!result.Success)
        {
            throw new DeployForgeException(
                $"Failed to extract file: {string.Join(Environment.NewLine, result.Errors)}");
        }
    }
    
    /// <summary>
    /// Parses the mount result from PowerShell output.
    /// </summary>
    private static MountResult ParseMountResult(PowerShellResult result)
    {
        var mountResult = new MountResult { Success = result.Success };
        
        if (result.Output.FirstOrDefault() is PSObject psObject)
        {
            mountResult.MountPath = GetPropertyValue<string>(psObject, "MountPath") ?? "";
            mountResult.ImagePath = GetPropertyValue<string>(psObject, "ImagePath") ?? "";
            mountResult.Index = GetPropertyValue<int>(psObject, "Index");
            mountResult.ReadOnly = GetPropertyValue<bool>(psObject, "ReadOnly");
            
            var formatStr = GetPropertyValue<string>(psObject, "Format");
            if (Enum.TryParse<ImageFormat>(formatStr, true, out var format))
            {
                mountResult.Format = format;
            }
        }
        
        return mountResult;
    }
    
    /// <summary>
    /// Parses the dismount result from PowerShell output.
    /// </summary>
    private static DismountResult ParseDismountResult(PowerShellResult result)
    {
        var dismountResult = new DismountResult { Success = result.Success };
        
        if (result.Output.FirstOrDefault() is PSObject psObject)
        {
            dismountResult.MountPath = GetPropertyValue<string>(psObject, "MountPath") ?? "";
            dismountResult.ChangesSaved = GetPropertyValue<bool>(psObject, "ChangesSaved");
        }
        
        return dismountResult;
    }
    
    /// <summary>
    /// Parses image info from PowerShell output.
    /// </summary>
    private static ImageInfo ParseImageInfo(PowerShellResult result, string imagePath)
    {
        var info = new ImageInfo
        {
            Path = imagePath,
            FileName = Path.GetFileName(imagePath),
            FileSize = new FileInfo(imagePath).Length
        };
        
        // Determine format from extension
        var ext = Path.GetExtension(imagePath).ToLowerInvariant();
        info.Format = ext switch
        {
            ".wim" => ImageFormat.WIM,
            ".esd" => ImageFormat.ESD,
            ".vhd" => ImageFormat.VHD,
            ".vhdx" => ImageFormat.VHDX,
            ".iso" => ImageFormat.ISO,
            _ => ImageFormat.WIM
        };
        
        foreach (var output in result.Output)
        {
            if (output is PSObject psObject)
            {
                var indexInfo = new ImageIndexInfo
                {
                    Index = GetPropertyValue<int>(psObject, "ImageIndex"),
                    Name = GetPropertyValue<string>(psObject, "ImageName") ?? "",
                    Description = GetPropertyValue<string>(psObject, "ImageDescription") ?? "",
                    Size = GetPropertyValue<long>(psObject, "ImageSize"),
                    Architecture = GetPropertyValue<string>(psObject, "Architecture") ?? "x64",
                    Version = GetPropertyValue<string>(psObject, "Version") ?? ""
                };
                
                var createdStr = GetPropertyValue<string>(psObject, "CreatedTime");
                if (DateTime.TryParse(createdStr, out var created))
                {
                    indexInfo.Created = created;
                }
                
                var modifiedStr = GetPropertyValue<string>(psObject, "ModifiedTime");
                if (DateTime.TryParse(modifiedStr, out var modified))
                {
                    indexInfo.Modified = modified;
                }
                
                info.Indexes.Add(indexInfo);
            }
        }
        
        return info;
    }
    
    /// <summary>
    /// Parses file list from PowerShell output.
    /// </summary>
    private static IEnumerable<ImageFileInfo> ParseFileList(PowerShellResult result)
    {
        var files = new List<ImageFileInfo>();
        
        foreach (var output in result.Output)
        {
            if (output is PSObject psObject)
            {
                var fileInfo = new ImageFileInfo
                {
                    Name = GetPropertyValue<string>(psObject, "Name") ?? "",
                    FullPath = GetPropertyValue<string>(psObject, "FullPath") ?? "",
                    Size = GetPropertyValue<long>(psObject, "Size"),
                    IsDirectory = GetPropertyValue<bool>(psObject, "IsDirectory")
                };
                
                var modifiedStr = GetPropertyValue<string>(psObject, "LastWriteTime");
                if (DateTime.TryParse(modifiedStr, out var modified))
                {
                    fileInfo.LastModified = modified;
                }
                
                files.Add(fileInfo);
            }
        }
        
        return files;
    }
    
    /// <summary>
    /// Gets a property value from a PSObject.
    /// </summary>
    private static T? GetPropertyValue<T>(PSObject psObject, string propertyName)
    {
        var prop = psObject.Properties[propertyName];
        if (prop?.Value == null) return default;
        
        try
        {
            if (typeof(T) == typeof(string))
            {
                return (T)(object)prop.Value.ToString()!;
            }
            
            return (T)Convert.ChangeType(prop.Value, typeof(T));
        }
        catch
        {
            return default;
        }
    }
}
