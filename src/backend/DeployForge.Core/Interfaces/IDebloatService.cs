using DeployForge.Common.Models;

namespace DeployForge.Core.Interfaces;

/// <summary>
/// Service for debloating Windows images
/// </summary>
public interface IDebloatService
{
    /// <summary>
    /// Get available debloat presets
    /// </summary>
    /// <param name="level">Filter by debloat level</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>List of presets</returns>
    Task<OperationResult<List<DebloatPreset>>> GetPresetsAsync(
        DebloatLevel? level = null,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Get a specific preset by ID
    /// </summary>
    /// <param name="presetId">Preset identifier</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Debloat preset</returns>
    Task<OperationResult<DebloatPreset>> GetPresetAsync(
        string presetId,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Analyze impact of applying a debloat preset
    /// </summary>
    /// <param name="request">Debloat request (dry run)</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Analysis result</returns>
    Task<OperationResult<DebloatAnalysis>> AnalyzeImpactAsync(
        ApplyDebloatRequest request,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Apply a debloat preset to an image
    /// </summary>
    /// <param name="request">Debloat request</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Debloat result</returns>
    Task<OperationResult<DebloatResult>> ApplyPresetAsync(
        ApplyDebloatRequest request,
        CancellationToken cancellationToken = default);
}
