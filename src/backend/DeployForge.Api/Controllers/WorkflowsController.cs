using DeployForge.Common.Models;
using DeployForge.Core.Interfaces;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace DeployForge.Api.Controllers;

[ApiController]
[Authorize]
[Route("api/[controller]")]
public class WorkflowsController : ControllerBase
{
    private readonly IWorkflowService _workflowService;
    private readonly ILogger<WorkflowsController> _logger;

    public WorkflowsController(
        IWorkflowService workflowService,
        ILogger<WorkflowsController> logger)
    {
        _workflowService = workflowService;
        _logger = logger;
    }

    /// <summary>
    /// Get workflow templates
    /// </summary>
    [HttpGet("templates")]
    public async Task<ActionResult<List<WorkflowDefinition>>> GetTemplates(
        [FromQuery] string? tag = null,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Getting workflow templates, tag filter: {Tag}", tag);

        var result = await _workflowService.GetTemplatesAsync(tag, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to get templates: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Get a specific template by ID
    /// </summary>
    [HttpGet("templates/{templateId}")]
    public async Task<ActionResult<WorkflowDefinition>> GetTemplate(
        string templateId,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Getting workflow template {TemplateId}", templateId);

        var result = await _workflowService.GetTemplateAsync(templateId, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to get template: {Error}", result.ErrorMessage);
            return NotFound(result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Validate a workflow definition
    /// </summary>
    [HttpPost("validate")]
    public async Task<ActionResult<List<string>>> ValidateWorkflow(
        [FromBody] WorkflowDefinition workflow,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Validating workflow: {WorkflowName}", workflow.Name);

        var result = await _workflowService.ValidateWorkflowAsync(workflow, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to validate workflow: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        if (result.Data != null && result.Data.Any())
        {
            return Ok(new { valid = false, errors = result.Data });
        }

        return Ok(new { valid = true, errors = new List<string>() });
    }

    /// <summary>
    /// Execute a workflow
    /// </summary>
    [HttpPost("execute")]
    public async Task<ActionResult<WorkflowExecutionResult>> ExecuteWorkflow(
        [FromBody] ExecuteWorkflowRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Executing workflow: {WorkflowName} on {ImagePath} (DryRun: {DryRun})",
            request.Workflow.Name, request.ImagePath, request.DryRun);

        if (string.IsNullOrWhiteSpace(request.ImagePath))
        {
            return BadRequest("Image path is required");
        }

        if (string.IsNullOrWhiteSpace(request.MountPath))
        {
            return BadRequest("Mount path is required");
        }

        var result = await _workflowService.ExecuteWorkflowAsync(request, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to execute workflow: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }
}
