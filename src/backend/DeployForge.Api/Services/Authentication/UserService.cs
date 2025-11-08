using BCrypt.Net;
using DeployForge.Api.Configuration;
using DeployForge.Api.Data;
using DeployForge.Api.Models.Authentication;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Options;

namespace DeployForge.Api.Services.Authentication;

/// <summary>
/// Implementation of user management service
/// </summary>
public class UserService : IUserService
{
    private readonly AuthenticationDbContext _dbContext;
    private readonly UserConfiguration _userConfig;
    private readonly ILogger<UserService> _logger;

    public UserService(
        AuthenticationDbContext dbContext,
        IOptions<AuthenticationConfiguration> authConfig,
        ILogger<UserService> logger)
    {
        _dbContext = dbContext;
        _userConfig = authConfig.Value.DefaultUsers;
        _logger = logger;
    }

    /// <summary>
    /// Authenticates a user with username and password
    /// </summary>
    public async Task<User?> AuthenticateAsync(string username, string password, CancellationToken cancellationToken = default)
    {
        var user = await _dbContext.Users
            .FirstOrDefaultAsync(u => u.Username == username, cancellationToken);

        if (user == null)
        {
            _logger.LogWarning("Authentication failed: User '{Username}' not found", username);
            return null;
        }

        if (!user.IsActive)
        {
            _logger.LogWarning("Authentication failed: User '{Username}' is not active", username);
            return null;
        }

        if (!BCrypt.Net.BCrypt.Verify(password, user.PasswordHash))
        {
            _logger.LogWarning("Authentication failed: Invalid password for user '{Username}'", username);
            return null;
        }

        _logger.LogInformation("User '{Username}' authenticated successfully", username);
        return user;
    }

    /// <summary>
    /// Creates a new user
    /// </summary>
    public async Task<User> CreateUserAsync(
        string username,
        string email,
        string password,
        string role,
        CancellationToken cancellationToken = default)
    {
        // Validate role
        if (!Roles.All.Contains(role))
        {
            throw new ArgumentException($"Invalid role '{role}'. Must be one of: {string.Join(", ", Roles.All)}", nameof(role));
        }

        // Check if username already exists
        var existingUser = await _dbContext.Users
            .FirstOrDefaultAsync(u => u.Username == username, cancellationToken);

        if (existingUser != null)
        {
            throw new InvalidOperationException($"Username '{username}' already exists");
        }

        // Check if email already exists
        var existingEmail = await _dbContext.Users
            .FirstOrDefaultAsync(u => u.Email == email, cancellationToken);

        if (existingEmail != null)
        {
            throw new InvalidOperationException($"Email '{email}' already exists");
        }

        // Hash password
        var passwordHash = BCrypt.Net.BCrypt.HashPassword(password, BCrypt.Net.BCrypt.GenerateSalt(12));

        var user = new User
        {
            Username = username,
            Email = email,
            PasswordHash = passwordHash,
            Role = role,
            IsActive = true,
            CreatedAt = DateTime.UtcNow
        };

        _dbContext.Users.Add(user);
        await _dbContext.SaveChangesAsync(cancellationToken);

        _logger.LogInformation("Created user '{Username}' with role '{Role}'", username, role);

        return user;
    }

    /// <summary>
    /// Gets a user by ID
    /// </summary>
    public async Task<User?> GetUserByIdAsync(string userId, CancellationToken cancellationToken = default)
    {
        return await _dbContext.Users.FindAsync(new object[] { userId }, cancellationToken);
    }

    /// <summary>
    /// Gets a user by username
    /// </summary>
    public async Task<User?> GetUserByUsernameAsync(string username, CancellationToken cancellationToken = default)
    {
        return await _dbContext.Users
            .FirstOrDefaultAsync(u => u.Username == username, cancellationToken);
    }

    /// <summary>
    /// Updates a user's password
    /// </summary>
    public async Task<bool> ChangePasswordAsync(
        string userId,
        string currentPassword,
        string newPassword,
        CancellationToken cancellationToken = default)
    {
        var user = await _dbContext.Users.FindAsync(new object[] { userId }, cancellationToken);

        if (user == null)
        {
            _logger.LogWarning("Password change failed: User {UserId} not found", userId);
            return false;
        }

        if (!BCrypt.Net.BCrypt.Verify(currentPassword, user.PasswordHash))
        {
            _logger.LogWarning("Password change failed: Invalid current password for user {UserId}", userId);
            return false;
        }

        user.PasswordHash = BCrypt.Net.BCrypt.HashPassword(newPassword, BCrypt.Net.BCrypt.GenerateSalt(12));
        user.UpdatedAt = DateTime.UtcNow;

        await _dbContext.SaveChangesAsync(cancellationToken);

        _logger.LogInformation("Password changed successfully for user {UserId}", userId);

        return true;
    }

    /// <summary>
    /// Updates user's last login timestamp
    /// </summary>
    public async Task UpdateLastLoginAsync(string userId, CancellationToken cancellationToken = default)
    {
        var user = await _dbContext.Users.FindAsync(new object[] { userId }, cancellationToken);

        if (user != null)
        {
            user.LastLoginAt = DateTime.UtcNow;
            await _dbContext.SaveChangesAsync(cancellationToken);
        }
    }

    /// <summary>
    /// Deactivates a user
    /// </summary>
    public async Task<bool> DeactivateUserAsync(string userId, CancellationToken cancellationToken = default)
    {
        var user = await _dbContext.Users.FindAsync(new object[] { userId }, cancellationToken);

        if (user == null)
        {
            _logger.LogWarning("Deactivate failed: User {UserId} not found", userId);
            return false;
        }

        user.IsActive = false;
        user.UpdatedAt = DateTime.UtcNow;

        await _dbContext.SaveChangesAsync(cancellationToken);

        _logger.LogInformation("User {UserId} ({Username}) deactivated", userId, user.Username);

        return true;
    }

    /// <summary>
    /// Activates a user
    /// </summary>
    public async Task<bool> ActivateUserAsync(string userId, CancellationToken cancellationToken = default)
    {
        var user = await _dbContext.Users.FindAsync(new object[] { userId }, cancellationToken);

        if (user == null)
        {
            _logger.LogWarning("Activate failed: User {UserId} not found", userId);
            return false;
        }

        user.IsActive = true;
        user.UpdatedAt = DateTime.UtcNow;

        await _dbContext.SaveChangesAsync(cancellationToken);

        _logger.LogInformation("User {UserId} ({Username}) activated", userId, user.Username);

        return true;
    }

    /// <summary>
    /// Creates default admin user if it doesn't exist
    /// </summary>
    public async Task EnsureDefaultAdminExistsAsync(CancellationToken cancellationToken = default)
    {
        if (!_userConfig.CreateDefaultAdmin)
        {
            _logger.LogInformation("Default admin creation is disabled in configuration");
            return;
        }

        var adminExists = await _dbContext.Users
            .AnyAsync(u => u.Username == _userConfig.AdminUsername, cancellationToken);

        if (adminExists)
        {
            _logger.LogDebug("Default admin user already exists");
            return;
        }

        try
        {
            await CreateUserAsync(
                _userConfig.AdminUsername,
                _userConfig.AdminEmail,
                _userConfig.AdminPassword,
                Roles.Admin,
                cancellationToken);

            _logger.LogWarning(
                "⚠️  DEFAULT ADMIN USER CREATED ⚠️\n" +
                "Username: {Username}\n" +
                "Password: {Password}\n" +
                "PLEASE CHANGE THE PASSWORD IMMEDIATELY!",
                _userConfig.AdminUsername,
                _userConfig.AdminPassword);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to create default admin user");
        }
    }
}
