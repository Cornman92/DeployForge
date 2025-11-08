using System.Text;
using DeployForge.Api.Configuration;
using DeployForge.Api.Data;
using DeployForge.Api.Services.Authentication;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.Authorization;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using Microsoft.OpenApi.Models;

namespace DeployForge.Api.Middleware;

/// <summary>
/// Extension methods for configuring authentication
/// </summary>
public static class AuthenticationExtensions
{
    /// <summary>
    /// Adds authentication services (JWT + API Key)
    /// </summary>
    public static IServiceCollection AddDeployForgeAuthentication(
        this IServiceCollection services,
        IConfiguration configuration)
    {
        // Bind authentication configuration
        var authConfig = configuration.GetSection("Authentication").Get<AuthenticationConfiguration>()
            ?? new AuthenticationConfiguration();

        services.Configure<AuthenticationConfiguration>(configuration.GetSection("Authentication"));

        // Validate JWT configuration
        if (string.IsNullOrEmpty(authConfig.Jwt.SecretKey) || authConfig.Jwt.SecretKey.Length < 32)
        {
            throw new InvalidOperationException(
                "JWT Secret Key must be configured and at least 32 characters long. " +
                "Set Authentication:Jwt:SecretKey in appsettings.json");
        }

        // Add database context
        var connectionString = configuration.GetConnectionString("AuthenticationDb")
            ?? "Data Source=authentication.db";

        services.AddDbContext<AuthenticationDbContext>(options =>
            options.UseSqlite(connectionString));

        // Add authentication services
        services.AddScoped<IUserService, UserService>();
        services.AddScoped<IJwtTokenService, JwtTokenService>();
        services.AddScoped<IApiKeyService, ApiKeyService>();

        // Configure JWT Bearer authentication
        var key = Encoding.UTF8.GetBytes(authConfig.Jwt.SecretKey);

        services.AddAuthentication(options =>
        {
            options.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
            options.DefaultChallengeScheme = JwtBearerDefaults.AuthenticationScheme;
            options.DefaultScheme = JwtBearerDefaults.AuthenticationScheme;
        })
        .AddJwtBearer(options =>
        {
            options.SaveToken = true;
            options.RequireHttpsMetadata = authConfig.Jwt.RequireHttpsMetadata;
            options.TokenValidationParameters = new TokenValidationParameters
            {
                ValidateIssuer = authConfig.Jwt.ValidateIssuer,
                ValidateAudience = authConfig.Jwt.ValidateAudience,
                ValidateLifetime = authConfig.Jwt.ValidateLifetime,
                ValidateIssuerSigningKey = true,
                ValidIssuer = authConfig.Jwt.Issuer,
                ValidAudience = authConfig.Jwt.Audience,
                IssuerSigningKey = new SymmetricSecurityKey(key),
                ClockSkew = TimeSpan.FromMinutes(authConfig.Jwt.ClockSkewMinutes)
            };

            // Support API Key authentication in addition to JWT
            options.Events = new JwtBearerEvents
            {
                OnMessageReceived = async context =>
                {
                    // Try API key authentication if no JWT token is present
                    var apiKeyHeaderName = authConfig.ApiKey.HeaderName;
                    if (context.Request.Headers.TryGetValue(apiKeyHeaderName, out var apiKey) &&
                        !string.IsNullOrEmpty(apiKey))
                    {
                        var apiKeyService = context.HttpContext.RequestServices
                            .GetRequiredService<IApiKeyService>();

                        var (isValid, user) = await apiKeyService.ValidateApiKeyAsync(apiKey!);

                        if (isValid && user != null)
                        {
                            // Create claims for API key authentication
                            var claims = new[]
                            {
                                new System.Security.Claims.Claim(System.Security.Claims.ClaimTypes.NameIdentifier, user.Id),
                                new System.Security.Claims.Claim(System.Security.Claims.ClaimTypes.Name, user.Username),
                                new System.Security.Claims.Claim(System.Security.Claims.ClaimTypes.Email, user.Email),
                                new System.Security.Claims.Claim(System.Security.Claims.ClaimTypes.Role, user.Role)
                            };

                            var identity = new System.Security.Claims.ClaimsIdentity(
                                claims, "ApiKey");

                            context.Principal = new System.Security.Claims.ClaimsPrincipal(identity);
                            context.Success();
                        }
                    }
                },
                OnAuthenticationFailed = context =>
                {
                    if (context.Exception is SecurityTokenExpiredException)
                    {
                        context.Response.Headers.Add("Token-Expired", "true");
                    }
                    return Task.CompletedTask;
                },
                OnChallenge = context =>
                {
                    context.HandleResponse();

                    if (!context.Response.HasStarted)
                    {
                        context.Response.StatusCode = StatusCodes.Status401Unauthorized;
                        context.Response.ContentType = "application/json";

                        var problemDetails = new
                        {
                            type = "https://tools.ietf.org/html/rfc7235#section-3.1",
                            title = "Unauthorized",
                            status = StatusCodes.Status401Unauthorized,
                            detail = "Authentication required. Provide a valid JWT token in Authorization header or API key in X-API-Key header.",
                            instance = context.Request.Path.Value
                        };

                        return context.Response.WriteAsJsonAsync(problemDetails);
                    }

                    return Task.CompletedTask;
                },
                OnForbidden = context =>
                {
                    context.Response.StatusCode = StatusCodes.Status403Forbidden;
                    context.Response.ContentType = "application/json";

                    var problemDetails = new
                    {
                        type = "https://tools.ietf.org/html/rfc7231#section-6.5.3",
                        title = "Forbidden",
                        status = StatusCodes.Status403Forbidden,
                        detail = "You do not have permission to access this resource.",
                        instance = context.Request.Path.Value
                    };

                    return context.Response.WriteAsJsonAsync(problemDetails);
                }
            };
        });

        // Configure authorization policies
        services.AddAuthorization(options =>
        {
            // Default policy - requires authentication
            options.DefaultPolicy = new AuthorizationPolicyBuilder()
                .RequireAuthenticatedUser()
                .Build();

            // Admin-only policy
            options.AddPolicy("AdminOnly", policy =>
                policy.RequireRole(Roles.Admin));

            // Admin or User policy
            options.AddPolicy("AdminOrUser", policy =>
                policy.RequireRole(Roles.Admin, Roles.User));

            // Any authenticated user policy
            options.AddPolicy("Authenticated", policy =>
                policy.RequireAuthenticatedUser());
        });

        return services;
    }

    /// <summary>
    /// Configures Swagger to support JWT authentication
    /// </summary>
    public static void AddSwaggerAuthentication(this SwaggerGenOptions options)
    {
        // Define JWT security scheme
        options.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme
        {
            Description = @"JWT Authorization header using the Bearer scheme.
                          Enter 'Bearer' [space] and then your token in the text input below.
                          Example: 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'",
            Name = "Authorization",
            In = ParameterLocation.Header,
            Type = SecuritySchemeType.ApiKey,
            Scheme = "Bearer",
            BearerFormat = "JWT"
        });

        // Define API Key security scheme
        options.AddSecurityDefinition("ApiKey", new OpenApiSecurityScheme
        {
            Description = "API Key authentication using X-API-Key header",
            Name = "X-API-Key",
            In = ParameterLocation.Header,
            Type = SecuritySchemeType.ApiKey
        });

        // Add security requirement
        options.AddSecurityRequirement(new OpenApiSecurityRequirement
        {
            {
                new OpenApiSecurityScheme
                {
                    Reference = new OpenApiReference
                    {
                        Type = ReferenceType.SecurityScheme,
                        Id = "Bearer"
                    }
                },
                Array.Empty<string>()
            },
            {
                new OpenApiSecurityScheme
                {
                    Reference = new OpenApiReference
                    {
                        Type = ReferenceType.SecurityScheme,
                        Id = "ApiKey"
                    }
                },
                Array.Empty<string>()
            }
        });
    }

    /// <summary>
    /// Ensures database is created and default admin user exists
    /// </summary>
    public static async Task<IApplicationBuilder> EnsureAuthenticationDatabaseAsync(this IApplicationBuilder app)
    {
        using var scope = app.ApplicationServices.CreateScope();
        var dbContext = scope.ServiceProvider.GetRequiredService<AuthenticationDbContext>();
        var userService = scope.ServiceProvider.GetRequiredService<IUserService>();
        var logger = scope.ServiceProvider.GetRequiredService<ILogger<AuthenticationDbContext>>();

        try
        {
            // Create database if it doesn't exist
            await dbContext.Database.EnsureCreatedAsync();
            logger.LogInformation("Authentication database initialized");

            // Create default admin user
            await userService.EnsureDefaultAdminExistsAsync();
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "Failed to initialize authentication database");
            throw;
        }

        return app;
    }
}
