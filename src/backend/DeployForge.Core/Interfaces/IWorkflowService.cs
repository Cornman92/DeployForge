using DeployForge.Common.Models;

namespace DeployForge.Core.Interfaces;

/// <summary>
/// Service for managing and executing workflows
/// </summary>
public interface IWorkflowService
{
    /// <summary>
    /// Validate a workflow definition
    /// </summary>
    /// <param name="workflow">Workflow to validate</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Validation result with errors</returns>
    Task<OperationResult<List<string>>> ValidateWorkflowAsync(
        WorkflowDefinition workflow,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Execute a workflow
    /// </summary>
    /// <param name="request">Execution request</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Execution result</returns>
    Task<OperationResult<WorkflowExecutionResult>> ExecuteWorkflowAsync(
        ExecuteWorkflowRequest request,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Get predefined workflow templates
    /// </summary>
    /// <param name="tag">Filter by tag</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>List of workflow templates</returns>
    Task<OperationResult<List<WorkflowDefinition>>> GetTemplatesAsync(
        string? tag = null,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Get a specific template by ID
    /// </summary>
    /// <param name="templateId">Template identifier</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Workflow template</returns>
    Task<OperationResult<WorkflowDefinition>> GetTemplateAsync(
        string templateId,
        CancellationToken cancellationToken = default);
}
