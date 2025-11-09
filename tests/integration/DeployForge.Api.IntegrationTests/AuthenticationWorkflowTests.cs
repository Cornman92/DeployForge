using FluentAssertions;
using System.Net;
using System.Net.Http.Json;
using System.Text.Json;
using Xunit;
using DeployForge.Api.Models.Authentication;

namespace DeployForge.Api.IntegrationTests;

/// <summary>
/// Integration tests for authentication and authorization functionality
/// Tests JWT authentication, API keys, RBAC, and security workflows
/// </summary>
public class AuthenticationWorkflowTests : IClassFixture<ApiTestFixture>
{
    private readonly HttpClient _client;
    private readonly ApiTestFixture _fixture;

    public AuthenticationWorkflowTests(ApiTestFixture fixture)
    {
        _fixture = fixture;
        _client = fixture.CreateClient();
    }

    #region Login Tests

    [Fact]
    public async Task Login_With_Valid_Credentials_Should_Return_Tokens()
    {
        // Arrange
        var loginRequest = new LoginRequest
        {
            Username = "admin",
            Password = "Admin@123!ChangeME"
        };

        // Act
        var response = await _client.PostAsJsonAsync("/api/auth/login", loginRequest);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var loginResponse = await response.Content.ReadFromJsonAsync<LoginResponse>();
        loginResponse.Should().NotBeNull();
        loginResponse!.Success.Should().BeTrue();
        loginResponse.AccessToken.Should().NotBeNullOrEmpty();
        loginResponse.RefreshToken.Should().NotBeNullOrEmpty();
        loginResponse.ExpiresAt.Should().BeAfter(DateTime.UtcNow);
        loginResponse.User.Should().NotBeNull();
        loginResponse.User!.Username.Should().Be("admin");
        loginResponse.User.Role.Should().Be("Admin");
    }

    [Fact]
    public async Task Login_With_Invalid_Credentials_Should_Return_Unauthorized()
    {
        // Arrange
        var loginRequest = new LoginRequest
        {
            Username = "admin",
            Password = "WrongPassword123!"
        };

        // Act
        var response = await _client.PostAsJsonAsync("/api/auth/login", loginRequest);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.Unauthorized);

        var loginResponse = await response.Content.ReadFromJsonAsync<LoginResponse>();
        loginResponse.Should().NotBeNull();
        loginResponse!.Success.Should().BeFalse();
        loginResponse.AccessToken.Should().BeNullOrEmpty();
    }

    [Fact]
    public async Task Login_With_Missing_Username_Should_Return_BadRequest()
    {
        // Arrange
        var loginRequest = new
        {
            Username = "",
            Password = "Admin@123!ChangeME"
        };

        // Act
        var response = await _client.PostAsJsonAsync("/api/auth/login", loginRequest);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.BadRequest);
    }

    [Fact]
    public async Task Login_With_Short_Password_Should_Return_BadRequest()
    {
        // Arrange
        var loginRequest = new
        {
            Username = "admin",
            Password = "short"
        };

        // Act
        var response = await _client.PostAsJsonAsync("/api/auth/login", loginRequest);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.BadRequest);
    }

    #endregion

    #region JWT Token Tests

    [Fact]
    public async Task Access_Protected_Endpoint_Without_Token_Should_Return_Unauthorized()
    {
        // Act
        var response = await _client.GetAsync("/api/images");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.Unauthorized);
    }

    [Fact]
    public async Task Access_Protected_Endpoint_With_Valid_Token_Should_Succeed()
    {
        // Arrange
        var token = await GetValidAccessTokenAsync();
        _client.DefaultRequestHeaders.Authorization =
            new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", token);

        // Act
        var response = await _client.GetAsync("/api/health");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);
    }

    [Fact]
    public async Task Access_Protected_Endpoint_With_Invalid_Token_Should_Return_Unauthorized()
    {
        // Arrange
        _client.DefaultRequestHeaders.Authorization =
            new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", "invalid.token.here");

        // Act
        var response = await _client.GetAsync("/api/images");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.Unauthorized);
    }

    [Fact]
    public async Task Refresh_Token_With_Valid_Refresh_Token_Should_Return_New_Tokens()
    {
        // Arrange - Login first to get refresh token
        var loginResponse = await LoginAsync();
        var refreshRequest = new RefreshTokenRequest
        {
            RefreshToken = loginResponse.RefreshToken!
        };

        // Act
        var response = await _client.PostAsJsonAsync("/api/auth/refresh", refreshRequest);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var refreshResponse = await response.Content.ReadFromJsonAsync<LoginResponse>();
        refreshResponse.Should().NotBeNull();
        refreshResponse!.Success.Should().BeTrue();
        refreshResponse.AccessToken.Should().NotBeNullOrEmpty();
        refreshResponse.RefreshToken.Should().NotBeNullOrEmpty();
        refreshResponse.RefreshToken.Should().NotBe(loginResponse.RefreshToken,
            "New refresh token should be different from old one");
    }

    [Fact]
    public async Task Refresh_Token_With_Invalid_Token_Should_Return_Unauthorized()
    {
        // Arrange
        var refreshRequest = new RefreshTokenRequest
        {
            RefreshToken = "invalid_refresh_token_12345"
        };

        // Act
        var response = await _client.PostAsJsonAsync("/api/auth/refresh", refreshRequest);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.Unauthorized);
    }

    [Fact]
    public async Task Logout_Should_Revoke_Refresh_Token()
    {
        // Arrange - Login and get tokens
        var loginResponse = await LoginAsync();
        var token = loginResponse.AccessToken!;
        var refreshToken = loginResponse.RefreshToken!;

        var client = _fixture.CreateClient();
        client.DefaultRequestHeaders.Authorization =
            new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", token);

        // Act - Logout
        var logoutRequest = new RefreshTokenRequest { RefreshToken = refreshToken };
        var logoutResponse = await client.PostAsJsonAsync("/api/auth/logout", logoutRequest);

        // Assert
        logoutResponse.StatusCode.Should().Be(HttpStatusCode.OK);

        // Try to use the refresh token - should fail
        var refreshRequest = new RefreshTokenRequest { RefreshToken = refreshToken };
        var refreshResponse = await _client.PostAsJsonAsync("/api/auth/refresh", refreshRequest);
        refreshResponse.StatusCode.Should().Be(HttpStatusCode.Unauthorized,
            "Revoked refresh token should not work");
    }

    #endregion

    #region API Key Authentication Tests

    [Fact]
    public async Task Create_API_Key_Should_Return_Key_With_Secret()
    {
        // Arrange
        var token = await GetValidAccessTokenAsync();
        var client = _fixture.CreateClient();
        client.DefaultRequestHeaders.Authorization =
            new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", token);

        var createRequest = new CreateApiKeyRequest
        {
            Name = "Test API Key",
            Role = "User",
            ExpirationDays = 30
        };

        // Act
        var response = await client.PostAsJsonAsync("/api/auth/api-keys", createRequest);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.Created);

        var apiKeyResponse = await response.Content.ReadFromJsonAsync<ApiKeyResponse>();
        apiKeyResponse.Should().NotBeNull();
        apiKeyResponse!.Key.Should().NotBeNullOrEmpty("API key should be returned on creation");
        apiKeyResponse.KeyPrefix.Should().NotBeNullOrEmpty();
        apiKeyResponse.Name.Should().Be("Test API Key");
        apiKeyResponse.Role.Should().Be("User");
        apiKeyResponse.IsActive.Should().BeTrue();
        apiKeyResponse.ExpiresAt.Should().NotBeNull();
    }

    [Fact]
    public async Task Access_Endpoint_With_Valid_API_Key_Should_Succeed()
    {
        // Arrange - Create API key
        var apiKey = await CreateApiKeyAsync();

        var client = _fixture.CreateClient();
        client.DefaultRequestHeaders.Add("X-API-Key", apiKey);

        // Act
        var response = await client.GetAsync("/api/health");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);
    }

    [Fact]
    public async Task Access_Endpoint_With_Invalid_API_Key_Should_Return_Unauthorized()
    {
        // Arrange
        var client = _fixture.CreateClient();
        client.DefaultRequestHeaders.Add("X-API-Key", "invalid_api_key_12345");

        // Act
        var response = await client.GetAsync("/api/images");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.Unauthorized);
    }

    [Fact]
    public async Task Get_API_Keys_Should_Return_User_Keys()
    {
        // Arrange - Create an API key first
        var apiKey = await CreateApiKeyAsync();
        var token = await GetValidAccessTokenAsync();

        var client = _fixture.CreateClient();
        client.DefaultRequestHeaders.Authorization =
            new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", token);

        // Act
        var response = await client.GetAsync("/api/auth/api-keys");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var apiKeys = await response.Content.ReadFromJsonAsync<List<ApiKeyResponse>>();
        apiKeys.Should().NotBeNull();
        apiKeys!.Should().HaveCountGreaterThan(0, "Should have at least one API key");
        apiKeys.All(k => k.Key == null).Should().BeTrue("API keys should not include the secret in list view");
    }

    [Fact]
    public async Task Revoke_API_Key_Should_Make_It_Inactive()
    {
        // Arrange - Create and get API key ID
        var token = await GetValidAccessTokenAsync();
        var client = _fixture.CreateClient();
        client.DefaultRequestHeaders.Authorization =
            new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", token);

        // Create key
        var createRequest = new CreateApiKeyRequest
        {
            Name = "Key To Revoke",
            Role = "ReadOnly"
        };
        var createResponse = await client.PostAsJsonAsync("/api/auth/api-keys", createRequest);
        var createdKey = await createResponse.Content.ReadFromJsonAsync<ApiKeyResponse>();
        var keyId = createdKey!.Id;
        var keySecret = createdKey.Key!;

        // Act - Revoke the key
        var revokeResponse = await client.DeleteAsync($"/api/auth/api-keys/{keyId}");

        // Assert
        revokeResponse.StatusCode.Should().Be(HttpStatusCode.OK);

        // Try to use the revoked key
        var testClient = _fixture.CreateClient();
        testClient.DefaultRequestHeaders.Add("X-API-Key", keySecret);
        var testResponse = await testClient.GetAsync("/api/health");
        testResponse.StatusCode.Should().Be(HttpStatusCode.Unauthorized,
            "Revoked API key should not work");
    }

    #endregion

    #region Role-Based Authorization Tests

    [Fact]
    public async Task Admin_User_Can_Register_New_Users()
    {
        // Arrange
        var token = await GetValidAccessTokenAsync(); // Admin token
        var client = _fixture.CreateClient();
        client.DefaultRequestHeaders.Authorization =
            new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", token);

        var registerRequest = new RegisterUserRequest
        {
            Username = $"testuser_{Guid.NewGuid():N}",
            Email = $"test_{Guid.NewGuid():N}@example.com",
            Password = "TestPass@123!",
            Role = "User"
        };

        // Act
        var response = await client.PostAsJsonAsync("/api/auth/register", registerRequest);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.Created);
    }

    [Fact]
    public async Task User_With_API_Key_Can_Create_Lower_Role_Keys()
    {
        // Arrange - Get API key with User role
        var userApiKey = await CreateApiKeyAsync("User");
        var client = _fixture.CreateClient();
        client.DefaultRequestHeaders.Add("X-API-Key", userApiKey);

        var createRequest = new CreateApiKeyRequest
        {
            Name = "ReadOnly Key",
            Role = "ReadOnly"
        };

        // Act
        var response = await client.PostAsJsonAsync("/api/auth/api-keys", createRequest);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.Created,
            "User should be able to create ReadOnly keys");
    }

    [Fact]
    public async Task Get_Current_User_Info_Should_Return_User_Details()
    {
        // Arrange
        var token = await GetValidAccessTokenAsync();
        var client = _fixture.CreateClient();
        client.DefaultRequestHeaders.Authorization =
            new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", token);

        // Act
        var response = await client.GetAsync("/api/auth/me");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var userInfo = await response.Content.ReadFromJsonAsync<UserInfo>();
        userInfo.Should().NotBeNull();
        userInfo!.Username.Should().Be("admin");
        userInfo.Role.Should().Be("Admin");
        userInfo.Email.Should().NotBeNullOrEmpty();
    }

    #endregion

    #region Password Management Tests

    [Fact]
    public async Task Change_Password_With_Valid_Current_Password_Should_Succeed()
    {
        // Arrange - First create a test user
        var token = await GetValidAccessTokenAsync();
        var adminClient = _fixture.CreateClient();
        adminClient.DefaultRequestHeaders.Authorization =
            new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", token);

        var username = $"pwdtest_{Guid.NewGuid():N}";
        var registerRequest = new RegisterUserRequest
        {
            Username = username,
            Email = $"{username}@example.com",
            Password = "OldPass@123!",
            Role = "User"
        };
        await adminClient.PostAsJsonAsync("/api/auth/register", registerRequest);

        // Login as the new user
        var loginRequest = new LoginRequest
        {
            Username = username,
            Password = "OldPass@123!"
        };
        var loginResponse = await _client.PostAsJsonAsync("/api/auth/login", loginRequest);
        var loginData = await loginResponse.Content.ReadFromJsonAsync<LoginResponse>();

        var userClient = _fixture.CreateClient();
        userClient.DefaultRequestHeaders.Authorization =
            new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", loginData!.AccessToken!);

        var changeRequest = new ChangePasswordRequest
        {
            CurrentPassword = "OldPass@123!",
            NewPassword = "NewPass@456!",
            ConfirmNewPassword = "NewPass@456!"
        };

        // Act
        var response = await userClient.PostAsJsonAsync("/api/auth/change-password", changeRequest);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        // Verify old password no longer works
        var oldLoginRequest = new LoginRequest
        {
            Username = username,
            Password = "OldPass@123!"
        };
        var oldLoginResponse = await _client.PostAsJsonAsync("/api/auth/login", oldLoginRequest);
        oldLoginResponse.StatusCode.Should().Be(HttpStatusCode.Unauthorized,
            "Old password should not work after change");

        // Verify new password works
        var newLoginRequest = new LoginRequest
        {
            Username = username,
            Password = "NewPass@456!"
        };
        var newLoginResponse = await _client.PostAsJsonAsync("/api/auth/login", newLoginRequest);
        newLoginResponse.StatusCode.Should().Be(HttpStatusCode.OK,
            "New password should work after change");
    }

    [Fact]
    public async Task Change_Password_With_Wrong_Current_Password_Should_Fail()
    {
        // Arrange
        var token = await GetValidAccessTokenAsync();
        var client = _fixture.CreateClient();
        client.DefaultRequestHeaders.Authorization =
            new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", token);

        var changeRequest = new ChangePasswordRequest
        {
            CurrentPassword = "WrongPassword123!",
            NewPassword = "NewPass@456!",
            ConfirmNewPassword = "NewPass@456!"
        };

        // Act
        var response = await client.PostAsJsonAsync("/api/auth/change-password", changeRequest);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.BadRequest);
    }

    [Fact]
    public async Task Change_Password_With_Weak_Password_Should_Return_BadRequest()
    {
        // Arrange
        var token = await GetValidAccessTokenAsync();
        var client = _fixture.CreateClient();
        client.DefaultRequestHeaders.Authorization =
            new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", token);

        var changeRequest = new
        {
            CurrentPassword = "Admin@123!ChangeME",
            NewPassword = "weak", // Too short, no uppercase, no special char
            ConfirmNewPassword = "weak"
        };

        // Act
        var response = await client.PostAsJsonAsync("/api/auth/change-password", changeRequest);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.BadRequest);
    }

    #endregion

    #region Helper Methods

    private async Task<LoginResponse> LoginAsync()
    {
        var loginRequest = new LoginRequest
        {
            Username = "admin",
            Password = "Admin@123!ChangeME"
        };

        var response = await _client.PostAsJsonAsync("/api/auth/login", loginRequest);
        response.EnsureSuccessStatusCode();

        var loginResponse = await response.Content.ReadFromJsonAsync<LoginResponse>();
        return loginResponse!;
    }

    private async Task<string> GetValidAccessTokenAsync()
    {
        var loginResponse = await LoginAsync();
        return loginResponse.AccessToken!;
    }

    private async Task<string> CreateApiKeyAsync(string role = "User")
    {
        var token = await GetValidAccessTokenAsync();
        var client = _fixture.CreateClient();
        client.DefaultRequestHeaders.Authorization =
            new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", token);

        var createRequest = new CreateApiKeyRequest
        {
            Name = $"Test Key {Guid.NewGuid():N}",
            Role = role
        };

        var response = await client.PostAsJsonAsync("/api/auth/api-keys", createRequest);
        response.EnsureSuccessStatusCode();

        var apiKeyResponse = await response.Content.ReadFromJsonAsync<ApiKeyResponse>();
        return apiKeyResponse!.Key!;
    }

    #endregion
}
