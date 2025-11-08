using DeployForge.Common.Models;
using DeployForge.Core.Interfaces;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace DeployForge.Api.Controllers;

/// <summary>
/// Controller for image and deployment validation
/// </summary>
[ApiController]
[Authorize]
[Route("api/[controller]")]
[Produces("application/json")]
public class ValidationController : ControllerBase
{
    private readonly IValidationService _validationService;
    private readonly IProgressService _progressService;
    private readonly ILogger<ValidationController> _logger;

    public ValidationController(
        IValidationService validationService,
        IProgressService progressService,
        ILogger<ValidationController> logger)
    {
        _validationService = validationService;
        _progressService = progressService;
        _logger = logger;
    }

    /// <summary>
    /// Validates an image with comprehensive checks
    /// </summary>
    /// <param name="request">Validation request</param>
    /// <param name="operationId">Operation ID for progress tracking</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Validation result</returns>
    [HttpPost("validate-image")]
    [ProducesResponseType(typeof(ValidationResult), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<ValidationResult>> ValidateImage(
        [FromBody] ValidateImageRequest request,
        [FromQuery] string? operationId = null,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Validating image: {ImagePath}", request.ImagePath);

        var opId = operationId ?? Guid.NewGuid().ToString();
        var progress = _progressService.CreateProgressReporter(opId);

        var result = await _validationService.ValidateImageAsync(
            request,
            new ValidationOptions(),
            progress,
            cancellationToken);

        if (!result.Success)
        {
            return BadRequest(result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Validates deployment readiness
    /// </summary>
    /// <param name="request">Deployment validation request</param>
    /// <param name="operationId">Operation ID for progress tracking</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Validation result</returns>
    [HttpPost("validate-deployment")]
    [ProducesResponseType(typeof(ValidationResult), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<ValidationResult>> ValidateDeployment(
        [FromBody] ValidateDeploymentRequest request,
        [FromQuery] string? operationId = null,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Validating deployment readiness for: {ImagePath} via {Method}",
            request.ImagePath, request.DeploymentMethod);

        var opId = operationId ?? Guid.NewGuid().ToString();
        var progress = _progressService.CreateProgressReporter(opId);

        var result = await _validationService.ValidateDeploymentReadinessAsync(
            request,
            progress,
            cancellationToken);

        if (!result.Success)
        {
            return BadRequest(result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Validates image integrity
    /// </summary>
    /// <param name="imagePath">Path to the image</param>
    /// <param name="deepValidation">Perform deep validation</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Validation check result</returns>
    [HttpPost("validate-integrity")]
    [ProducesResponseType(typeof(ValidationCheck), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<ValidationCheck>> ValidateIntegrity(
        [FromQuery] string imagePath,
        [FromQuery] bool deepValidation = false,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Validating image integrity: {ImagePath} (deep: {Deep})",
            imagePath, deepValidation);

        var result = await _validationService.ValidateImageIntegrityAsync(
            imagePath,
            deepValidation,
            cancellationToken);

        if (!result.Success)
        {
            return BadRequest(result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Validates boot files
    /// </summary>
    /// <param name="request">Boot files validation request</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Validation check result</returns>
    [HttpPost("validate-bootfiles")]
    [ProducesResponseType(typeof(ValidationCheck), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<ValidationCheck>> ValidateBootFiles(
        [FromBody] ValidateBootFilesRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Validating boot files for: {MountPath}", request.MountPath);

        var result = await _validationService.ValidateBootFilesAsync(request, cancellationToken);

        if (!result.Success)
        {
            return BadRequest(result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Validates component dependencies
    /// </summary>
    /// <param name="request">Component dependencies validation request</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Validation check result</returns>
    [HttpPost("validate-components")]
    [ProducesResponseType(typeof(ValidationCheck), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<ValidationCheck>> ValidateComponents(
        [FromBody] ValidateComponentDependenciesRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Validating component dependencies for: {MountPath}", request.MountPath);

        var result = await _validationService.ValidateComponentDependenciesAsync(request, cancellationToken);

        if (!result.Success)
        {
            return BadRequest(result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Validates registry consistency
    /// </summary>
    /// <param name="mountPath">Mount path</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Validation check result</returns>
    [HttpPost("validate-registry")]
    [ProducesResponseType(typeof(ValidationCheck), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<ValidationCheck>> ValidateRegistry(
        [FromQuery] string mountPath,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Validating registry consistency for: {MountPath}", mountPath);

        var result = await _validationService.ValidateRegistryConsistencyAsync(mountPath, cancellationToken);

        if (!result.Success)
        {
            return BadRequest(result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Validates drivers
    /// </summary>
    /// <param name="mountPath">Mount path</param>
    /// <param name="checkSignatures">Check driver signatures</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Validation check result</returns>
    [HttpPost("validate-drivers")]
    [ProducesResponseType(typeof(ValidationCheck), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<ValidationCheck>> ValidateDrivers(
        [FromQuery] string mountPath,
        [FromQuery] bool checkSignatures = true,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Validating drivers for: {MountPath} (checkSignatures: {Check})",
            mountPath, checkSignatures);

        var result = await _validationService.ValidateDriversAsync(
            mountPath,
            checkSignatures,
            cancellationToken);

        if (!result.Success)
        {
            return BadRequest(result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Validates available disk space
    /// </summary>
    /// <param name="imagePath">Image path</param>
    /// <param name="operations">Required operations</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Validation check result</returns>
    [HttpPost("validate-diskspace")]
    [ProducesResponseType(typeof(ValidationCheck), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<ValidationCheck>> ValidateDiskSpace(
        [FromQuery] string imagePath,
        [FromBody] List<string>? operations = null,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Validating disk space for: {ImagePath}", imagePath);

        var result = await _validationService.ValidateDiskSpaceAsync(
            imagePath,
            operations ?? new List<string>(),
            cancellationToken);

        if (!result.Success)
        {
            return BadRequest(result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Validates file system
    /// </summary>
    /// <param name="mountPath">Mount path</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Validation check result</returns>
    [HttpPost("validate-filesystem")]
    [ProducesResponseType(typeof(ValidationCheck), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<ValidationCheck>> ValidateFileSystem(
        [FromQuery] string mountPath,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Validating file system for: {MountPath}", mountPath);

        var result = await _validationService.ValidateFileSystemAsync(mountPath, cancellationToken);

        if (!result.Success)
        {
            return BadRequest(result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Performs pre-flight system checks
    /// </summary>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Pre-flight check result</returns>
    [HttpGet("preflight")]
    [ProducesResponseType(typeof(PreFlightCheckResult), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<PreFlightCheckResult>> PreFlightChecks(
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Performing pre-flight system checks");

        var result = await _validationService.PerformPreFlightChecksAsync(cancellationToken);

        if (!result.Success)
        {
            return StatusCode(StatusCodes.Status500InternalServerError, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Validates system requirements
    /// </summary>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Validation check result</returns>
    [HttpGet("system-requirements")]
    [ProducesResponseType(typeof(ValidationCheck), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<ValidationCheck>> ValidateSystemRequirements(
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Validating system requirements");

        var result = await _validationService.ValidateSystemRequirementsAsync(cancellationToken);

        if (!result.Success)
        {
            return StatusCode(StatusCodes.Status500InternalServerError, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Generates a validation report
    /// </summary>
    /// <param name="validationResult">Validation result</param>
    /// <param name="outputPath">Output path</param>
    /// <param name="format">Report format (JSON, HTML, TXT)</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Path to generated report</returns>
    [HttpPost("generate-report")]
    [ProducesResponseType(typeof(string), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult> GenerateReport(
        [FromBody] ValidationResult validationResult,
        [FromQuery] string outputPath,
        [FromQuery] string format = "JSON",
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Generating validation report in {Format} format to {Path}",
            format, outputPath);

        var result = await _validationService.GenerateValidationReportAsync(
            validationResult,
            outputPath,
            format,
            cancellationToken);

        if (!result.Success)
        {
            return BadRequest(result.ErrorMessage);
        }

        return Ok(new { ReportPath = result.Data });
    }
}
