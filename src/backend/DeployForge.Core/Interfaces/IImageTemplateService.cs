using DeployForge.Common.Models;

namespace DeployForge.Core.Interfaces;

/// <summary>
/// Service for managing image templates
/// </summary>
public interface IImageTemplateService
{
    /// <summary>
    /// Get all templates
    /// </summary>
    Task<OperationResult<List<ImageTemplate>>> GetTemplatesAsync(string? tag = null, CancellationToken cancellationToken = default);

    /// <summary>
    /// Get template by ID
    /// </summary>
    Task<OperationResult<ImageTemplate>> GetTemplateAsync(string templateId, CancellationToken cancellationToken = default);

    /// <summary>
    /// Create new template
    /// </summary>
    Task<OperationResult<ImageTemplate>> CreateTemplateAsync(ImageTemplate template, CancellationToken cancellationToken = default);

    /// <summary>
    /// Update existing template
    /// </summary>
    Task<OperationResult<ImageTemplate>> UpdateTemplateAsync(ImageTemplate template, CancellationToken cancellationToken = default);

    /// <summary>
    /// Delete template
    /// </summary>
    Task<OperationResult> DeleteTemplateAsync(string templateId, CancellationToken cancellationToken = default);

    /// <summary>
    /// Apply template to an image
    /// </summary>
    Task<OperationResult<ApplyTemplateResult>> ApplyTemplateAsync(ApplyTemplateRequest request, CancellationToken cancellationToken = default);

    /// <summary>
    /// Export template to JSON file
    /// </summary>
    Task<OperationResult<string>> ExportTemplateAsync(string templateId, string destinationPath, CancellationToken cancellationToken = default);

    /// <summary>
    /// Import template from JSON file
    /// </summary>
    Task<OperationResult<ImageTemplate>> ImportTemplateAsync(string filePath, CancellationToken cancellationToken = default);

    /// <summary>
    /// Validate template
    /// </summary>
    Task<OperationResult<List<string>>> ValidateTemplateAsync(ImageTemplate template, CancellationToken cancellationToken = default);

    /// <summary>
    /// Get predefined templates
    /// </summary>
    Task<OperationResult<List<ImageTemplate>>> GetPredefinedTemplatesAsync(CancellationToken cancellationToken = default);
}
