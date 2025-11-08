using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using DeployForge.Api;
using System.Net.Http;

namespace DeployForge.Api.IntegrationTests;

/// <summary>
/// Base test fixture for API integration tests
/// </summary>
public class ApiTestFixture : WebApplicationFactory<Program>
{
    protected override IHost CreateHost(IHostBuilder builder)
    {
        // Configure test services
        builder.ConfigureServices(services =>
        {
            // Override services for testing if needed
            // For example, replace database with in-memory version
        });

        return base.CreateHost(builder);
    }

    public HttpClient CreateAuthenticatedClient()
    {
        var client = CreateClient();
        // Add authentication headers if needed
        return client;
    }
}

/// <summary>
/// Collection fixture for sharing test context across test classes
/// </summary>
[CollectionDefinition("API Integration Tests")]
public class ApiIntegrationTestCollection : ICollectionFixture<ApiTestFixture>
{
    // This class has no code, and is never created. Its purpose is simply
    // to be the place to apply [CollectionDefinition] and all the
    // ICollectionFixture<> interfaces.
}
