using DeployForge.Common.Models;

namespace DeployForge.Core.Interfaces;

/// <summary>
/// Service for deployment operations (ISO creation, USB, autounattend)
/// </summary>
public interface IDeploymentService
{
    /// <summary>
    /// Create bootable ISO image
    /// </summary>
    /// <param name="request">ISO creation request</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Creation result</returns>
    Task<OperationResult<MediaCreationResult>> CreateISOAsync(
        ISOCreationRequest request,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Create bootable USB drive
    /// </summary>
    /// <param name="request">USB creation request</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Creation result</returns>
    Task<OperationResult<MediaCreationResult>> CreateBootableUSBAsync(
        BootableUSBRequest request,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Generate autounattend.xml file
    /// </summary>
    /// <param name="config">Autounattend configuration</param>
    /// <param name="outputPath">Output file path</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Operation result</returns>
    Task<OperationResult<string>> GenerateAutounattendAsync(
        AutounattendConfig config,
        string outputPath,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Get available USB drives
    /// </summary>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>List of removable drives</returns>
    Task<OperationResult<List<DriveInfo>>> GetRemovableDrivesAsync(
        CancellationToken cancellationToken = default);
}

/// <summary>
/// Information about a drive
/// </summary>
public class DriveInfo
{
    public string DriveLetter { get; set; } = string.Empty;
    public string VolumeLabel { get; set; } = string.Empty;
    public long TotalSize { get; set; }
    public long FreeSpace { get; set; }
    public string FileSystem { get; set; } = string.Empty;
    public bool IsReady { get; set; }
}
