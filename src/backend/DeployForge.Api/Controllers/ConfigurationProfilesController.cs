using DeployForge.Common.Models;
using DeployForge.Core.Interfaces;
using Microsoft.AspNetCore.Mvc;

namespace DeployForge.Api.Controllers;

/// <summary>
/// Controller for managing configuration profiles
/// </summary>
[ApiController]
[Route("api/[controller]")]
[Produces("application/json")]
public class ConfigurationProfilesController : ControllerBase
{
    private readonly IConfigurationProfileService _profileService;
    private readonly ILogger<ConfigurationProfilesController> _logger;

    public ConfigurationProfilesController(
        IConfigurationProfileService profileService,
        ILogger<ConfigurationProfilesController> logger)
    {
        _profileService = profileService;
        _logger = logger;
    }

    /// <summary>
    /// Gets all configuration profiles
    /// </summary>
    /// <param name="includeShared">Include shared profiles</param>
    /// <param name="tag">Filter by tag</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>List of configuration profiles</returns>
    [HttpGet]
    [ProducesResponseType(typeof(List<ConfigurationProfile>), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<List<ConfigurationProfile>>> GetProfiles(
        [FromQuery] bool includeShared = true,
        [FromQuery] string? tag = null,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Getting configuration profiles (includeShared: {IncludeShared}, tag: {Tag})",
            includeShared, tag ?? "none");

        var result = await _profileService.GetProfilesAsync(includeShared, tag, cancellationToken);

        if (!result.Success)
        {
            return StatusCode(StatusCodes.Status500InternalServerError, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Gets a specific configuration profile
    /// </summary>
    /// <param name="profileId">Profile identifier</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>The configuration profile</returns>
    [HttpGet("{profileId}")]
    [ProducesResponseType(typeof(ConfigurationProfile), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<ConfigurationProfile>> GetProfile(
        string profileId,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Getting configuration profile: {ProfileId}", profileId);

        var result = await _profileService.GetProfileAsync(profileId, cancellationToken);

        if (!result.Success)
        {
            return NotFound(result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Gets the default configuration profile
    /// </summary>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>The default configuration profile</returns>
    [HttpGet("default")]
    [ProducesResponseType(typeof(ConfigurationProfile), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<ConfigurationProfile>> GetDefaultProfile(
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Getting default configuration profile");

        var result = await _profileService.GetDefaultProfileAsync(cancellationToken);

        if (!result.Success)
        {
            return StatusCode(StatusCodes.Status500InternalServerError, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Creates a new configuration profile
    /// </summary>
    /// <param name="request">Create profile request</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>The created profile</returns>
    [HttpPost]
    [ProducesResponseType(typeof(ConfigurationProfile), StatusCodes.Status201Created)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<ConfigurationProfile>> CreateProfile(
        [FromBody] CreateProfileRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Creating configuration profile: {Name}", request.Profile.Name);

        var result = await _profileService.CreateProfileAsync(request.Profile, cancellationToken);

        if (!result.Success)
        {
            return BadRequest(result.ErrorMessage);
        }

        return CreatedAtAction(
            nameof(GetProfile),
            new { profileId = result.Data!.Id },
            result.Data);
    }

    /// <summary>
    /// Updates an existing configuration profile
    /// </summary>
    /// <param name="profileId">Profile identifier</param>
    /// <param name="request">Update profile request</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>The updated profile</returns>
    [HttpPut("{profileId}")]
    [ProducesResponseType(typeof(ConfigurationProfile), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<ConfigurationProfile>> UpdateProfile(
        string profileId,
        [FromBody] UpdateProfileRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Updating configuration profile: {ProfileId}", profileId);

        if (profileId != request.Profile.Id)
        {
            return BadRequest("Profile ID mismatch");
        }

        var result = await _profileService.UpdateProfileAsync(request.Profile, cancellationToken);

        if (!result.Success)
        {
            return NotFound(result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Deletes a configuration profile
    /// </summary>
    /// <param name="profileId">Profile identifier</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>No content</returns>
    [HttpDelete("{profileId}")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult> DeleteProfile(
        string profileId,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Deleting configuration profile: {ProfileId}", profileId);

        var result = await _profileService.DeleteProfileAsync(profileId, cancellationToken);

        if (!result.Success)
        {
            if (result.ErrorMessage?.Contains("not found") == true)
                return NotFound(result.ErrorMessage);
            return BadRequest(result.ErrorMessage);
        }

        return NoContent();
    }

    /// <summary>
    /// Sets a profile as the default
    /// </summary>
    /// <param name="profileId">Profile identifier</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>No content</returns>
    [HttpPost("{profileId}/set-default")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult> SetDefaultProfile(
        string profileId,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Setting default profile: {ProfileId}", profileId);

        var result = await _profileService.SetDefaultProfileAsync(profileId, cancellationToken);

        if (!result.Success)
        {
            return NotFound(result.ErrorMessage);
        }

        return NoContent();
    }

    /// <summary>
    /// Exports a profile to a file
    /// </summary>
    /// <param name="profileId">Profile identifier</param>
    /// <param name="request">Export profile request</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>The exported file path</returns>
    [HttpPost("{profileId}/export")]
    [ProducesResponseType(typeof(string), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult> ExportProfile(
        string profileId,
        [FromBody] ExportProfileRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Exporting profile {ProfileId} to {Path}", profileId, request.DestinationPath);

        var result = await _profileService.ExportProfileAsync(profileId, request.DestinationPath, cancellationToken);

        if (!result.Success)
        {
            return NotFound(result.ErrorMessage);
        }

        return Ok(new { Path = result.Data });
    }

    /// <summary>
    /// Imports a profile from a file
    /// </summary>
    /// <param name="request">Import profile request</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>The imported profile</returns>
    [HttpPost("import")]
    [ProducesResponseType(typeof(ConfigurationProfile), StatusCodes.Status201Created)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<ConfigurationProfile>> ImportProfile(
        [FromBody] ImportProfileRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Importing profile from {Path}", request.FilePath);

        var result = await _profileService.ImportProfileAsync(
            request.FilePath,
            request.SetAsDefault,
            cancellationToken);

        if (!result.Success)
        {
            return BadRequest(result.ErrorMessage);
        }

        return CreatedAtAction(
            nameof(GetProfile),
            new { profileId = result.Data!.Id },
            result.Data);
    }

    /// <summary>
    /// Duplicates an existing profile
    /// </summary>
    /// <param name="profileId">Profile to duplicate</param>
    /// <param name="newName">Name for the new profile</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>The duplicated profile</returns>
    [HttpPost("{profileId}/duplicate")]
    [ProducesResponseType(typeof(ConfigurationProfile), StatusCodes.Status201Created)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<ConfigurationProfile>> DuplicateProfile(
        string profileId,
        [FromQuery] string newName,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Duplicating profile {ProfileId} with new name '{NewName}'", profileId, newName);

        var result = await _profileService.DuplicateProfileAsync(profileId, newName, cancellationToken);

        if (!result.Success)
        {
            return NotFound(result.ErrorMessage);
        }

        return CreatedAtAction(
            nameof(GetProfile),
            new { profileId = result.Data!.Id },
            result.Data);
    }

    /// <summary>
    /// Validates a configuration profile
    /// </summary>
    /// <param name="profile">Profile to validate</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>List of validation errors</returns>
    [HttpPost("validate")]
    [ProducesResponseType(typeof(List<string>), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<List<string>>> ValidateProfile(
        [FromBody] ConfigurationProfile profile,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Validating profile: {Name}", profile.Name);

        var result = await _profileService.ValidateProfileAsync(profile, cancellationToken);

        if (!result.Success)
        {
            return StatusCode(StatusCodes.Status500InternalServerError, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Applies profile settings with optional overrides
    /// </summary>
    /// <param name="request">Apply profile override request</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>The effective configuration after applying overrides</returns>
    [HttpPost("apply-overrides")]
    [ProducesResponseType(typeof(ConfigurationProfile), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<ConfigurationProfile>> ApplyProfileWithOverrides(
        [FromBody] ApplyProfileOverrideRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Applying profile {ProfileId} with {OverrideCount} overrides",
            request.ProfileId, request.Overrides.Count);

        var result = await _profileService.ApplyProfileWithOverridesAsync(
            request.ProfileId,
            request.Overrides,
            cancellationToken);

        if (!result.Success)
        {
            return NotFound(result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Resets a profile to default settings
    /// </summary>
    /// <param name="profileId">Profile to reset</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>The reset profile</returns>
    [HttpPost("{profileId}/reset")]
    [ProducesResponseType(typeof(ConfigurationProfile), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<ConfigurationProfile>> ResetProfile(
        string profileId,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Resetting profile: {ProfileId}", profileId);

        var result = await _profileService.ResetProfileAsync(profileId, cancellationToken);

        if (!result.Success)
        {
            return NotFound(result.ErrorMessage);
        }

        return Ok(result.Data);
    }
}
