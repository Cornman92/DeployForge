using System.Security.Claims;
using DeployForge.Api.Configuration;
using DeployForge.Api.Models.Authentication;
using DeployForge.Api.Services.Authentication;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace DeployForge.Api.Controllers;

/// <summary>
/// Authentication controller for login, registration, and token management
/// </summary>
[ApiController]
[Route("api/[controller]")]
public class AuthController : ControllerBase
{
    private readonly IUserService _userService;
    private readonly IJwtTokenService _jwtTokenService;
    private readonly IApiKeyService _apiKeyService;
    private readonly ILogger<AuthController> _logger;

    public AuthController(
        IUserService userService,
        IJwtTokenService jwtTokenService,
        IApiKeyService apiKeyService,
        ILogger<AuthController> logger)
    {
        _userService = userService;
        _jwtTokenService = jwtTokenService;
        _apiKeyService = apiKeyService;
        _logger = logger;
    }

    /// <summary>
    /// Login with username and password
    /// </summary>
    [HttpPost("login")]
    [AllowAnonymous]
    [ProducesResponseType(typeof(LoginResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    public async Task<ActionResult<LoginResponse>> Login(
        [FromBody] LoginRequest request,
        CancellationToken cancellationToken)
    {
        if (!ModelState.IsValid)
        {
            return BadRequest(ModelState);
        }

        var user = await _userService.AuthenticateAsync(request.Username, request.Password, cancellationToken);

        if (user == null)
        {
            _logger.LogWarning("Failed login attempt for username: {Username}", request.Username);
            return Unauthorized(new LoginResponse
            {
                Success = false,
                Message = "Invalid username or password"
            });
        }

        // Generate tokens
        var accessToken = _jwtTokenService.GenerateAccessToken(user);
        var refreshToken = await _jwtTokenService.GenerateRefreshTokenAsync(user, cancellationToken);

        // Update last login
        await _userService.UpdateLastLoginAsync(user.Id, cancellationToken);

        _logger.LogInformation("User {Username} logged in successfully", user.Username);

        var expiresAt = DateTime.UtcNow.AddMinutes(15); // From JWT config

        return Ok(new LoginResponse
        {
            Success = true,
            Message = "Login successful",
            AccessToken = accessToken,
            RefreshToken = refreshToken.Token,
            ExpiresAt = expiresAt,
            User = new UserInfo
            {
                Id = user.Id,
                Username = user.Username,
                Email = user.Email,
                Role = user.Role
            }
        });
    }

    /// <summary>
    /// Refresh access token using refresh token
    /// </summary>
    [HttpPost("refresh")]
    [AllowAnonymous]
    [ProducesResponseType(typeof(LoginResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    public async Task<ActionResult<LoginResponse>> RefreshToken(
        [FromBody] RefreshTokenRequest request,
        CancellationToken cancellationToken)
    {
        if (!ModelState.IsValid)
        {
            return BadRequest(ModelState);
        }

        var (isValid, user) = await _jwtTokenService.ValidateRefreshTokenAsync(
            request.RefreshToken, cancellationToken);

        if (!isValid || user == null)
        {
            return Unauthorized(new LoginResponse
            {
                Success = false,
                Message = "Invalid or expired refresh token"
            });
        }

        // Generate new tokens
        var newAccessToken = _jwtTokenService.GenerateAccessToken(user);
        var newRefreshToken = await _jwtTokenService.GenerateRefreshTokenAsync(user, cancellationToken);

        // Revoke old refresh token
        await _jwtTokenService.RevokeRefreshTokenAsync(
            request.RefreshToken,
            newRefreshToken.Token,
            cancellationToken);

        _logger.LogInformation("Token refreshed for user {Username}", user.Username);

        var expiresAt = DateTime.UtcNow.AddMinutes(15);

        return Ok(new LoginResponse
        {
            Success = true,
            Message = "Token refreshed successfully",
            AccessToken = newAccessToken,
            RefreshToken = newRefreshToken.Token,
            ExpiresAt = expiresAt,
            User = new UserInfo
            {
                Id = user.Id,
                Username = user.Username,
                Email = user.Email,
                Role = user.Role
            }
        });
    }

    /// <summary>
    /// Logout - revokes refresh token
    /// </summary>
    [HttpPost("logout")]
    [Authorize]
    [ProducesResponseType(StatusCodes.Status200OK)]
    public async Task<IActionResult> Logout(
        [FromBody] RefreshTokenRequest? request,
        CancellationToken cancellationToken)
    {
        var userId = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;

        if (string.IsNullOrEmpty(userId))
        {
            return Unauthorized();
        }

        if (request != null && !string.IsNullOrEmpty(request.RefreshToken))
        {
            await _jwtTokenService.RevokeRefreshTokenAsync(request.RefreshToken, null, cancellationToken);
        }
        else
        {
            // Revoke all refresh tokens for user
            await _jwtTokenService.RevokeAllUserRefreshTokensAsync(userId, cancellationToken);
        }

        _logger.LogInformation("User {UserId} logged out", userId);

        return Ok(new { message = "Logged out successfully" });
    }

    /// <summary>
    /// Register a new user (Admin only)
    /// </summary>
    [HttpPost("register")]
    [Authorize(Roles = Roles.Admin)]
    [ProducesResponseType(typeof(UserInfo), StatusCodes.Status201Created)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    public async Task<ActionResult<UserInfo>> Register(
        [FromBody] RegisterUserRequest request,
        CancellationToken cancellationToken)
    {
        if (!ModelState.IsValid)
        {
            return BadRequest(ModelState);
        }

        try
        {
            var user = await _userService.CreateUserAsync(
                request.Username,
                request.Email,
                request.Password,
                request.Role,
                cancellationToken);

            _logger.LogInformation("New user {Username} created with role {Role}", user.Username, user.Role);

            var userInfo = new UserInfo
            {
                Id = user.Id,
                Username = user.Username,
                Email = user.Email,
                Role = user.Role
            };

            return CreatedAtAction(nameof(Register), userInfo);
        }
        catch (InvalidOperationException ex)
        {
            return BadRequest(new { message = ex.Message });
        }
        catch (ArgumentException ex)
        {
            return BadRequest(new { message = ex.Message });
        }
    }

    /// <summary>
    /// Change password
    /// </summary>
    [HttpPost("change-password")]
    [Authorize]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public async Task<IActionResult> ChangePassword(
        [FromBody] ChangePasswordRequest request,
        CancellationToken cancellationToken)
    {
        if (!ModelState.IsValid)
        {
            return BadRequest(ModelState);
        }

        var userId = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;

        if (string.IsNullOrEmpty(userId))
        {
            return Unauthorized();
        }

        var success = await _userService.ChangePasswordAsync(
            userId,
            request.CurrentPassword,
            request.NewPassword,
            cancellationToken);

        if (!success)
        {
            return BadRequest(new { message = "Failed to change password. Current password is incorrect." });
        }

        _logger.LogInformation("Password changed for user {UserId}", userId);

        return Ok(new { message = "Password changed successfully" });
    }

    /// <summary>
    /// Create API key
    /// </summary>
    [HttpPost("api-keys")]
    [Authorize]
    [ProducesResponseType(typeof(ApiKeyResponse), StatusCodes.Status201Created)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public async Task<ActionResult<ApiKeyResponse>> CreateApiKey(
        [FromBody] CreateApiKeyRequest request,
        CancellationToken cancellationToken)
    {
        if (!ModelState.IsValid)
        {
            return BadRequest(ModelState);
        }

        var userId = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        var userRole = User.FindFirst(ClaimTypes.Role)?.Value;

        if (string.IsNullOrEmpty(userId))
        {
            return Unauthorized();
        }

        // Users can only create API keys with their own role or lower
        if (!CanCreateRoleApiKey(userRole, request.Role))
        {
            return Forbid();
        }

        try
        {
            var (apiKey, plainKey) = await _apiKeyService.CreateApiKeyAsync(
                userId,
                request.Name,
                request.Role,
                request.ExpirationDays,
                cancellationToken);

            _logger.LogInformation("API key '{Name}' created for user {UserId}", request.Name, userId);

            var response = new ApiKeyResponse
            {
                Id = apiKey.Id,
                Name = apiKey.Name,
                Key = plainKey, // Only returned on creation
                KeyPrefix = apiKey.KeyPrefix,
                Role = apiKey.Role,
                CreatedAt = apiKey.CreatedAt,
                ExpiresAt = apiKey.ExpiresAt,
                IsActive = apiKey.IsActive
            };

            return CreatedAtAction(nameof(GetApiKeys), response);
        }
        catch (InvalidOperationException ex)
        {
            return BadRequest(new { message = ex.Message });
        }
    }

    /// <summary>
    /// Get all API keys for current user
    /// </summary>
    [HttpGet("api-keys")]
    [Authorize]
    [ProducesResponseType(typeof(List<ApiKeyResponse>), StatusCodes.Status200OK)]
    public async Task<ActionResult<List<ApiKeyResponse>>> GetApiKeys(CancellationToken cancellationToken)
    {
        var userId = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;

        if (string.IsNullOrEmpty(userId))
        {
            return Unauthorized();
        }

        var apiKeys = await _apiKeyService.GetUserApiKeysAsync(userId, cancellationToken);

        var response = apiKeys.Select(k => new ApiKeyResponse
        {
            Id = k.Id,
            Name = k.Name,
            KeyPrefix = k.KeyPrefix,
            Role = k.Role,
            CreatedAt = k.CreatedAt,
            ExpiresAt = k.ExpiresAt,
            LastUsedAt = k.LastUsedAt,
            IsActive = k.IsActive
        }).ToList();

        return Ok(response);
    }

    /// <summary>
    /// Revoke an API key
    /// </summary>
    [HttpDelete("api-keys/{apiKeyId}")]
    [Authorize]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> RevokeApiKey(string apiKeyId, CancellationToken cancellationToken)
    {
        var userId = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;

        if (string.IsNullOrEmpty(userId))
        {
            return Unauthorized();
        }

        var success = await _apiKeyService.RevokeApiKeyAsync(apiKeyId, userId, cancellationToken);

        if (!success)
        {
            return NotFound(new { message = "API key not found" });
        }

        _logger.LogInformation("API key {ApiKeyId} revoked by user {UserId}", apiKeyId, userId);

        return Ok(new { message = "API key revoked successfully" });
    }

    /// <summary>
    /// Get current user info
    /// </summary>
    [HttpGet("me")]
    [Authorize]
    [ProducesResponseType(typeof(UserInfo), StatusCodes.Status200OK)]
    public IActionResult GetCurrentUser()
    {
        var userId = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        var username = User.FindFirst(ClaimTypes.Name)?.Value;
        var email = User.FindFirst(ClaimTypes.Email)?.Value;
        var role = User.FindFirst(ClaimTypes.Role)?.Value;

        if (string.IsNullOrEmpty(userId))
        {
            return Unauthorized();
        }

        return Ok(new UserInfo
        {
            Id = userId,
            Username = username ?? "",
            Email = email ?? "",
            Role = role ?? ""
        });
    }

    /// <summary>
    /// Checks if a user can create an API key with the specified role
    /// </summary>
    private static bool CanCreateRoleApiKey(string? userRole, string keyRole)
    {
        return userRole switch
        {
            Roles.Admin => true, // Admin can create any role
            Roles.User => keyRole == Roles.User || keyRole == Roles.ReadOnly,
            Roles.ReadOnly => keyRole == Roles.ReadOnly,
            _ => false
        };
    }
}
