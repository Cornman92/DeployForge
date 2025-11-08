using DeployForge.Common.Models;
using DeployForge.Core.Interfaces;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace DeployForge.Api.Controllers;

[ApiController]
[Authorize]
[Route("api/[controller]")]
public class ImageTemplatesController : ControllerBase
{
    private readonly IImageTemplateService _templateService;
    private readonly ILogger<ImageTemplatesController> _logger;

    public ImageTemplatesController(
        IImageTemplateService templateService,
        ILogger<ImageTemplatesController> logger)
    {
        _templateService = templateService;
        _logger = logger;
    }

    /// <summary>
    /// Get all templates
    /// </summary>
    [HttpGet]
    public async Task<ActionResult<List<ImageTemplate>>> GetTemplates(
        [FromQuery] string? tag = null,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Getting templates. Tag: {Tag}", tag);

        var result = await _templateService.GetTemplatesAsync(tag, cancellationToken);

        if (!result.Success)
        {
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Get template by ID
    /// </summary>
    [HttpGet("{templateId}")]
    public async Task<ActionResult<ImageTemplate>> GetTemplate(
        string templateId,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Getting template {TemplateId}", templateId);

        var result = await _templateService.GetTemplateAsync(templateId, cancellationToken);

        if (!result.Success)
        {
            return NotFound(result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Create new template
    /// </summary>
    [HttpPost]
    public async Task<ActionResult<ImageTemplate>> CreateTemplate(
        [FromBody] ImageTemplate template,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Creating template {TemplateName}", template.Name);

        var result = await _templateService.CreateTemplateAsync(template, cancellationToken);

        if (!result.Success)
        {
            return StatusCode(500, result.ErrorMessage);
        }

        return CreatedAtAction(nameof(GetTemplate), new { templateId = result.Data?.Id }, result.Data);
    }

    /// <summary>
    /// Update template
    /// </summary>
    [HttpPut("{templateId}")]
    public async Task<ActionResult<ImageTemplate>> UpdateTemplate(
        string templateId,
        [FromBody] ImageTemplate template,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Updating template {TemplateId}", templateId);

        template.Id = templateId;
        var result = await _templateService.UpdateTemplateAsync(template, cancellationToken);

        if (!result.Success)
        {
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Delete template
    /// </summary>
    [HttpDelete("{templateId}")]
    public async Task<ActionResult> DeleteTemplate(
        string templateId,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Deleting template {TemplateId}", templateId);

        var result = await _templateService.DeleteTemplateAsync(templateId, cancellationToken);

        if (!result.Success)
        {
            return StatusCode(500, result.ErrorMessage);
        }

        return NoContent();
    }

    /// <summary>
    /// Apply template to image
    /// </summary>
    [HttpPost("apply")]
    public async Task<ActionResult<ApplyTemplateResult>> ApplyTemplate(
        [FromBody] ApplyTemplateRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Applying template {TemplateId} to {ImagePath}",
            request.TemplateId, request.ImagePath);

        var result = await _templateService.ApplyTemplateAsync(request, cancellationToken);

        if (!result.Success)
        {
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Export template
    /// </summary>
    [HttpPost("{templateId}/export")]
    public async Task<ActionResult> ExportTemplate(
        string templateId,
        [FromBody] ExportTemplateRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Exporting template {TemplateId} to {Path}",
            templateId, request.DestinationPath);

        var result = await _templateService.ExportTemplateAsync(templateId, request.DestinationPath, cancellationToken);

        if (!result.Success)
        {
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(new { path = result.Data });
    }

    /// <summary>
    /// Import template
    /// </summary>
    [HttpPost("import")]
    public async Task<ActionResult<ImageTemplate>> ImportTemplate(
        [FromBody] ImportTemplateRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Importing template from {Path}", request.FilePath);

        var result = await _templateService.ImportTemplateAsync(request.FilePath, cancellationToken);

        if (!result.Success)
        {
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Validate template
    /// </summary>
    [HttpPost("validate")]
    public async Task<ActionResult<List<string>>> ValidateTemplate(
        [FromBody] ImageTemplate template,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Validating template {TemplateName}", template.Name);

        var result = await _templateService.ValidateTemplateAsync(template, cancellationToken);

        if (!result.Success)
        {
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Get predefined templates
    /// </summary>
    [HttpGet("predefined")]
    public async Task<ActionResult<List<ImageTemplate>>> GetPredefinedTemplates(
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Getting predefined templates");

        var result = await _templateService.GetPredefinedTemplatesAsync(cancellationToken);

        if (!result.Success)
        {
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }
}

public class ExportTemplateRequest
{
    public string DestinationPath { get; set; } = string.Empty;
}

public class ImportTemplateRequest
{
    public string FilePath { get; set; } = string.Empty;
}
