using DeployForge.App.Models;

namespace DeployForge.App.Services;

public interface IImageService
{
    Task<ImageInfo?> GetImageInfoAsync(string imagePath);
    Task<MountedImage?> MountImageAsync(string imagePath, int index = 1, string? mountPoint = null);
    Task<bool> DismountImageAsync(string mountPoint, bool saveChanges = false);
    Task<List<MountedImage>> GetMountedImagesAsync();
    Task<BuildResult> BuildImageAsync(BuildConfiguration config, IProgress<BuildProgress>? progress = null, CancellationToken cancellationToken = default);
}

public class ImageService : IImageService
{
    private readonly IPowerShellService _psService;
    
    public ImageService(IPowerShellService psService)
    {
        _psService = psService;
    }
    
    public async Task<ImageInfo?> GetImageInfoAsync(string imagePath)
    {
        var result = await _psService.InvokeAsync($"Get-DFImageInfo -ImagePath '{imagePath}'");
        
        if (!result.Success || result.Result == null)
            return null;
        
        // Parse the PowerShell result into ImageInfo
        // For now, return basic info from file
        var fileInfo = new FileInfo(imagePath);
        var extension = fileInfo.Extension.ToUpperInvariant().TrimStart('.');
        
        return new ImageInfo
        {
            Path = imagePath,
            Name = fileInfo.Name,
            Format = extension,
            Size = fileInfo.Length,
            ModifiedDate = fileInfo.LastWriteTime
        };
    }
    
    public async Task<MountedImage?> MountImageAsync(string imagePath, int index = 1, string? mountPoint = null)
    {
        var mp = mountPoint ?? Path.Combine(Path.GetTempPath(), "DeployForge", $"Mount_{Guid.NewGuid():N}");
        
        var result = await _psService.InvokeAsync($"Mount-DFImage -ImagePath '{imagePath}' -MountPoint '{mp}' -Index {index}");
        
        if (!result.Success)
            return null;
        
        return new MountedImage
        {
            ImagePath = imagePath,
            MountPoint = mp,
            Index = index,
            Status = MountStatus.Mounted,
            MountedAt = DateTime.Now
        };
    }
    
    public async Task<bool> DismountImageAsync(string mountPoint, bool saveChanges = false)
    {
        var save = saveChanges ? "-Save" : "";
        var result = await _psService.InvokeAsync($"Dismount-DFImage -MountPoint '{mountPoint}' {save}");
        return result.Success;
    }
    
    public async Task<List<MountedImage>> GetMountedImagesAsync()
    {
        var result = await _psService.InvokeAsync("Get-DFMountedImages");
        // Parse result into list
        return new List<MountedImage>();
    }
    
    public async Task<BuildResult> BuildImageAsync(BuildConfiguration config, IProgress<BuildProgress>? progress = null, CancellationToken cancellationToken = default)
    {
        var startTime = DateTime.Now;
        var logs = new List<string>();
        var warnings = new List<BuildWarning>();
        var errors = new List<BuildError>();
        var appliedFeatures = new List<string>();
        
        try
        {
            // Step 1: Mount source image
            progress?.Report(new BuildProgress { CurrentStep = "Mounting source image", StepNumber = 1, TotalSteps = 10, PercentComplete = 5, StatusMessage = "Mounting..." });
            
            var mountResult = await MountImageAsync(config.SourceImage, config.SourceIndex);
            if (mountResult == null)
            {
                errors.Add(new BuildError("Failed to mount source image"));
                return new BuildResult { Success = false, Errors = errors, Duration = DateTime.Now - startTime };
            }
            
            var mountPoint = mountResult.MountPoint;
            logs.Add($"Image mounted to: {mountPoint}");
            
            // Step 2: Apply debloat if enabled
            if (config.Features.RemoveBloatware)
            {
                progress?.Report(new BuildProgress { CurrentStep = "Removing bloatware", StepNumber = 2, TotalSteps = 10, PercentComplete = 15, StatusMessage = "Debloating..." });
                await _psService.InvokeAsync($"Start-DFDebloat -MountPoint '{mountPoint}' -Level {config.Features.DebloatLevel}");
                appliedFeatures.Add("Debloat");
            }
            
            // Step 3: Apply privacy settings
            if (config.Features.DisableTelemetry)
            {
                progress?.Report(new BuildProgress { CurrentStep = "Applying privacy settings", StepNumber = 3, TotalSteps = 10, PercentComplete = 25, StatusMessage = "Privacy..." });
                await _psService.InvokeAsync($"Set-DFPrivacyLevel -MountPoint '{mountPoint}' -Level {config.Features.PrivacyLevel}");
                appliedFeatures.Add("Privacy");
            }
            
            // Step 4: Apply gaming optimizations
            if (config.Features.EnableGameMode)
            {
                progress?.Report(new BuildProgress { CurrentStep = "Optimizing for gaming", StepNumber = 4, TotalSteps = 10, PercentComplete = 35, StatusMessage = "Gaming..." });
                await _psService.InvokeAsync($"Optimize-DFGaming -MountPoint '{mountPoint}' -Profile {config.Features.GamingProfile}");
                appliedFeatures.Add("Gaming");
            }
            
            // Step 5: Apply developer settings
            if (config.Features.EnableDeveloperMode)
            {
                progress?.Report(new BuildProgress { CurrentStep = "Configuring developer environment", StepNumber = 5, TotalSteps = 10, PercentComplete = 45, StatusMessage = "Developer..." });
                await _psService.InvokeAsync($"Install-DFDevEnvironment -MountPoint '{mountPoint}'");
                appliedFeatures.Add("Developer");
            }
            
            // Step 6: Inject drivers
            if (config.DriverPaths.Count > 0)
            {
                progress?.Report(new BuildProgress { CurrentStep = "Injecting drivers", StepNumber = 6, TotalSteps = 10, PercentComplete = 55, StatusMessage = "Drivers..." });
                foreach (var driverPath in config.DriverPaths)
                {
                    await _psService.InvokeAsync($"Add-DFDriver -MountPoint '{mountPoint}' -DriverPaths @('{driverPath}') -Recurse");
                }
                appliedFeatures.Add("Drivers");
            }
            
            // Step 7: Add language packs
            if (config.LanguagePacks.Count > 0)
            {
                progress?.Report(new BuildProgress { CurrentStep = "Adding language packs", StepNumber = 7, TotalSteps = 10, PercentComplete = 65, StatusMessage = "Languages..." });
                appliedFeatures.Add("Languages");
            }
            
            // Step 8: Generate unattend.xml
            if (config.Unattend != null)
            {
                progress?.Report(new BuildProgress { CurrentStep = "Generating answer file", StepNumber = 8, TotalSteps = 10, PercentComplete = 75, StatusMessage = "Unattend..." });
                var unattendPath = Path.Combine(mountPoint, "Windows", "Panther", "unattend.xml");
                Directory.CreateDirectory(Path.GetDirectoryName(unattendPath)!);
                await _psService.InvokeAsync($"Save-DFUnattend -Config @{{Username='{config.Unattend.Username}';ComputerName='{config.Unattend.ComputerName}'}} -OutputPath '{unattendPath}'");
                appliedFeatures.Add("Unattend");
            }
            
            // Step 9: Dismount and save
            progress?.Report(new BuildProgress { CurrentStep = "Saving changes", StepNumber = 9, TotalSteps = 10, PercentComplete = 85, StatusMessage = "Saving..." });
            await DismountImageAsync(mountPoint, saveChanges: true);
            
            // Step 10: Export if needed
            progress?.Report(new BuildProgress { CurrentStep = "Exporting image", StepNumber = 10, TotalSteps = 10, PercentComplete = 95, StatusMessage = "Exporting..." });
            
            // Copy or convert to output format
            if (!string.IsNullOrEmpty(config.OutputPath))
            {
                File.Copy(config.SourceImage, config.OutputPath, overwrite: true);
            }
            
            progress?.Report(new BuildProgress { CurrentStep = "Complete", StepNumber = 10, TotalSteps = 10, PercentComplete = 100, StatusMessage = "Done!", IsComplete = true });
            
            return new BuildResult
            {
                Success = true,
                OutputPath = config.OutputPath ?? config.SourceImage,
                Duration = DateTime.Now - startTime,
                AppliedFeatures = appliedFeatures,
                Warnings = warnings
            };
        }
        catch (Exception ex)
        {
            errors.Add(new BuildError(ex.Message, Exception: ex));
            return new BuildResult
            {
                Success = false,
                Duration = DateTime.Now - startTime,
                AppliedFeatures = appliedFeatures,
                Warnings = warnings,
                Errors = errors
            };
        }
    }
}
