using DeployForge.Api.Models.Authentication;

namespace DeployForge.Api.Services.Authentication;

/// <summary>
/// Interface for user management service
/// </summary>
public interface IUserService
{
    /// <summary>
    /// Authenticates a user with username and password
    /// </summary>
    Task<User?> AuthenticateAsync(string username, string password, CancellationToken cancellationToken = default);

    /// <summary>
    /// Creates a new user
    /// </summary>
    Task<User> CreateUserAsync(string username, string email, string password, string role, CancellationToken cancellationToken = default);

    /// <summary>
    /// Gets a user by ID
    /// </summary>
    Task<User?> GetUserByIdAsync(string userId, CancellationToken cancellationToken = default);

    /// <summary>
    /// Gets a user by username
    /// </summary>
    Task<User?> GetUserByUsernameAsync(string username, CancellationToken cancellationToken = default);

    /// <summary>
    /// Updates a user's password
    /// </summary>
    Task<bool> ChangePasswordAsync(string userId, string currentPassword, string newPassword, CancellationToken cancellationToken = default);

    /// <summary>
    /// Updates user's last login timestamp
    /// </summary>
    Task UpdateLastLoginAsync(string userId, CancellationToken cancellationToken = default);

    /// <summary>
    /// Deactivates a user
    /// </summary>
    Task<bool> DeactivateUserAsync(string userId, CancellationToken cancellationToken = default);

    /// <summary>
    /// Activates a user
    /// </summary>
    Task<bool> ActivateUserAsync(string userId, CancellationToken cancellationToken = default);

    /// <summary>
    /// Creates default admin user if it doesn't exist
    /// </summary>
    Task EnsureDefaultAdminExistsAsync(CancellationToken cancellationToken = default);
}
