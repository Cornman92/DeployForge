using DeployForge.Common.Models;

namespace DeployForge.Core.Interfaces;

/// <summary>
/// Service for managing batch operations on multiple images
/// </summary>
public interface IBatchOperationService
{
    /// <summary>
    /// Creates a new batch operation
    /// </summary>
    /// <param name="request">Batch operation request</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Created batch operation</returns>
    Task<OperationResult<BatchOperation>> CreateBatchOperationAsync(
        CreateBatchOperationRequest request,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Gets a specific batch operation
    /// </summary>
    /// <param name="operationId">Batch operation ID</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Batch operation</returns>
    Task<OperationResult<BatchOperation>> GetBatchOperationAsync(
        string operationId,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Queries batch operations with filtering
    /// </summary>
    /// <param name="query">Query parameters</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Query results</returns>
    Task<OperationResult<BatchOperationQueryResult>> QueryBatchOperationsAsync(
        BatchOperationQuery query,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Starts a batch operation
    /// </summary>
    /// <param name="operationId">Batch operation ID</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Operation result</returns>
    Task<OperationResult> StartBatchOperationAsync(
        string operationId,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Pauses a running batch operation
    /// </summary>
    /// <param name="operationId">Batch operation ID</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Operation result</returns>
    Task<OperationResult> PauseBatchOperationAsync(
        string operationId,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Resumes a paused batch operation
    /// </summary>
    /// <param name="operationId">Batch operation ID</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Operation result</returns>
    Task<OperationResult> ResumeBatchOperationAsync(
        string operationId,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Cancels a batch operation
    /// </summary>
    /// <param name="operationId">Batch operation ID</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Operation result</returns>
    Task<OperationResult> CancelBatchOperationAsync(
        string operationId,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Deletes a batch operation
    /// </summary>
    /// <param name="operationId">Batch operation ID</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Operation result</returns>
    Task<OperationResult> DeleteBatchOperationAsync(
        string operationId,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Gets the current status and progress of a batch operation
    /// </summary>
    /// <param name="operationId">Batch operation ID</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Batch operation with current status</returns>
    Task<OperationResult<BatchOperation>> GetBatchOperationStatusAsync(
        string operationId,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Gets batch operation statistics
    /// </summary>
    /// <param name="startDate">Start date filter</param>
    /// <param name="endDate">End date filter</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Batch operation statistics</returns>
    Task<OperationResult<BatchOperationStatistics>> GetStatisticsAsync(
        DateTime? startDate = null,
        DateTime? endDate = null,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Retries failed images in a batch operation
    /// </summary>
    /// <param name="operationId">Batch operation ID</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Operation result</returns>
    Task<OperationResult> RetryFailedImagesAsync(
        string operationId,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Gets active (running or queued) batch operations
    /// </summary>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>List of active batch operations</returns>
    Task<OperationResult<List<BatchOperation>>> GetActiveBatchOperationsAsync(
        CancellationToken cancellationToken = default);
}
