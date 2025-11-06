using DeployForge.Common.Models;
using DeployForge.Core.Interfaces;
using Microsoft.AspNetCore.Mvc;

namespace DeployForge.Api.Controllers;

/// <summary>
/// Controller for managing batch operations
/// </summary>
[ApiController]
[Route("api/[controller]")]
[Produces("application/json")]
public class BatchOperationsController : ControllerBase
{
    private readonly IBatchOperationService _batchOperationService;
    private readonly ILogger<BatchOperationsController> _logger;

    public BatchOperationsController(
        IBatchOperationService batchOperationService,
        ILogger<BatchOperationsController> logger)
    {
        _batchOperationService = batchOperationService;
        _logger = logger;
    }

    /// <summary>
    /// Creates a new batch operation
    /// </summary>
    /// <param name="request">Batch operation request</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Created batch operation</returns>
    [HttpPost]
    [ProducesResponseType(typeof(BatchOperation), StatusCodes.Status201Created)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<BatchOperation>> CreateBatchOperation(
        [FromBody] CreateBatchOperationRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Creating batch operation: {Name} ({Type})", request.Name, request.Type);

        var result = await _batchOperationService.CreateBatchOperationAsync(request, cancellationToken);

        if (!result.Success)
        {
            return BadRequest(result.ErrorMessage);
        }

        return CreatedAtAction(
            nameof(GetBatchOperation),
            new { operationId = result.Data!.Id },
            result.Data);
    }

    /// <summary>
    /// Gets a specific batch operation
    /// </summary>
    /// <param name="operationId">Batch operation ID</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Batch operation</returns>
    [HttpGet("{operationId}")]
    [ProducesResponseType(typeof(BatchOperation), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<BatchOperation>> GetBatchOperation(
        string operationId,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Getting batch operation: {OperationId}", operationId);

        var result = await _batchOperationService.GetBatchOperationAsync(operationId, cancellationToken);

        if (!result.Success)
        {
            return NotFound(result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Queries batch operations with filtering
    /// </summary>
    /// <param name="query">Query parameters</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Query results</returns>
    [HttpPost("query")]
    [ProducesResponseType(typeof(BatchOperationQueryResult), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<BatchOperationQueryResult>> QueryBatchOperations(
        [FromBody] BatchOperationQuery query,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Querying batch operations");

        var result = await _batchOperationService.QueryBatchOperationsAsync(query, cancellationToken);

        if (!result.Success)
        {
            return BadRequest(result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Starts a batch operation
    /// </summary>
    /// <param name="operationId">Batch operation ID</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Operation result</returns>
    [HttpPost("{operationId}/start")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult> StartBatchOperation(
        string operationId,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Starting batch operation: {OperationId}", operationId);

        var result = await _batchOperationService.StartBatchOperationAsync(operationId, cancellationToken);

        if (!result.Success)
        {
            return BadRequest(result.ErrorMessage);
        }

        return NoContent();
    }

    /// <summary>
    /// Pauses a running batch operation
    /// </summary>
    /// <param name="operationId">Batch operation ID</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Operation result</returns>
    [HttpPost("{operationId}/pause")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult> PauseBatchOperation(
        string operationId,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Pausing batch operation: {OperationId}", operationId);

        var result = await _batchOperationService.PauseBatchOperationAsync(operationId, cancellationToken);

        if (!result.Success)
        {
            return BadRequest(result.ErrorMessage);
        }

        return NoContent();
    }

    /// <summary>
    /// Resumes a paused batch operation
    /// </summary>
    /// <param name="operationId">Batch operation ID</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Operation result</returns>
    [HttpPost("{operationId}/resume")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult> ResumeBatchOperation(
        string operationId,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Resuming batch operation: {OperationId}", operationId);

        var result = await _batchOperationService.ResumeBatchOperationAsync(operationId, cancellationToken);

        if (!result.Success)
        {
            return BadRequest(result.ErrorMessage);
        }

        return NoContent();
    }

    /// <summary>
    /// Cancels a batch operation
    /// </summary>
    /// <param name="operationId">Batch operation ID</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Operation result</returns>
    [HttpPost("{operationId}/cancel")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult> CancelBatchOperation(
        string operationId,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Cancelling batch operation: {OperationId}", operationId);

        var result = await _batchOperationService.CancelBatchOperationAsync(operationId, cancellationToken);

        if (!result.Success)
        {
            return BadRequest(result.ErrorMessage);
        }

        return NoContent();
    }

    /// <summary>
    /// Deletes a batch operation
    /// </summary>
    /// <param name="operationId">Batch operation ID</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Operation result</returns>
    [HttpDelete("{operationId}")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult> DeleteBatchOperation(
        string operationId,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Deleting batch operation: {OperationId}", operationId);

        var result = await _batchOperationService.DeleteBatchOperationAsync(operationId, cancellationToken);

        if (!result.Success)
        {
            return BadRequest(result.ErrorMessage);
        }

        return NoContent();
    }

    /// <summary>
    /// Gets the current status of a batch operation
    /// </summary>
    /// <param name="operationId">Batch operation ID</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Batch operation status</returns>
    [HttpGet("{operationId}/status")]
    [ProducesResponseType(typeof(BatchOperation), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<BatchOperation>> GetBatchOperationStatus(
        string operationId,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Getting batch operation status: {OperationId}", operationId);

        var result = await _batchOperationService.GetBatchOperationStatusAsync(operationId, cancellationToken);

        if (!result.Success)
        {
            return NotFound(result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Gets batch operation statistics
    /// </summary>
    /// <param name="startDate">Start date filter</param>
    /// <param name="endDate">End date filter</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Batch operation statistics</returns>
    [HttpGet("statistics")]
    [ProducesResponseType(typeof(BatchOperationStatistics), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<BatchOperationStatistics>> GetStatistics(
        [FromQuery] DateTime? startDate = null,
        [FromQuery] DateTime? endDate = null,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Getting batch operation statistics");

        var result = await _batchOperationService.GetStatisticsAsync(startDate, endDate, cancellationToken);

        if (!result.Success)
        {
            return StatusCode(StatusCodes.Status500InternalServerError, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Retries failed images in a batch operation
    /// </summary>
    /// <param name="operationId">Batch operation ID</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Operation result</returns>
    [HttpPost("{operationId}/retry")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult> RetryFailedImages(
        string operationId,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Retrying failed images for batch operation: {OperationId}", operationId);

        var result = await _batchOperationService.RetryFailedImagesAsync(operationId, cancellationToken);

        if (!result.Success)
        {
            return BadRequest(result.ErrorMessage);
        }

        return NoContent();
    }

    /// <summary>
    /// Gets active batch operations
    /// </summary>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>List of active batch operations</returns>
    [HttpGet("active")]
    [ProducesResponseType(typeof(List<BatchOperation>), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<List<BatchOperation>>> GetActiveBatchOperations(
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Getting active batch operations");

        var result = await _batchOperationService.GetActiveBatchOperationsAsync(cancellationToken);

        if (!result.Success)
        {
            return StatusCode(StatusCodes.Status500InternalServerError, result.ErrorMessage);
        }

        return Ok(result.Data);
    }
}
