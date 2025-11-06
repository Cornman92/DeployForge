using DeployForge.Common.Models;

namespace DeployForge.Core.Interfaces;

/// <summary>
/// Service for validating images and deployments
/// </summary>
public interface IValidationService
{
    /// <summary>
    /// Performs comprehensive validation on an image
    /// </summary>
    /// <param name="request">Validation request</param>
    /// <param name="options">Validation options</param>
    /// <param name="progress">Progress reporter</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Validation result</returns>
    Task<OperationResult<ValidationResult>> ValidateImageAsync(
        ValidateImageRequest request,
        ValidationOptions? options = null,
        IProgress<ProgressReport>? progress = null,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Validates deployment readiness
    /// </summary>
    /// <param name="request">Deployment validation request</param>
    /// <param name="progress">Progress reporter</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Validation result</returns>
    Task<OperationResult<ValidationResult>> ValidateDeploymentReadinessAsync(
        ValidateDeploymentRequest request,
        IProgress<ProgressReport>? progress = null,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Validates image integrity (checksum, file structure, etc.)
    /// </summary>
    /// <param name="imagePath">Path to the image</param>
    /// <param name="deepValidation">Whether to perform deep validation</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Validation result</returns>
    Task<OperationResult<ValidationCheck>> ValidateImageIntegrityAsync(
        string imagePath,
        bool deepValidation = false,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Validates boot files and configuration
    /// </summary>
    /// <param name="request">Boot files validation request</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Validation result</returns>
    Task<OperationResult<ValidationCheck>> ValidateBootFilesAsync(
        ValidateBootFilesRequest request,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Validates component dependencies
    /// </summary>
    /// <param name="request">Component dependencies validation request</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Validation result</returns>
    Task<OperationResult<ValidationCheck>> ValidateComponentDependenciesAsync(
        ValidateComponentDependenciesRequest request,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Validates registry consistency
    /// </summary>
    /// <param name="mountPath">Mount path of the image</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Validation result</returns>
    Task<OperationResult<ValidationCheck>> ValidateRegistryConsistencyAsync(
        string mountPath,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Validates driver integrity and signing
    /// </summary>
    /// <param name="mountPath">Mount path of the image</param>
    /// <param name="checkSignatures">Whether to verify driver signatures</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Validation result</returns>
    Task<OperationResult<ValidationCheck>> ValidateDriversAsync(
        string mountPath,
        bool checkSignatures = true,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Validates available disk space for operations
    /// </summary>
    /// <param name="imagePath">Path to the image</param>
    /// <param name="requiredOperations">List of operations that will be performed</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Validation result</returns>
    Task<OperationResult<ValidationCheck>> ValidateDiskSpaceAsync(
        string imagePath,
        List<string> requiredOperations,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Validates file system consistency
    /// </summary>
    /// <param name="mountPath">Mount path of the image</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Validation result</returns>
    Task<OperationResult<ValidationCheck>> ValidateFileSystemAsync(
        string mountPath,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Performs pre-flight system checks
    /// </summary>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Pre-flight check result</returns>
    Task<OperationResult<PreFlightCheckResult>> PerformPreFlightChecksAsync(
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Validates that required tools and dependencies are available
    /// </summary>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Validation result</returns>
    Task<OperationResult<ValidationCheck>> ValidateSystemRequirementsAsync(
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Generates a detailed validation report
    /// </summary>
    /// <param name="validationResult">Validation result to generate report from</param>
    /// <param name="outputPath">Path to save the report</param>
    /// <param name="format">Report format (JSON, HTML, TXT)</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Path to the generated report</returns>
    Task<OperationResult<string>> GenerateValidationReportAsync(
        ValidationResult validationResult,
        string outputPath,
        string format = "JSON",
        CancellationToken cancellationToken = default);
}
